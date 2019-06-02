import json
import re
import os.path
import requests
from urllib.parse import urlencode
from datetime import datetime
from urllib.request import urlopen

from flask import Flask, render_template, redirect, session, flash, g
from flask_openid import OpenID
from flask_sqlalchemy import SQLAlchemy
from werkzeug.urls import url_encode

app = Flask(__name__)
app.config.from_envvar('STEAMLENS_SETTINGS')

oid = OpenID(app, os.path.join(os.path.dirname(__file__), app.config['OPENID_STIRE']))
db = SQLAlchemy(app)

#######################
# Recommender Service #
#######################

@app.context_processor
def inject_current_time():
    return {'current_time': datetime.utcnow()}


@app.route('/')
def index():
    return redirect('/pop')


@app.route('/pop')
def pop():
    # Get nickname
    nickname = None
    if g.user:
        nickname = g.user.nickname
    # Get items
    r = requests.get('http://127.0.0.1:8080/popular?number=30')
    items = [v['ItemId'] for v in r.json()]
    # Render page
    return render_template('page_gallery.jinja2', title='Popular Games', items=items, nickname=nickname)


@app.route('/random')
def random():
    # Get nickname
    nickname = None
    if g.user:
        nickname = g.user.nickname
    # Get items
    r = requests.get('http://127.0.0.1:8080/random?number=30')
    items = [v['ItemId'] for v in r.json()]
    # Render page
    return render_template('page_gallery.jinja2', title='Random Games', items=items, nickname=nickname)


@app.route('/recommend')
def recommend():
    # Check login
    if g.user is None:
        return render_template('page_gallery.jinja2', title='Please login first', items=[])
    # Get items
    r = requests.get('http://127.0.0.1:8080/recommends/%s?number=30' % g.user.steam_id)
    # Render page
    if r.status_code == 200:
        items = [v['ItemId'] for v in r.json()]
        return render_template('page_gallery.jinja2', title='Recommended Games', items=items, nickname=g.user.nickname)
    return render_template('page_gallery.jinja2', title='Generating Recommended Games...', items=[], nickname=g.user.nickname)


@app.route('/item/<int:app_id>')
def item(app_id: int):
    # Get nickname
    nickname = None
    if g.user:
        nickname = g.user.nickname
    # Get items
    r = requests.get('http://127.0.0.1:8080/neighbors/%d?number=30' % app_id)
    items = [v['ItemId'] for v in r.json()]
    # Render page
    return render_template('page_app.jinja2', item_id=app_id, title='Similar Games', items=items, nickname=nickname)


@app.route('/user')
def user():
    # Check login
    if g.user is None:
        return render_template('page_gallery.jinja2', title='Please login first', items=[])
    # Get items
    r = requests.get('http://127.0.0.1:8080/user/%s' % g.user.steam_id)
    # Render page
    if r.status_code == 200:
        items = [v['ItemId'] for v in r.json()]
        return render_template('page_gallery.jinja2', title='Owned Games', items=items, nickname=g.user.nickname)
    return render_template('page_gallery.jinja2', title='Synchronizing Owned Games ...', items=[], nickname=g.user.nickname)

#################
# Steam Service #
#################

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String(40))
    nickname = db.Column(db.String(80))

    @staticmethod
    def get_or_create(steam_id):
        rv = User.query.filter_by(steam_id=steam_id).first()
        if rv is None:
            rv = User()
            rv.steam_id = steam_id
            db.session.add(rv)
        return rv


@app.route("/login")
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    else:
        return oid.try_login("http://steamcommunity.com/openid")


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/pop')


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter_by(id=session['user_id']).first()


@oid.after_login
def new_user(resp):
    _steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')
    match = _steam_id_re.search(resp.identity_url)
    g.user = User.get_or_create(match.group(1))
    steamdata = get_steam_userinfo(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    db.session.commit()
    session['user_id'] = g.user.id
    # Add games to gorse
    games = get_owned_games(g.user.steam_id)
    data = [{'UserId': int(g.user.steam_id), 'ItemId': int(v['appid']), 'Feedback': float(v['playtime_forever'])} for v in games]
    headers = {"Content-Type": "application/json"}
    requests.put('http://127.0.0.1:8080/feedback', data=json.dumps(data), headers=headers)
    return redirect(oid.get_next_url())


def get_steam_userinfo(steam_id):
    options = {
        'key': app.secret_key,
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
          'GetPlayerSummaries/v0001/?%s' % urlencode(options)
    rv = json.load(urlopen(url))
    return rv['response']['players']['player'][0] or {}


def get_owned_games(steam_id):
    options = {
        'key': app.secret_key,
        'steamid': steam_id,
        'format': 'json'
    }
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?%s' % urlencode(options)
    rv = json.load(urlopen(url))
    return rv['response']['games']


db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
