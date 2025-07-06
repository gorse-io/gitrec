import datetime
import os
from threading import Thread

import click
import requests
from bs4 import BeautifulSoup
from github import Github
from github.GithubException import *
from gorse import Gorse
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from utils import *

# Setup logger
logger = get_logger("cronjobs")

# Setup clients
github_client = Github(os.getenv("GITHUB_ACCESS_TOKEN"))
gorse_client = Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))

# Setup sqlalchemy
engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
Session = sessionmaker()
Session.configure(bind=engine)


TRENDING_PAGES = [
    "",
    "python",
    "java",
    "javascript",
    "c++",
    "go",
    "typescript",
    "php",
    "ruby",
    "c",
    "c#",
    "nix",
    "shell",
    "scala",
    "rust",
    "kotlin",
    "dart",
    "swift",
    "unknown",
]


def get_trending():
    """
    Get trending repositories of C, C++, Go, Python, JS, Java, Rust, TS and unknown.
    """
    full_names = []
    for language_page in TRENDING_PAGES:
        r = requests.get("https://github.com/trending/%s" % language_page)
        if r.status_code != 200:
            return full_names
        soup = BeautifulSoup(r.text, "html.parser")
        for article in soup.find_all("article"):
            full_names.append(article.h2.a["href"][1:])
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
            item = get_repo_info(github_client, trending_repo)
            gorse_client.insert_item(item)
            trending_count += 1
        except Exception as e:
            logger.error(
                "failed to insert trending repository",
                extra={"tags": {"repo": trending_repo, "exception": str(e)}},
            )
    logger.info(
        "insert trending repository succeed",
        extra={"tags": {"num_repos": trending_count}},
    )


def insert_trending_entry():
    try:
        insert_trending()
    except Exception as e:
        logger.exception("failed to insert trending repositories")


def update_users():
    """
    Update user starred repositories.
    """
    session = Session()
    for user in session.query(User).filter(
        or_(
            User.pulled_at == None,
            User.pulled_at < datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
    ):
        # print(user.login, user.token["access_token"], user.pulled_at)
        try:
            update_user(
                gorse_client, user.token["access_token"], user.pulled_at)
            user.pulled_at = datetime.datetime.now()
        except BadCredentialsException as e:
            session.delete(user)
            logger.warning(
                "invalid user token",
                extra={"tags": {"login": user.login, "exception": str(e)}},
            )
        session.commit()


def insert_users_entry():
    try:
        update_users()
    except:
        logger.exception("failed to update user labels and feedback")


@click.command()
@click.option("--update-users", is_flag=True)
@click.option("--insert-trending", is_flag=True)
def main(update_users: bool, insert_trending: bool):
    threads = []
    run_all = update_users is False and insert_trending is False
    if run_all or insert_trending:
        threads.append(Thread(target=insert_trending_entry))
    if run_all or update_users:
        threads.append(Thread(target=insert_users_entry))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
