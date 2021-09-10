from github import Github
from typing import List, Tuple
from github import Github
from github.GithubException import *
import json
import time
from tqdm import tqdm
import mysql.connector as mysql


def get_user_topics(user_id: str, token: str, n: int=5) -> Tuple[str, List[str]]:
    g = Github(token)
    user = g.get_user(user_id)
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
    return user.login, list(topics_set)





db = mysql.connect(
    host="192.168.199.166",
    user="gorse",
    password="gorse_pass",
    database='gorse',
)


if __name__ == '__main__':
    g = Github('6726621fbb7ca3061773452e79bd7d05072aaa4a')
    # g = Github('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')
    cursor = db.cursor()
    # while True:
    cursor.execute("select user_id from users where labels = cast('[]' as json)")
    rows = cursor.fetchall()
    for row in tqdm(rows):
        try:
            user_id, topics = get_user_topics(row[0], '6726621fbb7ca3061773452e79bd7d05072aaa4a')
            # user_id, topics = get_user_topics(row[0], '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')
            cursor.execute('update users set labels = %s where user_id = %s', (json.dumps(topics), user_id))
            db.commit()
        except RateLimitExceededException as e:
            print(e)
            time.sleep(60*10)
            continue
        except UnknownObjectException as e:
            print(row[0], type(e), e)
            continue
        except GithubException as e:
            print(row[0], type(e), e)
            break
            # cursor.execute("update users set labels = '[]' where user_id = %s", (row[0], ))
            # db.commit()
        # break
        #     try:
        #         repo_id = row[0].replace(':', '/')
        #         repo = g.get_repo(repo_id)
        #         languages = list(repo.get_languages().items())
        #         topics = []
        #         if len(languages) > 0:
        #             topics = [languages[0][0].lower()]
        #         # print(repo_id, languages, topics)
        #         cursor.execute('update items set labels = %s where item_id = %s', (json.dumps(topics), row[0]))
        #         db.commit()
        #     except RateLimitExceededException as e:
        #         print(e)
        #         time.sleep(60*60)
        #         continue
        #     except UnknownObjectException:
        #         print('repo not found:', row[0])
        #         cursor.execute('delete from items where item_id = %s', (row[0],))
        #         db.commit()
        #         continue
        #     except Exception as e:
        #         print(row[0], type(e), e)
        #         continue
