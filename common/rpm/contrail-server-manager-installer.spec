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


Name:		    contrail-server-manager-installer
Version:	    %{_verstr}
Release:	    %{_relstr}~%{_sku}%{?dist}
Summary:	    Contrail Server Manager Installer %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc



%description
Contrail Server Manager Installer Packages - Container of Server Manager and Its dependend RPMs

%install
# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}/etc/
install -d -m 755 %{buildroot}/etc/yum.repos.d/
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_server_manager/
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_server_manager/packages/

# install files
pushd %{_builddir}/..
install -p -m 755 tools/packaging/build/rpm_server_manager_setup.sh %{buildroot}%{_contrailopt}/contrail_server_manager/setup.sh
install -p -m 755 tools/packaging/build/puppetmaster.conf %{buildroot}%{_contrailopt}/contrail_server_manager/puppetmaster.conf
install -p -m 755 tools/packaging/build/server_manager.repo %{buildroot}/etc/yum.repos.d/server_manager.repo
install -p -m 755 tools/packaging/build/rpm_server_manager_readme %{buildroot}%{_contrailopt}/contrail_server_manager/README
popd

if [ -f %{_flist} ]; then echo "Using TGZ FILE = %{_flist}"; tar xzf %{_flist} -C %{buildroot}%{_contrailopt}/contrail_server_manager/packages/; else echo "ERROR: TGZ file containing all rpms is not supplied or not present"; echo "Supply Argument: FILE_LIST=<TGZ FILE>"; exit 1; fi

%files
%defattr(-, root, root)
%{_contrailopt}/contrail_server_manager/
/etc/yum.repos.d/server_manager.repo

%changelog
* Mon Oct 20 2014 Nagendra Chandran <npchandran@juniper.net>
- Initial build
