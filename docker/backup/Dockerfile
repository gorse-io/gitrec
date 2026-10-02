FROM mysql:8.4

# Use the official MySQL dump client for MySQL generated-column support.
# Install Python and gzip for the S3 client and compressed backups.
RUN microdnf install -y python3-pip gzip && microdnf clean all

# Install S3 client.
RUN pip3 install --no-cache-dir s3cmd

# Copy files.
COPY scripts/backup.sh ./

# Run backup task.
ENTRYPOINT []
CMD ["bash", "backup.sh"]
