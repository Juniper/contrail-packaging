%define         _distropkgdir tools/packaging/common/control_files
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
Release:           %{_relstr}%{?dist}
Summary: Contrail Openstack %{?_gitVer}
Name: contrail-openstack
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: python-contrail >= %{_verstr}-%{_relstr}
Requires: openstack-dashboard
Requires: openstack-glance
Requires: openstack-keystone
Requires: openstack-nova
Requires: openstack-cinder
Requires: mysql-server >= 5.1.73
Requires: openssl098e
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}
Requires: memcached
Requires: openstack-nova-novncproxy
Requires: python-glance
Requires: python-glanceclient
Requires: euca2ools
Requires: m2crypto
Requires: qpid-cpp-server
Requires: haproxy
Requires: rabbitmq-server
Requires: supervisor
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires: python-importlib
%endif
%if 0%{?centos} >= 6
Requires: contrail-heat >= %{_verstr}-%{_relstr}
Requires: openstack-heat-api
Requires: openstack-heat-common
Requires: openstack-heat-engine
Requires: crudini
Requires: openstack-utils >= 2014.1-1
Requires: contrail-nova-networkapi >= %{_verstr}-%{_relstr}
Requires: openstack-heat-api-cfn
Requires: python-openstackclient
%endif

%description
Contrail Package Requirements for Contrail Openstack

%install

%files

%changelog
* Mon Aug 08 2016 Nagendra Maynattamai <npchandran@juniper.net>
- Remove packaging empty bin dir

* Mon Jun 20 2016 Nagendra Maynattamai <npchandran@juniper.net>
- Remove supervisord support

* Thu Jun 2 2016 Nagendra Maynattamai <npchandran@juniper.net>
- Added python-openstackclient as one of the dependency

* Tue Sep 26 2013 <ndramesh@juniper.net>
* Initial build.
