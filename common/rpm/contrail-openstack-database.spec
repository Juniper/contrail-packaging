%define  _nodemgr_config controller/src/nodemgr/database_nodemgr

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
Release:	    %{_relstr}%{?dist}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif

Summary: Contrail Openstack Database %{?_gitVer}
Name: contrail-openstack-database
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-database-common >= %{_verstr}-%{_relstr}
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}
Requires: contrail-nodemgr >= %{_verstr}-%{_relstr}
Requires: supervisor

%description
Contrail Package Requirements for Contrail Database

%install
pushd %{_builddir}/..
install -D -m 755 %{_nodemgr_config}/contrail-database-nodemgr.conf %{buildroot}/etc/contrail/contrail-database-nodemgr.conf
install -D -m 755 %{_nodemgr_config}/contrail-database-nodemgr.initd.supervisord %{buildroot}/etc/init.d/contrail-database-nodemgr
popd

%files
%config(noreplace) /etc/contrail/contrail-database-nodemgr.conf
/etc/init.d/contrail-database-nodemgr

%pre
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContrail daemon" contrail

%post
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/
chown contrail:contrail /usr/share/contrail/contrail-cassandra-status.py
chown -h contrail:contrail /usr/bin/contrail-cassandra-status

if [ -f /var/log/cassandra/status.log]; then
    mv /var/log/cassandra/status-up /var/log/contrail/cassandra-status-up
    chown contrail:contrail /var/log/contrail/cassandra-status-up
    mv /var/log/cassandra/status.log /var/log/contrail/cassandra-status.log
    chown contrail:contrail /var/log/contrail/cassandra-status.log
fi

# Run nodemgr as contrail user
if [ -f /var/log/contrail/contrail-analytics-nodemgr-stdout.log ]; then
    chown contrail:contrail /var/log/contrail/process_statecontrail-database.json
    chown contrail:contrail /var/log/contrail/contrail-database-nodemgr-stderr.log
    chown contrail:contrail /var/log/contrail/contrail-database-nodemgr-stdout.log
fi

%changelog
* Fri Jul  15 2016 <ijohnson@juniper.net>
* Moving cassandra/zookeper to contrail database common package

* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.
