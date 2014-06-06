#!/bin/bash

source /etc/contrail/agent_param

mac=$(cat /sys/class/net/$dev/address)

# Set VHOST in cross connect mode
vif --add $dev --mac $mac --vrf 0 --type physical --mode x
vif --add $DEVICE --mac $mac --vrf 0 --type vhost --mode x --xconnect $dev

if [ $vgw_subnet_ip != __VGW_SUBNET_IP__ ]
then
    vgw_subnet=$vgw_subnet_ip"/"$vgw_subnet_mask
    route delete -net $vgw_subnet dev vgw
    ifconfig vgw down
fi
