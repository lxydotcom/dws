#!/bin/bash

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


### Install delivery system within container
DELIVERY_ROOT_PATH="`get_current_script_location`"

# add entries to cron table. 10 minutes interval
crontab <<EOF
*/10 * * * * ${DELIVERY_ROOT_PATH}/bin/service BUILD ra 552 main > /dev/null 2>&1
*/10 * * * * ${DELIVERY_ROOT_PATH}/bin/service IMAGE ra 552 main > /dev/null 2>&1
EOF

# start cron service foreground 
exec cron -f
