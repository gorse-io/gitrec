import os
from typing import Dict, List, Tuple

import requests
from celery import Celery
from github import Github
from github.GithubException import *

from gorse import Gorse

gorse_client = Gorse(os.getenv("GORSE_ADDRESS"))


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


app = Celery("crawler_starred", broker=os.getenv("BROKER_ADDRESS"))


@app.task
def pull(token: str):
    # Pull user labels
    user = get_user_topics(token)
    gorse_client.insert_user(user)
    # Pull user starred repos
    g = GraphQLGitHub(token)
    stars = g.get_viewer_starred()
    gorse_client.insert_feedbacks(stars)
    print(
        "insert %d feedback and %d user labels from %s"
        % (len(stars), len(user["Labels"]), user["UserId"])
    )
