
%define         _contrailetc /etc/contrail
%define         _contrailcontrol /opt/contrail/control-node
%define         _supervisordir /etc/contrail/supervisord_control_files
%define         _distropkgdir tools/packaging/common/control_files

%if 0%{?fedora} >= 17
%define         _servicedir  /usr/lib/systemd/system
%endif

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

Name:             contrail-control
Version:	    %{_verstr}
Release:	  %{_relstr}%{?dist}
Summary:          Contrail Control %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	  contrail-libs
Requires:         supervisor
Requires:         contrail-control-venv
Requires:         xmltodict
%define _venv_root    /opt/contrail/control-venv
%define _venvtr       --prefix=%{_venv_root}

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages

BuildRequires:    make
BuildRequires:    gcc

%description
Contrail Control package

%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}

# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=contrail-controller
grep $gitrepo %{_builddir}/.git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi


%build
scons -U src/sandesh/common
pushd %{_builddir}/../tools/
scons -U sandesh/library/python:pysandesh
popd
scons -U src/discovery
scons -U src/control-node
if [ $? -ne 0 ] ; then
    echo "build failed"
    exit -1
fi

%install

# Setup directories
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_contrailcontrol}
install -d -m 755 %{buildroot}%{_supervisordir}
install -d -m 755 %{buildroot}%{_venv_root}
install -d -m 755 %{buildroot}%{_venv_root}/bin

pushd %{_builddir}/..

%if 0%{?fedora} >= 17
install -d -m 755 %{buildroot}%{_servicedir}
%endif
%if 0%{?fedora} >= 17
install -D -m 644 %{_distropkgdir}/supervisor-control.service %{buildroot}%{_servicedir}/supervisor-control.service
%endif
install -D -m 755 %{_distropkgdir}/supervisor-control.initd %{buildroot}%{_initddir}/supervisor-control
install -D -m 755 %{_distropkgdir}/contrail-control.initd.supervisord %{buildroot}%{_initddir}/contrail-control
%if 0%{?rhel}
install -D -m 755 %{_distropkgdir}/supervisor-control.initd %{buildroot}%{_initddir}/supervisor-control
install -D -m 755 %{_distropkgdir}/contrail-control.initd.supervisord %{buildroot}%{_initddir}/contrail-control
%endif


#install files
install -d -m 755 %{buildroot}%{_bindir}
install -p -m 755 build/debug/control-node/control-node %{buildroot}%{_bindir}/control-node
install -D -m 644 controller/src/control-node/control-node.conf %{buildroot}/%{_contrailetc}/control-node.conf

#install .ini files for supervisord
install -p -m 755 %{_distropkgdir}/supervisord_control.conf %{buildroot}%{_contrailetc}/supervisord_control.conf
install -p -m 755 %{_distropkgdir}/contrail-control.ini %{buildroot}%{_supervisordir}/contrail-control.ini
 
install -D -m 644 %{_distropkgdir}/control_param %{buildroot}/etc/contrail/control_param
install -p -m 755 %{_distropkgdir}/contrail-control.rules %{buildroot}%{_supervisordir}/contrail-control.rules
install -p -m 755 %{_distropkgdir}/contrail-nodemgr.py %{buildroot}%{_venv_root}/bin/contrail-nodemgr

# install pysandesh files
%define _build_dist %{_builddir}/../build/debug
install -d -m 755 %{buildroot}%{_venv_root}

mkdir -p build/python_dist
pushd build/python_dist

tar zxf %{_build_dist}/control-node/dist/Control-Node-0.1dev.tar.gz
pushd Control-Node-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
install -d -m 755 %{buildroot}/usr/share/doc/python-Control-Node
if [ -d doc ]; then
   cp -R doc/* %{buildroot}/usr/share/doc/python-Control-Node
fi
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

%files
%defattr(-,root,root,-)
%{_bindir}/control-node
%{_supervisordir}
%{_contrailetc}/supervisord_control.conf
%{_venv_root}
/usr/share/doc/
%if 0%{?fedora} >= 17
/usr/lib/systemd/system
%{_initddir}/supervisor-control
%{_initddir}/contrail-control
%endif
%if 0%{?rhel}
%{_initddir}/supervisor-control
%{_initddir}/contrail-control
%endif
%if 0%{?fedora} >= 17
%{_servicedir}/supervisor-control.service
%endif

%config(noreplace) /etc/contrail/control_param
%config(noreplace) %{_contrailetc}/control-node.conf
%{_venv_root}/bin/contrail-nodemgr

%post
(umask 007; /bin/echo "HOSTNAME=$(hostname)" >> /etc/contrail/control_param)
if [ -x /bin/systemctl ]; then
   /bin/systemctl --system daemon-reload
fi

%changelog
* Tue Dec 18 2012 Ted <ted@contrailsystems.com> - 1
- Initial package 
