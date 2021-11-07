########################
# STEP 1: Build frontend
########################
FROM node:16
COPY frontend frontend
WORKDIR /frontend
RUN yarn install && yarn build

#################################
# STEP 2: Setup python enviroment
#################################
FROM python:3.9

# Install packages
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy frontend
COPY --from=0 /frontend/dist /frontend/dist

# Copy backend
COPY backend backend
COPY gunicorn.conf.py gunicorn.conf.py

# Start gitrec
CMD PYTHONPATH=backend gunicorn backend.app:app -c gunicorn.conf.py
