from collections import OrderedDict
from . import utils, docker
import time

# request is a simulated flask request 
def getEnvironmentInfo(request = None):
  output = OrderedDict()
  lock = None
  try:
    # get the query parameters
    if request is None:
      from flask import request

    # get the query parameters
    fullEnvironmentId = request.args.get("environment_id", "")

    # get the environment session data
    session = fullEnvironmentId
    parameters = {}
    for piece in session.split('|'):
      if not piece:
        continue;
      (key, value) = piece.split(':')
      parameters[key] = value

    environmentId = parameters["id"] if "id" in parameters else ""
    productName = parameters["product_name"] if "product_name" in parameters else ""
    productVersion = parameters["product_version"] if "product_version" in parameters else ""
    branch = parameters["branch"] if "branch" in parameters else ""
    buildNumber = parameters["build_number"] if "build_number" in parameters else ""
    serverType = parameters["server_type"] if "server_type" in parameters else ""
    serverPin = parameters["server_pin"] if "server_pin" in parameters else ""
    dbType = parameters["db_type"] if "db_type" in parameters else ""
    dbPin = parameters["db_pin"] if "db_pin" in parameters else ""
    hostname = parameters["hostname"] if "hostname" in parameters else ""
    serverHttpPort = parameters["http_port"] if "http_port" in parameters else ""
    serverHttpsPort = parameters["https_port"] if "https_port" in parameters else ""
    serverVncPort = parameters["vnc_port"] if "vnc_port" in parameters else ""
    serverSshPort = parameters["ssh_port"] if "ssh_port" in parameters else ""
    dbPort = parameters["db_port"] if "db_port" in parameters else ""

    if not environmentId:
      raise RuntimeError("Failed to parse full environment id")

    from .RunContext import RunContext
    rc = RunContext(productName, productVersion, branch, serverType, dbType)

    SERVER_CONTAINER_NAME = 'server_' + environmentId
    SERVER_HTTP_PORT = int(rc.general.server_http_port)
    SERVER_HTTPS_PORT = int(rc.general.server_https_port)
    SERVER_VNC_PORT = int(rc.general.server_vnc_port)
    SERVER_SSH_PORT = int(rc.general.server_ssh_port)

    DB_CONTAINER_NAME = 'db_' + environmentId
    DB_PORT = int(rc.general.db_port)

    # get the db port
    getDbPort = utils.DOCKER_CLIENT + " port %s" % DB_CONTAINER_NAME
    result = utils.runCommand(getDbPort, "Failed to get DB port")
    out = result[1]  # "3306/tcp -> 0.0.0.0:32768\n80/tcp -> 0.0.0.0:32769"
    dbPort = 0
    if '/' in out and ':' in out:
      for line in out.split('\n'):
        if line != '':
          originalPort = int(line.split('/')[0])
          masqPort = int(line.split(':')[1])
          if originalPort == DB_PORT:
            dbPort = masqPort
    else:
      raise RuntimeError("Failed to parse DB port")

    # get the http(s), vnc and ssh ports
    getServerPort = utils.DOCKER_CLIENT + " port %s" % SERVER_CONTAINER_NAME
    result = utils.runCommand(getServerPort, "Failed to get HTTP(S) ports")
    out = result[1]  # "8443/tcp -> 0.0.0.0:34342\n8080/tcp -> 0.0.0.0:12233"
    serverHttpPort = 0
    serverHttpsPort = 0
    serverVncPort = 0
    serverSshPort = 0
    if '/' in out and ':' in out:
      for line in out.split('\n'):
        if line != '':
          originalPort = int(line.split('/')[0])
          masqPort = int(line.split(':')[1])
          if originalPort == SERVER_HTTP_PORT:
            serverHttpPort = masqPort
          elif originalPort == SERVER_HTTPS_PORT:
            serverHttpsPort = masqPort
          elif originalPort == SERVER_VNC_PORT:
            serverVncPort = masqPort
          elif originalPort == SERVER_SSH_PORT:
            serverSshPort = masqPort
    else:
      raise RuntimeError("Failed to parse HTTP(S) ports")

    # generate a session string for the environment to keep its data
    # this session string is used as full environment id passed through
    session = "id:%s|product_name:%s|product_version:%s|branch:%s|build_number:%s|server_type:%s|server_pin:%s|db_type:%s|db_pin:%s|hostname:%s|http_port:%s|https_port:%s|vnc_port:%s|ssh_port:%s|db_port:%s" \
              % (environmentId, productName, productVersion, branch, buildNumber, serverType, serverPin, dbType, dbPin, hostname, serverHttpPort, serverHttpsPort, serverVncPort, serverSshPort, dbPort)
    fullEnvironmentId = session


    output["result"] = "successful"
    output["environment_id"] = fullEnvironmentId

    output["product_name"] = productName
    output["product_version"] = productVersion
    output["branch"] = branch
    output["build_number"] = buildNumber
    output["server_type"] = serverType
    output["server_pin"] = serverPin
    output["db_type"] = dbType
    output["db_pin"] = dbPin

    output["hostname"] = hostname
    output["http_port"] = serverHttpPort
    output["https_port"] = serverHttpsPort
    output["vnc_port"] = serverVncPort
    output["ssh_port"] = serverSshPort
    output["db_port"] = (dbPort if dbType else 0)
  except Exception as e:
    # TODO roll back
    output["result"] = "failed"
    output["error"] = str(e).replace('\n', r'\n')
  finally:
    pass

  return output
