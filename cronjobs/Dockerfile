FROM python

RUN pip3 install requests PyGithub PyGorse beautifulsoup4 language_detector

COPY cronjobs.py cronjobs.py

CMD while true; do python3 cronjobs.py; sleep 3600; done;
