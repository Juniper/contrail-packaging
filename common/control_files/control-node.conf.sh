#!/usr/bin/env bash

CONFIG_FILE="/etc/contrail/control-node.conf"
SIGNATURE="Control-node configuration options, generated from control_param"

if [ ! -e /etc/contrail/control_param ]; then
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

source /etc/contrail/control_param

(
cat << EOF
#
# Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
#
# $SIGNATURE
#

[DEFAULTS]
hostip=$HOSTIP # Resolved IP of `hostname`
hostname=$HOSTNAME # Retrieved as `hostname`
http-server-port=8083
xmpp-server-port=5269

[BGP]
config-file=bgp_config.xml
port=$BGP_PORT

[COLLECTOR]
port=8086
server= # Provided by discovery server

[DISCOVERY]
port=5998
server=$DISCOVERY # discovery-server IP address

[IFMAP]
certs-store=$CERT_OPTS
password=$IFMAP_PASWD
server-url=https://$IFMAP_SERVER:$IFMAP_PORT
user=$IFMAP_USER

[LOG]
category=
disable=0
file=/var/log/contrail/control-node.log
level=SYS_NOTICE
local=0

EOF
) > $CONFIG_FILE
