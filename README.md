# GitRec

<img width=160 src="assets/logo.png"/>

[![test](https://github.com/zhenghaoz/gitrec/actions/workflows/build_test.yml/badge.svg)](https://github.com/zhenghaoz/gitrec/actions/workflows/build_test.yml)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fgitrec.gorse.io)](https://gitrec.gorse.io)
[![Discord](https://img.shields.io/discord/830635934210588743)](https://discord.gg/x6gAtNNkAE)
[![Twitter Follow](https://img.shields.io/twitter/follow/gorse_io?label=Follow&style=social)](https://twitter.com/gorse_io)

GitRec is the missing recommender system for GitHub repositories based on [Gorse](https://github.com/zhenghaoz/gorse).

![](assets/gitrec.png)

## Browser Extensions

<table>
  <tbody>
    <tr>
      <td>
        <a href="https://chrome.google.com/webstore/detail/gitrec/eihokbaeiebdenibjophfipedicippfl" target="_blank">
          <img src="https://i.loli.net/2021/04/23/IqpU7COKQvzrcyG.png" />
        </a>
      </td>
    <td>
      <a href="https://microsoftedge.microsoft.com/addons/detail/gitrec/cpcfbfpnagiffgpmfljmcdokmfjffdpa" target="_blank">
        <img src="https://i.loli.net/2021/04/23/EnS3eDi4I86Yv2N.png" />
      </a>
    </td>
    </tr>
  </tbody>
</table>

## Architecture

<img width="480px" src="assets/architecture.png">

- The trending crawler crawls trending repositories and insert them into Gorse as new items.
- The user starred crawler crawls user starred repositories and insert them into Gorse as new feedback.
- GitRec web service pulls recommendations from Gorse and show to users. It also submits a crawling request to the user
  starred crawler when a new user signed in.

## Quick Start

- First, clone the repository and enter the folder.

```bash
git clone https://github.com/zhenghaoz/gitrec.git
cd gitrec
```

- Create a `.env` file.

```bash
GORSE_DASHBOARD_USER_NAME=xxxxxxxx
GORSE_DASHBOARD_PASSWORD=xxxxxxxx
GITHUB_ACCESS_TOKEN=xxxxxxxx
GITHUB_OAUTH_CLIENT_ID=xxxxxxxx
GITHUB_OAUTH_CLIENT_SECRET=xxxxxxxx
SECRET_KEY=xxxxxxxx
```

- Generate a [personal access token](https://github.com/settings/tokens) from GitHub and fill the `GITHUB_ACCESS_TOKEN`
  variable in the `.env` file.

```bash
GITHUB_ACCESS_TOKEN=xxxxxxxx # personal access token
```

- Create a [GitHub OAuth app](https://github.com/settings/developers). The authorization callback URL should
  be `http://127.0.0.1:5000/login/github/authorized`. Then, fill following variables
  in the `.env` file.

```bash
GITHUB_OAUTH_CLIENT_ID=xxxxxxxx     # client ID
GITHUB_OAUTH_CLIENT_SECRET=xxxxxxxx # client secret
SECRET_KEY=xxxxxxxx                 # random string
```

- Start the cluster using Docker Compose.

```bash
docker-compose up -d
```

- Download the SQL file [github.sql](https://cdn.gorse.io/example/github.sql) and import to the MySQL instance.

```bash
mysql -h 127.0.0.1 -u gorse -pgorse_pass gorse < github.sql
```

- Restart the master node to apply imported data.

```bash
docker-compose restart
```

- Play with GitRec:

| Entry                     | Link                          |
| ------------------------- | ----------------------------- |
| GitRec                    | http://127.0.0.1:5000/        |
| Grafana Dashboard         | http://127.0.0.1:3000/        |
| Master Dashboard          | http://127.0.0.1:8088/        |
| Master Prometheus Metrics | http://127.0.0.1:8088/metrics |
| Server RESTful API        | http://127.0.0.1:8087/apidocs |
| Server Prometheus Metrics | http://127.0.0.1:8087/metrics |
| Worker Prometheus Metrics | http://127.0.0.1:8089/metrics |
