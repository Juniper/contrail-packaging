%define         _distropkgdir tools/packaging/common/control_files
%define         _distrothirdpartydir distro/third_party
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
Requires: rabbitmq-server
Requires: python-bottle
Requires: contrail-nodemgr
Requires: irond 
Requires: contrail-config-openstack
Requires: python-contrail

%description
Contrail Package Requirements for Contrail Config

%install
pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/kazoo
%{__python} setup.py install --root=%{buildroot} 
popd

pushd %{_distrothirdpartydir}/ncclient
%{__python} setup.py install --root=%{buildroot} 
popd

pushd %{_builddir}/..
install -D -m 644 %{_distropkgdir}/api_server.conf %{buildroot}%{_sysconfdir}/contrail/api_server.conf
install -D -m 644 %{_distropkgdir}/schema_transformer.conf %{buildroot}%{_sysconfdir}/contrail/schema_transformer.conf
install -D -m 644 %{_distropkgdir}/svc_monitor.conf %{buildroot}%{_sysconfdir}/contrail/svc_monitor.conf
install -D -m 755 %{_distropkgdir}/supervisor-config.initd %{buildroot}%{_initddir}/supervisor-config
install -D -m 755 %{_distropkgdir}/contrail-api.initd.supervisord %{buildroot}%{_initddir}/contrail-api
install -D -m 755 %{_distropkgdir}/rabbitmq-server.initd.supervisord %{buildroot}%{_initddir}/rabbitmq-server.initdnitd.supervisord.supervisord
install -D -m 755 %{_distropkgdir}/contrail-discovery.initd.supervisord %{buildroot}%{_initddir}/contrail-discovery
install -D -m 755 %{_distropkgdir}/contrail-svc-monitor.initd.supervisord %{buildroot}%{_initddir}/contrail-svc-monitor
install -p -m 755 %{_distropkgdir}/supervisord_config.conf %{buildroot}%{_sysconfdir}/contrail/supervisord_config.conf
install -d -m 755 %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files
install -p -m 755 %{_distropkgdir}/contrail-api.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-api.ini
install -p -m 755 %{_distropkgdir}/rabbitmq-server.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/rabbitmq-server.ini
install -p -m 755 %{_distropkgdir}/contrail-schema.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-schema.ini
install -p -m 755 %{_distropkgdir}/contrail-svc-monitor.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-svc-monitor.ini
install -p -m 755 %{_distropkgdir}/contrail-discovery-centos.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-discovery.ini
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail-api.kill %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-api.kill
install -p -m 755 %{_distropkgdir}/contrail-config.rules %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-config.rules
install -D -m 755 %{_distropkgdir}/zookeeper.initd %{buildroot}%{_initddir}/zookeeper
pushd %{_builddir}
install -D -m 755 src/config/schema-transformer/ifmap_view.py %{buildroot}%{_bindir}/ifmap_view.py
#install -D -m 755 src/config/utils/encap.py %{buildroot}%{_bindir}/encap.py
popd
install -d -m 777 %{buildroot}%{_localstatedir}/log/contrail

install -D -m 755 %{_distropkgdir}/venv-helper %{buildroot}%{_bindir}/venv-helper

pushd %{buildroot}

for f in $(find . -type f -exec grep -nH "^#\!.*BUILD.*python" {} \; | grep -v 'Binary file' | cut -d: -f1); do
    sed "s/#\!.*python/#!\/usr\/bin\/python/g" $f > ${f}.b
    mv ${f}.b $f
    echo "changed $f .... Done!"
done
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/kazoo
%{python_sitelib}/kazoo-*
%{python_sitelib}/ncclient
%{python_sitelib}/ncclient-*
#/usr/share/doc/python-vnc_cfg_api_server
%{_sysconfdir}/contrail
%dir %attr(0777, root, root) %{_localstatedir}/log/contrail
%{_bindir}/ifmap_view.py
%{_bindir}/venv-helper
#%{_bindir}/encap.py
%{_initddir}
#%{_venv_root}/bin
%config(noreplace) %{_sysconfdir}/contrail/supervisord_config.conf
%config(noreplace) %{_sysconfdir}/contrail/supervisord_config_files/contrail-api.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_config_files/rabbitmq-server.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_config_files/contrail-schema.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_config_files/contrail-svc-monitor.ini
%config(noreplace) %{_sysconfdir}/contrail/supervisord_config_files/contrail-discovery.ini
%config(noreplace) %{_sysconfdir}/contrail/api_server.conf
%config(noreplace) %{_sysconfdir}/contrail/schema_transformer.conf
%config(noreplace) %{_sysconfdir}/contrail/svc_monitor.conf

%post
if [ $1 -eq 1 -a -x /bin/systemctl ] ; then
   /bin/systemctl daemon-reload > /dev/null
fi
for svc in rabbitmq-server; do
    if [ -f %{_initddir}/$svc ]; then
        service $svc stop || true
        mv /etc/init/$svc.conf /etc/init/$svc.conf.backup
        mv %{_initddir}/$svc %{_initddir}/$svc.backup
        cp %{_initddir}/$svc.initd.supervisord %{_initddir}/$svc
    fi
done

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

