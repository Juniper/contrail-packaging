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

%if 0%{?_osVer:1}
%define         _osver   %(echo %{_osVer} | sed 's,[-|.],,g')
%else
%define         _osver   %(PYTHONPATH=%{PYTHONPATH}:%{_builddir}/../tools/packaging/tools/scripts/ python -c "import package_utils; print package_utils.get_platform()")
%endif

%define         _contrail_smgr /server_manager
%define         _contrail_smgr_src          %{_builddir}/../tools/contrail-server-manager/src/
%define         _third_party        %{_builddir}/../../../third_party/

%define         _contrailopt /opt/contrail/
%define         _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define         _pysitepkg    /usr/lib/python%{_pyver}/site-packages

Name:            contrail-server-manager-monitoring
Version:            %{_verstr}
Release:          %{_relstr}%{?dist}
Summary:          contrail-server-manager-monitoring %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

#Requires:        python-contrail >= %{_verstr}-%{_relstr}
Requires:         python-contrail
Requires:         python-gevent

BuildRequires:    make
BuildRequires:    gcc

%description
Contrail Server-Manager Monitoring package

%prep
gitrepo=contrail-controller
grep $gitrepo %{_builddir}/.git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi

%build

if [ $? -ne 0 ] ; then
    echo "build failed"
    exit -1
fi

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}
scons -U install_contrail_sm_monitoring --root=%{buildroot}
install -d -m 755 %{buildroot}%{_contrailopt}%{_contrail_smgr}
install -p -m 755 %{_contrail_smgr_src}server_mgr_ipmi_monitoring.py %{buildroot}%{_contrailopt}%{_contrail_smgr}
install -p -m 755 %{_contrail_smgr_src}sm-monitoring-config.ini %{buildroot}%{_contrailopt}%{_contrail_smgr}

%files
%defattr(-,root,root,-)
%{python_sitelib}/contrail_sm_monitoring*
%{_contrailopt}%{_contrail_smgr}/*

%post
if [ -x /bin/systemctl ]; then
   /bin/systemctl --system daemon-reload
fi
HOST_IP_LIST=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp'`
HOST_IP=`echo $HOST_IP_LIST | cut -d' ' -f1`
if [ -f /opt/contrail/contrail_server_manager/IP.txt ];
then
   HOST_IP=$(cat /opt/contrail/contrail_server_manager/IP.txt)
fi
echo $HOST_IP
sed -i "s/127.0.0.1/$HOST_IP/g" /opt/contrail/server_manager/sm-monitoring-config.ini
cat /opt/contrail/server_manager/sm-monitoring-config.ini >> /opt/contrail/server_manager/sm-config.ini
%changelog
