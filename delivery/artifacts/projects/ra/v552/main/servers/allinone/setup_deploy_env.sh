#!/bin/bash

func_install() {
  pre_install_server || return $?

  install_server
  local status_code=$?

  post_install_server || return $?

  return ${status_code}
}

install_server() {
  # log file
  _log_loc="${PROJECT_PATH}/var/log"
  local install_server_silent_log_path="${_log_loc}/install_server_${SERVER_TYPE}_${DB_TYPE}_b${BUILD_NUM}_silent.log"

  # silent response file
  local build_silent_response_path="${PROJECT_DB_PATH}/etc/server.response.varfile"

  # install server
  install_build `get_build_path` "${build_silent_response_path}" "${install_server_silent_log_path}" || return $?

  wait_port_status localhost 6600 up 300 || return $?
  wait_port_status localhost 6900 up 300 || return $?
  wait_port_status localhost 8080 up 300 || return $?
  wait_port_status localhost 8443 up 300 || return $?
  wait_port_status localhost 8005 up 300 || return $?
  wait_port_status localhost 8009 up 300 || return $?

  # check the product services all ready, and warm up for 3 minutes
  ${PROJECT_SERVER_PATH}/etc/waitServerReady.py || return $?

  stop_service "/etc/init.d/nolioagent" || return $?
  stop_service "/etc/init.d/NolioASAP" || return $?
  stop_service "/etc/init.d/nolio_update_service" || return $?

  # check the product services all down
  wait_port_status localhost 6600 down 300 || return $?
  wait_port_status localhost 6900 down 300 || return $?
  wait_port_status localhost 8080 down 300 || return $?
  wait_port_status localhost 8443 down 300 || return $?
  wait_port_status localhost 8005 down 300 || return $?
  wait_port_status localhost 8009 down 300 || return $?

  # wait 1 minutes to cool down
  sleep 60

  # add product programs to supervisor conf
  ${PROJECT_SERVER_PATH}/etc/addCustomizedSupervisorConf.py ${PRODUCT_NAME} ${PRODUCT_VERSION} ${BRANCH} || return $?

  return 0
}

install_build() {
  local build_path="${1}"
  local silent_response_path="${2}"
  local silent_log_path="${3}"

  "${build_path}" -q -varfile "${silent_response_path}" –Dinstall4j.alternativeLogfile=${silent_log_path} -Dinstall4j.keepLog=true || return $?

  echo "[Done] Install build."
  return 0
}

pre_install_server() {
  # sub setup can override it
  return 0
}

post_install_server() {
  # sub setup can override it
  return 0
}
