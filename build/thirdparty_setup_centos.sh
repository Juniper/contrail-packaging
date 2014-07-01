#!/bin/bash

# create contrail thirdparty repo
cat << __EOT__ > /etc/yum.repos.d/contrail-thirdparty.repo
[contrail_thirdparty_repo]
name=contrail_thirdparty_repo
baseurl=file:///opt/contrail/contrail_thirdparty_repo/
enabled=1
priority=1
gpgcheck=0
__EOT__

exit 0
