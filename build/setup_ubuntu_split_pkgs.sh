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

DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated --fix-broken install

#install python-software-properties and curl
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install python-software-properties
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install curl

# install base packages and fabric utils
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-crypto
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-netaddr
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-paramiko
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install libyaml-0-2
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-yaml

CONTRAIL_FAB=`ls /opt/contrail/contrail_installer_package/contrail-fabric-utils_*.deb`

DEBIAN_FRONTEND=noninteractive dpkg -i --force-overwrite $CONTRAIL_FAB

# install ecdsa and fabric
pip install --upgrade --no-deps --index-url='' /opt/contrail/python_packages/ecdsa-0.10.tar.gz
pip install --upgrade --no-deps --index-url='' /opt/contrail/python_packages/Fabric-1.7.0.tar.gz

#disabled sun-java-jre and sun-java-bin prompt during installation, add oracle license acceptance in debconf
echo 'sun-java6-plugin shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'sun-java6-bin shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'sun-java6-jre shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'debconf shared/accepted-oracle-license-v1-1 select true' | sudo debconf-set-selections
echo 'debconf shared/accepted-oracle-license-v1-1 seen true' | sudo debconf-set-selections

#sudo add-apt-repository -y cloud-archive:havana
#sudo add-apt-repository -y ppa:webupd8team/java
#sudo add-apt-repository -y ppa:nilarimogard/webupd8
#echo "deb http://www.apache.org/dist/cassandra/debian 11x main" |     sudo tee /etc/apt/sources.list.d/cassandra.list
#curl https://www.apache.org/dist/cassandra/KEYS | sudo apt-key add
#apt-get update
