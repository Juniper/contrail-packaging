#
# Spec  file for server manager...
#

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building contrail-server-manager rpm for release %{_relstr}\n"}
%if 0%{?_fileList:1}
%define         _flist      %{_fileList}
%else
%define         _flist      None
%endif
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
%if 0%{?_skuTag:1}
%define         _sku     %{_skuTag}
%else
%define         _sku      None
%endif


%if 0%{?_osVer:1}
%define         _osver   %(echo %{_osVer} | sed 's,[-|.],,g')
%else
%define         _osver   %(PYTHONPATH=%{PYTHONPATH}:%{_builddir}/../tools/packaging/tools/scripts/ python -c "import package_utils; print package_utils.get_platform()")
%endif

%if 0%{?_pkgFile:1}
%define _pkg_file  %{_pkgFile}
%else
%define _pkg_file  %{_builddir}/../tools/packaging/tools/scripts/server-manager-thirdparty
%endif

%if 0%{?_centospkgFile:1}
%define _centos_pkg_file  %{_centospkgFile}
%else
%define _centos_pkg_file  %{_builddir}/../tools/packaging/tools/scripts/server-manager-centos
%endif

%if 0%{?_redhatpkgFile:1}
%define _redhat_pkg_file  %{_redhatpkgFile}
%else
%define _redhat_pkg_file  %{_builddir}/../tools/packaging/tools/scripts/server-manager-redhat
%endif

%if 0%{?_pkgDirs:1}
%define _pkg_sources  %{_pkgDirs}
%else
%define _pkg_sources  /cs-shared/builder/cache/%{_osver}/server-manager/
%endif


%define         _contrailetc /etc/contrail_smgr
%define         _initd/etc /etc/init.d
%define         _contrailutils /opt/contrail/utils
%define		_etc /etc
%define		_contrail_smgr /server_manager
%define		_contrail_smgr_src	    %{_builddir}/../tools/contrail-server-manager/src/
%define		_third_party	    %{_builddir}/../../../third_party/
%define         _vmware /vmware/

%define		_mydate %(date)
%define		_initdetc   /etc/init.d/
%define		_etc	    /etc/
%define		_cobbleretc /etc/cobbler/
%define		_puppetetc /etc/puppet/
%define		_contrailopt /opt/contrail/
%define		_sbinusr    /usr/sbin/
%define         _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define         _pysitepkg    /usr/lib/python%{_pyver}/site-packages


Name: contrail-server-manager
Version: %{_verstr}
Release: %{_relstr}%{?dist}
Summary: Contrail Server Manager - Server package

Group: Applications/System
License: Commercial
URL: http://www.juniper.net/
Vendor: Juniper Networks Inc

BuildArch: noarch
SOURCE0 : %{name}-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

#BuildRequires:
Requires: puppetlabs-release
Requires: python >= 2.6.6
Requires: httpd
Requires: httpd-devel
Requires: mod_ssl
Requires: ruby-devel
Requires: rubygems
Requires: sqlite
Requires: cobbler
Requires: cobbler-web
Requires:fence-agents
Requires: puppet = 3.7.3-1.el6
Requires: puppet-server = 3.7.3-1.el6
Requires: python-devel
Requires: python-pip
Requires: dhcp
Requires: ntp
Requires: autoconf
Requires: gcc
Requires: bind
Requires: tftp
Requires: ntp
Requires: wget
Requires: sendmail
Requires: dpkg
Requires: dpkg-devel
Requires: syslinux
Requires: python-gevent
Requires: gcc-c++
Requires: libcurl-devel
Requires: openssl-devel
Requires: zlib-devel

%description
A Server manager description

%prep
#%setup -q

%post
HOST_IP_LIST=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp'`
HOST_IP=`echo $HOST_IP_LIST | cut -d' ' -f1`
if [ -f /opt/contrail/contrail_server_manager/IP.txt ];
then
   HOST_IP=$(cat /opt/contrail/contrail_server_manager/IP.txt)
fi
echo $HOST_IP

if [ "$1" -le 1 ]; then
  cp -r %{_contrailetc}/cobbler /etc/
fi

# Copy cobbler distro signatures file that contains esxi5.5 signature.
mv /etc/cobbler/distro_signatures.json /etc/cobbler/distro_signatures.json-save
mv /var/lib/cobbler/distro_signatures.json /var/lib/cobbler/distro_signatures.json-save
cp %{_contrailetc}/cobbler/distro_signatures.json-esxi55 /etc/cobbler/distro_signatures.json
cp %{_contrailetc}/cobbler/distro_signatures.json-esxi55 /var/lib/cobbler/distro_signatures.json

# Copy cobbler boot.cfg template file for esxi5.5
cp -f %{_contrailetc}/cobbler/bootcfg_esxi55.template /etc/cobbler/pxe

# Copy cobbler pxesystem template file for esxi
mv /etc/cobbler/pxe/pxesystem_esxi.template /etc/cobbler/pxe/pxesystem_esxi.template-save
cp %{_contrailetc}/cobbler/pxesystem_esxi.template /etc/cobbler/pxe

cp -r %{_contrailetc}/puppet /etc/
cp -r %{_contrailetc}/kickstarts /var/www/html/
cp %{_contrailetc}/sendmail.cf /etc/mail/

# Saving and replacing default NTP configuration (Server Manager node acts as NTP Server for Cluster)
mv /etc/ntp.conf /etc/ntp.conf.default
cp %{_contrailetc}/ntp.conf /etc/ntp.conf

if [ "$1" -le 1 ]; then
  cp /usr/bin/server_manager/dhcp.template /etc/cobbler/
fi
cp -r /usr/bin/server_manager/kickstarts /var/www/html/
mkdir -p /var/www/html/contrail
mkdir -p /var/www/html/contrail/config_file
mkdir -p /var/www/html/contrail/images
mkdir -p /var/log/contrail-server-manager/

cp -u /etc/puppet/puppet_init_rd /var/www/cobbler/aux/puppet

easy_install argparse
easy_install paramiko
easy_install pycrypto
easy_install ordereddict

mkdir -p %{_contrailetc}/images/

cd %{_contrailetc}/contrail-centos-repo
createrepo .

cd %{_contrailetc}/contrail-redhat-repo
createrepo .

service httpd start
service xinetd restart
service sqlite start
service cobblerd start

service puppetmaster start
service puppet start

service postfix stop
service sendmail restart

# Set IP address in cobbler settings file
sed -i "s/__\$IPADDRESS__/$HOST_IP/" /etc/cobbler/settings
sed -i 's|webdir: /var/www/cobbler|webdir: /srv/www/cobbler|g' /etc/cobbler/settings
/sbin/chkconfig --add contrail-server-manager
sed -i "s/module = authn_.*/module = authn_configfile/g" /etc/cobbler/modules.conf

# Set IP address in server manager configuration file.
sed -i "s/__\$IPADDRESS__/$HOST_IP/g" /opt/contrail/server_manager/sm-config.ini

# Set IP Address in smgr_dhcp_event.py DHCP hook.
sed -i "s/__\$IPADDRESS__/$HOST_IP/g" /opt/contrail/server_manager/smgr_dhcp_event.py

cd /var/www/html/thirdparty_packages
dpkg-scanpackages . | gzip -9c > Packages.gz

chkconfig httpd on
chkconfig puppetmaster on
chkconfig contrail-server-manager on
chkconfig puppet on

%preun
rm -vv /var/www/html/thirdparty_packages/Packages.gz

%build

%install

rm -rf %{buildroot}
mkdir -p  %{buildroot}
install -d -m 755 %{buildroot}/var/www/html/thirdparty_packages
install -d -m 755 %{buildroot}%usr
install -d -m 755 %{buildroot}%{_sbinusr}

install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_initdetc}
install -d -m 755 %{buildroot}%{_contrailopt}%{_contrail_smgr}
install -d -m 755 %{buildroot}%{_contrailetc}/contrail-centos-repo
install -d -m 755 %{buildroot}%{_contrailetc}/contrail-redhat-repo
#install -d -m 755 %{buildroot}%{_cobbleretc}
#install -d -m 755 %{buildroot}%{_puppetetc}

#cp *.py %{buildroot}%{_bindir}%{_contrail_smgr}
pwd
#install -p -m 755 server_mgr_main.py %{buildroot}%{_bindir}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_main.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_db.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_cobbler.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_puppet.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_exception.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_logger.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_status.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}smgr_dhcp_event.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_defaults.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_err.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}openstack_hieradata.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}contrail_defaults.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}server_mgr_mon_base_plugin.py %{buildroot}%{_contrailopt}%{_contrail_smgr}

cp %{_contrail_smgr_src}utils/send_mail.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}sm-config.ini %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}tags.ini %{buildroot}%{_contrailetc}
cp %{_contrail_smgr_src}logger.conf %{buildroot}%{_contrailopt}%{_contrail_smgr}
cp %{_contrail_smgr_src}%{_vmware}esxi_contrailvm.py %{buildroot}%{_contrailopt}%{_contrail_smgr}


cp %{_contrail_smgr_src}third_party/bottle.py %{buildroot}%{_contrailopt}%{_contrail_smgr}


cp %{_contrail_smgr_src}contrail-server-manager %{buildroot}%{_initdetc}
cp -r %{_contrail_smgr_src}/puppet %{buildroot}%{_contrailetc}
#cp -r %{_contrail_smgr_src}repos/contrail-centos-repo %{buildroot}%{_contrailetc}
cp -r %{_contrail_smgr_src}cobbler %{buildroot}%{_contrailetc}
cp -r %{_contrail_smgr_src}kickstarts %{buildroot}%{_contrailetc}
cp %{_contrail_smgr_src}contrail-server-manager.start %{buildroot}%{_sbinusr}contrail-server-manager
cp %{_contrail_smgr_src}utils/sendmail.cf %{buildroot}%{_contrailetc}
cp %{_contrail_smgr_src}ntp.conf %{buildroot}%{_contrailetc}
#install -p -m 755 %{_contrail_smgr_src}cobbler/dhcp.template %{buildroot}%{_bindir}%{_contrail_smgr}
#install -p -m 755 %{_contrail_smgr_src}cobbler/settings %{buildroot}%{_bindir}%{_contrail_smgr}

install -d -m 755 %{buildroot}%{_pysitepkg}/cobbler/modules
cp %{_contrail_smgr_src}third_party/server_post_install.py %{buildroot}%{_pysitepkg}/cobbler/modules/
cp %{_contrail_smgr_src}third_party/server_pre_install.py %{buildroot}%{_pysitepkg}/cobbler/modules/

%{_builddir}/../tools/packaging/tools/scripts/copy_thirdparty_packages.py --package-file %{_pkg_file} \
 --destination-dir %{buildroot}/var/www/html/thirdparty_packages \
 --source-dirs %{_pkg_sources} || (echo "Copying Built packages failed"; exit 1)

%{_builddir}/../tools/packaging/tools/scripts/copy_thirdparty_packages.py --package-file %{_centos_pkg_file} \
 --destination-dir %{buildroot}%{_contrailetc}/contrail-centos-repo \
 --source-dirs %{_pkg_sources} || (echo "Copying Built centos packages failed"; exit 1)

%{_builddir}/../tools/packaging/tools/scripts/copy_thirdparty_packages.py --package-file %{_redhat_pkg_file} \
 --destination-dir %{buildroot}%{_contrailetc}/contrail-redhat-repo \
 --source-dirs %{_pkg_sources} || (echo "Copying Built redhat packages failed"; exit 1)

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
#%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{_contrailopt}/*
/usr/sbin/*
/etc/init.d/contrail-server-manager
%config(noreplace) %{_contrailetc}/tags.ini
%config(noreplace) %{_contrailetc}/sendmail.cf
%config(noreplace) %{_contrailetc}/ntp.conf
%{_contrailetc}/cobbler/*
%{_contrailetc}/puppet/*
%{_contrailetc}/kickstarts/*
%{_contrailetc}/contrail-redhat-repo/*
%{_contrailetc}/contrail-centos-repo/*
#/etc/cobbler/dhcp.template
#/etc/cobbler/dhcp.template
#/etc/puppet/*
%{_pysitepkg}/cobbler/modules/*
/var/www/html/thirdparty_packages
/var/www/html/thirdparty_packages/*
%changelog
* Thu Nov 29 2013  Thilak Raj S <tsurendra@juniper.net> 1.0-1
- First Build
