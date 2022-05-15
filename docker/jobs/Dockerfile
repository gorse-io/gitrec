FROM python:3.9

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY jobs.py common.py ./

ENTRYPOINT ["celery", "-A", "jobs", "worker", "--loglevel=INFO"]
