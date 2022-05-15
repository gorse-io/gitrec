import os
import logging
import logging_loki
import requests
from bs4 import BeautifulSoup
from github import Github
from github.GithubException import *
from gorse import Gorse
from common import get_repo_info

# Setup logger
handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"job": "cronjobs"},
    version="1",
)
logger = logging.getLogger("cronjobs")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Setup clients
github_client = Github(os.getenv("GITHUB_ACCESS_TOKEN"))
gorse_client = Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))


def get_trending():
    """
    Get trending repositories of C, C++, Go, Python, JS, Java, Rust, TS and unknown.
    """
    full_names = []
    languages = [
        "",
        "c",
        "c++",
        "go",
        "python",
        "javascript",
        "java",
        "rust",
        "typescript",
        "unknown",
        "?spoken_language_code=zh",
    ]
    for language in languages:
        r = requests.get("https://github.com/trending/%s" % language)
        if r.status_code != 200:
            return full_names
        soup = BeautifulSoup(r.text, "html.parser")
        for article in soup.find_all("article"):
            full_names.append(article.h1.a["href"][1:])
    return full_names


def insert_trending():
    """
    Insert trending repositories of C, C++, Go, Python, JS, Java, Rust, TS and unknown.
    """
    logger.info("start pull trending repos")
    trending_count = 0
    trending_repos = get_trending()
    for trending_repo in trending_repos:
        try:
            gorse_client.insert_item(get_repo_info(github_client, trending_repo))
            trending_count += 1
        except Exception as e:
            logger.error(
                "failed to insert trending repo",
                extra={"tags": {"repo": trending_repo, "exception": e}},
            )
    logger.info("insert trending repos", extra={"tags": {"num_repos": trending_count}})


def update_user_starred():
    """
    Update user starred repositories.
    """
    pass


if __name__ == "__main__":
    # Insert trending repositories.
    try:
        insert_trending()
    except Exception as e:
        logger.error(
            "failed to insert trending repos", extra={"tags": {"exception": e}}
        )
    # Update user starred repositories.
    # try:
    #     update_user_starred()
    # except Exception as e:
    #     logger.error('failed to update user starred repositories', extra={'tags': {'exception': e}})
