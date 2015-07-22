# simulate http request context for faked http parameters
class Args:
  def __init__(self, **kwargs):
    self.query_parameters = kwargs

  def get(self, query_parameter, default_value = None):
    if query_parameter in self.query_parameters and self.query_parameters[query_parameter]:
      return self.query_parameters[query_parameter]
    else:
      return default_value

class Request:
  def __init__(self, **kwargs):
    self.args = Args(**kwargs)
