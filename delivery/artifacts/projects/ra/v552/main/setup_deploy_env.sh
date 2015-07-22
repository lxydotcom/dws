#!/bin/bash

# build
export BUILD_NAME_TEMPLATE="nolio_server_linux-x64_5_5_2_b\${BUILD_NUM}.sh"
export BUILDS_LOC="${PROJECT_PATH}/builds"

get_build_path() {
  # evaluate to get installer name
  local BUILD_NUM="${BUILD_NUM}"
  build_name=`eval "echo ${BUILD_NAME_TEMPLATE}"`

  echo "${BUILDS_LOC}/${BUILD_NUM}/${build_name}"
}
