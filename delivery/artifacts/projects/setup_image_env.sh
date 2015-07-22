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

setup_image_project_env() {
  export PRODUCT_NAME=$1
  export PRODUCT_VERSION=$2
  export BRANCH=$3

  # project for this context
  export PROJECT_ID="${PRODUCT_NAME}_v${PRODUCT_VERSION}_${BRANCH}"
  export PROJECT_PATH="${PROJECT_ROOT_PATH}/${PRODUCT_NAME}/v${PRODUCT_VERSION}/${BRANCH}"

  # TODO build, image, deploy and run should use the same deliver construct of directory and deliver setup hierarchy
  local setup_script="${PROJECT_PATH}/setup_image_project_env.sh"

  [ -e "${setup_script}" ] && . "${setup_script}"
}

setup_image_server_env() {
  export SERVER_TYPE=$1
  
  export SERVER_ID="${PROJECT_ID}_${SERVER_TYPE}"
  export PROJECT_SERVER_PATH="${PROJECT_PATH}/servers/${SERVER_TYPE}"

  # TODO build, image, deploy and run should use the same deliver construct of directory and deliver setup hierarchy
  local setup_script="${PROJECT_SERVER_PATH}/setup_image_server_env.sh"
  [ -e "${setup_script}" ] && . "${setup_script}"
}

setup_image_db_env() {
  export DB_TYPE=$1

  export DB_ID="${SERVER_ID}_${DB_TYPE}"
  export PROJECT_DB_PATH="${PROJECT_SERVER_PATH}/deliver/image/dbs/${DB_TYPE}"

  # TODO build, image, deploy and run should use the same deliver construct of directory and deliver setup hierarchy
  local setup_script="${PROJECT_DB_PATH}/setup_image_db_env.sh"
  [ -e "${setup_script}" ] && . "${setup_script}"
}

setup_image_build_number_env() {
  export BUILD_NUM=${1}
}

func_post_start_db() {
  # empty function
  return 0
}

func_pre_stop_db() {
  # empty function
  return 0
}


#####
# common env
#####
export DOCKER_HOST_HOSTNAME="localhost"

export DOCKER_HOST_USER="docker"
export DOCKER_HOST_PASSWORD="interOP@123"

export PROJECT_ROOT_PATH=`get_current_script_location`

export BUILDS_DOWNLOAD_ROOT_LOC="/mnt/builds"
echo ${DOCKER_HOST_PASSWORD} | sudo -S mkdir -p -m 0777 ${BUILDS_DOWNLOAD_ROOT_LOC}

export BROADCAST_MAIL_TO="lijla02@ca.com"
export ADMIN_MAIL_TO="lijla02@ca.com"

export HOST_PATH=`get_absolute_path "${PROJECT_ROOT_PATH}/../.."`
export HOST_PATH_IN_CONTAINER='/mnt/host'

export SCRIPTS_LOC_IN_CONTAINER="${HOST_PATH_IN_CONTAINER}/Scripts"

export DEPLOY_SERVER_CMD_IN_CONTAINER="${SCRIPTS_LOC_IN_CONTAINER}/deploy_server"

export DOCKER_REG="${DOCKER_HOST_HOSTNAME}:5000"

# all projects (not used)
#export ALL_PROJECTS=("ra_v552_main" "ra_v552_puppet")
