import datetime
import json
import logging
import os
import re
import sys
from typing import List, Optional, Tuple, Dict, Any

import pytz
import requests
from dateutil import parser
from github import Github
from github.GithubException import *
from gorse import Gorse, GorseException
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base
from openai import OpenAI
from pydantic import BaseModel

MAX_COMMENT_LENGTH = 512


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE")
)

# OpenAI model for chat completions (default: qwen-turbo)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "qwen-turbo")


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
    Create a logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Logging to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(LogFormatter())
    logger.addHandler(handler)
    return logger


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



class KvCache(Base):
    """Key-value cache model for storing API responses."""
    __tablename__ = 'kv_cache'

    k = Column(String(256), primary_key=True)
    v = Column(Text, nullable=False)
    expire = Column(DateTime, nullable=False)

    DEFAULT_EXPIRY_HOURS = 24

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return self.expire < datetime.datetime.utcnow()


def get_cached(k: str) -> Optional[Any]:
    """Get cached data by key. Returns None if not found or expired."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        cache = session.query(KvCache).filter(KvCache.k == k).first()
        if cache and not cache.is_expired():
            return json.loads(cache.v)
        return None
    finally:
        session.close()


def save_cache(k: str, v: Any, expiry_hours: int = KvCache.DEFAULT_EXPIRY_HOURS) -> None:
    """Save data to cache with optional expiry time in hours."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        cache = session.query(KvCache).filter(KvCache.k == k).first()
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
        if cache:
            cache.v = json.dumps(v)
            cache.expire = expire_time
        else:
            cache = KvCache(k=k, v=json.dumps(v), expire=expire_time)
            session.add(cache)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

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


def embedding(text: str) -> list:
    resp = openai_client.embeddings.create(
        model="text-embedding-v3",
        input=text,
        dimensions=512,
    )
    return resp.data[0].embedding


def tldr(text: str) -> str:
    prompt = (
        "Write a short description of the GitHub repository in one sentence. "
        + "Don't start with 'This GitHub repository' or 'A GitHub repository'. "
        + f"The README of the repository is: \n\n{text}"
    )
    resp = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return resp.choices[0].message.content


class AIRelevance(BaseModel):
    """Model for AI relevance detection."""

    is_ai_related: bool


def isai(text: str) -> bool:
    """
    Determine if a repository is related to AI based on its description.

    Args:
        text: The repository description or README content.

    Returns:
        True if the repository is AI-related, False otherwise.
    """
    prompt = (
        "Determine if this GitHub repository is related to Artificial Intelligence (AI), "
        "Large Language Models (LLMs), Vision Language Model (VLM), World Model, "
        "Retrieval-Augmented Generation (RAG), Vector Database, Embedding, Agent,"
        "Vibe Coding, Harness Engineering, or other AI fields. "
        "Consider libraries, frameworks, models, and tools for AI development.\n\n"
        f"Repository description/README:\n{text}"
    )

    resp = openai_client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format=AIRelevance,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False,
            }
        },
    )

    return resp.choices[0].message.parsed.is_ai_related


def get_repo_info(github_client: Github, full_name: str) -> Optional[Dict]:
    """
    Get GitHub repository information.
    """
    repo = github_client.get_repo(full_name)
    # Ignore repo with less than 100 stars or archived
    if repo.stargazers_count < 100 or repo.archived:
        return None
    # Fetch languages.
    categories = None
    languages = repo.get_languages()
    if len(languages) > 0:
        categories = [max(languages, key=languages.get).lower()]
    # Encode embedding.
    description = repo.description
    if description is None:
        description = tldr(repo.get_readme().decoded_content.decode("utf-8"))
        print("QWEN:", description)

    # Check if repository is AI-related and add "ai" category
    if isai(description):
        if categories is None:
            categories = ["ai"]
        elif "ai" not in categories:
            categories.append("ai")

    description_embedding = embedding(description)
    item = {
        "ItemId": full_name.replace("/", ":").lower(),
        "Timestamp": str(repo.updated_at),
        "Labels": {
            "embedding": description_embedding,
            "topics": repo.get_topics(),
        },
        "Categories": categories,
        "Comment": repo.description,
    }
    return item


def update_user(
    gorse_client: Gorse,
    token: str,
    pulled_at: datetime.datetime,
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
        try:
            item = get_repo_info(github_client, full_name)
            if item is not None:
                gorse_client.insert_item(item)
                item_count += 1
        except Exception as e:
            logger.exception("failed to get repo info")
        pull_count += 1
    logger.info(
        "insert user starred repositories",
        extra={
            "tags": {"user_id": github_client.get_user().login, "num_items": item_count}
        },
    )
    # Insert feedback
    gorse_client.insert_feedbacks(stars)
    logger.info(
        "insert feedback from user",
        extra={
            "tags": {
                "user_id": github_client.get_user().login,
                "num_feedback": len(stars),
            }
        },
    )
