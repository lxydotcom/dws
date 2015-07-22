from app.app_and_db import app, db
from flask import Response, make_response, render_template_string, render_template, redirect, url_for, request
from flask_user import current_user, login_required, roles_required

from flask_wtf import Form
import wtforms.fields as fields

class RecordFilterForm(Form):
  status = fields.SelectField('Status', default = '', 
    choices = [
      ('', 'All'),
      ('starting', 'Starting'),
      ('running', 'Running'),
      ('stopping', 'Stopping'),
      ('stopped', 'Stopped'),
      ('removing', 'Removing'),
      ('failed', 'Failed')])


@app.route('/provisioning/ui/get_build_numbers')
@login_required
def get_build_numbers():
  class MyDict(dict):
    pass
  build = MyDict()
  build['product_name'] = 'ra'
  build['product_version'] = '552'
  build['branch'] = 'main'
  build['server_type'] = 'allinone'
  build['db_type'] = 'mysql'
  build['last_build_number'] = '0'

  if request.args.get('product_name') is None:
    query_string = '&'.join(['%s=%s' % (key, value) for key, value in build.iteritems()])
    return redirect('%s?%s' % (url_for('get_build_numbers'), query_string))

  from ..core.get_build_numbers import getBuildNumbers
  output = getBuildNumbers()

  output = dict(output)

  if output['result'] not in ['failed', 'none']:
    later_build_numbers = output['later_build_numbers']
    if later_build_numbers:
      later_build_numbers = later_build_numbers.split(',')
    else:
      later_build_numbers = []
    latest_build_number = output['latest_build_number']

    # if there is build numbers available
    if later_build_numbers and latest_build_number and int(latest_build_number) > 0:
      # populate the build numbers select field
      class BuildNumberForm(Form):
        build_number = fields.SelectField('Build Numbers', default = latest_build_number,
          choices = [(build_number, build_number) for build_number in later_build_numbers]
        )
        environment_name = fields.StringField(default = '')

        product_name = fields.HiddenField(default = build['product_name'])
        product_version = fields.HiddenField(default = build['product_version'])
        branch = fields.HiddenField(default = build['branch'])
        server_type = fields.HiddenField(default = build['server_type'])
        db_type = fields.HiddenField(default = build['db_type'])

      form = BuildNumberForm()

      build['build_number_form'] = form
  else:
    print "[Provisioning] Failed to get build numbers [%s, %s, %s, %s, %s] since %s, the result is: %s" % (
      build['product_name'], build['product_version'], build['branch'], build['server_type'], build['db_type'], build['last_build_number'],
      output['error'] if 'error' in output else output['result'])

  builds = [build]
  return render_template('provisioning/get_build_number.html', builds = builds)


@app.route('/provisioning/ui/list_environment', methods=('GET', 'POST'))
@login_required
def list_environments():
  # filter form
  formdata = request.args if request.method == 'GET' else request.form
  form = RecordFilterForm(formdata)
  status = form.status.data

  if status:
    environments = current_user.environments.filter_by(status = status).all()
  else:
    environments = current_user.environments.all()

  from .environment_record import EnvironmentRecord
  environment_list = []
  for environment in environments:
    environment_record = EnvironmentRecord(environment)

    query_parameters = {'id': environment.id}
    query_string = '&'.join(['%s=%s' % (key, value) for key, value in query_parameters.iteritems()])
    environment_record.query_string = query_string

    environment_list.append(environment_record)
  
  return render_template('provisioning/list_environments.html', 
    environment_ids = EnvironmentRecord.ids, environment_display_names = EnvironmentRecord.display_names, environment_list = environment_list, form = form)


@app.route('/provisioning/ui/change_environment', methods = ('GET', 'POST'))
@login_required
def change_environment():
  formdata = request.args if request.method == 'GET' else request.form
  env_id = formdata.get('pk')
  column_name = formdata.get('name')
  column_value = formdata.get('value')

  from .models import Environment
  env = Environment.query.filter_by(id = env_id).first()

  # validate the request, if failed, return 400 bad request
  if not hasattr(env, column_name):
    return ('No such field for environment: %s' % column_name, 400)
  elif len(column_value) > 255:
    return ('Value length %d exceeds the limitation 255' % len(column_value), 400)

  # change the env
  setattr(env, column_name, column_value)
  db.session.commit()

  return ('', 200)



@app.route('/provisioning/ui/start_environment', methods = ('GET', 'POST'))
@login_required
def start_environment():
  formdata = request.args if request.method == 'GET' else request.form

  # create an record for starting environment
  from .models import Environment
  env = Environment()
  env.status = 'starting'
  env.status_detail = 'starting'
  env.environment_name = formdata.get('environment_name')
  env.product_name = formdata.get('product_name')
  env.product_version = formdata.get('product_version')
  env.branch = formdata.get('branch')
  env.build_number = formdata.get('build_number')
  env.server_type = formdata.get('server_type')
  env.start_server_pin = formdata.get('server_pin')
  env.db_type = formdata.get('db_type')
  env.start_db_pin = formdata.get('db_pin')
  env.user = current_user
  db.session.add(env)
  db.session.commit()

  # run task in background
  result = start_environment_task.delay(env.id)
  return redirect(url_for('list_environments', status = 'starting'))
  
@app.route('/provisioning/ui/stop_environment')
@login_required
def stop_environment(removal = False):
  env_id = request.args.get('id')
  if not env_id:
    raise RuntimeError('environment id is not specified')

  from .models import Environment
  env = Environment.query.filter_by(id = env_id).first()
  if env:
    removal_on_stopped = env.status == 'stopped' if removal else False
    status = "removing" if removal else "stopping"
    env.status = status
    env.status_detail = status
    env.stop_server_pin = request.args.get('server_pin', '')
    env.stop_db_pin = request.args.get('db_pin', '')
    db.session.commit()

    # run task in background
    result = stop_environment_task.delay(env_id, removal, removal_on_stopped)

  redirect_endpoint = request.args.get('redirect', 'list_environments')
  return redirect(url_for(redirect_endpoint))


@app.route('/provisioning/ui/remove_environment')
@login_required
def remove_environment():
  # stop and remove it in backgroup if it exists
  return stop_environment(True)


@app.celery.task
def start_environment_task(env_id):
  with app.app_context():
    from .models import Environment
    env = Environment.query.filter_by(id = env_id).first()

    from .utils import Request
    parameters = {
        'product_name': env.product_name,
        'product_version': env.product_version,
        'branch': env.branch,
        'build_number': env.build_number,
        'server_type': env.server_type,
        'server_pin': env.start_server_pin,
        'db_type': env.db_type,
        'db_pin': env.start_db_pin
    }
    simulated_request = Request(**parameters)

    from ..core.start_environment import startEnvironment
    output = startEnvironment(simulated_request)

    output = dict(output)

    if output['result'] == 'failed':
      env.status = 'failed'
      env.status_detail = output['error']
    else:
      from .environment_record import fill_environment_from_output
      fill_environment_from_output(env, output)
      env.status = 'running'
      env.status_detail = 'running'

    db.session.commit()


@app.celery.task
def stop_environment_task(env_id, removal = False, removal_on_stopped = False):
  with app.app_context():
    from .models import Environment
    env = Environment.query.filter_by(id = env_id).first()

    if env:
      if env.environment_id and env.status != 'stopped' and (not removal_on_stopped):
        from .utils import Request
        parameters = {
          'environment_id': env.environment_id,
          'server_pin': env.stop_server_pin if not removal else None,
          'db_pin': env.stop_db_pin if not removal else None
        }
        simulated_request = Request(**parameters)

        from ..core.stop_environment import stopEnvironment
        output = stopEnvironment(simulated_request)

        output = dict(output)
        if output['result'] == 'failed':
          env.status = 'failed'
          env.status_detail = output['error']
        else:
          env.status = 'stopped'
          env.status_detail = 'stopped'
      else:
        # anyway, the stop process is completed here, mark the status as stopped
        env.status = 'stopped'
        env.status_detail = 'stopped'

      if removal and env.status == 'stopped':
        # delete it from DB if existing env stopped, or env not exists at all
        db.session.delete(env)

      db.session.commit()


@app.route('/provisioning/ui/admin', methods = ('GET', 'POST'))
@roles_required('admin')    # Limits access to users with the 'admin' role
def admin():
  # filter form
  form = RecordFilterForm()
  status = form.status.data

  from .models import Environment
  if status:
    environments = Environment.query.filter_by(status = status).all()
  else:
    environments = Environment.query.all()

  from .environment_record import EnvironmentRecord
  environment_list = []
  for environment in environments:
    environment_record = EnvironmentRecord(environment)

    query_parameters = {'id': environment.id}
    query_string = '&'.join(['%s=%s' % (key, value) for key, value in query_parameters.iteritems()])
    environment_record.query_string = query_string

    # user related to this env
    user = environment.user
    environment_record.user = "%s %s <%s>" % (user.first_name, user.last_name, user.email)

    environment_list.append(environment_record)
    
  return render_template('provisioning/admin.html', 
    environment_ids = EnvironmentRecord.ids, environment_display_names = EnvironmentRecord.display_names, environment_list = environment_list, form = form)

@app.route('/provisioning/ui/admin_update_environment')
@roles_required('admin')    # Limits access to users with the 'admin' role
def admin_update_environment():
  status = request.args.get('status', 'running')
  from .models import Environment
  environments = Environment.query.filter_by(status = status).all()

  from .admin import update_environment
  for environment in environments:
    try:
      update_environment(environment)
    except Exception as e:
      # log it and continue the next
      print "[Provisioning] Failed to update environment [id: " + str(environment.id) + "], error: " + str(e)

  db.session.commit()

  return redirect(url_for('admin'))


@app.route('/provisioning/ui/admin_restart_environment')
@roles_required('admin')    # Limits access to users with the 'admin' role
def admin_restart_environment():
  """
  BE CAREFUL! Admin specific operation, re-start the env if it not exist. 
  It would bring up several tasks to create the same env and only the last one is tracked, others will not be tracked.
  """
  env_id = request.args.get('id')
  if env_id:
    from .models import Environment
    env = Environment.query.filter_by(id = env_id).first()

    if env and (not env.environment_id):  # restart it if this environment not exist
      env.status_detail = 're-starting'
      db.session.commit()

      result = start_environment_task.delay(env_id)

  return redirect(url_for('admin'))


@app.route('/provisioning/ui/admin_restop_environment')
@roles_required('admin')    # Limits access to users with the 'admin' role
def admin_restop_environment():
  """
  BE CAREFUL! Admin specific operation, re-stop the env if it exists. 
  It would bring up several tasks to stop the same env. the env would be stopped if one of them succeeds
  """
  env_id = request.args.get('id')
  if env_id:
    from .models import Environment
    env = Environment.query.filter_by(id = env_id).first()

    if env and env.environment_id:  # restop it if this environment exists
      env.status_detail = 're-stopping'
      db.session.commit()

      result = stop_environment_task.delay(env_id)

  return redirect(url_for('admin'))


@app.route('/provisioning/ui/admin_reremove_environment')
@roles_required('admin')    # Limits access to users with the 'admin' role
def admin_reremove_environment():
  """
  BE CAREFUL! Admin specific operation, re-remove the env if it exists. 
  It would bring up several tasks to remove the same env. the env would be removed if one of them succeeds
  """
  env_id = request.args.get('id')
  if env_id:
    from .models import Environment
    env = Environment.query.filter_by(id = env_id).first()

    if env:  # reremove it even environment id not exist
      env.status_detail = 're-removing'
      db.session.commit()

      result = stop_environment_task.delay(env_id, True)

  return redirect(url_for('admin'))

