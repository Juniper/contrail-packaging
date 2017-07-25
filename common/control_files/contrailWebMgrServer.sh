#!/bin/bash

cd /usr/src/contrail/contrail-web-core;
node webServerStart.js --conf_file /etc/contrail/config.global.sm.js
