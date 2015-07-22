from flask import request
from app.app_and_db import app
from . import notify_users

@app.route('/utils/notify_all_users', methods=['GET', 'POST'])
def notify_all_users():
    subject = request.form.get("subject", "")
    body = request.form.get("body", "")
    notify_all_users_task.delay(subject, body)
    return "Schedule a task to notify all users"

@app.celery.task()
def notify_all_users_task(subject, body):
    with app.app_context():
        recipients = notify_users.get_all_user_recipients()
        notify_users.send_email(recipients, subject, body)

