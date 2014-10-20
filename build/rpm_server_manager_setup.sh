#!/bin/bash

# create contrail installer repo
cat << __EOT__ > /etc/yum.repos.d/server-manager-depends.repo
[server_manager_repo]
name=server_manager_repo
baseurl=file:///opt/contrail/server_manager_repo/
enabled=1
priority=1
gpgcheck=0
__EOT__

#Install basic packages
yum -y --disablerepo=* --enablerepo=server_manager_repo install contrail-server-manager contrail-server-manager-monitor
