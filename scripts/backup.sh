#!/usr/bin/env bash
set -eo pipefail

# MariaDB's dump client can emit explicit values for MySQL generated columns.
# Use the MySQL client so INSERTs omit those columns and remain importable.
if mysqldump --version | grep -qi mariadb; then
    echo "Backup requires MySQL mysqldump; rebuild the backup image to replace the MariaDB client." >&2
    exit 1
fi

while true; do

    SQL_FILE=$(date '+%Y-%m-%d.%H').sql.gz

    # Dump and compress database in one stream
    MYSQL_PWD="${MYSQL_PASSWORD:=gorse_pass}" mysqldump \
        --no-tablespaces --single-transaction --complete-insert \
        --column-statistics=0 --set-gtid-purged=OFF --ssl-mode=PREFERRED \
        -h "${MYSQL_HOST:=127.0.0.1}" -u "${MYSQL_USER:=gorse}" \
        "${MYSQL_DATABASE:=gorse}" users items feedback flask_dance_oauth \
        | gzip > "$SQL_FILE"

    # Upload SQL file
    s3cmd --access_key=$S3_ACCESS_KEY \
        --secret_key=$S3_SECRET_KEY \
        --region=$S3_BUCKET_LOCATION \
        --host=$S3_HOST_BASE \
        --host-bucket=$S3_HOST_BUCKET \
        put $SQL_FILE s3://${S3_BUCKET}${S3_PREFIX}/$SQL_FILE
    
    # Remove local SQL file
    rm $SQL_FILE

    # Keep only the latest 7 backups on remote
    BACKUP_FILES=$(s3cmd --access_key=$S3_ACCESS_KEY \
        --secret_key=$S3_SECRET_KEY \
        --region=$S3_BUCKET_LOCATION \
        --host=$S3_HOST_BASE \
        --host-bucket=$S3_HOST_BUCKET \
        ls s3://${S3_BUCKET}${S3_PREFIX}/ | grep '\.sql\.gz$' | sort -r | awk '{print $4}')
    
    # Count and delete old backups
    COUNT=0
    for FILE in $BACKUP_FILES; do
        COUNT=$((COUNT + 1))
        if [ $COUNT -gt 7 ]; then
            s3cmd --access_key=$S3_ACCESS_KEY \
                --secret_key=$S3_SECRET_KEY \
                --region=$S3_BUCKET_LOCATION \
                --host=$S3_HOST_BASE \
                --host-bucket=$S3_HOST_BUCKET \
                del $FILE
        fi
    done

    # Backup 1 day later.
    sleep 86400

done;
