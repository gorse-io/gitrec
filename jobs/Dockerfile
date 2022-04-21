FROM python

RUN pip3 install celery requests redis PyGithub PyGorse language_detector

COPY main.py main.py

ENTRYPOINT ["celery", "-A", "jobs", "worker", "--loglevel=INFO"]
