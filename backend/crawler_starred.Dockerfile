FROM python

RUN pip3 install celery requests

COPY gorse.py gorse.py

COPY crawler_starred.py crawler_starred.py

ENTRYPOINT ["celery", "-A", "crawler_starred", "worker", "--loglevel=INFO"]
