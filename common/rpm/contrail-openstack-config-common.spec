%define         _distropkgdir tools/packaging/common/control_files
%define         _distrothirdpartydir distro/third_party
%define         _nodemgr_config controller/src/nodemgr/config_nodemgr
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

#Requires: contrail-api-lib
Requires: contrail-config >= %{_verstr}-%{_relstr}
#python-neutron requires python-oslo-serialization, but that doesn't
#have dependency, adding it here as workaround
Requires: python-oslo-serialization
Requires: openstack-neutron
Requires: neutron-plugin-contrail >= %{_verstr}-%{_relstr}
Requires: python-novaclient
Requires: python-keystoneclient >= 0.2.0
Requires: python-psutil
Requires: mysql-server
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}
Requires: python-zope-interface
Requires: euca2ools
Requires: m2crypto
Requires: java-1.7.0-openjdk
Requires: haproxy
Requires: keepalived
Requires: rabbitmq-server >= 3.3.5
Requires: python-contrail >= %{_verstr}-%{_relstr}
Requires: contrail-config-openstack >= %{_verstr}-%{_relstr}
Requires: python-bottle
Requires: contrail-nodemgr  >= %{_verstr}-%{_relstr}
Requires: ifmap-server >= 0.3.2-2contrail
Requires: python-neutron-lbaas
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires: python-importlib
%endif

%description
Contrail Package Requirements for Contrail Config

%install
pushd %{_builddir}/..

pushd %{_builddir}/..
install -D -m 755 %{_distropkgdir}/ifmap.initd.supervisord %{buildroot}%{_initddir}/ifmap
install -d -m 755 %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files
install -p -m 755 %{_distropkgdir}/ifmap.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/ifmap.ini
install -p -m 755 %{_nodemgr_config}/contrail-config-nodemgr.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-config-nodemgr.ini
install -D -m 755 %{_distropkgdir}/zookeeper.initd %{buildroot}%{_initddir}/zookeeper
pushd %{_builddir}
install -D -m 755 src/config/schema-transformer/ifmap_view.py %{buildroot}%{_bindir}/ifmap_view.py
#install -D -m 755 src/config/utils/encap.py %{buildroot}%{_bindir}/encap.py
popd
install -d -m 777 %{buildroot}%{_localstatedir}/log/contrail

pushd %{buildroot}

for f in $(find . -type f -exec grep -nH "^#\!.*BUILD.*python" {} \; | grep -v 'Binary file' | cut -d: -f1); do
    sed "s/#\!.*python/#!\/usr\/bin\/python/g" $f > ${f}.b
    mv ${f}.b $f
    echo "changed $f .... Done!"
done
popd

%files
%defattr(-,root,root,-)
#/usr/share/doc/python-vnc_cfg_api_server
%{_sysconfdir}/contrail
%dir %attr(0777, contrail, contrail) %{_localstatedir}/log/contrail
%{_bindir}/ifmap_view.py
#%{_bindir}/encap.py
%{_initddir}
%config(noreplace) %{_sysconfdir}/contrail/supervisord_config_files/contrail-config-nodemgr.ini

%post
if [ $1 -eq 1 -a -x /bin/systemctl ] ; then
   /bin/systemctl daemon-reload > /dev/null
fi

%changelog
* Wed Jun 22 2016 Nagendra Maynattamai <npchandran@juniper.net>
* Remove supervisor-support-services and supervisor support for rabbitmq
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

