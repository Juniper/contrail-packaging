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

Requires: python-contrail
Requires: openstack-dashboard
Requires: contrail-openstack-dashboard
Requires: openstack-glance
Requires: openstack-keystone
Requires: openstack-nova
Requires: openstack-cinder
Requires: mysql-server
#Requires: MySQL-server
Requires: openssl098e
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

%install
pushd %{_builddir}/..
# Install supervisord config config files and directories
install -d -m 755 %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files
install -D -m 755 %{_distropkgdir}/supervisor-openstack.upstart %{buildroot}%{_initdir}/supervisor-openstack.conf.upstart_openstack
install -D -m 755 %{_distropkgdir}/supervisord_openstack.conf %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack.conf.supervisord_openstack
# Install supervisor init.d files
install -D -m 755 %{_distropkgdir}/keystone.initd.supervisord %{buildroot}%{_initddir}/keystone.initd.supervisord
install -D -m 755 %{_distropkgdir}/nova-api.initd.supervisord %{buildroot}%{_initddir}/nova-api.initd.supervisord
install -D -m 755 %{_distropkgdir}/nova-scheduler.initd.supervisord %{buildroot}%{_initddir}/nova-scheduler.initd.supervisord
install -D -m 755 %{_distropkgdir}/nova-conductor.initd.supervisord %{buildroot}%{_initddir}/nova-conductor.initd.supervisord
install -D -m 755 %{_distropkgdir}/nova-console.initd.supervisord %{buildroot}%{_initddir}/nova-console.initd.supervisord
install -D -m 755 %{_distropkgdir}/nova-consoleauth.initd.supervisord %{buildroot}%{_initddir}/nova-consoleauth.initd.supervisord
install -D -m 755 %{_distropkgdir}/nova-objectstore.initd.supervisord %{buildroot}%{_initddir}/nova-objectstore.initd.supervisord
install -D -m 755 %{_distropkgdir}/nova-novncproxy.initd.supervisord %{buildroot}%{_initddir}/nova-novncproxy.initd.supervisord
install -D -m 755 %{_distropkgdir}/glance-api.initd.supervisord %{buildroot}%{_initddir}/glance-api.initd.supervisord
install -D -m 755 %{_distropkgdir}/glance-registry.initd.supervisord %{buildroot}%{_initddir}/glance-registry.initd.supervisord
install -D -m 755 %{_distropkgdir}/cinder-api.initd.supervisord %{buildroot}%{_initddir}/cinder-api.initd.supervisord
install -D -m 755 %{_distropkgdir}/cinder-scheduler.initd.supervisord %{buildroot}%{_initddir}/cinder-scheduler.initd.supervisord
# Install supervisord config files
install -D -m 755 %{_distropkgdir}/keystone.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/keystone.ini
install -D -m 755 %{_distropkgdir}/glance-api.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/glance-api.ini
install -D -m 755 %{_distropkgdir}/glance-registry.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/glance-registry.ini
install -D -m 755 %{_distropkgdir}/cinder-api.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/cinder-api.ini
install -D -m 755 %{_distropkgdir}/cinder-scheduler.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/cinder-scheduler.ini
install -D -m 755 %{_distropkgdir}/nova-api.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-api.ini
install -D -m 755 %{_distropkgdir}/nova-scheduler.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-scheduler.ini
install -D -m 755 %{_distropkgdir}/nova-conductor.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-conductor.ini
install -D -m 755 %{_distropkgdir}/nova-console.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-console.ini
install -D -m 755 %{_distropkgdir}/nova-consoleauth.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-consoleauth.ini
install -D -m 755 %{_distropkgdir}/nova-objectstore.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-objectstore.ini
install -D -m 755 %{_distropkgdir}/nova-novncproxy.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_openstack_files/nova-novncproxy.ini
popd

%files
%defattr(-,root,root,-)
%{_sysconfdir}/contrail
%{_initddir}
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack.conf.supervisord_openstack
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/keystone.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/glance-api.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/glance-registry.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/cinder-api.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/cinder-scheduler.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-api.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-scheduler.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-conductor.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-console.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-consoleauth.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-objectstore.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_openstack_files/nova-novncproxy.ini

%post
for svc in keystone openstack-nova_api openstack-nova_scheduler\
           openstack-nova_conductor openstack-nova_console\
           openstack-nova_consoleauth openstack-nova_objectstore\
           openstack-nova_novncproxy openstack-glance_api\
           openstack-glance_registry openstack-cinder_api\
           openstack-cinder_scheduler; do
    if [ -f /etc/init/$svc.conf ]; then
        service $svc stop || true
        mv /etc/init/$svc.conf /etc/init/$svc.conf.backup
        mv %{_initddir}/$svc %{_initddir}/$svc.backup
        cp %{_initddir}/$svc.initd.supervisord %{_initddir}/$svc
    fi
done

if [ ! -f /etc/init/supervisor-openstack.conf ]; then
    mv /etc/init/supervisor-openstack.conf.upstart_openstack /etc/init/supervisor-openstack.conf
else
    rm /etc/init/supervisor-openstack.conf.upstart_openstack
fi
if [ ! -f /etc/contrail/supervisord_openstack.conf ]; then
    mv /etc/contrail/supervisord_openstack.conf.supervisord_openstack /etc/contrail/supervisord_openstack.conf
else
    rm /etc/contrail/supervisord_openstack.conf.supervisord_openstack
fi

# Start mysql at boot time
sudo update-rc.d -f mysql remove
sudo update-rc.d mysql defaults

%changelog
* Tue Sep 26 2013 <ndramesh@juniper.net>
* Initial build.
