from app.app_and_db import app
from flask_user.emails import _get_primary_email as get_primary_email_by_user
import sys

def get_all_user_recipients():
    """Get all user email addresses from provisioning db"""
    User = app.user_manager.db_adapter.UserClass
    users = User.query.all()
    recipients = []
    for user in users:
        email_address = get_primary_email_by_user(user)
        recipient = u"%s %s <%s>" % (unicode(user.first_name), unicode(user.last_name), email_address)
        recipients.append(recipient)

    return recipients


def send_email(recipients, subject, body):
    """Send email with specified subject and body to all recipients with specified email addresses"""
    # send email
    try:
        send_email_function = app.user_manager.send_email_function

        for recipient in recipients:
            send_email_function(recipient, subject, body, body)

        all_email_addresses = u"; ".join(recipients)
        print "Emails with subject <%s> have been sent to %s" % (subject, all_email_addresses)
    except Exception as e:
        print str(e)
