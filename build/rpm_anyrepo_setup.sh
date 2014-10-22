#!/bin/bash

# Remove existing python-crypto-2.0.1 rpm.
yum -y --disablerepo=* remove python-crypto-2.0.1

#Install basic packages
yum -y install contrail-setup contrail-fabric-utils python-pip
pip-python install /opt/contrail/python_packages/pycrypto-2.6.tar.gz
pip-python install /opt/contrail/python_packages/paramiko-1.11.0.tar.gz
pip-python install /opt/contrail/python_packages/Fabric-1.7.0.tar.gz
