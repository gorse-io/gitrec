# Build gorse
FROM golang
RUN go get github.com/zhenghaoz/gorse/...

# Create python environment
FROM python
EXPOSE 8080 5000
WORKDIR /root

# Install gorse
COPY --from=0 /go/bin/gorse /usr/local/bin

# Install packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy files
VOLUME ["/root/data"]
COPY steamlens steamlens
COPY config config
COPY data data

# Startup steamlens
COPY uwsgi.ini .
ENV STEAMLENS_SETTINGS ../config/steamlens.cfg
CMD gorse serve -c config/gorse.toml & uwsgi --ini uwsgi.ini