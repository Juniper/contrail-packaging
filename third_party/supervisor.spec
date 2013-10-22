%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}

%define         _distropkgdir tools/packaging/common/control_files
%define         _distrothirdpartydir distro/third_party

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%(grep -c Xen /etc/redhat-release)
%define		dist	.xen
%endif

Summary: supervisor %{?_gitVer}
Name: supervisor 
Version: 0.1
Release: %{_relstr}%{?dist}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires: python
Requires: python-gevent
Requires: python-requests

Requires:           contrail-analytics-venv
Requires:           contrail-api-venv
Requires:           contrail-vrouter-venv
Requires:           contrail-control-venv
%define             _venv_root    /opt/contrail/analytics-venv
%define             _venvtr       --prefix=%{_venv_root}
%define             _venv_root_api    /opt/contrail/api-venv
%define             _venvtr_api       --prefix=%{_venv_root_api}
%define             _venv_root_control    /opt/contrail/control-venv
%define             _venvtr_control       --prefix=%{_venv_root_control}
%define             _venv_root_vrouter    /opt/contrail/vrouter-venv
%define             _venvtr_vrouter       --prefix=%{_venv_root_vrouter}
Autoreq:0

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages
%description
%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}

# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=contrail-controller
grep $gitrepo .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "please run rpmbuild from ctrlplane git tree"
    exit -1
fi

%if 0%{?fedora} >= 17
%define         _servicedir  /usr/lib/systemd/system
%endif

%build
%install
%define         _contrailetc /etc/contrail
%define         _supervisordfiles /etc/contrail/supervisord_files

install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_supervisordfiles}
install -d -m 755 %{buildroot}%{_bindir}

# install in analytics venv
install -d -m 755 %{buildroot}%{_venv_root}
install -d -m 755 %{buildroot}%{_venv_root}/archive

pushd %{_builddir}/../%{_distrothirdpartydir}/elementtree-1.2.6-20050316
#pushd %{_distrothirdpartydir}/elementtree-1.2.6-20050316
%{__python} setup.py install --root=%{buildroot} %{?_venvtr}
popd

#pushd %{_builddir}/..
#pushd %{_distrothirdpartydir}/meld3-0.6.10
pushd %{_builddir}/../%{_distrothirdpartydir}/meld3-0.6.10
%{__python} setup.py install --root=%{buildroot} %{?_venvtr}
popd

pushd %{_builddir}/..
# save these files to restore
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save
pushd %{_distrothirdpartydir}/supervisor-3.0b2
%{__python} setup.py install --root=%{buildroot} %{?_venvtr}
%{__python} setup.py sdist
cp dist/* %{buildroot}%{_venv_root}/archive
popd
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO
install -p -m 755 %{_distropkgdir}/contrail-nodemgr.py %{buildroot}%{_venv_root}/bin/contrail-nodemgr
# done install in analytics venv

# install in api venv
install -d -m 755 %{buildroot}%{_venv_root_api}
install -d -m 755 %{buildroot}%{_venv_root_api}/archive

pushd %{_builddir}/../%{_distrothirdpartydir}/elementtree-1.2.6-20050316
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_api}
popd

pushd %{_builddir}/../%{_distrothirdpartydir}/meld3-0.6.10
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_api}
popd

# save these files to restore
pushd %{_builddir}/..
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save
#pushd %{_builddir}..
pushd %{_distrothirdpartydir}/supervisor-3.0b2
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_api}
%{__python} setup.py sdist
cp dist/* %{buildroot}%{_venv_root_api}/archive
popd
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO
install -p -m 755 %{_distropkgdir}/contrail-nodemgr.py %{buildroot}%{_venv_root_api}/bin/contrail-nodemgr
#done install in api venv

# install in vrouter venv
install -d -m 755 %{buildroot}%{_venv_root_vrouter}
install -d -m 755 %{buildroot}%{_venv_root_vrouter}/archive

pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/elementtree-1.2.6-20050316
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_vrouter}
popd

pushd %{_distrothirdpartydir}/meld3-0.6.10
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_vrouter}
popd

# save these files to restore
pushd %{_builddir}/..
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save
pushd %{_distrothirdpartydir}/supervisor-3.0b2
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_vrouter}
%{__python} setup.py sdist
cp dist/* %{buildroot}%{_venv_root_vrouter}/archive
popd
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO
install -p -m 755 %{_distropkgdir}/contrail-nodemgr.py %{buildroot}%{_venv_root_vrouter}/bin/contrail-nodemgr
#done install in vrouter venv

# install in control venv
install -d -m 755 %{buildroot}%{_venv_root_control}
install -d -m 755 %{buildroot}%{_venv_root_control}/archive

pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/elementtree-1.2.6-20050316
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_control}
popd

pushd %{_distrothirdpartydir}/meld3-0.6.10
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_control}
popd

# save these files to restore
pushd %{_builddir}/..
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save
pushd %{_distrothirdpartydir}/supervisor-3.0b2
%{__python} setup.py install --root=%{buildroot} %{?_venvtr_control}
%{__python} setup.py sdist
cp dist/* %{buildroot}%{_venv_root_control}/archive
popd
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO
install -p -m 755 %{_distropkgdir}/contrail-nodemgr.py %{buildroot}%{_venv_root_control}/bin/contrail-nodemgr
#done install in control venv


install -p -m 755 %{_distropkgdir}/supervisor_killall %{buildroot}%{_bindir}/supervisor_killall

%define _helper   %{_distropkgdir}/analytics-venv-helper
install -p -m 755 %{_helper} %{buildroot}%{_bindir}/echo_supervisord_conf
install -p -m 755 %{_helper} %{buildroot}%{_bindir}/pidproxy
install -p -m 755 %{_helper} %{buildroot}%{_bindir}/supervisorctl
install -p -m 755 %{_helper} %{buildroot}%{_bindir}/supervisord
install -p -m 755 %{_helper} %{buildroot}%{_bindir}/contrail-nodemgr

%clean
%files
%defattr(-,root,root,-)
/usr/bin/echo_supervisord_conf
/usr/bin/pidproxy
/usr/bin/supervisorctl
/usr/bin/supervisord
/usr/bin/supervisor_killall
/usr/bin/contrail-nodemgr
%{_venv_root}%{_pysitepkg}/supervisor
%{_venv_root}%{_pysitepkg}/supervisor-*
%{_venv_root}%{_pysitepkg}/meld3
%{_venv_root}%{_pysitepkg}/meld3-*
%{_venv_root}%{_pysitepkg}/elementtree
%{_venv_root}%{_pysitepkg}/elementtree-*
%{_venv_root}/bin/echo_supervisord_conf
%{_venv_root}/bin/pidproxy
%{_venv_root}/bin/supervisorctl
%{_venv_root}/bin/supervisord
%{_venv_root}/bin/contrail-nodemgr
%{_venv_root}/archive/supervisor-3.0b2.tar.gz
%{_venv_root_api}%{_pysitepkg}/supervisor
%{_venv_root_api}%{_pysitepkg}/supervisor-*
%{_venv_root_api}%{_pysitepkg}/meld3
%{_venv_root_api}%{_pysitepkg}/meld3-*
%{_venv_root_api}%{_pysitepkg}/elementtree
%{_venv_root_api}%{_pysitepkg}/elementtree-*
%{_venv_root_api}/bin/echo_supervisord_conf
%{_venv_root_api}/bin/pidproxy
%{_venv_root_api}/bin/supervisorctl
%{_venv_root_api}/bin/supervisord
%{_venv_root_api}/bin/contrail-nodemgr
%{_venv_root_api}/archive/supervisor-3.0b2.tar.gz
%{_venv_root_control}%{_pysitepkg}/supervisor
%{_venv_root_control}%{_pysitepkg}/supervisor-*
%{_venv_root_control}%{_pysitepkg}/meld3
%{_venv_root_control}%{_pysitepkg}/meld3-*
%{_venv_root_control}%{_pysitepkg}/elementtree
%{_venv_root_control}%{_pysitepkg}/elementtree-*
%{_venv_root_control}/bin/echo_supervisord_conf
%{_venv_root_control}/bin/pidproxy
%{_venv_root_control}/bin/supervisorctl
%{_venv_root_control}/bin/supervisord
%{_venv_root_control}/bin/contrail-nodemgr
%{_venv_root_control}/archive/supervisor-3.0b2.tar.gz
%{_venv_root_vrouter}%{_pysitepkg}/supervisor
%{_venv_root_vrouter}%{_pysitepkg}/supervisor-*
%{_venv_root_vrouter}%{_pysitepkg}/meld3
%{_venv_root_vrouter}%{_pysitepkg}/meld3-*
%{_venv_root_vrouter}%{_pysitepkg}/elementtree
%{_venv_root_vrouter}%{_pysitepkg}/elementtree-*
%{_venv_root_vrouter}/bin/echo_supervisord_conf
%{_venv_root_vrouter}/bin/pidproxy
%{_venv_root_vrouter}/bin/supervisorctl
%{_venv_root_vrouter}/bin/supervisord
%{_venv_root_vrouter}/bin/contrail-nodemgr
%{_venv_root_vrouter}/archive/supervisor-3.0b2.tar.gz
%changelog
* Mon Jul 22 2013 Chandan Mishra <cdmishra@juniper.net> - config-1
- Initial build.
