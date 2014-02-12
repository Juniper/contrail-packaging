# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail
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


Name:		    contrail-install-packages
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail Installer %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc



%description
Contrail Installer Packages - Container of Contrail RPMs

%install

# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailopt}/bin
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils

# install files
pushd %{_builddir}/..
install -p -m 644 tools/packaging/build/contrail_packages_%{_verstr}-%{_relstr}.tgz  %{buildroot}%{_contrailopt}/contrail_packages_%{_relstr}.tgz
install -p -m 755 tools/packaging/common/control_files/contrail_ifrename.sh %{buildroot}%{_contrailopt}/bin/getifname.sh

# install etc files
pushd %{_builddir}/build
install -p -m 644 contrail_installer.tgz  %{buildroot}%{_contrailopt}/contrail_installer.tgz
popd
pushd %{_builddir}/../distro/third_party
install -p -m 644 paramiko-1.11.0.tar.gz %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils/paramiko-1.11.0.tar.gz
install -p -m 644 pycrypto-2.6.tar.gz %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils/pycrypto-2.6.tar.gz
install -p -m 644 Fabric-1.7.0.tar.gz %{buildroot}%{_contrailopt}/contrail_installer/contrail_setup_utils/Fabric-1.7.0.tar.gz
popd

%post
cd %{_contrailopt}
tar xzvf contrail_packages_%{_relstr}.tgz
tar xzvf contrail_installer.tgz

%files
%defattr(-, root, root)
%{_contrailopt}/bin/getifname.sh
%{_contrailopt}/contrail_packages_%{_relstr}.tgz
%{_contrailopt}/contrail_installer.tgz
%{_contrailopt}/contrail_installer/contrail_setup_utils/paramiko-1.11.0.tar.gz
%{_contrailopt}/contrail_installer/contrail_setup_utils/Fabric-1.7.0.tar.gz
%{_contrailopt}/contrail_installer/contrail_setup_utils/pycrypto-2.6.tar.gz

%changelog

