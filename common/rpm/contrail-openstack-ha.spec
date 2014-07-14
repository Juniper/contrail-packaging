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
Summary: Contrail Openstack High Availability %{?_gitVer}
Name: contrail-openstack-ha
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: galera
Requires: keepalived
Requires: percona-xtrabackup

%description
Contrail Package Requirements for Contrail Openstack High Availability

%files

%changelog
* Thu May  29 2014 <ijohnson@juniper.net>
* Initial build.

