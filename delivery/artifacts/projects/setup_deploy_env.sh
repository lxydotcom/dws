#!/bin/bash

# common functions
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

# $1: product name
# $2: product version
# $3: branch
# $4: server type
# $5: db type, it must be empty string if there is no db type  
# $6: build number
_invoke_all_deploy_setup() {
  # check the must-have variables
  [ -z "${PRODUCT_NAME}" ] && echo "Warning: PRODUCT_NAME is empty" 
  [ -z "${PRODUCT_VERSION}" ] && echo "Warning: PRODUCT_VERSION is empty" 
  [ -z "${BRANCH}" ] && echo "Warning: BRANCH is empty" 
  [ -z "${SERVER_TYPE}" ] && echo "Warning: SERVER_TYPE is empty" 

  # check the optional variables
  [ -z "${DB_TYPE}" ] && echo "Note: DB_TYPE is empty" 

  local path="${PROJECT_ROOT_PATH}"
  local path_segments=("${PRODUCT_NAME}" "v${PRODUCT_VERSION}" "${BRANCH}" "servers/${SERVER_TYPE}")
  [ -n "${DB_TYPE}" ] && path_segments+=("deliver/deploy/dbs/${DB_TYPE}")

  for path_segment in "${path_segments[@]}"; do
    [ -z "$path_segment" ] && continue

    path="${path}/${path_segment}"
    local next_setup="${path}/setup_deploy_env.sh"

    [ -e "${next_setup}" ] && . "${next_setup}" "$@"
  done
}

func_build() {
  # empty function
  return 0
}

func_install() {
  # empty function
  return 0
}

func_config() {
  # empty function
  return 0
}

func_test() {
  # empty function
  return 0
}


# setup deploy env
export PROJECT_ROOT_PATH=`get_current_script_location`

export PRODUCT_NAME="${1}"
export PRODUCT_VERSION="${2}"
export BRANCH="${3}"
export SERVER_TYPE="${4}"
export DB_TYPE="${5}"
export BUILD_NUM="${6}"

# project, server, db for this context
export PROJECT_ID="${PRODUCT_NAME}_v${PRODUCT_VERSION}_${BRANCH}"
export PROJECT_PATH="${PROJECT_ROOT_PATH}/${PRODUCT_NAME}/v${PRODUCT_VERSION}/${BRANCH}"

export SERVER_ID="${PROJECT_ID}_${SERVER_TYPE}"
export PROJECT_SERVER_PATH="${PROJECT_PATH}/servers/${SERVER_TYPE}"

[ -n "${DB_TYPE}" ] && export DB_ID="${SERVER_ID}_${DB_TYPE}" && export PROJECT_DB_PATH="${PROJECT_SERVER_PATH}/deliver/deploy/dbs/${DB_TYPE}"

# build
export BUILD_LOC="${PROJECT_PATH}/builds"


# invoke all setup we can look for
_invoke_all_deploy_setup "$@"
