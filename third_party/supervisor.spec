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
BuildRoot:      %{_topdir}/BUILDROOT
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
%if  "%{dist}" != ".xen"
Requires: python-gevent
Requires: python-requests
%endif

Autoreq:0

%if  "%{dist}" == ".xen"
%define __python /usr/local/bin/python
%define python_sitelib /usr/local/lib/python2.7/site-packages
%endif
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
install -d -m 755 %{buildroot}%{python_sitelib}

# install in analytics venv
install -d -m 755 %{buildroot}
install -d -m 755 %{buildroot}/archive

pushd %{_builddir}/../%{_distrothirdpartydir}/elementtree-1.2.6-20050316
#pushd %{_distrothirdpartydir}/elementtree-1.2.6-20050316
%{__python} setup.py install --root=%{buildroot}
popd

#pushd %{_builddir}/..
#pushd %{_distrothirdpartydir}/meld3-0.6.10
pushd %{_builddir}/../%{_distrothirdpartydir}/meld3-0.6.10
%{__python} setup.py install --root=%{buildroot}
popd

pushd %{_builddir}/..
# save these files to restore
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save
cp %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save
pushd %{_distrothirdpartydir}/supervisor-3.0b2
%{__python} setup.py install --root=%{buildroot}
%{__python} setup.py sdist
cp dist/* %{buildroot}/archive
popd
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/SOURCES.txt
mv %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO.save %{_distrothirdpartydir}/supervisor-3.0b2/supervisor.egg-info/PKG-INFO
# done install in analytics venv

#Requires cleanup
install -p -m 755 %{_distropkgdir}/supervisor_killall %{buildroot}%{_bindir}/supervisor_killall

%clean
%files
%defattr(-,root,root,-)
%if  "%{dist}" == ".xen"
%undefine buildroot
/usr/local/bin/echo_supervisord_conf
/usr/local/bin/pidproxy
/usr/local/bin/supervisorctl
/usr/local/bin/supervisord
/usr/bin/supervisor_killall
/archive/supervisor-3.0b2.tar.gz
%else
/usr/bin/echo_supervisord_conf
/usr/bin/pidproxy
/usr/bin/supervisorctl
/usr/bin/supervisord
/usr/bin/supervisor_killall
%endif
/archive/supervisor-3.0b2.tar.gz
%{python_sitelib}/supervisor
%{python_sitelib}/supervisor-*
%{python_sitelib}/meld3
%{python_sitelib}/meld3-*
%{python_sitelib}/elementtree
%{python_sitelib}/elementtree-*

%if  "%{dist}" == ".xen"
%define buildroot %{_topdir}/BUILDROOT
%endif
%changelog
* Mon Jul 22 2013 Chandan Mishra <cdmishra@juniper.net> - config-1
- Initial build.
