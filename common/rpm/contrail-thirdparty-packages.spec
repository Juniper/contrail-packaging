# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail

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


Name:		    contrail-thirdparty-packages
Version:	    %{_verstr}
Release:	    %{_relstr}~%{_sku}%{?dist}
Summary:	    Contrail Installer %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc



%description
Contrail Thirdparty Packages - Container of Contrail Thirdparty RPMs

%install

# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_packages

# install files
pushd %{_builddir}/..
install -p -m 755 tools/packaging/build/thirdparty_setup.sh %{buildroot}%{_contrailopt}/contrail_packages/thirdparty_setup.sh
if [ -f %{_flist} ]; then echo "Using TGZ FILE = %{_flist}"; install -p -m 644 %{_flist} %{buildroot}%{_contrailopt}/contrail_packages/contrail_thirdparty_rpms.tgz; else echo "ERROR: TGZ file containing all rpms is not supplied or not present"; echo "Supply Argument: FILE_LIST=<TGZ FILE>"; exit 1; fi

%files
%defattr(-, root, root)
%{_contrailopt}/contrail_packages/contrail_thirdparty_rpms.tgz
%{_contrailopt}/contrail_packages/thirdparty_setup.sh

%changelog

