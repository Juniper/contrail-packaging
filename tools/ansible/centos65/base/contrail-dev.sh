#!/bin/sh


function setup_repo {

cat << EOT > /etc/yum.repos.d/cc-65.repo
[centos_build_repo]
name=centos_build_repo
baseurl=http://10.150.16.7/install_repo/centOS6.5/build/
enabled=1
priority=99
gpgcheck=0

[centos_base_repo]
name=centos_base_repo
baseurl=http://10.150.16.7/install_repo/centOS6.5/base/
enabled=1
priority=99
gpgcheck=0
EOT
}

function install_ssdtools {
  sddtools=(
    contrail-build
    repo
  )

  for tool in ${sddtools[*]}
    do
      if [ ! -e /usr/bin/$tool ]
      then
        wget --preserve-permissions --cut-dir=4 -npH -r --reject="index.html*" http://contrail-ec-build05.juniper.net/install_repo/ssd-tools/bin/$tool -P /usr/bin/; chmod +x /usr/bin/$tool
      fi
  done

  if [ ! -L /usr/local/bin/python2.7 ] ; then
    ln -s  /usr/bin/python  /usr/local/bin/python2.7
  fi
}


function yum_install {
  yum_packages=(
    libselinux-python
    polkit-0.96 
    polkit-devel-0.96
   docbook-style-dsssl 
   docbook-style-xsl 
   docbook-utils 
   gc 
   glib2-devel 
   gtk-doc 
   openjade 
   opensp 
   perl-SGMLSpm 
   polkit-docs 
   w3m 
   polkit-desktop-policy 
   polkit-gnome 
   wget  
   openssh-clients 
   ntpdate 
   ntp 
   vim 
   nfs-utils 
   screen 
   ypbind 
   autofs 
   gedit 
   gedit-plugins 
   quota 
   traceroute 
   tree 
   strace 
   tcsh 
   zsh 
   ant 
   autoconf-2.68 
   scons-2.2.0-1 
   bison 
   flex 
   gcc-c++ 
   gdb 
   openssl-devel 
   rpm-build 
   python-devel 
   git-1.7.3.4 
   cppunit-devel 
   devtoolset-1.1-gcc-c++ 
   openstack-utils 
   python-argparse 
   nodejs 
   libnl-devel 
   augeas 
   libpciaccess-devel 
   yajl-devel 
   sanlock-devel 
   libpcap-devel 
   parted-devel 
   numactl-devel 
   libcap-ng-devel 
   audit-libs-devel 
   systemtap 
   systemtap-sdt-devel 
   gnutls-devel 
   python-lxml 
   python-setuptools 
   libxslt-devel 
   python-virtualenv 
   python-netaddr 
   graphviz 
   python-routes 
   python-migrate 
   python-iso8601 
   ruby 
   readline-devel 
   libtasn1-devel 
   dnsmasq 
   radvd 
   ebtables 
   cyrus-sasl-devel 
   qemu-img 
   libcurl-devel 
   scrub 
   numad 
   createrepo 
   python-boto 
   python-eventlet 
   python-nose 
   python-webtest 
   libblkid-devel 
   pungi 
   python-sphinx 
   avahi-devel 
   netcf-devel 
   xhtml1-dtds 
   python-pip 
   libudev-devel 
   device-mapper-devel 
   cppunit-devel 
   libevent-devel 
   ant-nodeps 
   kernel-devel-2.6.32-431.el6 
   kernel-headers-2.6.32-431.el6 
   lcov 
   redis 
   sqlite-devel 
   log4cplus 
   python-d2to1 
   python-pbr 
   java-1.6.0-openjdk-devel 
   java-1.7.0-openjdk-devel 
   intltool 
   libtool 
   redhat-rpm-config 
   qemu-kvm
   libvirt 
   python-oslo-sphinx 
   git-review 
   python-pip
  )

  for pkg in ${yum_packages[*]}
    do yum -y install $pkg
  done

}

function install_pip {
  easy_install pip
}

function  pip_install {

pip install lxml
pip install PyGitHub==1.12.1 
pip install fabric==1.8.0 
pip install pep8==1.4.6 
pip install autopep8==0.9.7 
pip install paramiko==1.12.0 
pip install PIL==1.1.7 

}

function enable_selinux {
   sed -i"" s/^SELINUX=.*/SELINUX=enforcing/g /etc/selinux/config
}

function setup_sudoers {
  if grep -Fq "mganley" /etc/sudoers
    then
      sed -i"" s/^mganley.*/"mganley ALL=(ALL)     NOPASSWD: ALL"/g /etc/sudoers
    else
      echo "mganley ALL=(ALL)     NOPASSWD: ALL" >> /etc/sudoers
  fi
}

function disable_default_requiretty {
   sed -i"" -n 's/\(^Defaults.*requiretty.*\)/#\1/p' /etc/sudoers
}


trap "exit -1" SIGHUP SIGINT SIGTERM

setup_repo
yum_install
install_pip
pip_install
enable_selinux
setup_sudoers
install_ssdtools

