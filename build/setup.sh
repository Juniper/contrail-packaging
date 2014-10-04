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

# Remove contrail-fabric-utils
# Workaround to fix bug(https://bugs.launchpad.net/juniperopenstack/+bug/1361452)
yum -y --disablerepo=* remove contrail-fabric-utils

#Install basic packages 
mv /opt/contrail/contrail_packages/setup.sh /opt/contrail/contrail_packages/setup.sh.backup
yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-setup contrail-fabric-utils python-pip
mv /opt/contrail/contrail_packages/setup.sh.backup /opt/contrail/contrail_packages/setup.sh
pip-python install /opt/contrail/contrail_installer/contrail_setup_utils/pycrypto-2.6.tar.gz
pip-python install /opt/contrail/contrail_installer/contrail_setup_utils/paramiko-1.11.0.tar.gz
pip-python install /opt/contrail/contrail_installer/contrail_setup_utils/Fabric-1.7.0.tar.gz
