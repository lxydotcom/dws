#!/bin/bash

# env specific to this project

_nolio="${BUILDS_DOWNLOAD_ROOT_LOC}/nolio"

# mount build repository
if ! mountpoint -q "${_nolio}"; then
  echo ${DOCKER_HOST_PASSWORD} | sudo -S mkdir -p -m 0777 ${_nolio}
  echo ${DOCKER_HOST_PASSWORD} | sudo -S mount -t cifs -o username=lijla02,password=sign8L\>EE,rw,dir_mode=0777,file_mode=0777 //guaya03-dcamcn1/NolioBuilds ${_nolio}
fi

# build 
export BUILDS_DOWNLOAD_LOC="${_nolio}/v5.5.2/Main"
export BUILD_NAME_TEMPLATE="nolio_server_linux-x64_5_5_2_b\${BUILD_NUM}.sh"
export BUILDS_LOC="${PROJECT_PATH}/builds"

# log file
_log_loc="${PROJECT_PATH}/var/log"
export BUILD_LOG_PATH="${_log_loc}/build.log"
export IMAGE_LOG_PATH="${_log_loc}/image.log"

# var file
_var_path="${PROJECT_PATH}/var"
export STATUS_DB_PATH="${_var_path}/status/delivery_status.db"
export LOCK_TASK_PATH_PREFIX="${_var_path}/lock/.lock_task_"
export LOCK_WORKING_ENV_PATH="${_var_path}/lock/.lock_working_env"

# all server types, global variable
ALL_SERVER_TYPES=("allinone")
