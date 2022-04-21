FROM python

RUN pip3 install requests PyGithub PyGorse beautifulsoup4 language_detector

COPY main.py main.py

CMD while true; do python3 main.py; sleep 3600; done;
