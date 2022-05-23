import datetime
import os

from celery import Celery
from github import Github
from github.GithubException import *
from gorse import Gorse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import common

# Setup logger
logger = common.getLogger("jobs")


# Setup client
gorse_client = Gorse(os.getenv("GORSE_ADDRESS"), os.getenv("GORSE_API_KEY"))

# Setup celery
app = Celery("jobs", broker=os.getenv("BROKER_ADDRESS"))

# Setup sqlalchemy
engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
Session = sessionmaker()
Session.configure(bind=engine)


@app.task
def pull(token: str):
    try:
        # Fetch user login
        github_client = Github(token)
        login = github_client.get_user().login
        # Fetch user record
        session = Session()
        user = session.query(common.User).filter(common.User.login == login).one()
        try:
            common.update_user(gorse_client, user.token["access_token"], user.pulled_at)
            user.pulled_at = datetime.datetime.now()
        except BadCredentialsException as e:
            session.delete(user)
            logger.warning(
                "invalid user token",
                extra={"tags": {"login": user.login, "exception": str(e)}},
            )
        session.commit()
    except Exception as e:
        logger.exception("failed to update user labels and feedback")
