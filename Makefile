export GORSE_ADDRESS=http://127.0.0.1:8087
export BROKER_ADDRESS=redis://127.0.0.1:6379/2
export SQLALCHEMY_DATABASE_URI=sqlite:///./flask_dance_oauth.db
export FLASK_APP=app.py
export FLASK_ENV=development
export DATASET_MINIMAL_LINKAGE=2

cronjobs:
	python3 cronjobs.py

insert-trending:
	python3 cronjobs.py --insert-trending

update-users:
	python3 cronjobs.py --update-users

optimize-labels:
	python3 cronjobs.py --optimize-labels

jobs:
	celery -A jobs worker --loglevel=INFO 

web:
	flask run -p 5001

backend:
	flask run -p 5002

dump:
	docker exec gitrec_mysql_1 mysqldump -u root -proot_pass --complete-insert --single-transaction gorse feedback \
		--where 'item_id in (select item_id from feedback group by item_id having count(*) >= ${DATASET_MINIMAL_LINKAGE})' > github.sql
	docker exec gitrec_mysql_1 mysqldump -u root -proot_pass --complete-insert --single-transaction gorse users \
		--where 'user_id in (select user_id from feedback)' >> github.sql
	docker exec gitrec_mysql_1 mysqldump -u root -proot_pass --complete-insert --single-transaction gorse items \
		--where 'item_id in (select item_id from feedback group by item_id having count(*) >= ${DATASET_MINIMAL_LINKAGE})' >> github.sql
	gzip -k github.sql
