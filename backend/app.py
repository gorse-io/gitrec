import markdown
from flask import Flask, redirect, url_for, Response, session
from flask_dance.contrib.github import make_github_blueprint, github
from github import Github
import os

import gorse

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.getenv("GITHUB_OAUTH_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
blueprint = make_github_blueprint()
app.register_blueprint(blueprint, url_prefix="/login")

gorse_client = gorse.Gorse()


@app.route("/")
def index():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    print(github.token)
    session['user_id'] = resp.json()["login"]
    assert resp.ok
    return "You are @{login} on GitHub".format(login=resp.json()["login"])


@app.route("/repo/")
def get_repo():
    if not github.authorized:
        return Response("Permission denied", status=403)
    repo_id = gorse_client.get_recommend(session['user_id'])[0]
    full_name = repo_id.replace(':', '/')
    github_client = Github(github.token['access_token'])
    repo = github_client.get_repo(full_name)
    return {
        'item_id': repo_id,
        'full_name': repo.full_name,
        'html_url': repo.html_url,
        'stargazers_url': repo.stargazers_url,
        'forks_url': repo.forks_url,
        'stargazers': repo.get_stargazers().totalCount,
        'forks': repo.get_forks().totalCount,
        'readme': markdown.markdown(repo.get_readme().decoded_content.decode('unicode-escape')),
    }


@app.route("/like/<repo_name>")
def like_repo(repo_name: str):
    if not github.authorized:
        return Response("Permission denied", status=403)
    try:
        return gorse_client.insert_feedback('like', session['user_id'], repo_name)
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/read/<repo_name>")
def read_repo(repo_name: str):
    if not github.authorized:
        return Response("Permission denied", status=403)
    try:
        return gorse_client.insert_feedback('read', session['user_id'], repo_name)
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)
