import json
import urllib.request
from urllib.parse import urlencode
from urllib.request import urlopen

import click
import progressbar
import requests


def get_owned_games(key, steam_id):
    options = {
        'key': key,
        'steamid': steam_id,
        'format': 'json'
    }
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?%s' % urlencode(options)
    rv = json.load(urlopen(url))
    response = rv['response']
    if 'games' in response:
        return rv['response']['games']
    return []


@click.command()
@click.argument('host')
@click.argument('port')
@click.argument('steam_key')
def main(host, port, steam_key):
    print('UPDATE USER FEEDBACK')
    # Get users
    with urllib.request.urlopen("http://%s:%s/users" % (host, port)) as url:
        users = json.loads(url.read().decode())
    print('TOTAL USERS:', len(users))
    # Get user feedback
    pb = progressbar.ProgressBar()
    for user in pb(users):
        games = get_owned_games(steam_key, user)
        data = [{'UserId': int(user), 'ItemId': int(v['appid']), 'Feedback': float(v['playtime_forever'])} for v in games]
        headers = {"Content-Type": "application/json"}
        requests.put('http://%s:%s/feedback' % (host, port), data=json.dumps(data), headers=headers)
    print('DONE')


if __name__ == '__main__':
    main()

