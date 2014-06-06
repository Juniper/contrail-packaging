#! /bin/bash

source /etc/contrail/agent_param
source $VHOST_CFG

# rmmod $kmod &>> $LOG
DEV_MAC=$(cat /sys/class/net/$dev/address)
# Set VHOST in cross connect mode
vif --add $dev --mac $DEV_MAC --vrf 0 --type physical --mode x
vif --add $DEVICE --mac $DEV_MAC --vrf 0 --type vhost --xconnect $dev --mode x
