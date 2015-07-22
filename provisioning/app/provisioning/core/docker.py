import utils

# check if an image existing
def isImageExists(image, searchInRegistry=True, restoreLocally=False):
  # try to inspect the image locally
  inspectImage = utils.DOCKER_CLIENT + " inspect %s" % image
  result = utils.runCarelessCommand(inspectImage)
  if result[0] == 0:
    return True

  # try to pull the image from registry
  if searchInRegistry:
    pullImage = utils.DOCKER_CLIENT + " pull %s" % image
    result = utils.runCarelessCommand(pullImage)
    if result[0] == 0:
      if restoreLocally:
        # restore the workspace locally
        rmImage = utils.DOCKER_CLIENT + " rmi %s" % image
        utils.runCarelessCommand(rmImage)  # don't throw error if restore failed
      return True
  return False


# check the state of container
def inspectContainerState(container):
  # inspect its state, if there is error it means the object not exists
  inspect = utils.DOCKER_CLIENT + " inspect -f '{{.State.Running}}|{{.State.Paused}}' %s" % container
  result = utils.runCarelessCommand(inspect)
  code = result[0]
  if code != 0:
    return 'none'
  out = result[1].rstrip('\n')
  [running, paused] = out.split('|')
  if running == 'true' and paused == 'false':
    return 'running'
  elif running == 'true' and paused == 'true':
    return 'paused'
  elif running == 'false':
    return 'stopped'
  else:
    return 'none'


def inspectNodeHostname(container):
  # inspect container's Node info, get the Name from it, which is the hostname of node host
  inspectNode = utils.DOCKER_CLIENT + " inspect -f '{{.Node.Name}}' " + container
  result = utils.runCarelessCommand(inspectNode)
  code = result[0]
  if code != 0:
    return "<unknown>"
  out = result[1].rstrip('\n')
  if out == '<no value>':
    return "<unknown>"
  return out
        
