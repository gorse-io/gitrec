FROM python:3.9

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential

RUN pip3 install celery requests redis PyGithub PyGorse language_detector mysqlclient

COPY . jobs

ENTRYPOINT ["celery", "-A", "jobs", "worker", "--loglevel=INFO"]
