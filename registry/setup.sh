#!/bin/sh

cd `dirname $0`

. ./env
. ./lib

project_name='dws'
docker_compose_file='docker-compose.yml'
update_images "$FRONTEND_IMAGE $REGISTRY_IMAGE"
gen_compose_file $HOST_MOUNT_DIR $CONTAINER_MOUNT_DIR CONTAINER_REGISTRY_DIR $FRONTEND_IMAGE $REGISTRY_IMAGE > $docker_compose_file
up_compose $project_name $docker_compose_file
