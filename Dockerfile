# Build frontend
FROM node
COPY frontend frontend
WORKDIR /frontend
RUN yarn install && yarn build

# Setup python enviroment
FROM python
COPY backend backend
WORKDIR /backend

# Copy frontend
COPY --from=0 /frontend/dist /backend/static

# Install packages
RUN pip3 install -r requirements.txt

# # Startup steamlens
# CMD uwsgi --ini uwsgi.ini
