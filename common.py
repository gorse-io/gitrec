import datetime
import logging
import os
import sys
from typing import List, Tuple, Dict

import pytz
import requests
from dateutil import parser
from github import Github
from gorse import Gorse, GorseException
from logging_loki import LokiHandler, emitter
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base


class LogFormatter(logging.Formatter):

    COLORS = {
        logging.DEBUG: "\x1b[38;20m",   # grey
        logging.INFO: "\x1b[32;20m",    # green
        logging.WARNING: "\x1b[33;20m", # yellow
        logging.ERROR: "\x1b[31;20m",   # red
        logging.CRITICAL: "\x1b[34;20m",# blue
    }

    def format(self, record):
        format = self.COLORS.get(record.levelno)
        format += "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
        if "tags" in record.__dict__:
            format += " %(tags)s"
        format += "\x1b[0m"
        formatter = logging.Formatter(format)
        return formatter.format(record)


def getLogger(name: str):
    """
    Create a Loki logger.
    """
    loki_logger = logging.getLogger(name)
    loki_logger.setLevel(logging.INFO)
    loki_host = os.getenv("LOKI_HOST")
    loki_port = os.getenv("LOKI_PORT")
    if loki_host is not None and loki_port is not None:
        emitter.LokiEmitter.level_tag = "level"
        handler = LokiHandler(
            url="http://%s:%s/loki/api/v1/push" % (loki_host, loki_port),
            tags={"job": "gitrec"},
            version="1",
        )
        loki_logger.addHandler(handler)
    # Logging to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(LogFormatter())
    loki_logger.addHandler(handler)
    return loki_logger


# Setup logger
logger = getLogger("common")

Base = declarative_base()


class User(Base):
    __tablename__ = "flask_dance_oauth"
    id = Column(Integer, primary_key=True)
    provider = Column(String)
    created_at = Column(DateTime)
    token = Column(JSON)
    login = Column(String)
    pulled_at = Column(DateTime)


class GraphQLGitHub:
    """
    GraphQL client for GitHub APIs.
    """

    def __init__(self, token: str):
        self.token = token

    def __get_login(self) -> str:
        query = "query { viewer { login } }"
        return self.__query(query)["data"]["viewer"]["login"]

    def __get_starred(self, pulled_at: datetime.datetime) -> List[Tuple[str, str]]:
        stars = []
        cursor = ""
        has_next_page = True
        while has_next_page:
            query = (
                'query { viewer { starredRepositories(first: 10, after: "%s", orderBy: { direction: DESC, field: STARRED_AT }) { '
                "nodes { nameWithOwner } edges { starredAt } pageInfo { endCursor hasNextPage } } } }"
                % cursor
            )
            result = self.__query(query)
            starred_repositories = result["data"]["viewer"]["starredRepositories"]
            for node, edge in zip(
                starred_repositories["nodes"], starred_repositories["edges"]
            ):
                stars.append((node["nameWithOwner"], edge["starredAt"]))
            cursor = starred_repositories["pageInfo"]["endCursor"]
            has_next_page = starred_repositories["pageInfo"]["hasNextPage"]
            if len(stars) > 0 and pulled_at is not None:
                star_at = parser.parse(stars[-1][1])
                utc_pulled_at = pytz.UTC.localize(pulled_at)
                if star_at < utc_pulled_at:
                    break
        return stars

    def __query(self, q):
        # Send query
        request = requests.post(
            "https://api.github.com/graphql",
            json={"query": q},
            headers={"Authorization": "bearer %s" % self.token},
        )
        # Handle response
        if request.status_code == 200:
            return request.json()
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, q
            )
        )

    def get_starred(self, pulled_at: datetime.datetime = None) -> List[Dict]:
        stars = []
        user_id = self.__get_login()
        for item_id, timestamp in self.__get_starred(pulled_at):
            stars.append(
                {
                    "FeedbackType": "star",
                    "UserId": user_id.lower(),
                    "ItemId": item_id.replace("/", ":").lower(),
                    "Timestamp": timestamp,
                }
            )
        return stars

    def get_contributed(self) -> List[str]:
        repositories = []
        cursor = ""
        has_next_page = True
        while has_next_page:
            query = (
                "{ viewer { repositoriesContributedTo(first: 10, %s includeUserRepositories: true) { "
                "nodes { nameWithOwner } pageInfo { endCursor hasNextPage } } } }"
                % cursor
            )
            result = self.__query(query)
            contributed_repositories = result["data"]["viewer"][
                "repositoriesContributedTo"
            ]
            for node in contributed_repositories["nodes"]:
                repositories.append(node["nameWithOwner"])
            cursor = 'after: "%s",' % contributed_repositories["pageInfo"]["endCursor"]
            has_next_page = contributed_repositories["pageInfo"]["hasNextPage"]
        return repositories


def get_repo_info(github_client: Github, full_name: str):
    """
    Get GitHub repository information.
    """
    repo = github_client.get_repo(full_name)
    # Fetch labels.
    labels = [topic for topic in repo.get_topics()]
    languages = list(repo.get_languages().items())
    if len(languages) > 0:
        main_language = languages[0][0].lower()
        if main_language not in labels:
            labels.append(main_language)
    # Fetch categories.
    categories = []
    # TODO: Generate topics from README.md
    # try:
    #     readme = repo.get_readme().decoded_content.decode("utf-8")
    # except UnknownObjectException as e:
    #     logger.warning(
    #         "readme not found",
    #         extra={"tags": {"full_name": full_name, "exception": str(e)}},
    #     )
    return {
        "ItemId": full_name.replace("/", ":").lower(),
        "Timestamp": str(repo.updated_at),
        "Labels": labels,
        "Categories": categories,
        "Comment": repo.description,
    }


def get_user_info(gorse_client: Gorse, token: str):
    """
    Get GitHub user information.
    """
    github_client = Github(token)
    graphql_client = GraphQLGitHub(token)
    # Get n latest repos
    repos = []
    for repo in graphql_client.get_contributed():
        repos.append(repo)
    # Collect topics and languages
    topics_set = set()
    for repo in repos:
        try:
            item = gorse_client.get_item(repo.replace("/", ":"))
            topics_set.update(item["Labels"])
        except GorseException as e:
            if e.status_code != 404:
                raise e
            else:
                logger.debug(
                    "repository has not been indexed",
                    extra={"tags": {"full_name": repo, "exception": str(e)}},
                )
    return {
        "Labels": list(topics_set),
        "UserId": github_client.get_user().login.lower(),
    }


def update_user(gorse_client: Gorse, token: str, pulled_at: datetime.datetime):
    """
    Update GitHub user labels and starred repositories.
    """
    # Pull user labels
    user = get_user_info(gorse_client, token)
    gorse_client.insert_user(user)
    logger.info(
        "update user labels succeed",
        extra={"tags": {"user_id": user["UserId"], "num_labels": len(user["Labels"])}},
    )
    # Pull user starred repos
    github_client = Github(token)
    graphql_client = GraphQLGitHub(token)
    stars = graphql_client.get_starred(pulled_at)
    # Pull items
    item_count, pull_count = 0, 0
    for feedback in stars:
        item_id = feedback["ItemId"]

        try:
            # Skip indexed repositories.
            item = gorse_client.get_item(item_id)
            continue
        except GorseException:
            pass

        full_name = item_id.replace(":", "/")
        repo = github_client.get_repo(full_name)
        if repo.stargazers_count > 100:
            # Repositories indexed by Gorse must have stargazers more than 100.
            item = get_repo_info(github_client, full_name)
            if item is not None:
                gorse_client.insert_item(item)
                item_count += 1
            pull_count += 1
    logger.info(
        "insert user starred repositories",
        extra={"tags": {"user_id": user["UserId"], "num_items": item_count}},
    )
    # Insert feedback
    gorse_client.insert_feedbacks(stars)
    logger.info(
        "insert feedback from user",
        extra={"tags": {"user_id": user["UserId"], "num_feedback": len(stars)}},
    )
