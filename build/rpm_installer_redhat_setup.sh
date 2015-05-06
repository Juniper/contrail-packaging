#!/bin/bash

# Remove existing python-crypto-2.0.1 rpm.
yum -y --disablerepo=* remove python-crypto-2.0.1

# Install python fabric packages 
yum -y install python-pip createrepo python-netaddr gcc python python-devel

pip install /opt/contrail/python-packages/pycrypto-*.tar.gz
pip install /opt/contrail/python-packages/paramiko-*.tar.gz
pip install /opt/contrail/python-packages/Fabric-*.tar.gz

# Install contrail fabric package
yum -y --disablerepo=* --enablerepo=contrail* install contrail-fabric-utils
