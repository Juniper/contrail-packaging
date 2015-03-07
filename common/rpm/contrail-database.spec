%define  _distropkgdir tools/packaging/common/control_files
%define  _supervisordir /etc/contrail/supervisord_database_files
%define  _venv_root    /opt/contrail/database-venv
%define  _venvtr       --prefix=%{_venv_root}
%define  _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define  _pysitepkg    /lib/python%{_pyver}/site-packages

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
Release:            %{_relstr}%{?dist}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      99
%endif

Summary: Contrail Database %{?_gitVer}
Name: contrail-database
Version:            %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: cassandra12
Requires: supervisor
Requires: java-1.7.0-openjdk
Requires: kafka

Source1: supervisord_contrail_database.initd
Source2: supervisord_database.conf
Source3: contrail-database.initd
Source4: kafka.initd

%description
Contrail Database package

BuildRequires:  make
BuildRequires:  gcc
%prep

%build
scons -U src/analytics/database:database
if [ $? -ne 0 ] ; then
    echo " database build failed"
    exit -1
fi

scons -U src/sandesh/common
if [ $? -ne 0 ] ; then
    echo " sandesh common build failed"
    exit -1
fi

pushd %{_builddir}/../tools/
scons -U sandesh/library/python:pysandesh
popd
if [ $? -ne 0 ] ; then
    echo " sandesh python build failed"
    exit -1
fi
scons -U src/discovery:discovery
if [ $? -ne 0 ] ; then
    echo " discovery build failed"
    exit -1
fi

scons -U src/discovery:client
if [ $? -ne 0 ] ; then
    echo " discovery build failed"
    exit -1
fi

%define             _build_dist build/debug
%install

#install database
install -d -m 755 %{buildroot}%{_venv_root}
pushd %{_builddir}/..
tar zxvf %{_build_dist}/analytics/database/dist/database-0.1dev.tar.gz
pushd database-0.1dev
%{__python} setup.py install --root=%{buildroot} %{?_venvtr}
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

tar zxf %{_build_dist}/discovery/client/dist/discoveryclient-0.1dev.tar.gz
pushd discoveryclient-0.1dev
%{__python}  setup.py install --root=%{buildroot} %{?_venvtr}
popd

install -d -m 755 %{buildroot}%{_supervisordir}
install -d -m 755 %{buildroot}%{_initddir}
pushd %{_builddir}/..
install -D -m 755 %{_distropkgdir}/contrail-nodemgr-database.ini %{buildroot}%{_supervisordir}/contrail-nodemgr-database.ini
install -D -m 755 %{_distropkgdir}/contrail-database.rules %{buildroot}%{_supervisordir}/contrail-database.rules
install -D -m 755 %{_distropkgdir}/contrail-database-nodemgr.conf %{buildroot}/etc/contrail/contrail-database-nodemgr.conf
popd

%if 0%{?rhel}
install -D -m 755 %{_distropkgdir}/supervisord_contrail_database.initd          %{buildroot}%{_initddir}/supervisor-database
%endif

install -D -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/supervisor-database
install -D -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/contrail/supervisord_database.conf
install -D -m 755 %{SOURCE3} %{buildroot}%{_sysconfdir}/rc.d/init.d/contrail-database
install -D -m 755 %{SOURCE4} %{buildroot}%{_sysconfdir}/rc.d/init.d/kafka


pushd %{buildroot}

for f in $(find . -type f -exec grep -nH "^#\!.*BUILD.*python" {} \; | grep -v 'Binary file' | cut -d: -f1); do
    sed "s/#\!.*python/#!\/usr\/bin\/python/g" $f > ${f}.b
    mv ${f}.b $f
    echo "changed $f .... Done!"
done
popd

%post
# this is upgrade from 1.02 release to newer i.e cassandra 1.1.7 to 1.2.11
if [ -f /usr/share/cassandra/conf/cassandra.yaml.rpmsave ]; then
    CASSANDRA_CONF_OLD=/usr/share/cassandra/conf/cassandra.yaml.rpmsave
    CASSANDRA_CONF=/etc/cassandra/conf/cassandra.yaml

    CLUSTER_NAME=$(grep "^cluster_name:" ${CASSANDRA_CONF_OLD})
    sed -e "s/^cluster_name:.*/${CLUSTER_NAME}/g" ${CASSANDRA_CONF} > ${CASSANDRA_CONF}.save
    mv ${CASSANDRA_CONF}.save ${CASSANDRA_CONF}

    PARTITIONER=$(grep "^partitioner:" ${CASSANDRA_CONF_OLD})
    sed -e "s/^partitioner:.*/${PARTITIONER}/g" ${CASSANDRA_CONF} > ${CASSANDRA_CONF}.save
    mv ${CASSANDRA_CONF}.save ${CASSANDRA_CONF}

    DATA_DIR_OLD=$(grep -A1 "^data_file_directories:" ${CASSANDRA_CONF_OLD} | grep -v data_file_directories)
    DATA_DIR_NEW=$(grep -A1 "^data_file_directories:" ${CASSANDRA_CONF} | grep -v data_file_directories)
    sed -e "s@${DATA_DIR_NEW}@${DATA_DIR_OLD}@g" ${CASSANDRA_CONF} > ${CASSANDRA_CONF}.save
    mv ${CASSANDRA_CONF}.save ${CASSANDRA_CONF}

    COMMITLOG_DIR=$(grep "^commitlog_directory:" ${CASSANDRA_CONF_OLD})
    sed -e "s@^commitlog_directory:.*@${COMMITLOG_DIR}@g" ${CASSANDRA_CONF} > ${CASSANDRA_CONF}.save
    mv ${CASSANDRA_CONF}.save ${CASSANDRA_CONF}

    SAVEDCACHES_DIR=$(grep "^saved_caches_directory:" ${CASSANDRA_CONF_OLD})
    sed -e "s@^saved_caches_directory:.*@${SAVEDCACHES_DIR}@g" ${CASSANDRA_CONF} > ${CASSANDRA_CONF}.save
    mv ${CASSANDRA_CONF}.save ${CASSANDRA_CONF}

    SEEDS=$(grep "          - seeds:" ${CASSANDRA_CONF_OLD})
    sed -e "s/^          - seeds:.*/${SEEDS}/g" ${CASSANDRA_CONF} > ${CASSANDRA_CONF}.save
    mv ${CASSANDRA_CONF}.save ${CASSANDRA_CONF}

    LISTEN_ADDRESS=$(grep "^listen_address:" ${CASSANDRA_CONF_OLD})
    sed -e "s/^listen_address:.*/${LISTEN_ADDRESS}/g" ${CASSANDRA_CONF} > ${CASSANDRA_CONF}.save
    mv ${CASSANDRA_CONF}.save ${CASSANDRA_CONF}

    RPC_ADDRESS=$(grep "^rpc_address:" ${CASSANDRA_CONF_OLD})
    sed -e "s/^rpc_address:.*/${RPC_ADDRESS}/g" ${CASSANDRA_CONF} > ${CASSANDRA_CONF}.save
    mv ${CASSANDRA_CONF}.save ${CASSANDRA_CONF}

    rm -rf ${CASSANDRA_CONF_OLD}

    mv -f /usr/share/cassandra/conf/cassandra-env.sh.rpmsave /etc/cassandra/conf/cassandra-env.sh
fi

%files
%defattr(-,root,root,-)
%{_venv_root}
%{_supervisordir}/contrail-database.rules
%{_supervisordir}/contrail-nodemgr-database.ini
/etc/contrail/contrail-database-nodemgr.conf
%if 0%{?rhel}
%{_initddir}/supervisor-database
%endif
%doc
%{_sysconfdir}/rc.d/init.d/contrail-database
%{_sysconfdir}/rc.d/init.d/kafka
%{_sysconfdir}/rc.d/init.d/supervisor-database
%config(noreplace) %{_sysconfdir}/contrail/supervisord_database.conf

%changelog
* Wed Dec 12 2012 Pedro Marques <roque@build02> - 
- Initial build.

