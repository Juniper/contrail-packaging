#!/bin/bash

source /etc/contrail/agent_param

dev=$(cat /etc/contrail/agent.conf | \
    python -c 'import sys; from lxml import etree; \
	xdoc = etree.parse(sys.stdin); \
	print xdoc.find("./agent/eth-port/name").text')

vhost=$(cat /etc/contrail/agent.conf | \
    python -c 'import sys; from lxml import etree; \
	xdoc = etree.parse(sys.stdin); \
	print xdoc.find("./agent/vhost/name").text')

mac=$(cat /sys/class/net/$dev/address)

# Set VHOST in cross connect mode
vif --add $dev --mac $mac --vrf 0 --type physical --mode x
vif --add $vhost --mac $mac --vrf 0 --type vhost --mode x --xconnect $dev

if [ $vgw_subnet_ip != __VGW_SUBNET_IP__ ]
then
    vgw_subnet=$vgw_subnet_ip"/"$vgw_subnet_mask
    route delete -net $vgw_subnet dev vgw
    ifconfig vgw down
fi
