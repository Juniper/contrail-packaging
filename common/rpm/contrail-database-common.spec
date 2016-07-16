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
Summary: Contrail Database Common %{?_gitVer}
Name: contrail-database-common
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-database >= %{_verstr}-%{_relstr}
Requires: zookeeper
Requires: sysstat
Requires: datastax-agent

%description
Contrail Package Requirements for Contrail Database Common

%install
pushd %{_builddir}/..
install -D -m 755 %{_distropkgdir}/zookeeper.initd %{buildroot}%{_initddir}/zookeeper
popd

%files
%{_initddir}

%changelog
* Fri July  15 2016 <ijohnson@juniper.net>
* Initial build.

