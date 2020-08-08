import json
import os.path
import re
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen

import requests
from flask import Flask, render_template, redirect, session, g
from flask_openid import OpenID
from flask_sqlalchemy import SQLAlchemy

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
    r = requests.get('%s/popular?number=%d' % (app.config['GORSE_API_URI'], app.config['GORSE_NUM_ITEMS']))
    items = [v['ItemId'] for v in r.json()]
    # Render page
    return render_template('page_gallery.jinja2', title='Popular Games', items=items, nickname=nickname)


@app.route('/latest')
def latest():
    # Get nickname
    nickname = None
    if g.user:
        nickname = g.user.nickname
    # Get items
    r = requests.get('%s/latest?number=%d' % (app.config['GORSE_API_URI'], app.config['GORSE_NUM_ITEMS']))
    items = [v['ItemId'] for v in r.json()]
    # Render page
    return render_template('page_gallery.jinja2', title='Latest Games', items=items, nickname=nickname)


@app.route('/random')
def random():
    # Get nickname
    nickname = None
    if g.user:
        nickname = g.user.nickname
    # Get items
    r = requests.get('%s/random?number=%d' % (app.config['GORSE_API_URI'], app.config['GORSE_NUM_ITEMS']))
    items = [v['ItemId'] for v in r.json()]
    # Render page
    return render_template('page_gallery.jinja2', title='Random Games', items=items, nickname=nickname)


@app.route('/recommend')
def recommend():
    # Check login
    if g.user is None:
        return render_template('page_gallery.jinja2', title='Please login first', items=[])
    # Get items
    r = requests.get('%s/recommends/%s?number=%s' %
                     (app.config['GORSE_API_URI'], g.user.steam_id, app.config['GORSE_NUM_ITEMS']))
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
    r = requests.get('%s/neighbors/%d?number=%d' %
                     (app.config['GORSE_API_URI'], app_id, app.config['GORSE_NUM_ITEMS']))
    items = [v['ItemId'] for v in r.json()]
    # Render page
    return render_template('page_app.jinja2', item_id=app_id, title='Similar Games', items=items, nickname=nickname)


@app.route('/user')
def user():
    # Check login
    if g.user is None:
        return render_template('page_gallery.jinja2', title='Please login first', items=[])
    # Get items
    r = requests.get('%s/user/%s/feedback' % (app.config['GORSE_API_URI'], g.user.steam_id))
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
    steamdata = get_user_info(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    db.session.commit()
    session['user_id'] = g.user.id
    # Add games to gorse
    games = get_owned_games(g.user.steam_id)
    data = [{'UserId': str(g.user.steam_id), 'ItemId': str(v['appid']), 'Rating': float(v['playtime_forever'])} for v in games]
    headers = {"Content-Type": "application/json"}
    requests.put('http://127.0.0.1:8080/feedback', data=json.dumps(data), headers=headers)
    return redirect(oid.get_next_url())


def get_user_info(steam_id):
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


def get_friend_list(steam_id: str):
    options = {
        'key': app.secret_key,
        'steamid': steam_id,
        'format': 'json',
        'relationship': 'friend'
    }
    url = 'http://api.steampowered.com/IPlayerService/GetFriendList/v0001/?%s' % urlencode(options)
    rv = json.load(urlopen(url))
    return rv['friendslist']['friends']


# Create tables if not exists.
db.create_all()
