from cmath import exp
import os
import logging
from logging_loki import emitter, LokiHandler
from celery import Celery
from github import Github
from github.GithubException import *
from gorse import Gorse
import common

# Setup logger
logger = logging.getLogger("jobs")
logger.setLevel(logging.INFO)
loki_host = os.getenv("LOKI_HOST")
loki_port = os.getenv("LOKI_PORT")
if loki_host is not None and loki_port is not None:
    emitter.LokiEmitter.level_tag = "level"
    handler = LokiHandler(
        url="http://%s:%s/loki/api/v1/push" % (loki_host, loki_port),
        tags={"job": "gitrec"},
        version="1",
    )
    logger.addHandler(handler)

# Setup client
gorse_client = Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))

# Setup celery
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
