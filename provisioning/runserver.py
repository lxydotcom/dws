# This file starts the WSGI web application.
# - Heroku starts gunicorn, which loads Procfile, which starts runserver.py
# - Developers can run it from the command line: python runserver.py

from app.app_and_db import app, db
from app.startup.init_app import init_app

init_app(app, db)


# celery config
from celery import Celery
def make_celery(app):
  celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
  celery.conf.update(app.config)
  return celery

app.config.update(
  CELERY_BROKER_URL='redis://localhost:6379/0',
  CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

celery = make_celery(app)
app.celery = celery


# startup provisioning
from app.provisioning.startup import init_app
init_app(app, db)


# Start a development web server if executed from the command line
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555, debug=True)

