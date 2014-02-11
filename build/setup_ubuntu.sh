#! /bin/bash

# copy files over
mkdir -p /opt/contrail/contrail_install_repo
cd /opt/contrail/contrail_install_repo; tar xvzf /opt/contrail/contrail_packages/contrail_debs.tgz

# create shell scripts and put to bin
mkdir -p /opt/contrail/bin

cd /opt/contrail/contrail_install_repo
DEBIAN_FRONTEND=noninteractive dpkg -i binutils_2.22-6ubuntu1.1_amd64.deb dpkg-dev_1.16.1.2ubuntu7.2_all.deb libdpkg-perl_1.16.1.2ubuntu7.2_all.deb make_3.81-8.1ubuntu1.1_amd64.deb patch_2.6.1-3_amd64.deb python-pip_1.0-1build1_all.deb python-pkg-resources_0.6.24-1ubuntu1_all.deb python-setuptools_0.6.24-1ubuntu1_all.deb

cd /etc/apt/
# create repo with only local packages
datetime_string=`date +%Y_%m_%d__%H_%M_%S`
cp sources.list sources.list.$datetime_string
echo "deb file:/opt/contrail/contrail_install_repo ./" > local_repo
cat local_repo > sources.list

#scan pkgs in local repo and create Packages.gz
cd /opt/contrail/contrail_install_repo
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

#install local repo preferences from /opt/contrail/ to /etc/apt/
cp /opt/contrail/contrail_packages/preferences /etc/apt/preferences 
apt-get update

#install python-software-properties and curl
sudo apt-get -y install python-software-properties curl
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install dpkg-dev=1.16.1.2ubuntu7.2
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install python-pip=1.0-1build1
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install python-pkg-resources=0.6.24-1ubuntu1
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install python-setuptools=0.6.24-1ubuntu1

# install base packages and fabric utils
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install python-crypto
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install python-netaddr
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install python-paramiko
DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install contrail-fabric-utils

# install ecdsa and fabric
pip install --upgrade --no-deps --index-url='' /opt/contrail/contrail_installer/contrail_setup_utils/ecdsa-0.10.tar.gz
pip install --upgrade --no-deps --index-url='' /opt/contrail/contrail_installer/contrail_setup_utils/Fabric-1.7.0.tar.gz

#disabled sun-java-jre and sun-java-bin prompt during installation, add oracle license acceptance in debconf
echo 'sun-java6-plugin shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'sun-java6-bin shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'sun-java6-jre shared/accepted-sun-dlj-v1-1 boolean true' | /usr/bin/debconf-set-selections
echo 'debconf shared/accepted-oracle-license-v1-1 select true' | sudo debconf-set-selections
echo 'debconf shared/accepted-oracle-license-v1-1 seen true' | sudo debconf-set-selections

#additional sources list from stock needed if only contrail specific pkgs are in in local repo
cd /etc/apt/
#install sources.list from /opt/contrail/ to /etc/apt/
cp /opt/contrail/contrail_packages/sources.list /etc/apt/sources.list 
cat local_repo sources.list > new_sources.list
mv new_sources.list sources.list 

sudo add-apt-repository -y cloud-archive:havana
sudo add-apt-repository -y ppa:webupd8team/java
sudo add-apt-repository -y ppa:nilarimogard/webupd8
echo "deb http://www.apache.org/dist/cassandra/debian 11x main" |     sudo tee /etc/apt/sources.list.d/cassandra.list
curl https://www.apache.org/dist/cassandra/KEYS | sudo apt-key add
apt-get update
