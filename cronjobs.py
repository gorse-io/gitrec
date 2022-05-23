import datetime
import os

import requests
from bs4 import BeautifulSoup
from github import Github
from github.GithubException import *
from gorse import Gorse
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

import common

# Setup logger
logger = common.getLogger("cronjobs")

# Setup clients
github_client = Github(os.getenv("GITHUB_ACCESS_TOKEN"))
gorse_client = Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))

# Setup sqlalchemy
engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
Session = sessionmaker()
Session.configure(bind=engine)


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
            gorse_client.insert_item(common.get_repo_info(github_client, trending_repo))
            trending_count += 1
        except Exception as e:
            logger.error(
                "failed to insert trending repository",
                extra={"tags": {"repo": trending_repo, "exception": str(e)}},
            )
    logger.info("insert trending repository succeed", extra={"tags": {"num_repos": trending_count}})


def update_user():
    """
    Update user starred repositories.
    """
    session = Session()
    for user in session.query(common.User).filter(
        or_(
            common.User.pulled_at == None,
            common.User.pulled_at
            < datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
    ):
        # print(user.login, user.token["access_token"], user.pulled_at)
        try:
            common.update_user(gorse_client, user.token["access_token"], user.pulled_at)
            user.pulled_at = datetime.datetime.now()
        except BadCredentialsException as e:
            session.delete(user)
            logger.warning(
                "invalid user token",
                extra={"tags": {"login": user.login, "exception": str(e)}},
            )
        session.commit()


if __name__ == "__main__":
    # Insert trending repositories.
    try:
        insert_trending()
    except Exception as e:
        logger.exception("failed to insert trending repositories")

    # Update user labels and feedback.
    try:
        update_user()
    except Exception as e:
        logger.exception("failed to update user labels and feedback")
