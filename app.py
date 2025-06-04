import concurrent.futures
import io
import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Optional

import asciidoc3
import emoji
import gorse
import mistune
from asciidoc3.asciidoc3api import AsciiDoc3API
from bs4 import BeautifulSoup
from docutils.core import publish_parts
from flask import Flask, Response, session, redirect, request, flash
from flask_cors import CORS
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.contrib.github import make_github_blueprint
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_user,
    login_required,
)
from flask_sqlalchemy import SQLAlchemy
from github import Github
from github.GithubException import UnknownObjectException
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.middleware.proxy_fix import ProxyFix

from jobs import pull

# create flask app
app = Flask(__name__, static_folder="./frontend/dist", static_url_path="/")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Setup logger
log_path = os.getenv("FLASK_LOG_PATH")
if log_path is not None:
    file_handler = logging.FileHandler(log_path)
    app.logger.addHandler(file_handler)

# setup database models
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)


class OAuth(OAuthConsumerMixin, UserMixin, db.Model):
    login = db.Column(db.String(256), unique=True, nullable=False)
    pulled_at = db.Column(db.DateTime())


# setup SQLAlchemy backend
blueprint = make_github_blueprint()
blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)

app.secret_key = os.getenv("SECRET_KEY")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.getenv("GITHUB_OAUTH_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
app.register_blueprint(blueprint, url_prefix="/login")

# cross-origin resource sharing
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# create gorse client and github client
gorse_client = gorse.Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))
global_github_client = Github(os.getenv("GITHUB_ACCESS_TOKEN"))

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return OAuth.query.get(int(user_id))


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def github_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with GitHub.", category="error")
        return False

    resp = blueprint.session.get("/user")
    if not resp.ok:
        msg = "Failed to fetch user info from GitHub."
        flash(msg, category="error")
        return False

    github_info = resp.json()
    github_login = str(github_info["login"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(login=github_login)
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            login=github_login,
            token=token,
        )
        db.session.add_all([oauth])
        db.session.commit()
        pull.delay(token["access_token"])

    login_user(oauth)
    flash("Successfully signed in with GitHub.")
    return False


@app.after_request
def set_headers(response):
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect("/login")
    session.permanent = True
    return app.send_static_file("index.html")


@app.route("/login")
def login():
    return app.send_static_file("login.html")


@app.route("/privacy")
def privacy():
    return app.send_static_file("privacy.html")


def is_github_blob(url: str) -> bool:
    splits = url.split("/")
    return (
        len(splits) > 5
        and splits[0] == "https:"
        and splits[2] == "github.com"
        and splits[5] == "blob"
    )


def convert_github_blob(url: str) -> str:
    splits = url.split("/")
    if (
        len(splits) > 5
        and splits[0] == "https:"
        and splits[2] == "github.com"
        and splits[5] == "blob"
    ):
        splits[5] = "raw"
    return "/".join(splits)


@app.route("/api/repo")
@app.route("/api/repo/<category>")
@login_required
def get_repo(category: str = ""):
    for _ in range(2):
        try:
            repo_id = gorse_client.get_recommend(current_user.login, category)[0]
            full_name = repo_id.replace(":", "/")
            github_client = Github(current_user.token["access_token"])
            repo = github_client.get_repo(full_name)
            download_url = repo.get_readme().download_url.lower()
            break
        except UnknownObjectException:
            logging.warn("repo %s not found" % repo_id)
            gorse_client.delete_item(repo_id)
    # convert readme to html
    content = repo.get_readme().decoded_content.decode("utf-8")
    if download_url.endswith(".rst"):
        html = publish_parts(content, writer_name="html")["html_body"]
    elif download_url.endswith(".asciidoc"):
        infile = io.StringIO(content)
        outfile = io.StringIO()
        asciidoc3api = AsciiDoc3API(asciidoc3.__path__[0] + '/asciidoc3.py')
        asciidoc3api.options('--no-header-footer')
        asciidoc3api.execute(infile, outfile, backend='html4')
        html = outfile.getvalue()
    else:
        html = mistune.html(content)
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a"):
        if "href" in a.attrs:
            # open links in new tab
            a.attrs["target"] = "__blank"
            # redirect links to github
            src = a.attrs["href"]
            if not src.startswith("http://") and not src.startswith("https://"):
                a.attrs["href"] = (
                    repo.html_url + "/blob/" + repo.default_branch + "/" + src
                )
    for img in soup.find_all("img"):
        # redirect links to github
        if "src" in img.attrs:
            src = img.attrs["src"]
            if not src.startswith("http://") and not src.startswith("https://"):
                if src.startswith("./"):
                    src = src[2:]
                img.attrs["src"] = (
                    repo.html_url + "/raw/" + repo.default_branch + "/" + src
                )
            elif is_github_blob(src):
                img.attrs["src"] = convert_github_blob(src)
    return {
        "item_id": repo_id,
        "full_name": repo.full_name,
        "html_url": repo.html_url,
        "stargazers_url": repo.stargazers_url,
        "forks_url": repo.forks_url,
        "stargazers_count": repo.stargazers_count,
        "forks_count": repo.forks_count,
        "subscribers_count": repo.subscribers_count,
        "language": repo.language,
        "readme": emoji.emojize(str(soup), use_aliases=True),
    }


@app.route("/api/favorites")
@login_required
def get_favorites():
    """
    List "star" and "like" feedback.
    """
    positive_feedbacks = []
    for feedback_type in ["star", "like"]:
        for feedback in gorse_client.list_feedbacks(feedback_type, current_user.login):
            feedback["ItemId"] = feedback["ItemId"].replace(":", "/")
            positive_feedbacks.append(feedback)
    positive_feedbacks = sorted(
        positive_feedbacks, key=lambda d: d["Timestamp"], reverse=True
    )
    return Response(json.dumps(positive_feedbacks), mimetype="application/json")


@app.route("/api/like/<repo_name>", methods=["POST"])
@login_required
def like_repo(repo_name: str):
    """
    Insert a "like" feedback.
    """
    try:
        gorse_client.insert_feedback(
            "read", current_user.login, repo_name.lower(), datetime.now().isoformat()
        )
        return gorse_client.insert_feedback(
            "like", current_user.login, repo_name.lower(), datetime.now().isoformat()
        )
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/read/<repo_name>", methods=["POST"])
@login_required
def read_repo(repo_name: str):
    """
    Insert a "read" feedback.
    """
    try:
        return gorse_client.insert_feedback(
            "read", current_user.login, repo_name.lower(), datetime.now().isoformat(), 1
        )
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/delete/<repo_name>", methods=["POST"])
@login_required
def delete_repo(repo_name: str):
    """
    Delete an item if the repository has been removed or renamed.
    """
    try:
        full_name = repo_name.replace(":", "/")
        try:
            repo = global_github_client.get_repo(full_name)
            if repo.full_name.lower() != full_name.lower():
                # This repository has been renamed.
                return gorse_client.delete_item(repo_name)
        except UnknownObjectException:
            # This repository has been removed.
            return gorse_client.delete_item(repo_name)
        return '{"RowAffected": 0}'
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


def fetch_repo(github_client: Github, item_id: str) -> Optional[dict]:
    full_name = item_id.replace(":", "/")
    try:
        repo = github_client.get_repo(full_name)
        if repo.full_name.lower() != full_name.lower():
            # This repository has been renamed.
            gorse_client.delete_item(item_id)
            return None
        return {
            "item_id": item_id,
            "full_name": repo.full_name,
            "description": repo.description,
            "html_url": repo.html_url,
            "stargazers_count": repo.stargazers_count,
            "language": repo.language,
        }
    except UnknownObjectException:
        # This repository has been removed.
        gorse_client.delete_item(item_id)
        return None


def fetch_repos(github_client: Github, item_ids: List[str]) -> List[dict]:
    repos = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(fetch_repo, github_client, item_id) for item_id in item_ids
        ]
    for future in concurrent.futures.as_completed(futures):
        repo = future.result()
        if repo is not None:
            repos[repo["item_id"]] = repo
    return [repos[item_id] for item_id in item_ids if item_id in repos]


@app.route("/api/neighbors/<repo_name>", methods=["GET"])
def get_neighbors(repo_name: str):
    try:
        n = int(request.args.get("n", default="3"))
        offset = int(request.args.get("offset", default="0"))
        repo_names = gorse_client.get_neighbors(repo_name.lower(), n, offset)
        return Response(json.dumps(repo_names), mimetype="application/json")
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/v2/neighbors/<repo_name>", methods=["GET"])
def get_neighbors_v2(repo_name: str):
    try:
        n = int(request.args.get("n", default="3"))
        offset = int(request.args.get("offset", default="0"))
        scores = gorse_client.get_neighbors(repo_name.lower(), n, offset)
        if not current_user.is_authenticated:
            return Response(
                json.dumps({"is_authenticated": False, "scores": scores}),
                mimetype="application/json",
            )
        else:
            github_client = Github(current_user.token["access_token"])
            return Response(
                json.dumps(
                    {
                        "is_authenticated": True,
                        "scores": scores,
                        "repos": fetch_repos(
                            github_client, [score["Id"] for score in scores]
                        ),
                    }
                ),
                mimetype="application/json",
            )
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/v2/extension/recommend", methods=["GET"])
def extension_recommend_v2():
    if not current_user.is_authenticated:
        return Response(
            json.dumps({"is_authenticated": False}),
            mimetype="application/json",
        )
    try:
        recommended_items = gorse_client.get_recommend(
            current_user.login, n=3, write_back_type="read", write_back_delay="24h"
        )
        github_client = Github(current_user.token["access_token"])
        return Response(
            json.dumps(
                {
                    "is_authenticated": True,
                    "items": recommended_items,
                    "repos": fetch_repos(github_client, recommended_items),
                }
            ),
            mimetype="application/json",
        )
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/session/recommend", methods=["POST"])
def session_recommend():
    try:
        repo_names = json.loads(request.data)
        feedbacks = [
            {
                "FeedbackType": "star",
                "ItemId": v,
                "Timestamp": datetime.utcnow().isoformat(),
            }
            for v in repo_names
        ]
        repo_names = gorse_client.session_recommend(feedbacks, 3)
        return Response(json.dumps(repo_names), mimetype="application/json")
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/extension/recommend/<user_id>", methods=["POST"])
def extension_recommend_latency(user_id: str):
    try:
        # If the user is in Gorse.
        gorse_client.get_user(user_id)
        try:
            repo_names = gorse_client.get_recommend(user_id, n=3)
            return Response(
                json.dumps({"has_login": True, "recommend": repo_names}),
                mimetype="application/json",
            )
        except gorse.GorseException as e:
            return Response(e.message, status=e.status_code)
    except gorse.GorseException as e:
        # If the user isn't in Gorse.
        try:
            repo_names = json.loads(request.data)
            feedbacks = [
                {
                    "FeedbackType": "star",
                    "ItemId": v,
                    "Timestamp": datetime.utcnow().isoformat(),
                }
                for v in repo_names
            ]
            scores = gorse_client.session_recommend(feedbacks, 3)
            repo_names = [v["Id"] for v in scores]
            return Response(
                json.dumps({"has_login": True, "recommend": repo_names}),
                mimetype="application/json",
            )
        except gorse.GorseException as e:
            return Response(e.message, status=e.status_code)


if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
