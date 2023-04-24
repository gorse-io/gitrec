set -e

while true; do

    SQL_FILE=$(date '+%Y-%m-%d.%H').sql

    # Dump database
    mysqldump --no-tablespaces -h ${MYSQL_HOST:=127.0.0.1} -u ${MYSQL_USER:=gorse} -p${MYSQL_PASSWORD:=gorse_pass} ${MYSQL_DATABASE:=gorse} users items feedback flask_dance_oauth > $SQL_FILE

    # Upload SQL file
    s3cmd --access_key=$S3_ACCESS_KEY \
        --secret_key=$S3_SECRET_KEY \
        --region=$S3_BUCKET_LOCATION \
        --host=$S3_HOST_BASE \
        --host-bucket=$S3_HOST_BUCKET \
        put $SQL_FILE s3://${S3_BUCKET}${S3_PREFIX}/$SQL_FILE

    # Backup 1 day later.
    sleep 86400

done;
