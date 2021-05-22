FROM python

RUN pip3 install requests PyGithub beautifulsoup4

COPY crawler_trending.py crawler_trending.py

COPY gorse.py gorse.py

CMD while true; do python3 crawler_trending.py; sleep 3600; done;
