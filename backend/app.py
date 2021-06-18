import os
from datetime import datetime

import mistune
from bs4 import BeautifulSoup
from dateutil import parser
from docutils.core import publish_parts
from flask import Flask, Response, session, redirect
from flask_dance.contrib.github import make_github_blueprint, github
from github import Github
from werkzeug.middleware.proxy_fix import ProxyFix

import gorse
from crawler_starred import pull

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = os.getenv("SECRET_KEY")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.getenv("GITHUB_OAUTH_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
blueprint = make_github_blueprint()
app.register_blueprint(blueprint, url_prefix="/login")

gorse_client = gorse.Gorse(os.getenv("GORSE_ADDRESS"))


@app.route("/")
def index():
    if not github.authorized:
        return redirect("/login")
    # pull user_id
    if "user_id" not in session:
        resp = github.get("/user")
        session["user_id"] = resp.json()["login"]
    # pull starred
    if (
        "last_pull" not in session
        or (parser.parse(session["last_pull"]) - datetime.now()).days >= 1
    ):
        pull.delay(github.token["access_token"])
        session["last_pull"] = str(datetime.now())
    return app.send_static_file("index.html")


@app.route("/login")
def login():
    return app.send_static_file("login.html")


@app.route("/api/repo")
def get_repo():
    if not github.authorized:
        return Response("Permission denied", status=403)
    repo_id = gorse_client.get_recommend(session["user_id"])[0]
    full_name = repo_id.replace(":", "/")
    github_client = Github(github.token["access_token"])
    repo = github_client.get_repo(full_name)
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
    for img in soup.find_all("img"):
        # redirect links to github
        src = img.attrs["src"]
        if not src.startswith("http://") and not src.startswith("https://"):
            if src.startswith("./"):
                src = src[2:]
            img.attrs["src"] = repo.html_url + "/raw/" + repo.default_branch + "/" + src
    return {
        "item_id": repo_id,
        "full_name": repo.full_name,
        "html_url": repo.html_url,
        "stargazers_url": repo.stargazers_url,
        "forks_url": repo.forks_url,
        "stargazers": repo.get_stargazers().totalCount,
        "forks": repo.get_forks().totalCount,
        "readme": str(soup),
    }


@app.route("/api/like/<repo_name>")
def like_repo(repo_name: str):
    if not github.authorized:
        return Response("Permission denied", status=403)
    try:
        return gorse_client.insert_feedback("like", session["user_id"], repo_name)
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/read/<repo_name>")
def read_repo(repo_name: str):
    if not github.authorized:
        return Response("Permission denied", status=403)
    try:
        return gorse_client.insert_feedback("read", session["user_id"], repo_name)
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)
