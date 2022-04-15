FROM python

RUN pip3 install celery requests redis PyGithub PyGorse

COPY jobs.py jobs.py

ENTRYPOINT ["celery", "-A", "jobs", "worker", "--loglevel=INFO"]
