########################
# STEP 1: Build frontend
########################
FROM node:24
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY frontend frontend
WORKDIR /frontend
RUN pnpm install && pnpm build

#################################
# STEP 2: Setup python enviroment
#################################
FROM python:3.12

# Install packages
RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy frontend
COPY --from=0 /frontend/dist ./frontend/dist

# Copy backend
COPY app.py jobs.py gunicorn.conf.py utils.py ./

# Start gitrec
CMD PYTHONPATH=. gunicorn app:app -c gunicorn.conf.py
