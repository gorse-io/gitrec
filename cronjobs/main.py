import os

import requests
from bs4 import BeautifulSoup
from github import Github
from github.GithubException import *
from gorse import Gorse
from language_detector import detect_language


github_client = Github(os.getenv("GITHUB_ACCESS_TOKEN"))
gorse_client = Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))


def get_repo_info(full_name):
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
    try:
        readme = repo.get_readme().decoded_content.decode("utf-8")
        spoken_language = detect_language(readme)
        if spoken_language == "Mandarin":
            categories.append("language:zh")
        elif spoken_language == "English":
            categories.append("language:en")
    except UnknownObjectException as e:
        pass
    return {
        "ItemId": full_name.replace("/", ":").lower(),
        "Timestamp": str(repo.updated_at),
        "Labels": labels,
        "Categories": categories,
        "Comment": repo.description,
    }


def get_trending():
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


if __name__ == "__main__":
    print("start pull trending repos")
    trending_count = 0
    trending_repos = get_trending()
    for trending_repo in trending_repos:
        try:
            gorse_client.insert_item(get_repo_info(trending_repo))
            trending_count += 1
        except Exception as e:
            print('failed to pull repo: %s, %s' % (trending_repo, e))
    print("insert %d repos" % trending_count)
