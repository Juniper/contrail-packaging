%define         _distropkgdir tools/packaging/common/control_files

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
Release:	    %{_relstr}%{?dist}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
Summary: Contrail Openstack Database %{?_gitVer}
Name: contrail-openstack-database
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-database >= %{_verstr}-%{_relstr}
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}
Requires: contrail-nodemgr >= %{_verstr}-%{_relstr}
Requires: zookeeper
Requires: supervisor

%description
Contrail Package Requirements for Contrail Database

%install
pushd %{_builddir}/..
install -D -m 755 %{_distropkgdir}/zookeeper.initd %{buildroot}%{_initddir}/zookeeper
popd

%files
%{_initddir}

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

