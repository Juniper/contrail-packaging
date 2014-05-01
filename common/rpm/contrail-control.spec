
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
#Remove build of pysandesh,sandesh_common,discovery
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
#Removed installation of files that are now done by nodemgr

#install files
install -d -m 755 %{buildroot}%{_bindir}
install -p -m 755 build/debug/control-node/control-node %{buildroot}%{_bindir}/control-node
install -D -m 644 controller/src/control-node/control-node.conf %{buildroot}/%{_contrailetc}/control-node.conf
#Install of dns done by nodemgr

%define _build_dist %{_builddir}/../build/debug
#This definiton to install control_node pkg in venv as well
%define __python_venv %{buildroot}/../../BUILD/python2.7/bin/python

mkdir -p build/python_dist
pushd build/python_dist

tar zxf %{_build_dist}/control-node/dist/Control-Node-0.1dev.tar.gz
pushd Control-Node-0.1dev
#Need to install in venv as well
%{__python} setup.py install --root=%{buildroot}
%{__python_venv} setup.py install --root=%{buildroot}  %{?_venvtr}
install -d -m 755 %{buildroot}/usr/share/doc/python-Control-Node
if [ -d doc ]; then
   cp -R doc/* %{buildroot}/usr/share/doc/python-Control-Node
fi
popd

%files
%defattr(-,root,root,-)
%{_bindir}/control-node
%{_venv_root}
/usr/share/doc/
%{python_sitelib}/Control_Node*
%{python_sitelib}/control_node*
%config(noreplace) %{_contrailetc}/control-node.conf

%post
(umask 007; /bin/echo "HOSTNAME=$(hostname)" >> /etc/contrail/control_param)
if [ -x /bin/systemctl ]; then
   /bin/systemctl --system daemon-reload
fi

%changelog
* Tue Dec 18 2012 Ted <ted@contrailsystems.com> - 1
- Initial package 

