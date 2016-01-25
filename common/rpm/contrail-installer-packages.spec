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

%define SETUP_FILE %{_builddir}/../tools/packaging/build/rpm_installer_setup.sh


Name:		    contrail-installer-packages
Version:	    %{_verstr}
Release:	    %{_relstr}~%{_sku}%{?dist}
Summary:	    Contrail Installer %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

%description
Contrail Installer Packages - Contains packages to install contrail-fabric

%install

# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}/etc/
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_installer_packages
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_installer_repo
install -p -m 755 %{SETUP_FILE} %{buildroot}%{_contrailopt}/contrail_installer_packages/setup.sh

%if 0%{?rhel}
install -d -m 755 %{buildroot}/etc/yum.repos.d/
install -p -m 755 %{_builddir}/../tools/packaging/build/contrail-installer.repo %{buildroot}/etc/yum.repos.d/contrail-installer.repo
%endif
%if 0%{?suse_version}
install -d -m 755 %{buildroot}/etc/zypp/repos.d/
install -p -m 755 %{_builddir}/../tools/packaging/build/contrail-installer.repo %{buildroot}/etc/zypp/repos.d/contrail-installer.repo
%endif


if [ -f %{_flist} ]; then \
    echo "Using TGZ FILE = %{_flist}"; \
    tar xzf %{_flist} -C %{buildroot}%{_contrailopt}/contrail_installer_repo/ 2>/dev/null;
else \
    echo "ERROR: TGZ file containing all rpms is not supplied or not present"; \
    echo "Supply Argument: FILE_LIST=<TGZ FILE>"; \
    exit 1; \
fi

%files
%defattr(-, root, root)
/opt/*
%if 0%{?rhel}
/etc/yum.repos.d/*
%endif
%if 0%{?suse_version}
etc/zypp/repos.d/*
%endif


%changelog
* Mon Jan 25 2016 - npchandran@juniper.net
- Removing pip related steps in contrail cloud packages
* Wed Apr 22 2015 - npchandran@juniper.net
- Initial build
