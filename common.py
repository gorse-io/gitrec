from typing import List, Tuple, Dict
import requests
from logging_loki import LokiHandler, emitter
from sqlalchemy.orm import declarative_base
import logging
import os
from gorse import Gorse
from github import Github
from sqlalchemy import Column, String, Integer, DateTime, JSON
from github.GithubException import *


# Setup logger
logger = logging.getLogger("common")
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

    def __get_starred(self, n: int) -> List[Tuple[str, str]]:
        stars = []
        cursor = ""
        has_next_page = True
        while has_next_page and len(stars) < n:
            query = (
                'query { viewer { starredRepositories(first: 100, after: "%s") { '
                "nodes { nameWithOwner } edges { starredAt } pageInfo { endCursor hasNextPage } } } }"
                % cursor
            )
            starred_repositories = self.__query(query)["data"]["viewer"][
                "starredRepositories"
            ]
            for node, edge in zip(
                starred_repositories["nodes"], starred_repositories["edges"]
            ):
                stars.append((node["nameWithOwner"], edge["starredAt"]))
            cursor = starred_repositories["pageInfo"]["endCursor"]
            has_next_page = starred_repositories["pageInfo"]["hasNextPage"]
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

    def get_starred(self, n: int = 100) -> List[Dict]:
        stars = []
        user_id = self.__get_login()
        for item_id, timestamp in self.__get_starred(n):
            stars.append(
                {
                    "FeedbackType": "star",
                    "UserId": user_id.lower(),
                    "ItemId": item_id.replace("/", ":").lower(),
                    "Timestamp": timestamp,
                }
            )
        return stars


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
    # TODO: Generate topcis from README.md
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


def get_user_info(github_client: Github):
    """
    Get GitHub user information.
    """
    user = github_client.get_user()
    # Get n latest repos
    repos = []
    for repo in user.get_repos():
        repos.append(repo)
    # Collect topics and languages
    topics_set = set()
    for repo in repos:
        try:
            topics_set.update(repo.get_topics())
            languages = list(repo.get_languages().items())
            if len(languages) > 0:
                topics_set.add(languages[0][0].lower())
        except GithubException as e:
            if e.status not in {403, 404, 451}:
                raise e
            else:
                logger.warning(
                    "repository is unaviable",
                    extra={"tags": {"full_name": repo.full_name, "exception": str(e)}},
                )
    return {"Labels": list(topics_set), "UserId": user.login.lower()}


def update_user(gorse_client: Gorse, token: str):
    """
    Update GitHub user labels and starred repositories.
    """
    github_client = Github(token)
    # Pull user labels
    user = get_user_info(github_client)
    gorse_client.insert_user(user)
    logger.info(
        "update user",
        extra={"tags": {"user_id": user["UserId"], "num_labels": len(user["Labels"])}},
    )
    # Pull user starred repos
    graphql_client = GraphQLGitHub(token)
    stars = graphql_client.get_starred()
    stars.reverse()
    # Pull items
    item_count, pull_count = 0, 0
    for feedback in stars:
        if pull_count > 100:
            break
        item_id = feedback["ItemId"]
        full_name = item_id.replace(":", "/")
        repo = github_client.get_repo(full_name)
        if repo.stargazers_count > 100:
            item = get_repo_info(github_client, full_name)
            if item is not None:
                gorse_client.insert_item(item)
                item_count += 1
            pull_count += 1
    logger.info(
        "insert items from user",
        extra={"tags": {"user_id": user["UserId"], "num_items": item_count}},
    )
    # Insert feedback
    gorse_client.insert_feedbacks(stars)
    logger.info(
        "insert feedback from user",
        extra={"tags": {"user_id": user["UserId"], "num_feedback": len(stars)}},
    )
