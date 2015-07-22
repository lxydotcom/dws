from app.app_and_db import db
from app.users.models import User

class Environment(db.Model):
  id = db.Column(db.Integer(), primary_key = True, autoincrement = True)
  environment_id = db.Column(db.String(1023), nullable = False, server_default = '')
  environment_name = db.Column(db.String(255), nullable = False, server_default = '')
  product_name = db.Column(db.String(255), nullable = False, server_default = '')
  product_version = db.Column(db.String(20), nullable = False, server_default = '')
  branch = db.Column(db.String(255), nullable = False, server_default = '')
  build_number = db.Column(db.String(20), nullable = False, server_default = '')
  server_type = db.Column(db.String(255), nullable = False, server_default = '')
  hostname = db.Column(db.String(255), nullable = False, server_default = '')
  http_port = db.Column(db.Integer(), nullable = False, server_default = '0')
  https_port = db.Column(db.Integer(), nullable = False, server_default = '0')
  vnc_port = db.Column(db.Integer(), nullable = False, server_default = '0')
  ssh_port = db.Column(db.Integer(), nullable = False, server_default = '0')
  db_type = db.Column(db.String(255), nullable = False, server_default = '')
  db_port = db.Column(db.Integer(), nullable = False, server_default = '0')
  start_server_pin = db.Column(db.String(255), nullable = False, server_default = '')
  start_db_pin = db.Column(db.String(255), nullable = False, server_default = '')
  stop_server_pin = db.Column(db.String(255), nullable = False, server_default = '')
  stop_db_pin = db.Column(db.String(255), nullable = False, server_default = '')

  status = db.Column(db.String(20), nullable = False, server_default = '')
  status_detail = db.Column(db.String(1023), nullable = False, server_default = '')

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))

  user = db.relationship('User', uselist = False, backref = db.backref('environments', lazy = 'dynamic'))

class EnvironmentStatus(db.Model):
  from sqlalchemy import func
  id = db.Column(db.Integer(), primary_key = True, autoincrement = True)
  status = db.Column(db.String(255), nullable = False, server_default = '')
  status_detail = db.Column(db.String(1023), nullable = False, server_default = '')
  happen = db.Column(db.DateTime(), nullable = False, default = func.now())
  location = db.Column(db.String(255), nullable = False, server_default = '')
  owner = db.Column(db.String(255), nullable = False, server_default = '')

  env_id = db.Column(db.Integer(), db.ForeignKey('environment.id', ondelete='CASCADE'))

  environment = db.relationship('Environment', uselist = False, backref = db.backref('statuses', lazy = 'dynamic'))
