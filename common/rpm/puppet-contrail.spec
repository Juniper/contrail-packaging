%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif

%define         _installdir  /usr/share/openstack-puppet/modules/contrail/

%{echo: "Building release %{_relstr}\n"}

Name:           puppet-contrail
Version:        %{_verstr}
Release:        %{_relstr}%{?dist}
Summary:        puppet modules for tripleo contrail composable roles deployment%{?_gitVer}
Group:          Applications/System
License:        Commercial
URL:            http://www.juniper.net
Vendor:         Juniper Networks Inc

BuildArch:      noarch
    
%description
puppet modules for tripleo contrail composable roles deployment
    
%install
rm -rf %{buildroot}%{_installdir}
install -d -m 0755 %{buildroot}%{_installdir}
cp -rp  %{_builddir}/../tools/puppet-contrail/* %{buildroot}%{_installdir}

%files
%defattr(-, root, root)
%{_installdir}*

%changelog

