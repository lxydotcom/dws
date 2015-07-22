#!/bin/bash

# common env and functions

#####
# common functions
####
get_current_script_location() {
  local script=${BASH_SOURCE[1]}

  get_absolute_path `dirname ${script}`
}

get_absolute_path() {
  local path=$1

  local oldDir=`pwd`
  cd "${path}"
  local newDir=`pwd`
  cd "${oldDir}"

  echo "${newDir}"
}

#####
# common env
#####
DOCKER_HOST_HOSTNAME="`hostname`"

DOCKER_SERVER_PORT="2374"
DOCKER_SERVER_HOST="tcp://${DOCKER_HOST_HOSTNAME}:${DOCKER_SERVER_PORT}"
DOCKER_SWARM_PORT="2375"
DOCKER_SWARM_HOST="tcp://${DOCKER_HOST_HOSTNAME}:${DOCKER_SWARM_PORT}"
DOCKER_REG="${DOCKER_HOST_HOSTNAME}:5000"

_current_path=`get_current_script_location`
DWS_ROOT_PATH=${_current_path}/../
DWS_ROOT_PATH_IN_CONTAINER=/dws/

DOCKER_IMAGE_USER=lijla02
