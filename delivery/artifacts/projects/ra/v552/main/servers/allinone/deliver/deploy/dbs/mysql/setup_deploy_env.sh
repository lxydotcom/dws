#!/bin/bash

pre_install_server() {
  local mysql_file="${PROJECT_DB_PATH}/etc/mysql-connector-java-5.1.21.jar"

  # check if exists
  [ -e "${mysql_file}" ] || return 1

  # copy it to /tmp
  [ -e "/tmp" ] || mkdir -p /tmp
  cp "${mysql_file}" /tmp/

  return 0
}

post_install_server() {
  # clean tmp file
  local mysql_tmp_file="/tmp/mysql-connector-java-5.1.21.jar"
  [ -e "${mysql_tmp_file}" ] && rm -f "${mysql_tmp_file}"

  return 0
}

