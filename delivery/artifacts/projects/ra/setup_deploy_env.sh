#!/bin/bash

start_service() {
  s_cmd="${1}"

  "${s_cmd}" status | grep -i 'running' > /dev/null || "${s_cmd}" start
  [ $? -eq 0 ] || return 1

  echo "[Done] Start service ${s_cmd}."
  return 0
}

stop_service() {
  s_cmd="${1}"

  "${s_cmd}" status | grep -i 'running' > /dev/null && "${s_cmd}" stop
  [ $? -eq 0 ] || return 1

  echo "[Done] Stop service ${s_cmd}."
  return 0
}

wait_port_status() {
  i=1
  while [ $i -le $4 ]; do
    case $3 in
      UP|up)
        nc -z $1 $2 && break
        i=`expr $i + 1`
        ;;
      DOWN|down)
        nc -z $1 $2 || break
        i=`expr $i + 1`
        ;;
      *)
        echo "Invalid status provided, try [up|UP|down|DOWN]."
        return 1
    esac
    echo "Waiting $1:$2 $3 ..."
    sleep 1
  done
  [ $i -le $4 ] && echo "Port $1:$2 is $3." || (echo "Port $1:$2 is not $3." && return 1)
  return 0
}
