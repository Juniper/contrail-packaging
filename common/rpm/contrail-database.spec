%define  _distropkgdir tools/packaging/common/control_files
%define  _supervisordir /etc/contrail/supervisord_database_files
%define  _venv_root    /opt/contrail/database-venv
%define  _venvtr       --prefix=%{_venv_root}
%define  _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define  _pysitepkg    /lib/python%{_pyver}/site-packages
%define  _nodemgr_config controller/src/nodemgr/database_nodemgr

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

%if 0%{?el6}
Requires: cassandra12
%else
Requires: cassandra21
%endif
Requires: supervisor
Requires: java-1.7.0-openjdk
Requires: kafka >= 2.11

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
install -D -m 755 %{_nodemgr_config}/contrail-database-nodemgr.ini %{buildroot}%{_supervisordir}/contrail-database-nodemgr.ini
install -D -m 755 %{_distropkgdir}/contrail-database.rules %{buildroot}%{_supervisordir}/contrail-database.rules
install -D -m 755 %{_nodemgr_config}/contrail-database-nodemgr.conf %{buildroot}/etc/contrail/contrail-database-nodemgr.conf
popd

%if 0%{?rhel}
install -D -m 755 %{_distropkgdir}/supervisord_contrail_database.initd          %{buildroot}%{_initddir}/supervisor-database
%endif

install -D -m 755 %{SOURCE1} %{buildroot}%{_initddir}/supervisor-database
install -D -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/contrail/supervisord_database.conf
install -D -m 755 %{SOURCE3} %{buildroot}%{_initddir}/contrail-database
install -D -m 755 %{SOURCE4} %{buildroot}%{_initddir}/kafka


pushd %{buildroot}

for f in $(find . -type f -exec grep -nH "^#\!.*BUILD.*python" {} \; | grep -v 'Binary file' | cut -d: -f1); do
    sed "s/#\!.*python/#!\/usr\/bin\/python/g" $f > ${f}.b
    mv ${f}.b $f
    echo "changed $f .... Done!"
done
popd

%post
if [ "$1" = "1" ]; then
  service cassandra stop
  sleep 3
  ps auxw | grep -Eq "Dcassandra-pidfile=.*cassandra\.pid" 2>/dev/null
  if [ $? -eq 0 ] ; then
      kill `ps auxw | grep -E "Dcassandra-pidfile=.*cassandra\.pid" | grep -v grep | awk '{print $2}'` > /dev/null 2>&1
  fi
  rm -rf /var/lib/cassandra
fi
if [ "$1" = "2" ]; then
  PIDFILE=/var/run/cassandra/cassandra.pid
  # Create the /var/run/cassandra if it does not exist
  [ -e `dirname "$PIDFILE"` ] || \
        install -d -ocassandra -gcassandra -m755 `dirname $PIDFILE`
  # Write pid info to it
  ps auxw | grep -Eq "Dcassandra-pidfile=.*cassandra\.pid" 2>/dev/null
  if [ $? -eq 0 ] ; then
          echo `ps auxw | grep -E "Dcassandra-pidfile=.*cassandra\.pid" | grep -v grep | awk '{print $2}'` > /var/run/cassandra/cassandra.pid
          chown cassandra:cassandra /var/run/cassandra/cassandra.pid
  fi
fi

chkconfig cassandra off
chkconfig contrail-database on

%files
%defattr(-,root,root,-)
%{_venv_root}
%{_supervisordir}/contrail-database.rules
%config(noreplace) %{_supervisordir}/contrail-database-nodemgr.ini
%config(noreplace) /etc/contrail/contrail-database-nodemgr.conf
%if 0%{?rhel}
%{_initddir}/supervisor-database
%endif
%doc
%{_initddir}/contrail-database
%{_initddir}/kafka
%{_initddir}/supervisor-database
%config(noreplace) %{_sysconfdir}/contrail/supervisord_database.conf

%changelog
* Wed Dec 12 2012 Pedro Marques <roque@build02> - 
- Initial build.

