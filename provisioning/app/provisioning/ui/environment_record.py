def url_for(endpoint):
  url = '/'
  try:
    from flask import url_for
    url = url_for(endpoint)
  except Exception as e:
    # throw error due to celery wouldn't get web request context
    # just ignore it
    print e
  return url


_change_env_url = url_for('change_environment')
_render_for_running = '"$status" == "running"'

_environment_naming = [
  {'id': 'id', 'display': True, 'display_name': 'Id', 'column_id': 'id',
      'display_template': '<div id="id_div_$id" data-toggle="tooltip" data-container="#id_div_$id" data-placement="bottom" data-delay=\'{"show": 0, "hide": 10}\' title="$environment_id">$id</div'},
  {'id': 'environment_id', 'display': False, 'display_name': 'Environment Id', 'column_id': 'environment_id'},
  {'id': 'environment_name', 'display': True, 'display_name': 'Environment Name', 'column_id': 'environment_name',
      'display_template': '<a href="#" class="environment_name" data-name="environment_name" data-type="text" data-pk="$id" data-url="%s" data-title="Change Environment Name">$environment_name</a>' % _change_env_url},
  {'id': 'product_name', 'display': True, 'display_name': 'Product Name', 'column_id': 'product_name'},
  {'id': 'product_version', 'display': True, 'display_name': 'Product Version', 'column_id': 'product_version'},
  {'id': 'branch', 'display': True, 'display_name': 'Branch', 'column_id': 'branch'},
  {'id': 'build_number', 'display': True, 'display_name': 'Build Number', 'column_id': 'build_number'},
  {'id': 'server_type', 'display': True, 'display_name': 'Server Type', 'column_id': 'server_type'},
  {'id': 'hostname', 'display': True, 'display_name': 'Server Hostname', 'column_id': 'hostname'},
  {'id': 'http_port', 'display': _render_for_running, 'display_name': 'Server HTTP Port', 'column_id': 'http_port', 
      'display_template': '<a href="http://$hostname:$http_port/" target="_blank">$http_port</a>'},
  {'id': 'https_port', 'display': _render_for_running, 'display_name': 'Server HTTPS Port', 'column_id': 'https_port', 
      'display_template': '<a href="https://$hostname:$https_port/" target="_blank">$https_port</a>'},
  {'id': 'vnc_port', 'display': _render_for_running, 'display_name': 'Server VNC Port', 'column_id': 'vnc_port', 
      'display_template': '<a href="http://$hostname:$vnc_port/vnc.html" target="_blank">$vnc_port</a>'},
  {'id': 'db_type', 'display': True, 'display_name': 'DB Type', 'column_id': 'db_type'},
  {'id': 'db_port', 'display': True, 'display_name': 'DB Port', 'column_id': 'db_port'},
  {'id': 'start_server_pin', 'display': False, 'display_name': 'Server Start From', 'column_id': 'start_server_pin'},
  {'id': 'start_db_pin', 'display': False, 'display_name': 'DB Start From', 'column_id': 'start_db_pin'},
  {'id': 'status', 'display': True, 'display_name': 'Status', 'column_id': 'status',
      'display_template': '<div id="status_div_$id" data-toggle="tooltip" data-container="#status_div_$id" data-placement="bottom" data-delay=\'{"show": 0, "hide": 10}\' title="$status_detail">$status</div'},
  {'id': 'status_detail', 'display': False, 'display_name': 'Status Detail', 'column_id': 'status_detail'},
  {'id': 'stop_server_pin', 'display': False, 'display_name': 'Server Stop To', 'column_id': 'stop_server_pin'},
  {'id': 'stop_db_pin', 'display': False, 'display_name': 'DB Stop To', 'column_id': 'stop_db_pin'}
]

_ids = []
_display_names = []
for naming_item in _environment_naming:
  if naming_item['display']:
    _ids.append(naming_item['id'])
    _display_names.append(naming_item['display_name'])


class EnvironmentRecord:
  class ItemValue:
    def __str__(self):
      return unicode(self.value)

    def __unicode__(self):
      return unicode(self.value)

    def __init__(self, record, value, display, display_template):
      self.record = record
      self.value = value
      self.display = display
      self.display_template = display_template

    def render(self):
      if self.display_template and self._canBeRendered():
        from string import Template
        return Template(self.display_template).substitute(self.record)
      else:
        return self.get_value()

    def get_value(self):
      return self.value

    def _canBeRendered(self):
      if self.display:
        if self.display == True:
          return True

        display_cond = str(self.display)
        from string import Template
        display_cond = Template(display_cond).substitute(self.record)
        able = eval(display_cond)
        return able
      else:
        return False


  ids = _ids
  display_names = _display_names

  def __init__(self, environment):
    for naming_item in _environment_naming:
      id = naming_item['id']

      if id == 'stop_server_pin':
        value = self._get_value_from_db(environment, 'start_server_pin')
      elif id == 'stop_db_pin':
        value = self._get_value_from_db(environment, 'start_db_pin')
      else:
        value = self._get_value_from_db(environment, naming_item['column_id'])

      display = naming_item['display'] if 'display' in naming_item else None
      display_template = naming_item['display_template'] if 'display_template' in naming_item else None
      self[id] = self._wrap(value, display, display_template)

  def _get_value_from_db(self, environment, column_id):
    if column_id:
      return getattr(environment, column_id)
    else:
      return None

  def _wrap(self, value, display, display_template):
    return self.ItemValue(self, value, display, display_template)

  def __setitem__(self, attr, value):
    setattr(self, attr, value)

  def __getitem__(self, attr):
    return getattr(self, attr)

  def __iter__(self):
    self.iter_index = -1
    return self

  def next(self):
    self.iter_index += 1
    if self.iter_index < len(self.ids):
      return self.ids[self.iter_index]
    else:
      raise StopIteration


def fill_environment_from_output(environment, output):
  for naming_item in _environment_naming:
    id = naming_item['id']
    column_id = naming_item['column_id']

    if column_id and hasattr(environment, column_id) and id in output:
      setattr(environment, column_id, output[id])
      
  return environment