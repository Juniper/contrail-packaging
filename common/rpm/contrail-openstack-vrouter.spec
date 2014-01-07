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

Requires: contrail-api-lib
Requires: contrail-vrouter
Requires: abrt
# abrt-addon-vmcore might be needed for centos. Add when package is available
%if 0%{?fedora} >= 17
Requires: abrt-addon-vmcore
Requires: kexec-tools
Requires: kernel = 3.6.6-1.fc17
%endif
Requires: openstack-nova-compute
Requires: openstack-utils
Requires: python-thrift
Requires: contrail-setup
Requires: haproxy

%if 0%{?rhel}
Requires: tunctl
%endif

%description
Contrail Package Requirements for Contrail vRouter

%files

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

