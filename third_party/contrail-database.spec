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

Source1: supervisord_contrail_database.initd
Source2: supervisord_contrail_database.conf
Source3: contrail-database.initd

%description
Contrail Database package

%install
install -D -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/supervisord-contrail-database
install -D -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/contrail/supervisord_contrail_database.conf
install -D -m 755 %{SOURCE3} %{buildroot}%{_sysconfdir}/rc.d/init.d/contrail-database

%post
# this is upgrade from 1.02 release to newer i.e cassandra 1.1.7 to 1.2.11
if [ -f /usr/share/cassandra/conf/cassandra.yaml.rpmsave ]; then
    CASSANDRA_CONF_OLD=/etc/cassandra/conf/cassandra.yaml.rpmsave
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

    rm -rf {CASSANDRA_CONF_OLD}

    mv -f /usr/share/cassandra/conf/cassandra-env.sh.rpmsave /etc/cassandra/conf/cassandra-env.sh
fi

%files
%defattr(-,root,root,-)
%doc
%{_sysconfdir}/rc.d/init.d/contrail-database
%{_sysconfdir}/rc.d/init.d/supervisord-contrail-database
%{_sysconfdir}/contrail/supervisord_contrail_database.conf

%changelog
* Wed Dec 12 2012 Pedro Marques <roque@build02> - 
- Initial build.

