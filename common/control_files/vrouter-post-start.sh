#!/bin/bash

source /etc/contrail/agent_param
ip link set dev $dev up

# apport updates the core pattern; overwrite here to use /var/crashes pattern
echo "/var/crashes/core.%e.%p.%h.%t" > /proc/sys/kernel/core_pattern
