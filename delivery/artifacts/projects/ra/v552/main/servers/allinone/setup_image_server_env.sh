#!/bin/bash

# env specific to this project and server type

export SERVER_BASE_IMAGE="${DOCKER_REG}/lijla02/ubuntu-desktop-lxde-vnc"

export SERVER_INSTALL_HOME="/usr/local/ReleaseAutomationServer"

# all db types, global variable
ALL_DB_TYPES=("mysql")
