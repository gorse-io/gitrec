# GitRec

[![Website](https://img.shields.io/website?url=https%3A%2F%2Fgitrec.gorse.io)](https://gitrec.gorse.io)
[![DeepSource](https://deepsource.io/gh/zhenghaoz/gitrec.svg/?label=active+issues&token=ZnHSLOJyn5VxtqPIJ17wpVa5)](https://deepsource.io/gh/zhenghaoz/gitrec/?ref=repository-badge)

GitRec is the missing recommender system for GitHub repositories based on [Gorse](https://github.com/zhenghaoz/gorse).

## Architecture

<img width="480px" src="https://github.com/zhenghaoz/gitrec/blob/master/assets/architecture.png">

- The trending crawler crawls trending repositories and insert them into Gorse as new items.
- The user starred crawler crawls user starred repositories and insert them into Gorse as new fewdback.
- GitRec web service pulls recommendations from Gorse and show to users. It also submits a crawling request to the user starred crawler when a new user signed in.

## Quick Start

- First, clone the repository and enter the folder.

```bash
git clone https://github.com/zhenghaoz/gitrec.git
cd gitrec
```

- Generate a [personal access token](https://github.com/settings/tokens) from GitHub and fill the `GITHUB_ACCESS_TOKEN` variable in [docker-compose.yml](https://github.com/zhenghaoz/gitrec/blob/master/docker-compose.yml).

```yaml
GITHUB_ACCESS_TOKEN: # personal access token
```

- Create a [GitHub OAuth app](https://github.com/settings/developers). The authorization callback URL should be `http://127.0.0.1:5000/login/github/authorized`. Then, fill following variables in [docker-compose.yml](https://github.com/zhenghaoz/gitrec/blob/master/docker-compose.yml).

```yaml
GITHUB_OAUTH_CLIENT_ID: # client ID
GITHUB_OAUTH_CLIENT_SECRET: # client secret
SECRET_KEY: # random string
```

- Start the cluster using Docker Compose.

```bash
docker-compose up -d
```

- Download the SQL file [github.sql](https://cdn.gorse.io/example/github.sql) and import to the MySQL instance.

```bash
mysql -h 127.0.0.1 -u root -proot_pass gorse < github.sql
```

- Play with GitRec:

| Entry                     | Link                          |
| ------------------------- | ----------------------------- |
| GitRec                    | http://127.0.0.1:5000/        |
| Master Dashboard          | http://127.0.0.1:8088/        |
| Server RESTful API        | http://127.0.0.1:8087/apidocs |
| Server Prometheus Metrics | http://127.0.0.1:8087/metrics |
| Worker Prometheus Metrics | http://127.0.0.1:8089/metrics |
