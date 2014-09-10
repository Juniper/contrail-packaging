#!/bin/bash

set -e

yum -y install libselinux-python-2.0.94-5.3.el6_4.1.x86_64
yum -y install polkit-0.96-5.el6_4.x86_64
yum -y install polkit-devel-0.96-5.el6_4.x86_64
yum -y install docbook-style-dsssl-1.79-10.el6.noarch
yum -y install docbook-style-xsl-1.75.2-6.el6.noarch
yum -y install docbook-utils-0.6.14-25.el6.noarch
yum -y install gc-7.1-10.el6.x86_64
yum -y install glib2-devel-2.26.1-3.el6.x86_64
yum -y install gtk-doc-1.11-5.1.el6.noarch
yum -y install openjade-1.3.2-36.el6.x86_64
yum -y install opensp-1.5.2-12.1.el6.x86_64
yum -y install perl-SGMLSpm-1.03ii-21.el6.noarch
yum -y install polkit-docs-0.96-5.el6_4.x86_64
yum -y install w3m-0.5.2-16.el6.x86_64
yum -y install polkit-desktop-policy-0.96-5.el6_4.noarch
yum -y install polkit-gnome-0.96-3.el6.x86_64
yum -y install wget-1.12-1.8.el6.x86_64
yum -y install openssh-clients-5.3p1-94.el6.x86_64
yum -y install ntpdate-4.2.6p5-1.el6.centos.x86_64
yum -y install ntp-4.2.6p5-1.el6.centos.x86_64
yum -y install vim-common-7.2.411-1.8.el6.x86_64
yum -y install vim-enhanced-7.2.411-1.8.el6.x86_64
yum -y install vim-minimal-7.2.411-1.8.el6.x86_64
yum -y install nfs-utils-1.2.3-39.el6_5.3.x86_64
yum -y install screen-4.0.3-16.el6.x86_64
yum -y install ypbind-1.20.4-30.el6.x86_64
yum -y install autofs-5.0.5-89.el6_5.2.x86_64
yum -y install gedit-2.28.4-3.el6.x86_64
yum -y install gedit-plugins-2.28.0-2.el6.x86_64
yum -y install quota-3.17-20.el6.x86_64
yum -y install traceroute-2.0.14-2.el6.x86_64
yum -y install tree-1.5.3-2.el6.x86_64
yum -y install strace-4.5.19-1.17.el6.x86_64
yum -y install tcsh-6.17-24.el6.x86_64
yum -y install zsh-4.3.10-7.el6.x86_64
yum -y install ant-1.7.1-13.el6.x86_64
# yum -y install autoconf-2.68-2.fc15.noarch (No package autoconf-2.68-2.fc15.noarch available.)
# yum -y install scons-2.2.0-1.noarch (No package scons-2.2.0-1.noarch available.)
yum -y install bison-2.4.1-5.el6.x86_64
yum -y install flex-2.5.35-8.el6.x86_64
yum -y install gcc-c++-4.4.7-4.el6.x86_64
yum -y install gdb-7.2-60.el6_4.1.x86_64
yum -y install openssl-devel-1.0.1e-15.el6.x86_64
yum -y install rpm-build-4.8.0-37.el6.x86_64
yum -y install python-devel-2.6.6-51.el6.x86_64
# yum -y install git-1.7.3.4-1.el6.rfx.x86_64 (No package git-1.7.3.4-1.el6.rfx.x86_64 available.)
yum -y install cppunit-devel-1.12.1-3.1.el6.x86_64
# yum -y install devtoolset-1.1-gcc-c++-4.7.2-5.el6.x86_64 (No package devtoolset-1.1-gcc-c++-4.7.2-5.el6.x86_64 available.)
# yum -y install openstack-utils-2013.1-8.el6ost.noarch (No package openstack-utils-2013.1-8.el6ost.noarch available.)
# yum -y install python-argparse-1.2.1-2.1.el6.noarch (No package python-argparse-1.2.1-2.1.el6.noarch available.)
# yum -y install nodejs-0.10.9-1.el6.x86_64 (No package nodejs-0.10.9-1.el6.x86_64 available.)
yum -y install libnl-devel-1.1.4-2.el6.x86_64
# yum -y install augeas-0.9.0-4.el6.x86_64 (No package augeas-0.9.0-4.el6.x86_64 available.)
yum -y install libpciaccess-devel-0.13.1-2.el6.x86_64
yum -y install yajl-devel-1.0.7-3.el6.x86_64
# yum -y install sanlock-devel-2.6-2.el6.x86_64 (No package sanlock-devel-2.6-2.el6.x86_64 available.)
# yum -y install libpcap-devel-1.0.0-6.20091201git117cb5.el6.x86_64 (No package libpcap-devel-1.0.0-6.20091201git117cb5.el6.x86_64 available.)
# yum -y install parted-devel-2.1-19.el6.x86_64 (No package parted-devel-2.1-19.el6.x86_64 available.)
yum -y install numactl-devel-2.0.7-8.el6.x86_64
yum -y install libcap-ng-devel-0.6.4-3.el6_0.1.x86_64
yum -y install audit-libs-devel-2.2-2.el6.x86_64
yum -y install systemtap-2.3-3.el6.x86_64
yum -y install systemtap-sdt-devel-2.3-3.el6.x86_64
# yum -y --skip-broken install gnutls-devel-2.8.5-10.el6_4.2.x86_64 (Error:  Multilib version problems found.)
yum -y install python-lxml-2.2.3-1.1.el6.x86_64
yum -y install python-setuptools-0.6.10-3.el6.noarch
yum -y install libxslt-devel-1.1.26-2.el6_3.1.x86_64
# yum -y install python-virtualenv-1.10.1-1.el6.noarch (No package python-virtualenv-1.10.1-1.el6.noarch available.)
yum -y install python-netaddr-0.7.5-4.el6.noarch
yum -y install graphviz-2.26.0-10.el6.x86_64
yum -y install python-routes-1.10.3-2.el6.noarch
# yum -y install python-migrate-0.7.2-0.noarch (No package python-migrate-0.7.2-0.noarch available.)
# yum -y install python-iso8601-0.1.4-2.el6.noarch (No package python-iso8601-0.1.4-2.el6.noarch available.)
yum -y install ruby-1.8.7.352-12.el6_4.x86_64
yum -y install readline-devel-6.0-4.el6.x86_64
yum -y install libtasn1-devel-2.3-3.el6_2.1.x86_64
yum -y install dnsmasq-2.48-13.el6.x86_64
yum -y install radvd-1.6-1.el6.x86_64
yum -y install ebtables-2.0.9-6.el6.x86_64
yum -y install cyrus-sasl-devel-2.1.23-13.el6_3.1.x86_64
yum -y install qemu-img-0.12.1.2-2.415.el6_5.6.x86_64
yum -y install libcurl-devel-7.19.7-37.el6_4.x86_64
yum -y install scrub-2.2-1.el6.x86_64
yum -y install numad-0.5-9.20130814git.el6.x86_64
yum -y install createrepo-0.9.9-18.el6.noarch
# yum -y install python-boto-2.5.2-1.1.el6.noarch (No package python-boto-2.5.2-1.1.el6.noarch available.)
# yum -y install python-eventlet-0.9.17-2.el6.noarch (No package python-eventlet-0.9.17-2.el6.noarch available.)
yum -y install python-nose-0.10.4-3.1.el6.noarch
yum -y install python-webtest-1.2-2.el6.noarch 
# yum -y install libblkid-devel-2.17.2-12.14.el6.x86_64 (Error:  Multilib version problems found.)
# yum -y install pungi-2.0.22-1.el6.R.noarch (No package pungi-2.0.22-1.el6.R.noarch available.)
# yum -y install python-sphinx-1.0.8-1.el6.noarch (No package python-sphinx-1.0.8-1.el6.noarch available.)
# yum -y install avahi-devel-0.6.25-12.el6.x86_64 (Error:  Multilib version problems found.)
# yum -y install netcf-devel-0.1.9-3.el6.x86_64 (No package netcf-devel-0.1.9-3.el6.x86_64 available.)
yum -y install xhtml1-dtds-1.0-20020801.7.noarch
# yum -y install python-pip-1.3.1-1.el6.noarch (No package python-pip-1.3.1-1.el6.noarch available.)
#pip install PyGitHub==1.12.1
#pip install fabric==1.8.0
#pip install pep8==1.4.6
#pip install autopep8==0.9.7
#pip install paramiko==1.12.0
#pip install PIL==1.1.7

yum -y install libudev-devel-147-2.51.el6.x86_64
yum -y install device-mapper-devel-1.02.79-8.el6.x86_64
yum -y install libevent-devel-1.4.13-4.el6.x86_64
yum -y install ant-nodeps-1.7.1-13.el6.x86_64
yum -y install kernel-devel-2.6.32-431.el6.x86_64
yum -y install kernel-headers-2.6.32-431.el6.x86_64
# yum -y install lcov-1.10-1.noarch (No package lcov-1.10-1.noarch available.)
# yum -y install redis-2.6.13-3.el6.art.x86_64 (No package redis-2.6.13-3.el6.art.x86_64 available.)
yum -y install sqlite-devel-3.6.20-1.el6.x86_64
# yum -y install log4cplus-1.1.1-1.el6.x86_64 (No package log4cplus-1.1.1-1.el6.x86_64 available.)
# yum -y install python-d2to1-0.2.10-1.el6.noarch (No package python-d2to1-0.2.10-1.el6.noarch available.)
# yum -y install python-pbr-0.5.21-2.el6.noarch (No package python-pbr-0.5.21-2.el6.noarch available.)
yum -y install java-1.6.0-openjdk-devel-1.6.0.0-1.66.1.13.0.el6.x86_64
yum -y install java-1.7.0-openjdk-devel-1.7.0.45-2.4.3.3.el6.x86_64
yum -y install intltool-0.41.0-1.1.el6.noarch
yum -y install libtool-2.2.6-15.5.el6.x86_64
yum -y install redhat-rpm-config-9.0.3-42.el6.centos.noarch
yum -y install qemu-kvm-0.12.1.2-2.415.el6_5.6.x86_64
yum -y install libvirt-0.10.2-29.el6_5.5.x86_64
# yum -y install python-oslo-sphinx-1.1-1.el6.noarch (No package python-oslo-sphinx-1.1-1.el6.noarch available.)
# yum -y install git-review-1.17-2.el6.noarch (No package git-review-1.17-2.el6.noarch available.)
yum -y install libselinux-python-2.0.94-5.3.el6_4.1.x86_64
# yum -y install devtoolset-1.1-gcc-4.7.2-5.el6.x86_64 (No package devtoolset-1.1-gcc-4.7.2-5.el6.x86_64 available.)
# yum -y install sshpass-1.05-1.el6.x86_64 (No package sshpass-1.05-1.el6.x86_64 available.)
yum -y install rpcbind-0.2.0-11.el6.x86_64

chkconfig ntpd on
chkconfig ntpdate on
service ntpd start
service rpcbind start
service nfs start

# yum -y install protobuf-2.3.0-7.el6.x86_64 (No package protobuf-2.3.0-7.el6.x86_64 available.)
# yum -y install protobuf-compiler-2.3.0-7.el6.x86_64 (No package protobuf-compiler-2.3.0-7.el6.x86_64 available.)
# yum -y install protobuf-devel-2.3.0-7.el6.x86_64 (No package protobuf-devel-2.3.0-7.el6.x86_64 available.)
