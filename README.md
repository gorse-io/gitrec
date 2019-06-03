<img width="160" src="https://img.sine-x.com/steam-lens.png">

# SteamLens

[![Website](https://img.shields.io/website-up-down-green-red/https/steamlens.gorse.io.svg)](https://steamlens.gorse.io)

SteamLens is a tutorial steam video game recommender system based on Flask and gorse.

## Usage

### Download Source

First, clone the repo and enter the folder.

```bash
# Download source
git clone https://github.com/zhenghaoz/SteamLens.git

# Enter source folder
cd SteamLens
```

### Create database

It's a good idea to build recomender system based on existed dataset such as [Steam Dataset](https://steam.internet.byu.edu/). 
The original dataset is huge, we sampled 15000 users and it's available in `games.csv`.

```bash
# Download data
wget https://cdn.sine-x.com/backups/games.csv

# Create data folder
mkdir data

# Create a database and import data
gorse import-feedback data/gorse.db games.csv --sep ','
```

### Get Secret Key

To integrate with Steam, we need to [apply a secret key from Steam](https://steamcommunity.com/dev/apikey) and place it into `config/steamlens.cfg`.

```python
SECRET_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```

### Build & Run

Build the Docker image and run an instance. Remember to mount the data folder and expose the port of uWSGI.

```bash
# Build Docker image
docker build -t zhenghaoz/SteamLens .

# Run an instance
docker run -d -v $(pwd)/data:/root/data \
    -p 5000:5000 \
    zhenghaoz/SteamLens
```

### Pass via Nginx 

Set `uwsgi_pass` in Nginx.

```nginx
location / {
    include uwsgi_params;
    uwsgi_pass 127.0.0.1:5000;
}
```
