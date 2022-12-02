FROM python:3.9

# Install MySQL client.
RUN apt-get update && apt-get install -y mariadb-client

# Install S3 client.
RUN pip install s3cmd

# Copy files.
COPY backup.sh ./

# Run backup task.
CMD bash backup.sh
