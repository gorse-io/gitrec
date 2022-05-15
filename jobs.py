from cmath import exp
import os
from typing import Dict, List, Tuple

import requests
from celery import Celery
from github import Github
from github.GithubException import *

from gorse import Gorse
import common


gorse_client = Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))


app = Celery("jobs", broker=os.getenv("BROKER_ADDRESS"))


@app.task
def pull(token: str):
    github_client = Github(token)
    # Pull user labels
    user = common.get_user_info(github_client)
    gorse_client.insert_user(user)
    print("insert user `%s` with %d labels" % (user["UserId"], len(user["Labels"])))
    # Pull user starred repos
    g = common.GraphQLGitHub(token)
    stars = g.get_viewer_starred()
    stars.reverse()
    # Pull items
    item_count, pull_count = 0, 0
    for feedback in stars:
        if pull_count > 100:
            break
        item_id = feedback["ItemId"]
        full_name = item_id.replace(":", "/")
        item = common.get_repo_info(github_client, full_name)
        if item is not None:
            gorse_client.insert_item(item)
            item_count += 1
        pull_count += 1
    print("insert %d items from user `%s`" % (item_count, user["UserId"]))
    # Insert feedback
    gorse_client.insert_feedbacks(stars)
    print("insert %d feedback from user `%s`" % (len(stars), user["UserId"]))
