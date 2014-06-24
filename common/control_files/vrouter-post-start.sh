#!/bin/bash

dev=$(cat /etc/contrail/agent.conf | \
    python -c 'import sys; from lxml import etree; \
	xdoc = etree.parse(sys.stdin); \
	print xdoc.find("./agent/eth-port/name").text')
ip link set dev $dev up

# apport updates the core pattern; overwrite here to use /var/crashes pattern
echo "/var/crashes/core.%e.%p.%h.%t" > /proc/sys/kernel/core_pattern
