#!/usr/bin/env bash

CONFIG_FILE="/etc/contrail/dns.conf"
SIGNATURE="Dns configuration options, generated from dns_param"

if [ ! -e /etc/contrail/dns_param ]; then
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

source /etc/contrail/dns_param

(
cat << EOF
#
# Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
#
# $SIGNATURE
#

[DEFAULTS]
dns-config-file=dns_config.xml
hostip=$HOSTIP # Resolved IP of `hostname`
http-server-port=8092

[COLLECTOR]
port=8086
server= # Provided by discovery server

[DISCOVERY]
port=5998
server=$DISCOVERY # discovery-server IP address

[IFMAP]
password=$IFMAP_PASWD
server-url=https://$IFMAP_SERVER:$IFMAP_PORT
user=$IFMAP_USER
certs-store=$CERT_OPTS

[LOG]
category=
disable=0
file=/var/log/contrail/dns.log
level=SYS_NOTICE
local=0

EOF
) > $CONFIG_FILE
