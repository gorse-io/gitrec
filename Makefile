export GORSE_ADDRESS=http://127.0.0.1:8087
export BROKER_ADDRESS=redis://127.0.0.1:6379/2
export SQLALCHEMY_DATABASE_URI=sqlite:///./flask_dance_oauth.db
export FLASK_APP=app.py
export FLASK_ENV=development

cronjobs:
	python3 cronjobs.py

trending:
	python3 cronjobs.py

users:
	python3 cronjobs.py

labels:
	python3 cronjobs.py

jobs:
	celery -A jobs worker --loglevel=INFO 

web:
	flask run -p 5001
