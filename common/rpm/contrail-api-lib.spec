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
Release:	    %{_relstr}%{?dist}
Summary: Contrail Config API Library%{?_gitVer}
Name: contrail-api-lib
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: python-gevent
Requires: python-requests
Requires: python-zope-interface
Requires: qpid-cpp-server

%define _api_venv_archv    /opt/contrail/api-venv/archive
%define _anl_venv_archv    /opt/contrail/analytics-venv/archive

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages

%description
Contrail Config API Library package

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
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi


%build
scons -U src/sandesh/common
scons -U src/api-lib
scons -U src/config/common
pushd %{_builddir}/../tools/
scons -U sandesh/library/python
popd

%define _build_dist %{_builddir}/../build/debug
%install
install -d -m 755 %{buildroot}%{python_sitelib}
install -d -m 755 %{buildroot}%{_api_venv_archv}
install -d -m 755 %{buildroot}%{_anl_venv_archv}

mkdir -p build/python_dist
pushd build/python_dist

install -D -p -m 644 %{_build_dist}/api-lib/dist/vnc_api-0.1dev.tar.gz %{buildroot}%{_api_venv_archv}/vnc_api-0.1dev.tar.gz
install -D -p -m 644 %{_build_dist}/api-lib/dist/vnc_api-0.1dev.tar.gz %{buildroot}%{_anl_venv_archv}/vnc_api-0.1dev.tar.gz
tar zxf %{_build_dist}/api-lib/dist/vnc_api-0.1dev.tar.gz
pushd vnc_api-0.1dev
%{__python} setup.py install --root=%{buildroot}
popd

install -D -p -m 644 %{_build_dist}/config/common/dist/cfgm_common-0.1dev.tar.gz %{buildroot}%{_api_venv_archv}/cfgm_common-0.1dev.tar.gz
install -D -p -m 644 %{_build_dist}/config/common/dist/cfgm_common-0.1dev.tar.gz %{buildroot}%{_anl_venv_archv}/cfgm_common-0.1dev.tar.gz
tar zxf %{_build_dist}/config/common/dist/cfgm_common-0.1dev.tar.gz
pushd cfgm_common-0.1dev
%{__python}  setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/vnc_api
%{python_sitelib}/vnc_api-*
%{python_sitelib}/cfgm_common
%{python_sitelib}/cfgm_common-*
%{_api_venv_archv}/vnc_api-0.1dev.tar.gz
%{_anl_venv_archv}/vnc_api-0.1dev.tar.gz
%{_api_venv_archv}/cfgm_common-0.1dev.tar.gz
%{_anl_venv_archv}/cfgm_common-0.1dev.tar.gz

%post

if [ -f /opt/contrail/api-venv/bin/activate ] ; then
   source /opt/contrail/api-venv/bin/activate && pip install --upgrade %{_api_venv_archv}/vnc_api-0.1dev.tar.gz %{_api_venv_archv}/cfgm_common-0.1dev.tar.gz
fi

if [ -f /opt/contrail/analytics-venv/bin/activate ] ; then
   source /opt/contrail/analytics-venv/bin/activate && pip install --upgrade %{_anl_venv_archv}/vnc_api-0.1dev.tar.gz %{_anl_venv_archv}/cfgm_common-0.1dev.tar.gz
fi

%changelog
* Mon Dec 17 2012 Pedro Marques <roque@build01> - config-1
- Initial build.

