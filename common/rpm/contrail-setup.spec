# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail
%define         _distropkgdir tools/packaging/common/control_files
%define         _provdir      %{_builddir}/../tools/provisioning

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
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

Name:		    contrail-setup
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail Setup %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	    tar
Requires:	    python-pip
Requires:	    python-netifaces
Requires:	    gcc
Requires:	    python-devel
Requires:	    python-netaddr
Requires:	    openstack-utils
%if 0%{?fedora} >= 17
#Requires:	    python-Fabric
Requires:	    python-crypto
%endif
%if 0%{?rhel}
Requires:	    python-argparse
Requires:	    gdb
%endif

%description
Contrail Setup package with scripts for provisioning

BuildRequires:  systemd-units

%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}
# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=contrail-controller
grep $gitrepo .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "please run rpmbuild from ctrlplane git tree"
    exit -1
fi


%build
#%{__python} tools/provisioning/create_installer.py --embed_vrouter 
pushd %{_builddir}/build
%{__python} %{_provdir}/create_installer.py
popd

pushd src/config
tar cvfz ../../cfgm_utils.tgz utils
popd

pushd src/dns/scripts
tar cvfz ../../../dns_scripts.tgz *
popd

%install

# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailopt}/bin
install -d -m 755 %{buildroot}%{_contrailopt}/puppet
install -d -m 777 %{buildroot}%{_localstatedir}/log/contrail
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_packages
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils

# install files
pushd %{_builddir}/..
echo BUILDID=`echo %{_relstr} | cut -d "~" -f1` > %{buildroot}%{_contrailopt}/contrail_packages/VERSION
install -p -m 755 tools/packaging/build/setup.sh %{buildroot}%{_contrailopt}/contrail_packages/setup.sh
install -p -m 755 tools/packaging/build/README %{buildroot}%{_contrailopt}/contrail_packages/README
install -p -m 755 tools/packaging/common/control_files/contrail_ifrename.sh %{buildroot}%{_contrailopt}/bin/getifname.sh
if [ 0%{_sku} = 0icehouse ]; then
install -d -m 755 %{buildroot}/usr/bin
install -p -m 755 tools/provisioning/contrail_setup_utils/contrail-keystone-setup.sh %{buildroot}/usr/bin/contrail-keystone-setup.sh
fi
tar -cvzf %{_builddir}/../build/contrail-puppet-manifest.tgz -C %{_builddir}/../tools/puppet .
install -p -m 755 %{_builddir}/../build/contrail-puppet-manifest.tgz %{buildroot}%{_contrailopt}/puppet/contrail-puppet-manifest.tgz
popd

# install etc files
install -p -m 644 cfgm_utils.tgz  %{buildroot}%{_contrailopt}/cfgm_utils.tgz
install -p -m 644 dns_scripts.tgz  %{buildroot}%{_contrailopt}/dns_scripts.tgz
pushd %{_builddir}/build
install -p -m 644 contrail_installer.tgz  %{buildroot}%{_contrailopt}/contrail_installer.tgz
popd
%if 0%{?rhel}
pushd %{_builddir}/../distro/third_party
tar cvzf %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils/zope.interface-3.7.0.tar.gz ./zope.interface-3.7.0 
install -p -m 644 paramiko-1.11.0.tar.gz %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils/paramiko-1.11.0.tar.gz
install -p -m 644 pycrypto-2.6.tar.gz %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils/pycrypto-2.6.tar.gz
install -p -m 644 Fabric-1.7.0.tar.gz %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils/Fabric-1.7.0.tar.gz
popd
%endif

install -d -m 755 %{buildroot}/etc/contrail
if [ %{_flist} = None ]; then 
    %{_builddir}/../tools/packaging/build/create_pkg_list_file.py --sku %{_sku} %{buildroot}/etc/contrail/rpm_list.txt
else 
    cp %{_flist} %{buildroot}/etc/contrail/rpm_list.txt
fi
#install -p -m 644 %{_builddir}/../tools/packaging/common/rpm/rpm_list.txt  %{buildroot}/etc/contrail/rpm_list.txt

# install bin files
install -D -m 755 src/config/utils/contrail-version %{buildroot}%{_bindir}/contrail-version
install -D -m 755 src/config/utils/contrail-status.py %{buildroot}%{_bindir}/contrail-status


%post

cd %{_contrailopt}
tar xzvf cfgm_utils.tgz
tar xzvf dns_scripts.tgz -C utils
tar xzvf contrail_installer.tgz
#pip-python install /opt/contrail/contrail_installer/contrail_setup_utils/pycrypto-2.6.tar.gz
#pip-python install /opt/contrail/contrail_installer/contrail_setup_utils/paramiko-1.11.0.tar.gz
#pip-python install /opt/contrail/contrail_installer/contrail_setup_utils/Fabric-1.7.0.tar.gz

%files
%defattr(-, root, root)
%{_contrailopt}/bin/getifname.sh
%{_contrailopt}/contrail_packages/VERSION
%{_contrailopt}/contrail_packages/README
%{_contrailopt}/contrail_packages/setup.sh
%{_contrailopt}/cfgm_utils.tgz
%{_contrailopt}/dns_scripts.tgz
%{_contrailopt}/contrail_installer.tgz
%{_contrailopt}/puppet/contrail-puppet-manifest.tgz
%{_contrailopt}/contrail_installer/contrail_setup_utils/paramiko-1.11.0.tar.gz
%{_contrailopt}/contrail_installer/contrail_setup_utils/Fabric-1.7.0.tar.gz
%{_contrailopt}/contrail_installer/contrail_setup_utils/pycrypto-2.6.tar.gz
%if 0%{?rhel}
%{_contrailopt}/contrail_installer/contrail_setup_utils/zope.interface-3.7.0.tar.gz
%endif
%if 0%{?_fileList:1}
    /etc/contrail/rpm_list.txt
%endif
/etc/contrail
%dir %attr(0777, root, root) %{_localstatedir}/log/contrail
%{_bindir}/contrail-version
%{_bindir}/contrail-status
%if "0%{_sku}" == "0icehouse"
/usr/bin/contrail-keystone-setup.sh
%endif

%changelog

