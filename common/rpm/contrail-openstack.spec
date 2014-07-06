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
Summary: Contrail Openstack %{?_gitVer}
Name: contrail-openstack
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: python-contrail
Requires: openstack-dashboard
Requires: contrail-openstack-dashboard
Requires: openstack-glance
Requires: openstack-keystone
Requires: openstack-nova
Requires: openstack-cinder
Requires: mysql-server
Requires: contrail-setup
Requires: memcached
Requires: openstack-nova-novncproxy
Requires: python-glance
Requires: python-glanceclient
%if 0%{?rhel} 
Requires: python-importlib
%endif
Requires: euca2ools
Requires: m2crypto
Requires: qpid-cpp-server
Requires: haproxy
Requires: rabbitmq-server

%description
Contrail Package Requirements for Contrail Openstack

%files

%changelog
* Tue Sep 26 2013 <ndramesh@juniper.net>
* Initial build.

