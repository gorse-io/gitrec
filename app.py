import json
import logging
import os
import sys
from datetime import datetime

import emoji
import gorse
import mistune
from bs4 import BeautifulSoup
from docutils.core import publish_parts
from flask import Flask, Response, session, redirect, request, flash
from flask_cors import CORS
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.contrib.github import make_github_blueprint
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required
from flask_sqlalchemy import SQLAlchemy
from github import Github
from github.GithubException import UnknownObjectException
from logging_loki import LokiHandler, emitter
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.middleware.proxy_fix import ProxyFix

from jobs import pull

# create flask app
app = Flask(__name__, static_folder="./frontend/dist", static_url_path="/")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Setup logger
loki_host = os.getenv("LOKI_HOST")
loki_port = os.getenv("LOKI_PORT")
if loki_host is not None and loki_port is not None:
    emitter.LokiEmitter.level_tag = "level"
    handler = LokiHandler(
        url="http://%s:%s/loki/api/v1/push" % (loki_host, loki_port),
        tags={"job": "gitrec"},
        version="1",
    )
    app.logger.addHandler(handler)

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
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# create gorse client
gorse_client = gorse.Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))

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
            break
        except UnknownObjectException:
            logging.warn("repo %s not found" % repo_id)
            gorse_client.delete_item(repo_id)
    # convert readme to html
    download_url = repo.get_readme().download_url.lower()
    content = repo.get_readme().decoded_content.decode("utf-8")
    if download_url.endswith(".rst"):
        html = publish_parts(content, writer_name="html")["html_body"]
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
    blob_url = repo.html_url + "/blob/"
    for img in soup.find_all("img"):
        # redirect links to github
        if "src" in img.attrs:
            src = img.attrs["src"]
            if not src.startswith("http://") and not src.startswith("https://"):
                if src.startswith("./"):
                    src = src[2:]
                img.attrs["src"] = repo.html_url + \
                                   "/raw/" + repo.default_branch + "/" + src
            elif src.startswith(blob_url):
                img.attrs["src"] = repo.html_url + \
                                   "/raw/" + src[len(blob_url):]
    return {
        "item_id": repo_id,
        "full_name": repo.full_name,
        "html_url": repo.html_url,
        "stargazers_url": repo.stargazers_url,
        "forks_url": repo.forks_url,
        "stargazers": repo.get_stargazers().totalCount,
        "forks": repo.get_forks().totalCount,
        "readme": emoji.emojize(str(soup), use_aliases=True),
    }


@app.route("/api/favorites")
@login_required
def get_favorites():
    positive_feedbacks = []
    for feedback_type in ["star", "like"]:
        for feedback in gorse_client.list_feedbacks(feedback_type, current_user.login):
            feedback["ItemId"] = feedback["ItemId"].replace(":", "/")
            positive_feedbacks.append(feedback)
    positive_feedbacks = sorted(
        positive_feedbacks, key=lambda d: d["Timestamp"], reverse=True
    )
    return Response(json.dumps(positive_feedbacks), mimetype="application/json")


@app.route("/api/like/<repo_name>")
@login_required
def like_repo(repo_name: str):
    try:
        gorse_client.insert_feedback("read", current_user.login, repo_name, datetime.now().isoformat())
        return gorse_client.insert_feedback("like", current_user.login, repo_name, datetime.now().isoformat())
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/read/<repo_name>")
@login_required
def read_repo(repo_name: str):
    try:
        return gorse_client.insert_feedback("read", current_user.login, repo_name, datetime.now().isoformat())
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/neighbors/<repo_name>")
def get_neighbors(repo_name: str):
    try:
        repo_names = gorse_client.get_neighbors(repo_name.lower())
        return Response(json.dumps(repo_names), mimetype="application/json")
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
def extension_recommend(user_id: str):
    try:
        # If the user is in Gorse.
        gorse_client.get_user(user_id)
        try:
            repo_names = gorse_client.get_recommend(user_id, n=3)
            return Response(json.dumps({
                'has_login': True,
                'recommend': repo_names
            }), mimetype="application/json")
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
            repo_names = [v['Id'] for v in scores]
            return Response(json.dumps({
                'has_login': True,
                'recommend': repo_names
            }), mimetype="application/json")
        except gorse.GorseException as e:
            return Response(e.message, status=e.status_code)


if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
