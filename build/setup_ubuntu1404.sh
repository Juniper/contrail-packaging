#! /bin/bash

# backup old directories in case of upgrade
if [ -d /opt/contrail/contrail_install_repo ]; then
    mkdir -p /opt/contrail/contrail_install_repo_backup
    mv /opt/contrail/contrail_install_repo/* /opt/contrail/contrail_install_repo_backup/
fi

# copy files over
mkdir -p /opt/contrail/contrail_install_repo
cd /opt/contrail/contrail_install_repo; tar xvzf /opt/contrail/contrail_packages/contrail_debs.tgz

# create shell scripts and put to bin
mkdir -p /opt/contrail/bin

cd /opt/contrail/contrail_install_repo
DEBIAN_FRONTEND=noninteractive dpkg -i binutils_2.24-5ubuntu3_amd64.deb make_3.81-8.2ubuntu3_amd64.deb \
                                       libdpkg-perl_1.17.5ubuntu5.3_all.deb patch_2.7.1-4ubuntu1_amd64.deb \
                                       dpkg-dev_1.17.5ubuntu5.3_all.deb

#modify /etc/apt/soruces.list/ to add local repo on the top
grep "deb file:/opt/contrail/contrail_install_repo ./" /etc/apt/sources.list
if [ $? != 0 ]; then
    datetime_string=`date +%Y_%m_%d__%H_%M_%S`
    cp /etc/apt/sources.list /etc/apt/sources.list.$datetime_string
    echo >> /etc/apt/sources.list
    sed -i '1 i\deb file:/opt/contrail/contrail_install_repo ./' /etc/apt/sources.list
fi

# Allow unauthenticated pacakges to get installed.
# Do not over-write apt.conf. Instead just append what is necessary
# retaining other useful configurations such as http::proxy info.
apt_auth="APT::Get::AllowUnauthenticated \"true\";"
grep --quiet "$apt_auth" /etc/apt/apt.conf
if [ "$?" != "0" ]; then
    echo "$apt_auth" >> /etc/apt/apt.conf
fi

#install local repo preferences from /opt/contrail/ to /etc/apt/
cp /opt/contrail/contrail_packages/preferences /etc/apt/preferences

#scan pkgs in local repo and create Packages.gz
cd /opt/contrail/contrail_install_repo
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
apt-get update

#install python-software-properties and curl
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install python-software-properties
DEBIAN_FRONTEND=noninteractive sudo apt-get -y --force-yes --allow-unauthenticated install curl

# install base packages and fabric utils
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-pip
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-crypto
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-netaddr
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install python-paramiko
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install contrail-fabric-utils
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install contrail-setup

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
