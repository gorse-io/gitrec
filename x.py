import time
from requests.exceptions import ConnectionError
from typing import Optional

import click
import MySQLdb
from pickledb import PickleDB
from github.GithubException import GithubException, RateLimitExceededException, UnknownObjectException
from google.protobuf import message
from gorse import GorseException
from dotenv import load_dotenv
from openai import BadRequestError, InternalServerError, OpenAI
from tqdm import tqdm

# Load dot file
load_dotenv()

import protocol_pb2
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
@click.argument("full_name")
def upsert_repo(full_name):
    """Upsert a repository into GitRec."""
    repo = get_repo_info(github_client, full_name)
    if repo is not None:
        gorse_client.insert_item(repo)
        print('UPSERT', full_name)
    else:
        print('IGNORE', full_name)


@command.command()
@click.argument("full_name")
def get_repo(full_name):
    item = gorse_client.get_item(full_name.replace('/', ':').lower())
    print('GET', item)


@command.command()
@click.argument("full_name")
def delete_repo(full_name):
    gorse_client.delete_item(full_name.replace('/', ':').lower())
    print('DELETE', full_name)


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
        if item is not None:
            gorse_client.insert_item(item)
            print("INSERT " + repo.full_name)
        else:
            print("IGNORE " + repo.full_name)


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

                # Delete repo with less than 100 stars or archived
                if repo.stargazers_count < 100 or repo.archived:
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


def write_dump(f, data: message.Message):
    bytes_data = data.SerializeToString()
    f.write(len(bytes_data).to_bytes(8, byteorder='little'))
    f.write(bytes_data)


@command.command()
@click.argument("database")
@click.option("--username", "-u", prompt=True)
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.option("--cores", "-c", default=5, help="Dump subset of the data in which all users and items have at least N feedback.")
def dump_playground(database: str, username: Optional[str], password: Optional[str], cores: int = 5):
    """Dump GitRec playground data from MySQL database."""

    # Connect to MySQL
    conn = MySQLdb.connect(
        host="127.0.0.1",
        user=username,
        passwd=password,
        db=database,
    )
    cursor = conn.cursor()

    with open("github_playground.dump", "wb") as f:
        num_users, num_items, num_feedback = 0, 0, 0

        # Dump users
        f.write((-1).to_bytes(8, byteorder='little', signed=True))
        cursor.execute("SELECT user_id, labels, comment FROM users WHERE user_id in (select user_id from feedback group by user_id having count(*) >= %s)", (cores,))
        for row in cursor.fetchall():
            user_id, labels, comment = row
            write_dump(f, protocol_pb2.User(
                user_id=user_id,
                labels=labels.encode('utf-8'),
                comment=comment,
            ))
            num_users += 1

        # Dump items
        f.write((-2).to_bytes(8, byteorder='little', signed=True))
        cursor.execute("SELECT item_id, is_hidden, categories, time_stamp, labels, comment FROM items WHERE item_id in (select item_id from feedback group by item_id having count(*) >= %s)", (cores,))
        for row in cursor.fetchall():
            item_id, is_hidden, categories, timestamp, labels, comment = row
            write_dump(f, protocol_pb2.Item(
                item_id=item_id,
                is_hidden=bool(is_hidden),
                categories=categories.split(',') if categories else [],
                timestamp=int(timestamp.timestamp()),
                labels=labels.encode('utf-8'),
                comment=comment,
            ))
            num_items += 1

        # Dump feedback
        f.write((-3).to_bytes(8, byteorder='little', signed=True))
        cursor.execute("SELECT feedback_type, user_id, item_id, value, time_stamp, comment FROM feedback WHERE item_id in (select item_id from feedback group by item_id having count(*) >= %s) AND user_id in (select user_id from feedback group by user_id having count(*) >= %s)", (cores, cores))
        for row in cursor.fetchall():
            feedback_type, user_id, item_id, value, timestamp, comment = row
            write_dump(f, protocol_pb2.Feedback(
                feedback_type=feedback_type,
                user_id=user_id,
                item_id=item_id,
                value=value,
                timestamp=int(timestamp.timestamp()),
                comment=comment,
            ))
            num_feedback += 1

    print(f"Dump complete: {num_users} users, {num_items} items, {num_feedback} feedback.")


if __name__ == "__main__":
    command()
