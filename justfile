export GORSE_ADDRESS := "http://127.0.0.1:8087"
export BROKER_ADDRESS := "sqla+mysql://gorse:gorse_pass@127.0.0.1/gorse"
export SQLALCHEMY_DATABASE_URI := "mysql://gorse:gorse_pass@127.0.0.1:3306/gorse"
export FLASK_APP := "app.py"
export FLASK_ENV := "development"
export DATASET_MINIMAL_LINKAGE := "2"
export OAUTHLIB_INSECURE_TRANSPORT := "1"

# List recipes.
default:
	@just --list

# Stop web service.
stop-web:
	docker-compose stop web

# Stop cronjobs.
stop-cronjobs:
	docker compose stop cronjobs

# Stop schduled jobs.
stop-jobs:
	docker-compose stop jobs

# Start web service in debug mode.
debug-jobs: stop-jobs
	celery -A jobs worker --loglevel=INFO

# Start cronjobs in debug mode.
debug-cronjobs: stop-cronjobs
	python3 cronjobs.py

# Start web service in debug mode.
debug-web: stop-web
	flask run -p 5000

# Start web service for frontend develop.
debug-backend: stop-web
	flask run -p 5001

# Dump MySQL database to SQL file.
dump-sql path='dist':
	mkdir -p {{path}}
	docker compose exec mysql mysqldump -u root -proot_pass --complete-insert --single-transaction gorse feedback \
		--where "item_id in (select item_id from feedback group by item_id having count(*) >= ${DATASET_MINIMAL_LINKAGE})" > {{path}}/github.sql
	docker compose exec mysql mysqldump -u root -proot_pass --complete-insert --single-transaction gorse users \
		--where "user_id in (select user_id from feedback)" >> {{path}}/github.sql
	docker compose exec mysql mysqldump -u root -proot_pass --complete-insert --single-transaction gorse items \
		--where "item_id in (select item_id from feedback group by item_id having count(*) >= ${DATASET_MINIMAL_LINKAGE})" >> {{path}}/github.sql

# Dump MySQL database to compressed SQL file.
dump-sql-gzip path='dist': (dump-sql path)
	gzip -k {{path}}/github.sql
