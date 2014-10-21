#!/bin/bash

#Install basic packages
yum -y --disablerepo=* --enablerepo=server_manager_repo install contrail-server-manager contrail-server-manager-monitor
