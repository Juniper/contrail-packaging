#!/bin/bash

# create contrail installer repo
#cat << __EOT__ > /etc/yum.repos.d/contrail-install.repo
#[contrail_install_repo]
#name=contrail_install_repo
#baseurl=file:///opt/contrail/contrail_install_repo/
#enabled=1
#priority=1
#gpgcheck=0
#__EOT__
#
# copy files over
mkdir -p /opt/contrail/contrail_install_repo
mkdir -p /opt/contrail/bin
#mkdir -p /opt/contrail/contrail_install_repo/more_pkgs

cd /opt/contrail/contrail_install_repo; tar xvzf /opt/contrail/contrail_packages/contrail_packages.tgz 

# create shell scripts and put to bin
cp /opt/contrail/contrail_packages/helpers/* /opt/contrail/bin/

#Install basic packages 
cd /opt/contrail/contrail_install_repo
#DEBIAN_FRONTEND=noninteractive dpkg -i *.deb 
DEBIAN_FRONTEND=noninteractive dpkg -i binutils_2.22-6ubuntu1.1_amd64.deb dpkg-dev_1.16.1.2ubuntu7.2_all.deb libdpkg-perl_1.16.1.2ubuntu7.2_all.deb make_3.81-8.1ubuntu1.1_amd64.deb patch_2.6.1-3_amd64.deb python-netifaces_0.6-2ubuntu1_amd64.deb python-pip_1.0-1build1_all.deb python-pkg-resources_0.6.24-1ubuntu1_all.deb python-setuptools_0.6.24-1ubuntu1_all.deb libexpat1_2.1.0-4_amd64.deb

#Install packages from contrail_packages.tgz
cd /opt/contrail/contrail_install_repo
DEBIAN_FRONTEND=noninteractive dpkg -i *.deb 

#Install packages in noniteractive mode, some may need reinstallation due to sequence dependancies (TBD) 
dpkg -i gawk_1%3a3.1.8+dfsg-0.1ubuntu1_amd64.deb 
DEBIAN_FRONTEND=noninteractive dpkg -i mysql-server-5.5_5.5.34-0ubuntu0.12.04.1_amd64.deb
DEBIAN_FRONTEND=noninteractive dpkg -i mysql-server_5.5.34-0ubuntu0.12.04.1_all.deb
DEBIAN_FRONTEND=noninteractive dpkg -i nova-compute-kvm_*.deb nova-compute_*.deb


#Install basic packages 
#pip install /opt/contrail/contrail_installer/contrail_setup_utils/pycrypto-2.6.tar.gz
#pip install /opt/contrail/contrail_installer/contrail_setup_utils/paramiko-1.11.0.tar.gz
pip install /opt/contrail/contrail_installer/contrail_setup_utils/Fabric-1.7.0.tar.gz

#cassandra would start on its own as a part of installation. 
# need to stop cassandra service and clean /var/lib/cassandra, to bring it up through contrail-database
sudo service cassandra stop
sudo rm -rf /var/lib/cassandra/
touch /var/log/keystone/keystone.log
sudo chown keystone /var/log/keystone/keystone.log
sudo chgrp keystone /var/log/keystone/keystone.log
