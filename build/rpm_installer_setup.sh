#!/bin/bash

# Remove existing python-crypto-2.0.1 rpm.
yum -y --disablerepo=* remove python-crypto-2.0.1

# install if available
yum -y install yum-plugin-priorities

# Install python fabric packages
yum -y install createrepo python-netaddr gcc python python-devel

# Install contrail fabric package
yum -y install contrail-fabric-utils
