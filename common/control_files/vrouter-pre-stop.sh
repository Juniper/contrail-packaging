#!/bin/bash

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
vif --add $vhost --mac $mac --vrf 0 --type vhost --mode x
vif --add $dev --mac $mac --vrf 0 --type physical --mode x

