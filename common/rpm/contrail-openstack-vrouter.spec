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
Summary: Contrail Openstack vRouter %{?_gitVer}
Name: contrail-openstack-vrouter
Version:	    %{_verstr}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-vrouter-common >= %{_verstr}-%{_relstr}
Requires: contrail-nova-vif >= %{_verstr}-%{_relstr}
Requires: openstack-nova-compute
Requires: openstack-utils
Requires: librabbitmq

%description
Contrail Package Requirements for Contrail Openstack vRouter

%install

%post

%preun

%postun

%files

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

