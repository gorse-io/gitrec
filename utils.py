import datetime
import logging
import os
import re
import sys
from typing import List, Optional, Tuple, Dict

import inflect
import nltk
import pytz
import requests
from dateutil import parser
from github import Github
from github.GithubException import *
from gorse import Gorse, GorseException
from logging_loki import LokiHandler, emitter
from nltk.corpus import stopwords
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base


CATEGORIES = {"book", "game"}


def generate_categories(labels: List[str]) -> List[str]:
    categories = []
    for label in labels:
        if label in CATEGORIES:
            categories.append(label)
    return categories


class LabelGenerator:
    """
    LabelGenerator generate labels from repo description.
    """

    def __init__(self, gorse_client: Gorse, min_freq: Optional[int] = 5):
        # Download punkt
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

        # Create singular noun converter
        self.inflect = inflect.engine()

        # Load stop words
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords")
        self.stopwords = set(stopwords.words("english"))

        # Load block list
        with open("blocklist.txt") as f:
            self.block_list = f.readlines()
            self.block_list = [v.strip() for v in self.block_list]
            self.block_list = set(self.block_list)

        # Load existed topics
        topic_count = dict()
        cursor = ""
        while True:
            items, cursor = gorse_client.get_items(1000, cursor)
            for item in items:
                if item["Labels"] is not None:
                    for topic in item["Labels"]:
                        if topic not in topic_count:
                            topic_count[topic] = 1
                        else:
                            topic_count[topic] += 1
            if cursor == "":
                break
        self.topics = []
        for topic, count in topic_count.items():
            if count >= min_freq and topic not in self.block_list:
                self.topics.append(topic)

    def extract(self, text: Optional[str]) -> List[str]:
        if text is None:
            return []
        # Tokenize description
        tokens = nltk.word_tokenize(text)
        tokens = [v.lower() for v in tokens]
        # Convert plural to singular noun
        for i, token in enumerate(tokens):
            singular = self.inflect.singular_noun(token)
            if singular:
                tokens[i] = singular
        sentence = "-".join(tokens)
        labels = []
        for label in self.topics:
            if "-" not in label:
                if label in tokens:
                    labels.append(label)
            else:
                if label in sentence:
                    labels.append(label)
        return labels

    def optimize(self, item: dict) -> Optional[dict]:
        # description is required
        description = item["Comment"]
        if description is None or len(description) == 0:
            return None
        # Remove URL from description
        description = re.sub(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
            "",
            description,
        )
        # extract topics
        labels = self.extract(description)
        if len(labels) == 0:
            return None
        if item["Labels"] is not None and len(item["Labels"]) > 0:
            labels.extend(item["Labels"])
        # Remove stop words
        labels = [w for w in labels if w not in self.stopwords]
        # Remove block list words
        labels = [w for w in labels if w not in self.block_list]
        # update labels
        labels = list(set(labels))
        # Fetch categories
        categories = generate_categories(labels)

        if (
            item["Labels"] is not None
            and len(labels) == len(item["Labels"])
            and item["Categories"] is not None
            and len(categories) == len(item["Categories"])
        ):
            return None
        item["Labels"] = labels
        item["Categories"] = categories
        return item


class LogFormatter(logging.Formatter):

    COLORS = {
        logging.DEBUG: "\x1b[38;20m",  # grey
        logging.INFO: "\x1b[32;20m",  # green
        logging.WARNING: "\x1b[33;20m",  # yellow
        logging.ERROR: "\x1b[31;20m",  # red
        logging.CRITICAL: "\x1b[34;20m",  # blue
    }

    def format(self, record):
        format = self.COLORS.get(record.levelno)
        format += "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
        if "tags" in record.__dict__:
            format += " %(tags)s"
        format += "\x1b[0m"
        formatter = logging.Formatter(format)
        return formatter.format(record)


def get_logger(name: str):
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
logger = get_logger("common")

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
        r = requests.post(
            "https://api.github.com/graphql",
            json={"query": q},
            headers={"Authorization": "bearer %s" % self.token},
        )
        # Handle response
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            raise BadCredentialsException(r.status_code, r.text, r.headers)
        else:
            raise GithubException(r.status_code, r.text, r.headers)

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


def get_repo_info(github_client: Github, full_name: str, generator: LabelGenerator):
    """
    Get GitHub repository information.
    """
    repo = github_client.get_repo(full_name)
    # Fetch labels.
    labels = [topic for topic in repo.get_topics()]
    if repo.language is not None and repo.language not in labels:
        labels.append(repo.language.lower())
    item = {
        "ItemId": full_name.replace("/", ":").lower(),
        "Timestamp": str(repo.updated_at),
        "Labels": labels,
        "Categories": generate_categories(labels),
        "Comment": repo.description,
    }
    optimized = generator.optimize(item)
    if optimized:
        item = optimized
    return item


def update_user(
    gorse_client: Gorse,
    token: str,
    pulled_at: datetime.datetime,
    generator: LabelGenerator,
):
    """
    Update GitHub user labels and starred repositories.
    """
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
            item = get_repo_info(github_client, full_name, generator)
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
