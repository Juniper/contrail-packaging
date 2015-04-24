#!/bin/bash

# Remove existing python-crypto-2.0.1 rpm.
yum -y --disablerepo=* remove python-crypto-2.0.1

# Install python fabric packages 
yum -y --disablerepo=* --enablerepo=contrail* install python-pip createrepo python-netaddr gcc python python-devel

pip install /opt/contrail/python-packages/pycrypto-2.6.tar.gz
pip install /opt/contrail/python-packages/paramiko-1.11.0.tar.gz
pip install /opt/contrail/python-packages/Fabric-1.7.0.tar.gz

# Install contrail fabric package
yum -y --disablerepo=* --enablerepo=contrail* install contrail-fabric-utils
