#!/bin/bash
# Created by Wazuh, Inc. <info@wazuh.com>.
# Copyright (C) 2019 Wazuh Inc.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2
# This script need packages generation scripts to be on the Solaris machine.

######### GLOBAL VARIABLES #################################################

BUILD_PATH="/export/home/vagrant/build" # cloning in the /tmp/shared folder is too slow
PACKAGE_GENERATION_SCRIPTS_PATH="/tmp/shared/${SOL_PATH}" # this will be changed when we start using Jekins.

OUTPUT="/tmp/shared/${SOLARIS_VERSION}/output"
CHECKSUM="/tmp/shared/${SOLARIS_VERSION}/output"

############################################################################

if [ ! -d "${BUILD_PATH}" ]
then
    echo "Creating building directory at ${BUILD_PATH}"
    mkdir -p ${BUILD_PATH}
fi

echo "Entering build directory"
cd ${BUILD_PATH}

echo "Coping files from shared folder"
cp -r /tmp/shared/${SOLARIS_VERSION} .

cd ${SOLARIS_VERSION}
chmod +x *.sh

echo "Generating Wazuh package"
./generate_wazuh_packages.sh -b ${BRANCH_TAG} -s ${OUTPUT} -c ${CHECKSUM}

exit 0