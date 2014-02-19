#!/usr/bin/env bash

CONFIG_FILE="/etc/contrail/qe.conf"
SIGNATURE="Query Engine configuration options, generated from qe_param"

if [ ! -e /etc/contrail/qe_param ]; then
    exit
fi

# Ignore if the converted file is already generated once before
if [ -e $CONFIG_FILE ]; then
    grep --quiet "$SIGNATURE" $CONFIG_FILE > /dev/null

    # Exit if configuraiton already converted!
    if [ $? == 0 ]; then
        exit
    fi
fi

source /etc/contrail/qe_param

(
cat << EOF
#
# Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
#
# $SIGNATURE
#

[DEFAULTS]
analytics-data-ttl=0
cassandra-server=$CASSANDRA_SERVER_LIST
collector-server= # Provided by discovery server
http-server-port=8091
max-slice=100
max-tasks=16
start-time=0

[DISCOVERY]
port=5998
server=127.0.0.1 # discovery-server IP address

[LOG]
category=
file=/var/log/contrail/qe.log
level=SYS_DEBUG
local=1

[REDIS]
ip=$REDIS_SERVER
port=$REDIS_SERVER_PORT

EOF
) > $CONFIG_FILE
