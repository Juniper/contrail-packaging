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
Summary: Contrail Config %{?_gitVer}
Name: contrail-config
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: python-bitarray
Requires: python-gevent
#Requires: python-geventhttpclient
#Requires: python-pycassa
#Requires: python-thrift
Requires: python-keystone
Requires: python-psutil
Requires: python-requests
Requires: python-zope-interface
Requires: irond
Requires: zookeeper
Requires: zkpython
Requires: xmltodict >= 0.1
Requires: redis
Requires: redis-py
Requires: supervisor

Requires: contrail-api-venv
%define _venv_root    /opt/contrail/api-venv
%define _venvtr       --prefix=%{_venv_root}

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages
%description
Contrail Config package

%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}

# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=contrail-controller
grep $gitrepo .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi


%build
scons -U src/sandesh/common
scons -U src/api-lib
#scons -U src/cfgm/common
scons -U src/config/common
scons -U src/config/api-server
scons -U src/config/schema-transformer
scons -U src/config/svc-monitor
pushd %{_builddir}/../tools/
scons -U sandesh/library/python
popd
scons -U src/discovery

%define _build_dist %{_builddir}/../build/debug
%install
install -d -m 755 %{buildroot}%{_venv_root}

mkdir -p build/python_dist
pushd build/python_dist

tar zxf %{_build_dist}/config/api-server/dist/vnc_cfg_api_server-0.1dev.tar.gz
pushd vnc_cfg_api_server-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
install -d -m 755 %{buildroot}/usr/share/doc/python-vnc_cfg_api_server
if [ -d doc ]; then
   cp -R doc/* %{buildroot}/usr/share/doc/python-vnc_cfg_api_server
fi
popd

tar zxf %{_build_dist}/config/schema-transformer/dist/schema_transformer-0.1dev.tar.gz
pushd schema_transformer-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

tar zxf %{_build_dist}/config/svc-monitor/dist/svc_monitor-0.1dev.tar.gz
pushd svc_monitor-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

tar zxf %{_build_dist}/sandesh/common/dist/sandesh-common-0.1dev.tar.gz
pushd sandesh-common-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

tar zxf %{_build_dist}/tools/sandesh/library/python/dist/sandesh-0.1dev.tar.gz
pushd sandesh-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

tar zxf %{_build_dist}/discovery/dist/discovery-0.1dev.tar.gz
pushd discovery-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

# python_dist
popd

pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/kazoo
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

pushd %{_distrothirdpartydir}/ncclient
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

pushd %{_builddir}/..
install -D -m 644 %{_distropkgdir}/api_server.conf %{buildroot}%{_sysconfdir}/contrail/api_server.conf.rpmsave
install -D -m 644 %{_distropkgdir}/schema_transformer.conf %{buildroot}%{_sysconfdir}/contrail/schema_transformer.conf.rpmsave
install -D -m 644 %{_distropkgdir}/svc_monitor.conf %{buildroot}%{_sysconfdir}/contrail/svc_monitor.conf.rpmsave
install -D -m 644 %{_distropkgdir}/discovery.conf %{buildroot}%{_sysconfdir}/contrail/discovery.conf.rpmsave
%if 0%{?fedora} >= 17
install -D -m 644 %{_distropkgdir}/supervisor-config.service %{buildroot}/usr/lib/systemd/system/supervisor-config.service
%endif
%if 0%{?rhel}
install -D -m 755 %{_distropkgdir}/supervisor-config.initd %{buildroot}%{_initddir}/supervisor-config
install -D -m 755 %{_distropkgdir}/contrail-api.initd.supervisord %{buildroot}%{_initddir}/contrail-api
install -D -m 755 %{_distropkgdir}/contrail-discovery.initd.supervisord %{buildroot}%{_initddir}/contrail-discovery
install -D -m 755 %{_distropkgdir}/contrail-schema.initd.supervisord %{buildroot}%{_initddir}/contrail-schema
install -D -m 755 %{_distropkgdir}/contrail-svc-monitor.initd.supervisord %{buildroot}%{_initddir}/contrail-svc-monitor
%endif
install -p -m 755 %{_distropkgdir}/supervisord_config.conf %{buildroot}%{_sysconfdir}/contrail/supervisord_config.conf
install -d -m 755 %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files
install -p -m 755 %{_distropkgdir}/redis_config.conf %{buildroot}%{_sysconfdir}/contrail/
install -p -m 755 %{_distropkgdir}/contrail-api.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-api.ini
install -p -m 755 %{_distropkgdir}/contrail-schema.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-schema.ini
install -p -m 755 %{_distropkgdir}/contrail-svc-monitor.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-svc-monitor.ini
install -p -m 755 %{_distropkgdir}/contrail-discovery.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-discovery.ini
install -p -m 755 %{_distropkgdir}/redis-config.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail-api.kill %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-api.kill
install -p -m 755 %{_distropkgdir}/contrail-config.rules %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/contrail-config.rules
pushd %{_builddir}
install -D -m 755 src/config/schema-transformer/ifmap_view.py %{buildroot}%{_bindir}/ifmap_view.py
#install -D -m 755 src/config/utils/encap.py %{buildroot}%{_bindir}/encap.py
popd
install -d -m 777 %{buildroot}%{_localstatedir}/log/contrail

install -D -m 755 %{_distropkgdir}/venv-helper %{buildroot}%{_bindir}/venv-helper

%files
%defattr(-,root,root,-)
%{_venv_root}%{_pysitepkg}/discovery
%{_venv_root}%{_pysitepkg}/discovery-*
%{_venv_root}%{_pysitepkg}/kazoo
%{_venv_root}%{_pysitepkg}/kazoo-*
%{_venv_root}%{_pysitepkg}/ncclient
%{_venv_root}%{_pysitepkg}/ncclient-*
%{_venv_root}%{_pysitepkg}/pysandesh
%{_venv_root}%{_pysitepkg}/sandesh-*
%{_venv_root}%{_pysitepkg}/sandesh_common
%{_venv_root}%{_pysitepkg}/sandesh_common-*
%{_venv_root}%{_pysitepkg}/schema_transformer
%{_venv_root}%{_pysitepkg}/schema_transformer-*
%{_venv_root}%{_pysitepkg}/svc_monitor
%{_venv_root}%{_pysitepkg}/svc_monitor-*
%{_venv_root}%{_pysitepkg}/vnc_cfg_api_server
%{_venv_root}%{_pysitepkg}/vnc_cfg_api_server-*
/usr/share/doc/python-vnc_cfg_api_server
%{_sysconfdir}/contrail
%if 0%{?fedora} >= 17
/usr/lib/systemd/system/supervisor-config.service
%endif
%dir %attr(0777, root, root) %{_localstatedir}/log/contrail
%{_bindir}/ifmap_view.py
%{_bindir}/venv-helper
#%{_bindir}/encap.py
%if 0%{?rhel}
%{_initddir}
%endif

%post
if [ $1 -eq 1 -a -x /bin/systemctl ] ; then
   /bin/systemctl daemon-reload > /dev/null
fi

[ -f %{_sysconfdir}/contrail/api_server.conf ] || mv %{_sysconfdir}/contrail/api_server.conf.rpmsave  %{_sysconfdir}/contrail/api_server.conf
[ -f %{_sysconfdir}/contrail/schema_transformer.conf ] || mv %{_sysconfdir}/contrail/schema_transformer.conf.rpmsave  %{_sysconfdir}/contrail/schema_transformer.conf
[ -f %{_sysconfdir}/contrail/svc_monitor.conf ] || mv %{_sysconfdir}/contrail/svc_monitor.conf.rpmsave  %{_sysconfdir}/contrail/svc_monitor.conf
[ -f %{_sysconfdir}/contrail/discovery.conf ] || mv %{_sysconfdir}/contrail/discovery.conf.rpmsave  %{_sysconfdir}/contrail/discovery.conf

%changelog
* Mon Dec 17 2012 Pedro Marques <roque@build01> - config-1
- Initial build.

