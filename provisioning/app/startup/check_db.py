from __future__ import print_function
import datetime

from app.app_and_db import app, db
from app.startup.init_app import init_app
from app.users.models import User, UserAuth, Role
from app.provisioning.ui.models import Environment
from app.provisioning.ui.models import EnvironmentStatus

def reset_db(app, db):
    """
    Delete all tables; Create all tables; Populate roles and users.
    """

    # Drop all tables
    print('Dropping all tables')
    db.drop_all()

    check_db(app, db)


def check_db(app, db):
    """
    Check if the db table exists, create and populate the tables if not exists
    """

    # Create all tables, it would check firstly to see if each table exists
    print('Creating all tables if not exists')
    db.create_all()

    # Adding roles
    print('Adding roles if not exists')
    admin_role = Role.query.filter_by(name = 'admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        print('Added roles')

    # Add users
    print('Adding users if not exists')
    user_auth = UserAuth.query.filter_by(username = 'admin').first()
    if not user_auth:
        user = add_user(app, db, 'admin', 'Admin', 'User', 'admin@dockerhost.ca.com', 'interOP@123')
        user.roles.append(admin_role)
        print('Added users')

    db.session.commit()


def add_user(app, db, username, first_name, last_name, email, password):
    """
    Create UserAuth and User records.
    """
    user_auth = UserAuth(username=username, password=app.user_manager.hash_password(password))
    user = User(
        active=True,
        first_name=first_name,
        last_name=last_name,
        email=email,
        confirmed_at=datetime.datetime.now(),
        user_auth=user_auth
    )
    db.session.add(user_auth)
    db.session.add(user)
    return user


# Initialize the app and reset the database
if __name__ == "__main__":
    init_app(app, db)
    check_db(app, db)
