import datetime
import os
from threading import Thread

import requests
from bs4 import BeautifulSoup
from github import Github
from github.GithubException import *
from gorse import Gorse
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

import common
from labels import LabelGenerator

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
    logger.info(
        "insert trending repository succeed",
        extra={"tags": {"num_repos": trending_count}},
    )


def insert_trending_handler():
    try:
        insert_trending()
    except Exception as e:
        logger.exception("failed to insert trending repositories")


def update_users():
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


def insert_users_handler():
    try:
        update_users()
    except Exception as e:
        logger.exception("failed to update user labels and feedback")


def generate_labels():
    """
    Generate labels for items without any label
    """
    logger.info("start to generate labels for items")
    generator = LabelGenerator(gorse_client)
    total_count, generate_count, success_count = 0, 0, 0
    cursor = ""
    while True:
        items, cursor = gorse_client.get_items(1000, cursor)
        for item in items:
            total_count += 1
            if (item["Labels"] is None or len(item["Labels"]) <= 1) and item[
                "Comment"
            ] is not None:
                # Generate labels for items
                generate_count += 1
                labels = generator.extract(item["Comment"])
                is_success = False
                if len(labels) > 1:
                    success_count += 1
                    is_success = True
                if (
                    item["Labels"] is not None
                    and len(item["Labels"]) == 1
                    and item["Labels"][0] not in labels
                ):
                    labels.append(item["Labels"][0])
                # Update labels
                if is_success:
                    gorse_client.update_item(item['ItemId'], labels=labels)
        if cursor == "":
            break
    logger.info(
        "generate labels for items successfully",
        extra={
            "tags": {
                "total_item_count": total_count,
                "total_generate_count": generate_count,
                "success_generate_count": success_count,
            }
        },
    )


def generate_labels_handler():
    try:
        generate_labels()
    except Exception as e:
        logger.exception("failed to insert trending repositories")


if __name__ == "__main__":
    threads = [
        Thread(target=generate_labels_handler),
        Thread(target=insert_users_handler),
        Thread(target=insert_trending_handler)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
