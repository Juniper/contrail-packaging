#!/bin/bash

cd /usr/src/contrail/contrail-webui;
if command -v nodejs-contrail > /dev/null; then
  node_exec=nodejs-contrail;
else
  echo "error: Failed dependencies: nodejs-contrail is needed";
  exit;
fi;
$node_exec jobServerStart.js 0.0.0.0

