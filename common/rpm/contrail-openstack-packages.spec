# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building contrail-openstack-packages for release %{_relstr}\n"}
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


Name:		    contrail-openstack-packages
Version:	    %{_verstr}
Release:	    %{_relstr}~%{_sku}%{?dist}
Summary:	    Contrail Installer %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc



%description
Contrail Openstack Packages - Container of Contrail Openstack RPMs

%install
# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}/etc/
install -d -m 755 %{buildroot}/etc/yum.repos.d/
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_openstack_repo/

# install files
install -p -m 755 %{_builddir}/../tools/packaging/build/contrail-openstack.repo %{buildroot}/etc/yum.repos.d/contrail-openstack.repo
if [ -f %{_flist} ]; then echo "Using TGZ FILE = %{_flist}"; tar xzf %{_flist} -C %{buildroot}%{_contrailopt}/contrail_openstack_repo/ 2>/dev/null; else echo "ERROR: TGZ file containing all rpms is not supplied or not present"; echo "Supply Argument: FILE_LIST=<TGZ FILE>"; exit 1; fi

%files
%defattr(-, root, root)
%{_contrailopt}/contrail_openstack_repo/*
/etc/yum.repos.d/contrail-openstack.repo

%changelog
* Mon Oct 20 2014 Nagendra Chandran <npchandran@juniper.net>
- Initial build.
