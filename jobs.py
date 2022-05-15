from cmath import exp
import os
from typing import Dict, List, Tuple

import requests
from celery import Celery
from github import Github
from github.GithubException import *
from language_detector import detect_language

from gorse import Gorse

gorse_client = Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))


def get_user_topics(token: str):
    g = Github(token)
    user = g.get_user()
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
            if e.status not in {403, 451}:
                raise e
    return {"Labels": list(topics_set), "UserId": user.login.lower()}


class GraphQLGitHub:
    def __init__(self, token: str):
        self.token = token

    def __get_viewer_login(self) -> str:
        query = "query { viewer { login } }"
        return self.__query(query)["data"]["viewer"]["login"]

    def __get_viewer_starred(self) -> List[Tuple[str, str]]:
        stars = []
        cursor = ""
        has_next_page = True
        while has_next_page:
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

    def get_viewer_starred(self) -> List[Dict]:
        stars = []
        user_id = self.__get_viewer_login()
        for item_id, timestamp in self.__get_viewer_starred():
            stars.append(
                {
                    "FeedbackType": "star",
                    "UserId": user_id.lower(),
                    "ItemId": item_id.replace("/", ":").lower(),
                    "Timestamp": timestamp,
                }
            )
        return stars


def get_repo_info(token: str, full_name: str):
    g = Github(token)
    repo = g.get_repo(full_name)
    if repo.stargazers_count < 100:
        return None
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


app = Celery("jobs", broker=os.getenv("BROKER_ADDRESS"))


@app.task
def pull(token: str):
    # Pull user labels
    user = get_user_topics(token)
    gorse_client.insert_user(user)
    print('insert user `%s` with %d labels' % (user["UserId"], len(user["Labels"])))
    # Pull user starred repos
    g = GraphQLGitHub(token)
    stars = g.get_viewer_starred()
    stars.reverse()
    # Pull items
    item_count, pull_count = 0, 0
    for feedback in stars:
        if pull_count > 100:
            break
        item_id = feedback['ItemId']
        full_name = item_id.replace(':', '/')
        item = get_repo_info(token, full_name)
        if item is not None:
            gorse_client.insert_item(item)
            item_count += 1
        pull_count += 1
    print("insert %d items from user `%s`" % (item_count, user["UserId"]))
    # Insert feedback
    gorse_client.insert_feedbacks(stars)
    print("insert %d feedback from user `%s`" % (len(stars), user["UserId"]))
