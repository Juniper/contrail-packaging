#! /bin/bash

cd /opt/contrail/contrail_installer_repo
DEBIAN_FRONTEND=noninteractive dpkg -i binutils_*.deb dpkg-dev_*.deb libdpkg-perl_*.deb make_*.deb patch_*.deb

#modify /etc/apt/soruces.list/ to add local repo on the top
grep "^deb file:/opt/contrail/contrail_installer_repo ./" /etc/apt/sources.list
if [ $? != 0 ]; then
    datetime_string=$(date +%Y_%m_%d__%H_%M_%S)
    cp /etc/apt/sources.list /etc/apt/sources.list.$datetime_string.contrailbackup
    echo >> /etc/apt/sources.list
    sed -i '1 i\deb file:/opt/contrail/contrail_installer_repo ./' /etc/apt/sources.list
fi

# Allow unauthenticated pacakges to get installed.
apt_auth="APT::Get::AllowUnauthenticated \"true\";"
grep --quiet "^$apt_auth" /etc/apt/apt.conf
if [ $? != 0 ]; then
    echo "$apt_auth" >> /etc/apt/apt.conf
fi

#install local repo preferences from /opt/contrail/ to /etc/apt/
cp /opt/contrail/contrail_installer_packages/preferences /etc/apt/preferences 

#scan pkgs in local repo and create Packages.gz
cd /opt/contrail/contrail_installer_repo
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
apt-get update

#install python-software-properties and curl
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install python-pip
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install python-software-properties
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install curl

# install base packages and fabric utils
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-crypto
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-netaddr
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-paramiko
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install contrail-fabric-utils

# install ecdsa and fabric
pip install --upgrade --no-deps --index-url='' /opt/contrail/python-packages/Fabric-*.tar.gz

#disabled sun-java-jre and sun-java-bin prompt during installation, add oracle license acceptance in debconf
echo 'sun-java6-plugin shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'sun-java6-bin shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'sun-java6-jre shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'debconf shared/accepted-oracle-license-v1-1 select true' | sudo debconf-set-selections
echo 'debconf shared/accepted-oracle-license-v1-1 seen true' | sudo debconf-set-selections

