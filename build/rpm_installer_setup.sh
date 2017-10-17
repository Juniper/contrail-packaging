#!/bin/bash

# Remove existing python-crypto-2.0.1 rpm.
yum -y --disablerepo=* remove python-crypto-2.0.1

# install if available
yum -y install yum-plugin-priorities

# Priority Override for obsolete packages
priorities_conf="/etc/yum/pluginconf.d/priorities.conf"
[ -f $priorities_conf ] && \
grep -qi "\[main\]" $priorities_conf && \
! grep -q "check_obsoletes\s*=\s*1" $priorities_conf && \
sed -i 's/\[main\]$/&\ncheck_obsoletes = 1/' $priorities_conf && \
echo "PASS: Added Priority Override for Obsolete packages" || ( \
grep -q "check_obsoletes\s*=\s*1" $priorities_conf && \
echo "PASS: Priority Override for Obsolete packages already exists. Nothing to do" ) || ( \
[ ! -f $priorities_conf ] && echo "WARNING: $priorities_conf not found" ) || ( \
echo "WARNING: Couldnt add priority Override for Obsolete packages. Check..." && \
cat $priorities_conf )

# Install python fabric packages 
yum -y --disablerepo=* --enablerepo=contrail* install python-pip createrepo python-netaddr gcc python python-devel

pip install /opt/contrail/python-packages/pycrypto-*.tar.gz
pip install /opt/contrail/python-packages/paramiko-*.tar.gz
pip install /opt/contrail/python-packages/Fabric-*.tar.gz

# Install contrail fabric package
yum -y --disablerepo=* --enablerepo=contrail* install contrail-fabric-utils
