# Contribution Guide

GitRec is a website composed of multiple components. This guide will introduce how to setup a develop environment quickly.

## Setup Develop Environment

1. [Deploy GitRec](https://github.com/gorse-io/gitrec#quick-start) via Docker Compose.
2. Install Python dependencies:

```bash
 pip install -r requirements.txt 
```

3. Install npm and yarn:

```bash
# Install npm
sudo apt-get install npm

# Install yarn
sudo npm i -g yarn
```

## Develop Guide

> These following command should be executed in the root directory of GitRec source.

### CronJobs

```bash
# Stop cronjobs in docker compose
docker-compose stop cronjobs

# Start cronjobs outside docker compose
GORSE_ADDRESS=http://127.0.0.1:8087 \
SQLALCHEMY_DATABASE_URI=mysql://gorse:gorse_pass@127.0.0.1:3306/gorse \
python3 cronjobs.py
```

> `GITHUB_ACCESS_TOKEN` will be loaded from `.env` automatically.

### Jobs

```bash
# Stop jobs in docker compose
docker-compose stop jobs

# Start jobs outside docker compose
GORSE_ADDRESS=http://127.0.0.1:8087 \
BROKER_ADDRESS=redis://127.0.0.1:6379 \
SQLALCHEMY_DATABASE_URI=mysql://gorse:gorse_pass@127.0.0.1:3306/gorse \
celery -A jobs worker --loglevel=INFO 
```

### Web Backend

1. Build the frontend:

```bash
cd frontend
yarn install
yarn build
```

2. Replace web backend:

```bash
# Stop web in docker compose
docker-compose stop web

# Start web backend
GORSE_ADDRESS=http://127.0.0.1:8087 \
BROKER_ADDRESS=redis://127.0.0.1:6379/1 \
SQLALCHEMY_DATABASE_URI=mysql://gorse:gorse_pass@127.0.0.1:3306/gorse \
FLASK_APP=app.py \
FLASK_ENV=development \
flask run -p 5000
```

### Web Frontend

```bash
cd frontend
yarn install
yarn serve --port 5000
```
