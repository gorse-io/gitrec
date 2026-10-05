set -e

while true; do

    SQL_FILE=$(date '+%Y-%m-%d.%H').sql.gz

    # Dump and compress database in one stream
    mysqldump --no-tablespaces -h ${MYSQL_HOST:=127.0.0.1} -u ${MYSQL_USER:=gorse} -p${MYSQL_PASSWORD:=gorse_pass} --ssl-verify-server-cert=0 ${MYSQL_DATABASE:=gorse} users items feedback flask_dance_oauth | gzip > $SQL_FILE

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
