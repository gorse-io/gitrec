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
BROKER_ADDRESS=redis://127.0.0.1:6379/1 \
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

## Share Gorse Cluster with Production

Production instance and development instance of GitRec could share the same Gorse cluster, which is convenient to debug bugs found online.

### Prerequisite

1. Create another [GitHub OAuth app](https://github.com/settings/developers) for development. The authorization callback URL should
  be different to production (eg. `http://127.0.0.1:5001/login/github/authorized`). Then, fill following variables
  in the `.env` file.

```bash
GITHUB_OAUTH_CLIENT_ID=xxxxxxxx     # client ID
GITHUB_OAUTH_CLIENT_SECRET=xxxxxxxx # client secret
SECRET_KEY=xxxxxxxx                 # random string
```

2. For development, `GORSE_ADDRESS` should be the same to the production, while `BROKER_ADDRESS` and `SQLALCHEMY_DATABASE_URI` should be different from production. SQLite is recommended for `SQLALCHEMY_DATABASE_URI`:

```bash
# Create SQLite database
SQLALCHEMY_DATABASE_URI=sqlite:///./flask_dance_oauth.db python3 app.py --setup
```

### CronJobs

```bash
# Start jobs outside docker compose
GORSE_ADDRESS=http://127.0.0.1:8087 \
SQLALCHEMY_DATABASE_URI=sqlite:///./flask_dance_oauth.db \
python3 cronjobs.py
```

### Jobs

```bash
# Start jobs outside docker compose
GORSE_ADDRESS=http://127.0.0.1:8087 \
BROKER_ADDRESS=redis://127.0.0.1:6379/2 \
SQLALCHEMY_DATABASE_URI=sqlite:///./flask_dance_oauth.db \
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

The listening address must be different from production.

```bash
# Start web backend
GORSE_ADDRESS=http://127.0.0.1:8087 \
BROKER_ADDRESS=redis://127.0.0.1:6379/2 \
SQLALCHEMY_DATABASE_URI=sqlite:///./flask_dance_oauth.db \
FLASK_APP=app.py \
FLASK_ENV=development \
flask run -p 5001
```

### Web Frontend

1. Start web backend:

The listening address must be different from production and development. Vue development server proxy takes the role of web backend.

```bash
# Start web backend
GORSE_ADDRESS=http://127.0.0.1:8087 \
BROKER_ADDRESS=redis://127.0.0.1:6379/2 \
SQLALCHEMY_DATABASE_URI=sqlite:///./flask_dance_oauth.db \
FLASK_APP=app.py \
FLASK_ENV=development \
flask run -p 5002
```

2. Edit `frontend/vue.config.js`

```js
module.exports = {
  pages,
  chainWebpack: (config) => config.plugins.delete("named-chunks"),
  devServer: {
    disableHostCheck: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5002",    // web backend address
        changeOrigin: true,
        onProxyReq: function(proxyReq) {
            proxyReq.setHeader("Cookie", "session=xxxxxxxx");
        }
      },
    }
  },
};

```

3. Start web frontend:

```bash
cd frontend
yarn install
yarn serve --port 5001
```
