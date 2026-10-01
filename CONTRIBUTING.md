# Contribution Guide

GitRec is a website composed of multiple components. This guide will introduce how to setup a develop environment quickly.

## Setup Develop Environment

1. [Deploy GitRec](https://github.com/gorse-io/gitrec#quick-start) via Docker Compose.
2. Install [`just`](https://just.systems/man/en/) a command runner.
3. Install Python dependencies:

```bash
 pip install -r requirements.txt 
```

4. Install npm and yarn:

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
just debug-cronjobs
```

> `GITHUB_ACCESS_TOKEN` will be loaded from `.env` automatically.

### Jobs

```bash
just debug-jobs
```

### Web Backend

1. Build the frontend:

```bash
cd frontend
yarn install
yarn build
```

2. Start web service in debug mode:

```bash
just debug-web
```

### Web Frontend

1. Start web backend:

```bash
just debug-backend
```

2. Start web frontend:

```bash
cd frontend
yarn install
yarn serve --port 5000
```
