import os

import requests
from bs4 import BeautifulSoup
from github import Github

from gorse import Gorse

github_client = Github(os.getenv("GITHUB_ACCESS_TOKEN"))
gorse_client = Gorse(os.getenv("GORSE_ADDRESS"))


def get_repo_info(full_name):
    repo = github_client.get_repo(full_name)
    topics = [topic for topic in repo.get_topics()]
    languages = list(repo.get_languages().items())
    if len(languages) > 0:
        main_language = languages[0][0].lower()
        if main_language not in topics:
            topics.append(main_language)
    return {
        "ItemId": full_name.replace("/", ":"),
        "Timestamp": str(repo.updated_at),
        "Labels": topics,
        "Comment": repo.description,
    }


def get_trending():
    r = requests.get("https://github.com/trending")
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    full_names = []
    for article in soup.find_all("article"):
        full_names.append(article.h1.a["href"][1:])
    return full_names


if __name__ == "__main__":
    print("start pull trending repos")
    trending_repos = get_trending()
    for trending_repo in trending_repos:
        gorse_client.insert_item(get_repo_info(trending_repo))
    print("insert %d items" % len(trending_repos))
