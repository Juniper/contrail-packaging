#!/bin/bash

# create shell scripts and put to bin
mkdir -p /opt/contrail/bin

cd /opt/contrail/contrail_install_packages
CONTRAIL_DEP_PKG=`ls contrail-dependent-packages_*.deb`
CONTRAIL_THIRDPARTY_PKG=`ls contrail-thirdparty-packages_*.deb`
CONTRAIL_OS_PKG=`ls contrail-openstack-packages_*.deb`
CONTRAIL_PKG=`ls contrail-packages_*.deb`

DEBIAN_FRONTEND=noninteractive dpkg -i --force-overwrite $CONTRAIL_DEP_PKG $CONTRAIL_THIRDPARTY_PKG $CONTRAIL_OS_PKG $CONTRAIL_PKG

cd /opt/contrail/contrail_install_repo
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

cd /opt/contrail/contrail_dependents_repo
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

apt-get update

#install python-software-properties and curl
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install python-software-properties
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install curl

# install base packages and fabric utils
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-crypto
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-netaddr
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-paramiko
