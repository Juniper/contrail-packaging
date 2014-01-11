#!/bin/bash

dev=$(cat /etc/contrail/agent.conf | \
    python -c 'import sys; from lxml import etree; \
	xdoc = etree.parse(sys.stdin); \
	print xdoc.find("./agent/eth-port/name").text')
ip link set dev $dev up
