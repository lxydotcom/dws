from flask import request
from collections import OrderedDict
from . import utils, docker

# An exception indicates env already stopped
class AlreadyStoppedError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def stopEnvironment(request = None):
  output = OrderedDict()
  lock = None
  try:
    # get the query parameters
    if request is None:
      from flask import request
    fullEnvironmentId = request.args.get("environment_id", "")
    serverPin4Stop = request.args.get("server_pin", "")
    dbPin4Stop = request.args.get("db_pin", "")

    if not fullEnvironmentId:
      raise RuntimeError("No specified full environment id")

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
    serverPin4Start = parameters["server_pin"] if "server_pin" in parameters else ""
    dbType = parameters["db_type"] if "db_type" in parameters else ""
    dbPin4Start = parameters["db_pin"] if "db_pin" in parameters else ""
    hostname = parameters["hostname"] if "hostname" in parameters else ""
    serverHttpPort = parameters["http_port"] if "http_port" in parameters else ""
    serverHttpsPort = parameters["https_port"] if "https_port" in parameters else ""
    serverVncPort = parameters["vnc_port"] if "vnc_port" in parameters else ""
    serverSshPort = parameters["ssh_port"] if "ssh_port" in parameters else ""
    dbPort = parameters["db_port"] if "db_port" in parameters else ""

    from .RunContext import RunContext
    rc = RunContext(productName, productVersion, branch, serverType, dbType)

    # lock
    room = '%s_v%s_%s' % (productName, productVersion, branch)
    lock = utils.Lock(room)
    if not lock.acquire():
      raise RuntimeError('Can not get lock')

    # all of the constants
    HOSTNAME = rc.general.hostname
    REGISTRY_HOST = rc.general.registry_host
    IMAGE_USER_NAME = "%s_v%s_%s" % (productName, productVersion, branch)

    SERVER_CONTAINER_NAME = 'server_' + environmentId
    SERVER_HTTP_PORT = serverHttpPort
    SERVER_HTTPS_PORT = serverHttpsPort
    SERVER_VNC_PORT = serverVncPort
    SERVER_SSH_PORT = serverSshPort

    # server image tags for start and stop
    SERVER_IMAGE_TAG_FOR_START = serverPin4Start if serverPin4Start else buildNumber
    SERVER_IMAGE_FOR_START = "%s/%s/%s_v%s_%s_%s_%s_server:%s" % (REGISTRY_HOST, IMAGE_USER_NAME, productName, productVersion, branch, serverType, dbType, SERVER_IMAGE_TAG_FOR_START)
    if serverPin4Stop:
      SERVER_IMAGE_TAG_FOR_STOP = serverPin4Stop
      SERVER_IMAGE_FOR_STOP = "%s/%s/%s_v%s_%s_%s_%s_server:%s" % (REGISTRY_HOST, IMAGE_USER_NAME, productName, productVersion, branch, serverType, dbType, SERVER_IMAGE_TAG_FOR_STOP)


    if dbType:
      DB_CONTAINER_NAME = 'db_' + environmentId
      DB_PORT = dbPort

      # db image tags for start and stop
      DB_IMAGE_TAG_FOR_START = dbPin4Start if dbPin4Start else buildNumber
      DB_IMAGE_FOR_START = "%s/%s/%s_v%s_%s_%s_%s_db:%s" % (REGISTRY_HOST, IMAGE_USER_NAME, productName, productVersion, branch, serverType, dbType, DB_IMAGE_TAG_FOR_START)
      if dbPin4Stop:
        DB_IMAGE_TAG_FOR_STOP = dbPin4Stop
        DB_IMAGE_FOR_STOP = "%s/%s/%s_v%s_%s_%s_%s_db:%s" % (REGISTRY_HOST, IMAGE_USER_NAME, productName, productVersion, branch, serverType, dbType, DB_IMAGE_TAG_FOR_STOP)

    # all images not exist locally, means the environment already stopped
    serverImageExistsLocally = docker.isImageExists(SERVER_IMAGE_FOR_START, False)
    dbImageExistsLocally = docker.isImageExists(DB_IMAGE_FOR_START, False) if dbType else False
    if not serverImageExistsLocally and not dbImageExistsLocally:
      raise AlreadyStoppedError('The environment already stopped')

    # server container states
    serverContainerState = docker.inspectContainerState(SERVER_CONTAINER_NAME)

    # stop server container
    if serverContainerState in ['running', 'paused']:
      stopServer = utils.DOCKER_CLIENT + " stop %s" % SERVER_CONTAINER_NAME
      utils.runCommand(stopServer, "Failed to stop server")

    # pin this server if required
    if serverPin4Stop and serverContainerState != 'none':
      # if the same pin name is used for start and stop phase, it means it might already exists locally to create the server container for start phase
      if SERVER_IMAGE_FOR_START == SERVER_IMAGE_FOR_STOP and docker.isImageExists(SERVER_IMAGE_FOR_STOP, False):
        # rename the image locally and it will be removed later
        newServerImage4Start = utils.generateRandom()
        renameServerImage1 = utils.DOCKER_CLIENT + " tag %s %s" % (SERVER_IMAGE_FOR_START, newServerImage4Start)
        utils.runCommand(renameServerImage1, "Failed to rename DB image at step 1")
        renameServerImage2 = utils.DOCKER_CLIENT + " rmi %s" % SERVER_IMAGE_FOR_START
        utils.runCommand(renameServerImage2, "Failed to rename DB image at step 2")
        SERVER_IMAGE_FOR_START = newServerImage4Start


      # commit server container to image
      commitServerImage = utils.DOCKER_CLIENT + ' commit -a "Adam Lee <lang.li@ca.com>" -m "pinned" %s %s' % (SERVER_CONTAINER_NAME, SERVER_IMAGE_FOR_STOP)
      utils.runCommand(commitServerImage, "Failed to commit pinned server image")

      # push pinned server image to registry
      pushServerImage = utils.DOCKER_CLIENT + " push %s" % SERVER_IMAGE_FOR_STOP
      utils.runCommand(pushServerImage, "Failed to push pinned server image")

      # remove the pinned server image locally
      removeServerImage = utils.DOCKER_CLIENT + " rmi %s" % SERVER_IMAGE_FOR_STOP
      utils.runCommand(removeServerImage, "Failed to remove pinned server image")


    # remove server container
    if serverContainerState != 'none':
      removeServerContainer = utils.DOCKER_CLIENT + " rm %s" % SERVER_CONTAINER_NAME
      utils.runCommand(removeServerContainer, "Failed to remove server container")

    # remove server image locally, don't throw error if failed because it may be used for other containers
    if serverImageExistsLocally:
      removeServerImage = utils.DOCKER_CLIENT + " rmi %s" % SERVER_IMAGE_FOR_START
      utils.runCarelessCommand(removeServerImage)
    
    if dbType:
      # db container state
      dbContainerState = docker.inspectContainerState(DB_CONTAINER_NAME)

      # stop db container
      if dbContainerState in ['running', 'paused']:
        stopDbContainer = utils.DOCKER_CLIENT + " stop %s" % DB_CONTAINER_NAME
        utils.runCommand(stopDbContainer, "Failed to stop DB")
        
      # pin this db if required
      if dbPin4Stop and dbContainerState != 'none':
        # if the same pin name is used for start and stop phase, it means it might already exists locally to create the db container for start phase
        if DB_IMAGE_FOR_START == DB_IMAGE_FOR_STOP and docker.isImageExists(DB_IMAGE_FOR_STOP, False):
          # rename the image locally and it will be removed later
          newDbImage4Start = utils.generateRandom()
          renameDbImage1 = utils.DOCKER_CLIENT + " tag %s %s" % (DB_IMAGE_FOR_START, newDbImage4Start)
          utils.runCommand(renameDbImage1, "Failed to rename DB image at step 1")
          renameDbImage2 = utils.DOCKER_CLIENT + " rmi %s" % DB_IMAGE_FOR_START
          utils.runCommand(renameDbImage2, "Failed to rename DB image at step 2")
          DB_IMAGE_FOR_START = newDbImage4Start


        # commit db container to image
        commitDbImage = utils.DOCKER_CLIENT + ' commit -a "Adam Lee <lang.li@ca.com>" -m "pinned" %s %s' % (DB_CONTAINER_NAME, DB_IMAGE_FOR_STOP)
        utils.runCommand(commitDbImage, "Failed to commit pinned DB image")

        # push pinned db image to registry
        pushDbImage = utils.DOCKER_CLIENT + " push %s" % DB_IMAGE_FOR_STOP
        utils.runCommand(pushDbImage, "Failed to push pinned DB image")

        # remove the pinned db image locally
        removeDbImage = utils.DOCKER_CLIENT + " rmi %s" % DB_IMAGE_FOR_STOP
        utils.runCommand(removeDbImage, "Failed to remove pinned DB image")


      # remove db container
      if dbContainerState != 'none':
        removeDbContainer = utils.DOCKER_CLIENT + " rm %s" % DB_CONTAINER_NAME
        utils.runCommand(removeDbContainer, "Failed to remove DB container")

      # remove db image locally, don't throw error if failed because it may be used for other containers
      if dbImageExistsLocally:
        removeDbImage = utils.DOCKER_CLIENT + " rmi %s" % DB_IMAGE_FOR_START
        utils.runCarelessCommand(removeDbImage)

    # delete the session (nothing to do)


    output["result"] = "successful"
  except AlreadyStoppedError as e:
    output["result"] = "none"
  except Exception as e:
    # log it and continue the next
    environmentId = environmentId if 'environmentId' in locals() or 'environmentId' in globals() else None
    print "[Provisioning] Failed to stop environment [env id: " + str(environmentId) + "], error: " + str(e)

    # TODO forward roll
    output["result"] = "failed"
    output["error"] = str(e).replace('\n', r'\n')
  finally:
    if lock:
      lock.release()

  return output      