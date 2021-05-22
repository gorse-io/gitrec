# Build frontend
FROM node
COPY frontend frontend
WORKDIR /frontend
RUN yarn install && yarn build

# Setup python enviroment
FROM python
COPY backend backend
COPY requirements.txt requirements.txt
COPY gunicorn.conf.py gunicorn.conf.py

# Copy frontend
COPY --from=0 /frontend/dist /frontend/dist

# Install packages
RUN pip3 install -r requirements.txt

# Start gitrec
CMD PYTHONPATH=backend gunicorn backend.app:app -c gunicorn.conf.py
