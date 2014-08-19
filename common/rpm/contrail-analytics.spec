# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailetc /etc/contrail
%define         _contrailanalytics /opt/contrail/analytics
%define         _contrailutils /opt/contrail/utils
%define         _supervisordir /etc/contrail/supervisord_analytics_files
%define         _distropkgdir tools/packaging/common/control_files

%if 0%{?fedora} >= 17
%define         _servicedir  /usr/lib/systemd/system
%endif
%define         _osVer       3.6.6-1.fc17.x86_64
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

Name:		    contrail-analytics
Version:	    %{_verstr}
Release:            %{_relstr}%{?dist}
Summary:	    Contrail Analytics %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	    redis >= 2.6.13-1
Requires:	    redis-py
Requires:	    xmltodict
Requires:	    contrail-libs >= %{_verstr}-%{_relstr}
Requires:           python-pycassa
Requires:           supervisor

Requires:           contrail-analytics-venv >= %{_verstr}-%{_relstr}
%define             _venv_root    /opt/contrail/analytics-venv
%define             _venvtr       --prefix=%{_venv_root}

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages
%description
Contrail Analytics package

BuildRequires:  make
BuildRequires:  gcc


%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}
# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
#gitrepo=ctrlplane
#grep $gitrepo .git/config &> /dev/null
#if [ $? -ne 0 ]; then
#    echo "please run rpmbuild from ctrlplane git tree"
#    exit -1
#fi


%build
scons -U src/analytics:vizd
if [ $? -ne 0 ] ; then
    echo " analytics build failed"
    exit -1
fi

scons -U src/query_engine:qed
if [ $? -ne 0 ] ; then
    echo " analytics query engine build failed"
    exit -1
fi

scons -U src/opserver:opserver
if [ $? -ne 0 ] ; then
    echo " opserver build failed"
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
scons -U src/discovery:client
if [ $? -ne 0 ] ; then
    echo " discovery build failed"
    exit -1
fi

%define _build_dist build/debug
%install

# Setup directories
##pushd $( cat  %{SOURCE0} )
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_contrailanalytics}
install -d -m 755 %{buildroot}%{_supervisordir}

%if 0%{?fedora} >= 17
install -d -m 755 %{buildroot}%{_servicedir}
%endif

%if 0%{?fedora} >= 17
pushd %{_builddir}/..
install -p -m 755 %{_distropkgdir}/supervisor-analytics.service          %{buildroot}%{_servicedir}/supervisor-analytics.service
popd
%endif
install -d -m 755 %{buildroot}%{_initddir}

# Install Opserver 
install -d -m 755 %{buildroot}%{_venv_root}
pushd %{_builddir}/..
tar zxvf %{_build_dist}/opserver/dist/opserver-0.1dev.tar.gz
pushd opserver-0.1dev
%{__python} setup.py install --root=%{buildroot} %{?_venvtr}
install -d -m 755 %{buildroot}/usr/share/doc/python-vnc_opserver
## ND - this doesnt exist - check
#cp -R opserver/doc/* %{buildroot}/usr/share/doc/python-vnc_opserver
popd
tar zxf %{_build_dist}/sandesh/common/dist/sandesh-common-0.1dev.tar.gz
pushd sandesh-common-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd
tar zxf %{_build_dist}/tools/sandesh/library/python/dist/sandesh-0.1dev.tar.gz
pushd sandesh-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd
tar zxf %{_build_dist}/discovery/client/dist/discoveryclient-0.1dev.tar.gz
pushd discoveryclient-0.1dev
%{__python}  setup.py install --root=%{buildroot} %{?_venvtr}
popd

# install files
pushd %{_builddir}/..
install -p -m 755 build/debug/analytics/vizd    %{buildroot}%{_bindir}/contrail-collector
install -p -m 755 build/debug/query_engine/qed  %{buildroot}%{_bindir}/contrail-query-engine
install -p -m 755 %{_distropkgdir}/contrail-analytics.rules %{buildroot}%{_supervisordir}/contrail-analytics.rules
install -D -m 644 controller/src/analytics/contrail-collector.conf %{buildroot}/%{_contrailetc}/contrail-collector.conf
install -D -m 644 controller/src/query_engine/contrail-query-engine.conf %{buildroot}/%{_contrailetc}/contrail-query-engine.conf

#install wrapper scripts for supervisord
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail_collector_pre  %{buildroot}%{_bindir}/contrail_collector_pre
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail_qe_pre %{buildroot}%{_bindir}/contrail_qe_pre  

#install .ini files for supervisord
install -p -m 755 %{_distropkgdir}/supervisord_analytics.conf %{buildroot}%{_contrailetc}/supervisord_analytics.conf
install -p -m 755 %{_distropkgdir}/contrail-collector.ini %{buildroot}%{_supervisordir}/contrail-collector.ini
install -p -m 755 %{_distropkgdir}/contrail-opserver-centos.ini %{buildroot}%{_supervisordir}/contrail-analytics-api.ini
install -p -m 755 %{_distropkgdir}/contrail-query-engine.ini %{buildroot}%{_supervisordir}/contrail-query-engine.ini

#install .kill files for supervisord

%if 0%{?rhel}
install -p -m 755 %{_distropkgdir}/supervisor-analytics.initd          %{buildroot}%{_initddir}/supervisor-analytics
%endif
install -p -m 755 %{_distropkgdir}/contrail-collector.initd.supervisord          %{buildroot}%{_initddir}/contrail-collector
install -p -m 755 %{_distropkgdir}/contrail-qe.initd.supervisord          %{buildroot}%{_initddir}/contrail-query-engine
install -p -m 755 %{_distropkgdir}/contrail-opserver.initd.supervisord          %{buildroot}%{_initddir}/contrail-analytics-api
#perl -pi -e 's/python2.7/python%{_pyver}/g' %{buildroot}%{_supervisordir}/contrail-analytics-api.ini

pushd %{_builddir}
install -D -m 755 src/analytics/ruleparser/contrail-dbutils %{buildroot}%{_venv_root}/bin/contrail-dbutils

pushd %{_builddir}/..
%define _helper   %{_distropkgdir}/analytics-venv-helper
install -p -m 755 %{_helper} %{buildroot}%{_bindir}/contrail-dbutils
popd
install -D -m 644 src/opserver/log.py %{buildroot}%{_contrailutils}/log.py
install -D -m 644 src/opserver/stats.py %{buildroot}%{_contrailutils}/stats.py
install -D -m 644 src/opserver/flow.py %{buildroot}%{_contrailutils}/flow.py
install -D -m 755 src/opserver/contrail-logs %{buildroot}%{_contrailutils}/contrail-logs
install -D -m 755 src/opserver/contrail-logs %{buildroot}%{_bindir}/contrail-logs
install -D -m 755 src/opserver/contrail-stats %{buildroot}%{_contrailutils}/contrail-stats
install -D -m 755 src/opserver/contrail-stats %{buildroot}%{_bindir}/contrail-stats
install -D -m 755 src/opserver/contrail-flows %{buildroot}%{_contrailutils}/contrail-flows
install -D -m 755 src/opserver/contrail-flows %{buildroot}%{_bindir}/contrail-flows
popd

rm  -f %{buildroot}%{_venv_root}%{_pysitepkg}/gen_py/__init__.*
rm  -f %{buildroot}%{_venv_root}%{_pysitepkg}/bottle.py*

# install nodemgr
install -p -m 755 %{_distropkgdir}/contrail-nodemgr.py %{buildroot}%{_venv_root}/bin/contrail-nodemgr

for f in $(find %{buildroot} -type f -exec grep -l '^#!%{__python}' {} \; ); do
    sed 's/^#!.*python/#!\/usr\/bin\/python/g' $f > ${f}.b
    mv ${f}.b ${f}
done

%post
%if 0%{?fedora} >= 17
chmod -R 777 /var/log/contrail
if [ $1 -eq 1 ] ; then
   /bin/systemctl daemon-reload > /dev/null
fi
%endif

if [ -f /etc/contrail/vizd_param ]; then
    grep -q 'ANALYTICS_DATA_TTL' /etc/contrail/vizd_param || echo 'ANALYTICS_DATA_TTL=168' >> /etc/contrail/vizd_param
    HOST_IP=$(sed -n -e 's/HOST_IP=//p' /etc/contrail/vizd_param)
    if [ -f /etc/contrail/opserver_param ]; then
        grep -q 'HOST_IP' /etc/contrail/opserver_param || echo 'HOST_IP='${HOST_IP} >> /etc/contrail/opserver_param
    fi
fi

%preun
%postun

%files
%defattr(-, root, root)
%{_bindir}/contrail-collector
%{_bindir}/contrail-query-engine
%{_bindir}/contrail-dbutils
%{_bindir}/contrail_collector_pre
%{_bindir}/contrail_qe_pre
%config(noreplace) %{_contrailetc}/contrail-collector.conf
%config(noreplace) %{_contrailetc}/contrail-query-engine.conf
%{_venv_root}
%config(noreplace) %{_supervisordir}/contrail-collector.ini
%config(noreplace) %{_supervisordir}/contrail-analytics-api.ini
%config(noreplace) %{_supervisordir}/contrail-query-engine.ini
%{_supervisordir}/contrail-analytics.rules
%if 0%{?rhel}
%{_initddir}/supervisor-analytics
%endif
%{_initddir}/contrail-collector
%{_initddir}/contrail-query-engine
%{_initddir}/contrail-analytics-api
%{_contrailutils}/contrail-logs
%{_bindir}/contrail-logs
%{_contrailutils}/log.py
%{_contrailutils}/log.pyc
%{_contrailutils}/log.pyo
%{_contrailutils}/contrail-flows
%{_bindir}/contrail-flows
%{_contrailutils}/flow.py
%{_contrailutils}/flow.pyc
%{_contrailutils}/flow.pyo
%{_contrailutils}/contrail-stats
%{_bindir}/contrail-stats
%{_contrailutils}/stats.py
%{_contrailutils}/stats.pyc
%{_contrailutils}/stats.pyo
/usr/share/doc/python-vnc_opserver
%config(noreplace) %{_contrailetc}/supervisord_analytics.conf
%if 0%{?fedora} >= 17
%{_servicedir}/supervisor-analytics.service
%endif

%changelog

