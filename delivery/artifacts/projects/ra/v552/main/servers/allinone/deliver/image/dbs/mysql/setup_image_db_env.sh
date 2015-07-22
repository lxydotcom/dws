#!/bin/bash

# env specific to this project, server type and db type

export DB_BASE_IMAGE="${DOCKER_REG}/lijla02/mysql"
export DB_BASE_IMAGE_TAG="5.6"

export DB_PORT=3306
export DB_USER="root"
export DB_PASSWORD="interOP@123"
export DB_DATABASE="nolio_db"

export DB_RUNNING_ENV="MYSQL_ROOT_PASSWORD=${DB_PASSWORD}"


# db functions, override the empty functions

# $1, db container name
func_post_start_db() {
  local db_container=${1}

  local count=300
  local i=1
  while [ ${i} -le ${count} ]; do
      # invoke internal function of checking db ready
      _is_db_ready ${db_container}
      [ $? -eq 0 ] && break
      i=`expr $i + 1`
      echo "Waiting DB up ..."
      sleep 1
  done
  [ ${i} -le ${count} ] && echo "DB is up." || (echo "DB is not up." && return 1)
}

# $1, db container name
_is_db_ready() {
  local db_container=${1}

  local random="79763241AdamLee238703489"
  local ready=`docker exec ${db_container} mysql --user=${DB_USER} --password=${DB_PASSWORD} -e "select '${random}' as random from dual" 2> /dev/null`

  echo ${ready} | grep -q "${random}"
  return $?
}

# $1, db container name
func_pre_stop_db() {
    local db_container=${1}

    docker exec ${db_container} mysql --user=${DB_USER} --password=${DB_PASSWORD} -e "update exec_servers set hostname='127.0.0.1', broker_connection_name=concat('Broker : 127.0.0.1:', broker_port); select hostname, broker_connection_name from exec_servers" ${DB_DATABASE} 2> /dev/null
    [ $? -eq 0 ] && echo "DB is patched with 1 patch"
    docker exec ${db_container} mysql --user=${DB_USER} --password=${DB_PASSWORD} -e "update nac_nodes set ip='127.0.0.1'; select ip from nac_nodes" ${DB_DATABASE} 2> /dev/null
    [ $? -eq 0 ] && echo "DB is patched with 2 patches"
}
