from app.app_and_db import app
from flask import Response, make_response, render_template_string
from . import utils
import json

def _httpResponse(output):
  status = None
  if output.has_key('result') and output.get('result') == 'failed':
    status = utils.HTTP_CODE_500
  else:
    status = utils.HTTP_CODE_200

  template_string = json.dumps(output)
  response = make_response(render_template_string(template_string))
  response.headers['Content-Type'] = "application/json"
  if status:
    response.headers['Status'] = status
  return response


@app.route('/provisioning/core/get_build_numbers', endpoint = 'core.get_build_numbers')
def get_build_numbers():
  from .get_build_numbers import getBuildNumbers
  output = getBuildNumbers()
  return _httpResponse(output)

@app.route('/provisioning/core/start_environment', endpoint = 'core.start_environment')
def start_environment():
  from .start_environment import startEnvironment
  output = startEnvironment()
  return _httpResponse(output)
  
@app.route('/provisioning/core/stop_environment', endpoint = 'core.stop_environment')
def stop_environment():
  from .stop_environment import stopEnvironment
  output = stopEnvironment()
  return _httpResponse(output)

@app.route('/provisioning/core/get_environment_info', endpoint = 'core.get_environment_info')
def get_environment_info():
  from .get_environment_info import getEnvironmentInfo
  output = getEnvironmentInfo()
  return _httpResponse(output)

