#!/bin/bash

# create contrail installer repo
cat << __EOT__ > /etc/yum.repos.d/contrail-install.repo
[contrail_install_repo]
name=contrail_install_repo
baseurl=file:///opt/contrail/contrail_install_repo/
enabled=1
priority=1
gpgcheck=0
__EOT__

# copy files over
mkdir -p /opt/contrail/contrail_install_repo
mkdir -p /opt/contrail/bin

cd /opt/contrail/contrail_install_repo; tar xvzf /opt/contrail/contrail_packages/contrail_rpms.tgz

# create shell scripts and put to bin
cp /opt/contrail/contrail_packages/helpers/* /opt/contrail/bin/

# Remove existing python-crypto-2.0.1 rpm.
yum -y --disablerepo=* remove python-crypto-2.0.1

#Install basic packages
yum -y install contrail-setup contrail-fabric-utils python-pip
pip install /opt/contrail/python_packages/pycrypto-2.6.tar.gz
pip install /opt/contrail/python_packages/paramiko-1.11.0.tar.gz
pip install /opt/contrail/python_packages/Fabric-1.7.0.tar.gz
