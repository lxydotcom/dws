#!/bin/sh

########### start up the Docker Work System ############


test -f ./env.sh && . ./env.sh

### Prepare
# stop and remove current docker containers
docker stop `docker ps -aq`
docker rm -f `docker ps -aq`
# again, ensure all cleard
docker rm -f `docker ps -aq`

# build base images from Dockerfile
_dws_image_qname="${DOCKER_REG}/${DOCKER_IMAGE_USER}"
_dws_baseimage_root_path="${DWS_ROOT_PATH}/images/"

docker build -t ${_dws_image_qname}/delivery        ${_dws_baseimage_root_path}/delivery/
docker build -t ${_dws_image_qname}/mysql:5.6       ${_dws_baseimage_root_path}/mysql/5.6/
docker build -t ${_dws_image_qname}/uvd             ${_dws_baseimage_root_path}/uvd/
docker build -t ${_dws_image_qname}/workdb          ${_dws_baseimage_root_path}/workdb/
docker build -t ${_dws_image_qname}/provisioning    ${_dws_baseimage_root_path}/provisioning/

# remove orphaned images
docker rmi -f `docker images | grep "^<none>" | awk '{print $3}'`

# create a container as DWS data center, but not run it
docker create -v ${DWS_ROOT_PATH}:${DWS_ROOT_PATH_IN_CONTAINER} --name dws provisioning /bin/true

# startup containerized private registry and frontend
${DWS_ROOT_PATH}/registry/setup.sh


### Install DWS
# run docker swarm manager container, which is used as docker swarm server. 
# it will organizes nodes as cluster
# todo discovery service
#docker run --rm -d --name swarm_manager -p ${DOCKER_SWARM_PORT}:${DOCKER_SWARM_PORT} swarm manage -H 0.0.0.0:2375 

# run delivery container, which is used as background
# delivery system will manipulate the Docker server on host
docker run -d --volumes-from dws --name delivery \
    -p 10022:22 \
    -e DOCKER_HOST=${DOCKER_SERVER_HOST} \
    -e DELIVERY_ROOT_PATH=${DWS_ROOT_PATH_IN_CONTAINER}/delivery \
    ${_dws_image_qname}/delivery

# run work db container, which is used as database of foreground
docker run -d --volumes-from dws --name workdb \
    -p 13306:3306 \
    -e MYSQL_ROOT_PASSWORD=interOP@123 \
    ${_dws_image_qname}/workdb

# run provisioning container, which is used as foreground to users
# provisioning core will manipulate the Docker swarm server on host
docker run -d --volumes-from dws --name provisioning \
    --link workdb:workdb \
    -p 2222:22 \
    -p 5555:5555 \
    -e DOCKER_HOST=${DOCKER_SWARM_HOST} \
    -e PROVISIONING_ROOT_PATH=${DWS_ROOT_PATH_IN_CONTAINER}/provisioning/ \
    -e PROVISIONING_PROCESSES_COUNT=4 \
    ${_dws_image_qname}/provisioning
