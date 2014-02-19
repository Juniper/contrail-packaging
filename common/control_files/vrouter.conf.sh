#!/usr/bin/env bash

CONFIG_FILE="/etc/contrail/vrouter.conf"
SIGNATURE="Vrouter configuration options, generated from agent_param"

if [ ! -e /etc/contrail/agent_param ]; then
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

source /etc/contrail/agent_param

# if [ -e /etc/contrail/agent.conf ]; then
#
#     # Convert /etc/contrail/agent.conf xml file to param file and source it.
#     python /etc/contrail/vrouter_xml_to_param.py > /etc/contrail/vrouter_param
#     source /etc/contrail/vrouter_param
# fi

(
cat << EOF
#
# Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
#
# $SIGNATURE
#

[DEFAULTS]
hostname= # Retrieved as `hostname`
http-server-port=8085
config-file=/etc/contrail/agent.conf

[COLLECTOR]
port=8086
server= # Provided by discovery server

[HYPERVISOR]
type=kvm
xen-ll-ip-address=
xen-ll-prefix-len=0
xen-ll-port=
vmware-physical-port=

[LOG]
category=
file=/var/log/contrail/vrouter.log
level=SYS_DEBUG
local=0

[KERNEL]
disable-vhost=0
disable-ksync=0
disable-services=0
disable-packet=0

EOF
) > $CONFIG_FILE
