%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
Release:	    %{_relstr}%{?dist}
Summary: Contrail Openstack Config %{?_gitVer}
Name: contrail-openstack-config
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-api-lib
Requires: contrail-api-extension
Requires: contrail-config
Requires: openstack-quantum-contrail
Requires: python-novaclient
Requires: python-keystoneclient >= 0.2.0
Requires: python-psutil
Requires: mysql-server
Requires: contrail-setup
Requires: python-zope-interface
%if 0%{?rhel} 
Requires: python-importlib
%endif
Requires: euca2ools
Requires: m2crypto
Requires: openstack-nova
Requires: java-1.7.0-openjdk
Requires: haproxy

%description
Contrail Package Requirements for Contrail Config

%files

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

