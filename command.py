import click
import os
from github import Github
from gorse import Gorse
from utils import *
from dotenv import load_dotenv

# Load dot file
load_dotenv()

# Create Gorse client
gorse_client = Gorse("http://127.0.0.1:8088", os.getenv("GORSE_API_KEY"))

# Create GitHub client.
github_client = Github(os.getenv("GITHUB_ACCESS_TOKEN"))

# Create label generator.
generator = LabelGenerator(gorse_client)


@click.group()
def command():
    pass


@command.command()
@click.argument("item_id")
def update_repo(item_id):
    repo = get_repo_info(github_client, item_id, generator)
    gorse_client.insert_item(repo)
    print(repo)


if __name__ == "__main__":
    command()
