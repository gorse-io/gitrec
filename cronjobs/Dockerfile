FROM python:3.9

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential

RUN pip3 install requests PyGithub PyGorse beautifulsoup4 language_detector mysqlclient

COPY main.py main.py

CMD while true; do python3 main.py; sleep 3600; done;
