%define         _distrothirdpartydir distro/third_party
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif

%if 0%(grep -c Xen /etc/redhat-release)
%define		dist	.xen
%endif
Name: python-pycassa
Summary: python-pycassa %{?_gitVer}
Version: 1.7.2
Release: %{_relstr}%{?dist}
License: MIT
Group: Applications/System
URL: https://github.com/pycassa/pycassa

BuildArch: noarch

Requires: python-thrift

Requires:           contrail-analytics-venv
Requires:           contrail-api-venv
%define             _venv_root    /opt/contrail/api-venv
%define             _venvtr       --prefix=%{_venv_root}
%define             _anl_venv_root    /opt/contrail/analytics-venv
%define             _anl_venvtr       --prefix=%{_anl_venv_root}

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages
%description

%prep
grep controller .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi

%build

%install
pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/pycassa-1.10.0
install -d -m 755 %{buildroot}%{_bindir}
install -m 755 pycassaShell %{buildroot}%{_bindir}
##%{__python} setup.py install --root=%{buildroot} %{?_anl_venvtr}
popd

%files
%defattr(-,root,root,-)
## %{_venv_root}%{_pysitepkg}/pycassa
## %{_venv_root}%{_pysitepkg}/ez_setup.py*
## %{_venv_root}%{_pysitepkg}/pycassa*egg-info
## %{_venv_root}/bin/pycassaShell
## %{_anl_venv_root}%{_pysitepkg}/pycassa
## %{_anl_venv_root}%{_pysitepkg}/ez_setup.py*
## %{_anl_venv_root}%{_pysitepkg}/pycassa*egg-info
## %{_anl_venv_root}/bin/pycassaShell
/usr/bin/pycassaShell

%post

%changelog
* Mon Dec 17 2012 Pedro Marques <roque@build01> - config-1
- Initial build.

