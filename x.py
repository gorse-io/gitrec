import time
from requests.exceptions import ConnectionError
from typing import Optional

import click
from pickledb import PickleDB
from github.GithubException import GithubException, UnknownObjectException
from gorse import GorseException
from dotenv import load_dotenv
from openai import BadRequestError, InternalServerError, OpenAI
from tqdm import tqdm

# Load dot file
load_dotenv()

from utils import *


# Create Gorse client
gorse_client = Gorse("http://127.0.0.1:8088", os.getenv("GORSE_API_KEY"))

# Create GitHub client.
github_client = Github(os.getenv("GITHUB_ACCESS_TOKEN"))

# Create GraphQL client.
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE")
)


@click.group()
def command():
    pass


@command.command()
@click.argument("item_id")
def upsert_repo(item_id):
    """Upsert a repository into GitRec."""
    repo = get_repo_info(github_client, item_id)
    gorse_client.insert_item(repo)
    print(repo)


def search_and_upsert(topic: Optional[str] = None, language: Optional[str] = None):
    query = "stars:>100"
    if topic is not None:
        query += " topic:" + topic
    if language is not None:
        query += " language:" + language
    print("SEARCH " + query)
    repos = github_client.search_repositories(query)
    for repo in repos:
        # Skip existed repo.
        try:
            gorse_client.get_item(repo.full_name.replace("/", ":").lower())
            continue
        except GorseException as e:
            if e.status_code != 404:
                print(e)
                continue
        except RateLimitExceededException as e:
            print(e)
            time.sleep(1800)
            continue
        except Exception as e:
            print(e)
            continue
        # Insert repo
        item = get_repo_info(github_client, repo.full_name)
        gorse_client.insert_item(item)
        print("INSERT " + repo.full_name)


@command.command()
def insert_repos():
    """Insert popular repositories (stars >= 100) into GitRec"""
    # Load checkpoint
    db = PickleDB("checkpoint.json")
    # Load existed topics
    topics = set()
    cursor = ""
    while True:
        items, cursor = gorse_client.get_items(1000, cursor)
        for item in items:
            if item["Labels"] is not None and item["Labels"]["topics"] is not None:
                for topic in item["Labels"]["topics"]:
                    topics.add(topic)
        if cursor == "":
            break
    # Search and upsert
    for topic in topics:
        if not db.get(topic):
            while True:
                try:
                    search_and_upsert(topic)
                    db.set(topic, True)
                    break
                except RateLimitExceededException as e:
                    print(e)
                    time.sleep(1800)
                    continue
                except Exception as e:
                    print(e)
                    break


@command.command()
def upgrade_items():
    """Upgrade items in Gorse."""
    cursor = ""
    while True:
        items, cursor = gorse_client.get_items(1000, cursor)
        for item in items:
            if type(item["Labels"]) == list:
                # Fetch repo
                try:
                    repo = github_client.get_repo(item["ItemId"].replace(":", "/"))
                except UnknownObjectException as e:
                    gorse_client.delete_item(item["ItemId"])
                    print("DELETE " + item["ItemId"] + " " + str(e))
                    continue
                except GithubException as e:
                    if e.status == 451:
                        gorse_client.delete_item(item["ItemId"])
                        print("DELETE " + item["ItemId"] + " " + str(e))
                    elif e.status and e.data["message"] in (
                        "Repository access blocked"
                    ):
                        gorse_client.delete_item(item["ItemId"])
                        print("DELETE " + item["ItemId"] + " " + str(e))
                    else:
                        print("FAIL " + item["ItemId"] + " " + str(e))
                    continue

                # Delete repo with less than 100 stars
                if repo.stargazers_count < 100:
                    gorse_client.delete_item(item["ItemId"])
                    print("DELETE " + repo.full_name)
                    continue

                # Delete repp with description longer than 1000 characters
                if (
                    repo.description is not None
                    and len(repo.description) > MAX_COMMENT_LENGTH
                ):
                    gorse_client.delete_item(item["ItemId"])
                    print("DELETE " + repo.full_name + " with long description")
                    continue

                # Generate categories and labels
                try:
                    language = None
                    languages = repo.get_languages()
                    if len(languages) > 0:
                        language = [max(languages, key=languages.get).lower()]
                    description = repo.description
                    if description is None:
                        description = tldr(
                            repo.get_readme().decoded_content.decode("utf-8")
                        )
                        print("QWEN:", description)
                    description_embedding = embedding(description)
                except BadRequestError as e:
                    print("FAIL " + repo.full_name + " " + str(e))
                    continue
                except InternalServerError as e:
                    print("FAIL " + repo.full_name + " " + str(e))
                    continue
                except ConnectionError as e:
                    print("FAIL " + repo.full_name + " " + str(e))
                    continue
                except UnknownObjectException as e:
                    gorse_client.delete_item(item["ItemId"])
                    print("DELETE " + item["ItemId"] + " " + str(e))
                    continue
                except AssertionError as e:
                    print("FAIL " + repo.full_name + " " + str(e))
                    continue

                # Update item
                gorse_client.update_item(
                    item["ItemId"],
                    categories=language,
                    labels={
                        "embedding": description_embedding,
                        "topics": repo.get_topics(),
                    },
                    timestamp=repo.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    comment=repo.description,
                )
                print("UPGRADE " + repo.full_name)
        if cursor == "":
            break


@command.command()
def upgrade_embedding():
    """Upgrade embeddings."""
    cursor = ""
    while True:
        items, cursor = gorse_client.get_items(1000, cursor)
        if cursor == "":
            break
        for item in tqdm(items):
            if len(item["Comment"]) > 0:
                item["Labels"]["embedding"] = embedding(item["Comment"])
                gorse_client.update_item(
                    item["ItemId"],
                    labels=item["Labels"],
                )


if __name__ == "__main__":
    command()
