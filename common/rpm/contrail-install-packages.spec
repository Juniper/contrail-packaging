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
%if 0%{?_skuTag:1}
%define         _sku     %{_skuTag}
%else
%define         _sku      None
%endif


Name:		    contrail-install-packages
Version:	    %{_verstr}
Release:	    %{_relstr}~%{_sku}%{?dist}
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
install -d -m 755 %{buildroot}%{_contrailopt}/puppet
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_packages

# install files
pushd %{_builddir}/..
echo BUILDID=`echo %{_relstr} | cut -d "~" -f1` > %{buildroot}%{_contrailopt}/contrail_packages/VERSION
install -p -m 755 tools/packaging/build/setup.sh %{buildroot}%{_contrailopt}/contrail_packages/setup.sh
install -p -m 755 tools/packaging/build/README %{buildroot}%{_contrailopt}/contrail_packages/README
# Install puppet manifests
tar -cvzf %{_builddir}/../build/contrail-puppet-manifest.tgz -C %{_builddir}/../tools/puppet .
install -p -m 755 %{_builddir}/../build/contrail-puppet-manifest.tgz %{buildroot}%{_contrailopt}/puppet/contrail-puppet-manifest.tgz

if [ -f %{_flist} ]; then echo "Using TGZ FILE = %{_flist}"; install -p -m 644 %{_flist} %{buildroot}%{_contrailopt}/contrail_packages/contrail_rpms.tgz; else echo "ERROR: TGZ file containing all rpms is not supplied or not present"; echo "Supply Argument: FILE_LIST=<TGZ FILE>"; exit 1; fi

%post

%files
%defattr(-, root, root)
%{_contrailopt}/contrail_packages/VERSION
%{_contrailopt}/contrail_packages/README
%{_contrailopt}/contrail_packages/setup.sh
%{_contrailopt}/contrail_packages/contrail_rpms.tgz
%{_contrailopt}/puppet/contrail-puppet-manifest.tgz

%changelog

