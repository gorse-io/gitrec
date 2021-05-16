import os

import mistune
from bs4 import BeautifulSoup
from flask import Flask, Response, session, redirect, url_for
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import make_github_blueprint, github
from github import Github

import gorse

app = Flask(__name__, static_folder='../frontend/dist', static_url_path="/")
app.secret_key = os.getenv("SECRET_KEY")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.getenv("GITHUB_OAUTH_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
blueprint = make_github_blueprint()
app.register_blueprint(blueprint, url_prefix="/login")

gorse_client = gorse.Gorse()


@app.route('/')
def index():
    return app.send_static_file('login.html')
    # if not github.authorized:
    #     return app.send_static_file('login.html')
    # resp = github.get("/user")
    # session['user_id'] = resp.json()["login"]
    # return app.send_static_file('index.html')


@app.route("/api/repo/")
def get_repo():
    if not github.authorized:
        return Response("Permission denied", status=403)
    repo_id = gorse_client.get_recommend(session['user_id'])[0]
    full_name = repo_id.replace(':', '/')
    github_client = Github(github.token['access_token'])
    repo = github_client.get_repo(full_name)
    # convert readme to html
    html = mistune.html(repo.get_readme().decoded_content.decode('utf-8'))
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a'):
        # open links in new tab
        a.attrs['target'] = "__blank"
        # redirect links to github
        src = a.attrs['href']
        if not src.startswith('http://') and not src.startswith('https://'):
            a.attrs['href'] = repo.html_url + '/blob/master/' + src
    for img in soup.find_all('img'):
        # redirect links to github
        src = img.attrs['src']
        if not src.startswith('http://') and not src.startswith('https://'):
            img.attrs['src'] = repo.html_url + '/raw/master/' + src
    return {
        'item_id': repo_id,
        'full_name': repo.full_name,
        'html_url': repo.html_url,
        'stargazers_url': repo.stargazers_url,
        'forks_url': repo.forks_url,
        'stargazers': repo.get_stargazers().totalCount,
        'forks': repo.get_forks().totalCount,
        'readme': str(soup),
    }


@app.route("/login")
def login():
    return redirect(url_for("github.login"))


@app.route("/api/like/<repo_name>")
def like_repo(repo_name: str):
    if not github.authorized:
        return Response("Permission denied", status=403)
    try:
        return gorse_client.insert_feedback('like', session['user_id'], repo_name)
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)


@app.route("/api/read/<repo_name>")
def read_repo(repo_name: str):
    if not github.authorized:
        return Response("Permission denied", status=403)
    try:
        return gorse_client.insert_feedback('read', session['user_id'], repo_name)
    except gorse.GorseException as e:
        return Response(e.message, status=e.status_code)
