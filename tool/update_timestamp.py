import json
import urllib.request
from urllib.parse import urlencode
from urllib.request import urlopen

import click
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse


def get_release_date(app_id):
    url = requests.get("https://store.steampowered.com/app/%s" % app_id)
    soup = BeautifulSoup(url.text, features="html.parser")
    element = soup.find("div", {"class": "date"})
    if element is not None:
        return element.text
    return None


@click.command()
@click.argument('host')
@click.argument('port')
def main(host, port):
    print('UPDATE GAMES RELESE DATE')
    # Get games
    with urllib.request.urlopen("http://%s:%s/items" % (host, port)) as url:
        games = json.loads(url.read().decode())
    print('TOTAL GAMES:', len(games))

    for game in games:
        timestamp = parse(game['Timestamp'])
        if timestamp.year < 1970:
            # Get game release date
            app_id = game['ItemId']
            release_date = get_release_date(app_id)
            # Skip error
            if release_date is None:
                print("APP#%s: RELASE DATE NOT FOUND" % app_id)
                continue
            print("APP#%s: RELASE DATE <- %s" % (app_id, release_date))
            # Add timestamps to gorse
            data = [{"ItemId":app_id,"Timestamp":release_date}]
            headers = {"Content-Type": "application/json"}
            requests.put('http://%s:%s/items' % (host, port), data=json.dumps(data), headers=headers)
    print('DONE')

if __name__ == '__main__':
    main()

