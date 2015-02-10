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
Requires: openstack-dashboard = 2013.2-%{_verstr}.%{_relstr}
Requires: contrail-openstack-dashboard >= 2013.2-%{_verstr}.%{_relstr}
Requires: openstack-glance
Requires: openstack-keystone
Requires: openstack-nova = 2013.2-2contrail
Requires: openstack-cinder
Requires: mysql-server >= 5.1.73
Requires: openssl098e
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}
Requires: memcached
Requires: openstack-nova-novncproxy = 2013.2-2contrail
Requires: python-glance
Requires: python-glanceclient
%if 0%{?rhel} 
Requires: python-importlib
%endif
Requires: euca2ools >= 1.0-2contrail
Requires: m2crypto
Requires: qpid-cpp-server
Requires: haproxy
Requires: rabbitmq-server
Requires: supervisor
%if 0%{?rhel} <= 6
Requires: python-importlib
%endif

%description
Contrail Package Requirements for Contrail Openstack

%install
# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}/%{_bindir}

pushd %{_builddir}/..
# Install supervisord config config files and directories
install -d -m 755 %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files
install -D -m 755 %{_distropkgdir}/supervisor-openstack.initd %{buildroot}%{_initddir}/supervisor-openstack
install -D -m 755 %{_distropkgdir}/supervisord_openstack.conf %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack.conf
# Install supervisor init.d files
install -D -m 755 %{_distropkgdir}/keystone.initd.supervisord %{buildroot}%{_initddir}/keystone
install -D -m 755 %{_distropkgdir}/nova-api.initd.supervisord %{buildroot}%{_initddir}/nova-api
install -D -m 755 %{_distropkgdir}/nova-scheduler.initd.supervisord %{buildroot}%{_initddir}/nova-scheduler
install -D -m 755 %{_distropkgdir}/nova-conductor.initd.supervisord %{buildroot}%{_initddir}/nova-conductor
install -D -m 755 %{_distropkgdir}/nova-cert.initd.supervisord %{buildroot}%{_initddir}/nova-cert
install -D -m 755 %{_distropkgdir}/nova-consoleauth.initd.supervisord %{buildroot}%{_initddir}/nova-consoleauth
install -D -m 755 %{_distropkgdir}/nova-novncproxy.initd.supervisord %{buildroot}%{_initddir}/nova-novncproxy
install -D -m 755 %{_distropkgdir}/glance-api.initd.supervisord %{buildroot}%{_initddir}/glance-api
install -D -m 755 %{_distropkgdir}/glance-registry.initd.supervisord %{buildroot}%{_initddir}/glance-registry
install -D -m 755 %{_distropkgdir}/cinder-api.initd.supervisord %{buildroot}%{_initddir}/cinder-api
install -D -m 755 %{_distropkgdir}/cinder-scheduler.initd.supervisord %{buildroot}%{_initddir}/cinder-scheduler
# Install supervisord config files
install -D -m 755 %{_distropkgdir}/keystone.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/keystone.ini
install -D -m 755 %{_distropkgdir}/glance-api.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/glance-api.ini
install -D -m 755 %{_distropkgdir}/glance-registry.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/glance-registry.ini
install -D -m 755 %{_distropkgdir}/cinder-api.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/cinder-api.ini
install -D -m 755 %{_distropkgdir}/cinder-scheduler.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/cinder-scheduler.ini
install -D -m 755 %{_distropkgdir}/nova-api.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-api.ini
install -D -m 755 %{_distropkgdir}/nova-scheduler.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-scheduler.ini
install -D -m 755 %{_distropkgdir}/nova-conductor.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-conductor.ini
install -D -m 755 %{_distropkgdir}/nova-consoleauth.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-consoleauth.ini
install -D -m 755 %{_distropkgdir}/nova-novncproxy.ini.centos %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-novncproxy.ini
# Install contrail openstack-status
install -p -m 755 tools/provisioning/tools/openstack-status %{buildroot}/%{_bindir}/openstack-status.contrail
popd

%files
%defattr(-,root,root,-)
%{_sysconfdir}/contrail
%{_initddir}
%{_bindir}
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/keystone.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/glance-api.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/glance-registry.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/cinder-api.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/cinder-scheduler.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-api.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-scheduler.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-conductor.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-consoleauth.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-novncproxy.ini
%{_bindir}/openstack-status.contrail

%post
# Replace stock openstack-status with contrail openstack-status
if [ -f %{_bindir}/openstack-status ]; then
    mv %{_bindir}/openstack-status %{_bindir}/openstack-status.rpmsave
fi
mv %{_bindir}/openstack-status.contrail %{_bindir}/openstack-status

# Replace stock openstack initd scripts with contrail initd scripts
for svc in openstack-keystone openstack-nova-api openstack-nova-scheduler\
           openstack-nova-consoleauth openstack-nova-conductor\
           openstack-nova-novncproxy openstack-glance-api\
           openstack-glance-registry openstack-cinder-api\
           openstack-cinder-scheduler; do
    if [ -f %{_initddir}/$svc ]; then
        service $svc stop || true
        mv %{_initddir}/$svc %{_initddir}/$svc.backup
    fi
done

%changelog
* Tue Sep 26 2013 <ndramesh@juniper.net>
* Initial build.
