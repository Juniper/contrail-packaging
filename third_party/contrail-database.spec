%define         _thirdpartydir distro/third_party

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      99
%endif

%define cassandra_version 1.1.7

Summary: Apache Cassandra %{?_gitVer}
Name: contrail-database
Version:	    %{_verstr}
Release: %{_relstr}
License: Apache
Group: Contrail
URL: http://cassandra.apache.org
# http://mirror.metrocast.net/apache/cassandra/1.1.7/apache-cassandra-1.1.7-src.tar.gz
Source0: apache-cassandra-%{cassandra_version}-src.tar.gz
Source1: supervisord_contrail_database.initd
Source2: cassandra.in.sh
Source3: supervisord_contrail_database.conf
Source4: contrail-database.initd
#BuildRoot: %{_tmppath}/%{name}-%{cassandra_version}-%{release}-root

BuildArch: noarch
BuildRequires: ant

Requires: jre >= 1.6.0
Requires: jna
Requires: antlr3-java
#Requires: avro
#Requires: apache-commons-cli
Requires: apache-commons-codec
Requires: apache-commons-lang
#Requires: guava
#Requires: jackson
Requires: jline
#Requires: json_simple
Requires: log4j
Requires: slf4j
#Requires: snappy
#Requires: snakeyaml
Requires: supervisor

%description

%prep
#%setup -q -n apache-cassandra-%{cassandra_version}-src

%build
pushd %{_builddir}/..
pushd distro/third_party/apache-cassandra-1.1.7-src
#%{__python} setup.py install --root=%{buildroot} %{?_venvtr}
ant

%install
pushd %{_builddir}/..
pushd distro/third_party/apache-cassandra-1.1.7-src
install -D -m 755 bin/cassandra %{buildroot}%{_bindir}/cassandra
install -D -m 755 bin/cassandra-cli %{buildroot}%{_bindir}/cassandra-cli
install -D -m 755 bin/cqlsh %{buildroot}%{_bindir}/cqlsh
install -D -m 755 bin/json2sstable %{buildroot}%{_bindir}/json2sstable
install -D -m 755 bin/nodetool %{buildroot}%{_bindir}/nodetool
install -D -m 755 bin/sstable2json %{buildroot}%{_bindir}/sstable2json
install -D -m 755 bin/sstablekeys %{buildroot}%{_bindir}/sstablekeys
install -D -m 755 bin/sstableloader %{buildroot}%{_bindir}/sstableloadersstableloader
install -D -m 755 bin/sstablescrub %{buildroot}%{_bindir}/sstablescrub
install -D -m 755 bin/stop-server %{buildroot}%{_bindir}/stop-server
install -D -m 644 %{SOURCE2} %{buildroot}%{_datadir}/cassandra/cassandra.in.sh
install -D -m 644 interface/cassandra.thrift %{buildroot}%{_datadir}/cassandra/interface/cassandra.thrift
install -D -m 644 build/apache-cassandra-%{cassandra_version}-SNAPSHOT.jar %{buildroot}%{_datadir}/cassandra/apache-cassandra-%{cassandra_version}.jar
install -D -m 644 build/apache-cassandra-clientutil-%{cassandra_version}-SNAPSHOT.jar %{buildroot}%{_datadir}/cassandra/apache-cassandra-clientutil-%{cassandra_version}.jar
install -D -m 644 build/apache-cassandra-thrift-%{cassandra_version}-SNAPSHOT.jar %{buildroot}%{_datadir}/cassandra/apache-cassandra-thrift-%{cassandra_version}.jar
install -D -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/supervisord-contrail-database
install -D -m 755 %{SOURCE3} %{buildroot}%{_sysconfdir}/contrail/supervisord_contrail_database.conf
install -D -m 755 %{SOURCE4} %{buildroot}%{_sysconfdir}/rc.d/init.d/contrail-database
install -d -m 755 %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/avro-1.4.0-fixes.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/avro-1.4.0-sources-fixes.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/commons-cli-1.1.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/compress-lzf-0.8.4.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/concurrentlinkedhashmap-lru-1.3.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/cql-internal-only-1.4.0.zip %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/guava-r08.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/high-scale-lib-1.1.2.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/jackson-core-asl-1.9.2.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/jackson-mapper-asl-1.9.2.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/jamm-0.2.5.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/json-simple-1.1.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/libthrift-0.7.0.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/metrics-core-2.0.3.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/servlet-api-2.5-20081211.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/snakeyaml-1.6.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/snappy-java-1.0.4.1.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/snaptree-0.1.jar %{buildroot}%{_datadir}/cassandra/lib
install -D -m 644 lib/thrift-python-internal-only-0.7.0.zip %{buildroot}%{_datadir}/cassandra/lib
install -d -m 755 %{buildroot}%{_datadir}/cassandra/conf
install -D -m 644 conf/cassandra.yaml %{buildroot}%{_datadir}/cassandra/conf
install -D -m 644 conf/cassandra-env.sh %{buildroot}%{_datadir}/cassandra/conf
install -D -m 644 conf/log4j-server.properties %{buildroot}%{_datadir}/cassandra/conf
install -D -m 644 conf/log4j-tools.properties %{buildroot}%{_datadir}/cassandra/conf
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{_sysconfdir}/rc.d/init.d/contrail-database
%{_sysconfdir}/rc.d/init.d/supervisord-contrail-database
%{_sysconfdir}/contrail/supervisord_contrail_database.conf
%{_bindir}/cassandra
%{_bindir}/cassandra-cli
%{_bindir}/cqlsh
%{_bindir}/json2sstable
%{_bindir}/nodetool
%{_bindir}/sstable2json
%{_bindir}/sstablekeys
%{_bindir}/sstableloadersstableloader
%{_bindir}/sstablescrub
%{_bindir}/stop-server
%{_datadir}/cassandra/conf/*
%{_datadir}/cassandra/interface/cassandra.thrift
%{_datadir}/cassandra/cassandra.in.sh
%{_datadir}/cassandra/apache-cassandra-%{cassandra_version}.jar
%{_datadir}/cassandra/apache-cassandra-clientutil-%{cassandra_version}.jar
%{_datadir}/cassandra/apache-cassandra-thrift-%{cassandra_version}.jar
%{_datadir}/cassandra/lib/*

%config(noreplace) %{_datadir}/cassandra/conf/cassandra.yaml
%config(noreplace) %{_datadir}/cassandra/conf/cassandra-env.sh
%config(noreplace) %{_datadir}/cassandra/conf/log4j-server.properties
%config(noreplace) %{_datadir}/cassandra/conf/log4j-tools.properties

%pre
mkdir -p /var/log/cassandra
mkdir -p /var/lib/cassandra

%post

%preun
chkconfig --del contrail-database

%changelog
* Wed Dec 12 2012 Pedro Marques <roque@build02> - 
- Initial build.

