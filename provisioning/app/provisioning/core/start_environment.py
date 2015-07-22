from collections import OrderedDict
from . import utils, docker
import time

# request is a simulated flask request 
def startEnvironment(request = None):
  output = OrderedDict()
  lock = None
  try:
    # get the query parameters
    if request is None:
      from flask import request
    productName = request.args.get("product_name", "")
    productVersion = request.args.get("product_version", "")
    branch = request.args.get("branch", "")
    buildNumber = request.args.get("build_number", "")
    serverType = request.args.get("server_type", "")
    serverPin = request.args.get("server_pin", "")
    dbType = request.args.get("db_type", "")
    dbPin = request.args.get("db_pin", "")

    from .RunContext import RunContext
    rc = RunContext(productName, productVersion, branch, serverType, dbType)

    # lock
    room = '%s_v%s_%s' % (productName, productVersion, branch)
    lock = utils.Lock(room)
    if not lock.acquire():
      raise RuntimeError('Can not get lock')

    # generate a random string as env id
    environmentId = utils.generateRandom()

    # all of the constants
    HOSTNAME = rc.general.hostname
    REGISTRY_HOST = rc.general.registry_host
    IMAGE_USER_NAME = "%s_v%s_%s" % (productName, productVersion, branch)

    SERVER_HOSTNAME = 'myhost'
    SERVER_CONTAINER_NAME = 'server_' + environmentId
    SERVER_HTTP_PORT = int(rc.general.server_http_port)
    SERVER_HTTPS_PORT = int(rc.general.server_https_port)
    SERVER_VNC_PORT = int(rc.general.server_vnc_port)
    SERVER_SSH_PORT = int(rc.general.server_ssh_port)
    SERVER_IMAGE_TAG = serverPin if serverPin else buildNumber
    SERVER_IMAGE = "%s/%s/%s_v%s_%s_%s_%s_server:%s" % (REGISTRY_HOST, IMAGE_USER_NAME, productName, productVersion, branch, serverType, dbType, SERVER_IMAGE_TAG)
    SERVER_COMMAND = "/usr/bin/supervisord -c /etc/supervisor/supervisord.conf -n"

    if dbType:
      DB_HOSTNAME = 'mydb'
      DB_CONTAINER_NAME = 'db_' + environmentId
      DB_PORT = int(rc.general.db_port)
      DB_RUN_OPTIONS = ("-e %s" % rc.general.db_running_env) if rc.general.db_running_env else ""

      DB_IMAGE_TAG = dbPin if dbPin else buildNumber
      DB_IMAGE = "%s/%s/%s_v%s_%s_%s_%s_db:%s" % (REGISTRY_HOST, IMAGE_USER_NAME, productName, productVersion, branch, serverType, dbType, DB_IMAGE_TAG)

      # run the db image
      runDb = utils.DOCKER_CLIENT + " run -d --name %s -h %s -p %d %s %s" % (
                DB_CONTAINER_NAME, DB_HOSTNAME, DB_PORT, DB_RUN_OPTIONS, DB_IMAGE)
      utils.runCommand(runDb, "Failed to start DB")
    
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

    # TODO wait the db ready, for example mysql, use docker exec to get response, a specific script should be defined in run.conf: post_db_start, pre_db_stop
    time.sleep(10)

    # run the server image, link to db container
    if dbType:
      link = "--link %s:db" % DB_CONTAINER_NAME
    else:
      link = ""
    runServer = utils.DOCKER_CLIENT + " run -d --name %s -h %s -p %d -p %d -p %d -p %d %s %s %s" % ( # TODO
                    SERVER_CONTAINER_NAME, SERVER_HOSTNAME, SERVER_HTTP_PORT, SERVER_HTTPS_PORT, SERVER_VNC_PORT, SERVER_SSH_PORT, link, SERVER_IMAGE, SERVER_COMMAND)
    utils.runCommand(runServer, "Failed to start server")

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

    # get the node docker server hostname in which server container lives
    serverNodeHostname = docker.inspectNodeHostname(SERVER_CONTAINER_NAME)

    # wait the server ready
    serverReady = utils.checkServerReady(rc, serverNodeHostname, serverHttpPort, 5)
    if not serverReady:
      raise RuntimeError("Server is not ready")

    # get the hostname of server
    hostname = serverNodeHostname

    # generate a session string for the environment to keep its data
    # this session string is used as full environment id passed through
    session = "id:%s|product_name:%s|product_version:%s|branch:%s|build_number:%s|server_type:%s|server_pin:%s|db_type:%s|db_pin:%s|hostname:%s|http_port:%s|https_port:%s|vnc_port:%s|ssh_port:%s|db_port:%s" \
              % (environmentId, productName, productVersion, branch, buildNumber, serverType, serverPin, dbType, dbPin, hostname, serverHttpPort, serverHttpsPort, serverVncPort, serverSshPort, dbPort)
    fullEnvironmentId = session


    output["result"] = "successful"
    output["environment_id"] = fullEnvironmentId
    output["hostname"] = hostname
    output["http_port"] = serverHttpPort
    output["https_port"] = serverHttpsPort
    output["vnc_port"] = serverVncPort
    output["ssh_port"] = serverSshPort
    output["db_port"] = (dbPort if dbType else 0)
  except Exception as e:
    # log it and continue the next
    environmentId = environmentId if 'environmentId' in locals() or 'environmentId' in globals() else None
    print "[Provisioning] Failed to start environment [env id: " + str(environmentId) + "], error: " + str(e)

    # TODO roll back
    output["result"] = "failed"
    output["error"] = str(e).replace('\n', r'\n')
  finally:
    if lock:
      lock.release()

  return output
