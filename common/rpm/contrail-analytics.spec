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

Requires:	    redis 
Requires:	    redis-py
Requires:	    xmltodict
Requires:	    contrail-libs
Requires:           python-pycassa
Requires:           supervisor

Requires:           contrail-analytics-venv
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
scons -U src/discovery:discovery
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
tar zxf %{_build_dist}/discovery/dist/discovery-0.1dev.tar.gz 
pushd discovery-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

# install files
pushd %{_builddir}/..
install -p -m 755 build/debug/analytics/vizd    %{buildroot}%{_bindir}/vizd
install -p -m 755 build/debug/query_engine/qed  %{buildroot}%{_bindir}/qed
install -p -m 755 %{_distropkgdir}/contrail-analytics.rules %{buildroot}%{_supervisordir}/contrail-analytics.rules

#install wrapper scripts for supervisord
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail_collector_pre  %{buildroot}%{_bindir}/contrail_collector_pre
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail_qe_pre %{buildroot}%{_bindir}/contrail_qe_pre  

#install .ini files for supervisord
install -p -m 755 %{_distropkgdir}/supervisord_analytics.conf %{buildroot}%{_contrailetc}/supervisord_analytics.conf
install -p -m 755 %{_distropkgdir}/contrail-collector.ini %{buildroot}%{_supervisordir}/contrail-collector.ini
install -p -m 755 %{_distropkgdir}/contrail-opserver.ini %{buildroot}%{_supervisordir}/contrail-opserver.ini
install -p -m 755 %{_distropkgdir}/contrail-qe.ini %{buildroot}%{_supervisordir}/contrail-qe.ini
install -p -m 755 %{_distropkgdir}/redis-query.ini %{buildroot}%{_supervisordir}/redis-query.ini
install -p -m 755 %{_distropkgdir}/redis-sentinel.ini %{buildroot}%{_supervisordir}/redis-sentinel.ini
install -p -m 755 %{_distropkgdir}/redis-uve.ini %{buildroot}%{_supervisordir}/redis-uve.ini

#install .kill files for supervisord

%if 0%{?rhel}
install -p -m 755 %{_distropkgdir}/supervisor-analytics.initd          %{buildroot}%{_initddir}/supervisor-analytics
%endif
install -p -m 755 %{_distropkgdir}/contrail-collector.initd.supervisord          %{buildroot}%{_initddir}/contrail-collector
install -p -m 755 %{_distropkgdir}/contrail-qe.initd.supervisord          %{buildroot}%{_initddir}/contrail-qe
install -p -m 755 %{_distropkgdir}/contrail-opserver.initd.supervisord          %{buildroot}%{_initddir}/contrail-opserver
install -p -m 755 %{_distropkgdir}/redis-query.initd.supervisord          %{buildroot}%{_initddir}/redis-query
install -p -m 755 %{_distropkgdir}/redis-uve.initd.supervisord          %{buildroot}%{_initddir}/redis-uve
install -p -m 755 %{_distropkgdir}/redis-sentinel.initd.supervisord %{buildroot}%{_initddir}/redis-sentinel
#perl -pi -e 's/python2.7/python%{_pyver}/g' %{buildroot}%{_supervisordir}/contrail-opserver.ini

pushd %{_builddir}
install -D -m 644 src/analytics/ruleparser/tabledump.py %{buildroot}%{_contrailanalytics}/tabledump.py
install -D -m 755 src/analytics/ruleparser/tabledump %{buildroot}%{_contrailanalytics}/tabledump
install -D -m 755 src/analytics/ruleparser/contrail-dbutils %{buildroot}%{_venv_root}/bin/contrail-dbutils

pushd %{_builddir}/..
%define _helper   %{_distropkgdir}/analytics-venv-helper
install -p -m 755 %{_helper} %{buildroot}%{_bindir}/contrail-dbutils
popd
install -D -m 644 src/opserver/log.py %{buildroot}%{_contrailutils}/log.py
install -D -m 755 src/opserver/contrail-logs %{buildroot}%{_contrailutils}/contrail-logs
install -D -m 755 src/opserver/contrail-logs %{buildroot}%{_bindir}/contrail-logs
popd

# install etc files
install -p -m 755 %{_distropkgdir}/redis-query.conf %{buildroot}%{_contrailetc}/redis-query.conf
install -p -m 755 %{_distropkgdir}/redis-uve.conf %{buildroot}%{_contrailetc}/redis-uve.conf
install -p -m 755 %{_distropkgdir}/sentinel.conf %{buildroot}%{_contrailetc}/sentinel.conf

rm  -f %{buildroot}%{_venv_root}%{_pysitepkg}/gen_py/__init__.*
rm  -f %{buildroot}%{_venv_root}%{_pysitepkg}/bottle.py*

# install nodemgr
install -p -m 755 %{_distropkgdir}/contrail-nodemgr.py %{buildroot}%{_venv_root}/bin/contrail-nodemgr

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
if [ -f /etc/contrail/sentinel.conf ]; then
    SENTINEL_MONITOR_LINE=$(grep "sentinel monitor mymaster" /etc/contrail/sentinel.conf)
    SAVE_IFS=$IFS
    IFS=' ' read -a SENTINEL_MONITOR_LINE_TOKEN <<< "${SENTINEL_MONITOR_LINE}"
    # Change quorum to 1 if 0
    if [ ${SENTINEL_MONITOR_LINE_TOKEN[5]} == "0" ]; then
        SENTINEL_MONITOR_LINE_TOKEN[5]="1"
    fi
    # Change port to 6381 if 6379
    if [ ${SENTINEL_MONITOR_LINE_TOKEN[4]} == "6379" ]; then
        SENTINEL_MONITOR_LINE_TOKEN[4]="6381"
    fi
    # Change IP address to HOST_IP if 127.0.0.1
    if [ ${SENTINEL_MONITOR_LINE_TOKEN[3]} == "127.0.0.1" ]; then
        SENTINEL_MONITOR_LINE_TOKEN[3]=${HOST_IP}
    fi
    SENTINEL_MONITOR_MODIFY_LINE="${SENTINEL_MONITOR_LINE_TOKEN[*]}"
    sed -e "s/sentinel monitor mymaster.*/$SENTINEL_MONITOR_MODIFY_LINE/g" /etc/contrail/sentinel.conf > /etc/contrail/sentinel.conf.new
    mv /etc/contrail/sentinel.conf.new /etc/contrail/sentinel.conf
    IFS=$SAVE_IFS
fi


%preun
%postun

%files
%defattr(-, root, root)
%{_bindir}/vizd
%{_bindir}/qed
%{_bindir}/contrail-dbutils
%{_bindir}/contrail_collector_pre
%{_bindir}/contrail_qe_pre
%{_venv_root}
%{_supervisordir}/contrail-collector.ini
%{_supervisordir}/contrail-opserver.ini
%{_supervisordir}/contrail-qe.ini
%{_supervisordir}/redis-query.ini
%{_supervisordir}/redis-sentinel.ini
%{_supervisordir}/redis-uve.ini
%{_supervisordir}/contrail-analytics.rules
%if 0%{?rhel}
%{_initddir}/supervisor-analytics
%endif
%{_initddir}/contrail-collector
%{_initddir}/contrail-qe
%{_initddir}/contrail-opserver
%{_initddir}/redis-query
%{_initddir}/redis-uve
%{_initddir}/redis-sentinel
%{_contrailanalytics}/tabledump
%{_contrailanalytics}/tabledump.py
%{_contrailanalytics}/tabledump.pyc
%{_contrailanalytics}/tabledump.pyo
%{_contrailutils}/contrail-logs
%{_bindir}/contrail-logs
%{_contrailutils}/log.py
%{_contrailutils}/log.pyc
%{_contrailutils}/log.pyo
/usr/share/doc/python-vnc_opserver
%config(noreplace) %{_contrailetc}/redis-query.conf
%config(noreplace) %{_contrailetc}/redis-uve.conf
%config(noreplace) %{_contrailetc}/sentinel.conf
%{_contrailetc}/supervisord_analytics.conf
%if 0%{?fedora} >= 17
%{_servicedir}/supervisor-analytics.service
%endif
%{_venv_root}/bin/contrail-nodemgr

%changelog

