#!/bin/bash

# create shell scripts and put to bin
mkdir -p /opt/contrail/bin

cd /opt/contrail/contrail_installer_package
DEBIAN_FRONTEND=noninteractive dpkg -i binutils_2.22-6ubuntu1.1_amd64.deb dpkg-dev_1.16.1.2ubuntu7.2_all.deb libdpkg-perl_1.16.1.2ubuntu7.2_all.deb make_3.81-8.1ubuntu1.1_amd64.deb patch_2.6.1-3_amd64.deb python-pip_1.0-1build1_all.deb python-pkg-resources_0.6.24-1ubuntu1_all.deb python-setuptools_0.6.24-1ubuntu1_all.deb libyaml-0-2_0.1.4-2ubuntu0.12.04.3_amd64.deb python-yaml_3.10-2_amd64.deb contrail-fabric-utils_3.0-1232_all.deb

cd /etc/apt/
# Allow unauthenticated pacakges to get installed.
# Do not over-write apt.conf. Instead just append what is necessary
# retaining other useful configurations such as http::proxy info.
apt_auth="APT::Get::AllowUnauthenticated \"true\";"
grep --quiet "$apt_auth" apt.conf
if [ "$?" != "0" ]; then
    echo "$apt_auth" >> apt.conf
fi

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
