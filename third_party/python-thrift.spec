%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}

%define         _distrothirdpartydir distro/third_party

%define         _relstr      0contrail

%if 0%(grep -c XenServer /etc/redhat-release)
%define dist .xen
BuildRoot:	%{_topdir}/BUILDROOT
%endif

Name: python-thrift
Summary: Python Thrift Package %{?_gitVer}
%if  "%{dist}" == ".xen"
Version: 0.8.0
%else
Version: 0.9.1
%endif
Release: %{_relstr}%{?dist}
License: MIT
Group: Applications/System

%description

%prep
grep controller .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi

%build
pushd %{_builddir}/..
%if  "%{dist}" == ".xen"
pushd third_party/thrift-0.8.0/lib/py
%else
pushd %{_distrothirdpartydir}/thrift-0.9.1
%endif
CFLAGS="%{optflags}" %{__python} setup.py build

%install
pushd %{_builddir}/..
%if  "%{dist}" == ".xen"
pushd third_party/thrift-0.8.0/lib/py
%else
pushd %{_distrothirdpartydir}/thrift-0.9.1
%endif
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%files
%defattr(-,root,root,-)
%if  "%{dist}" == ".xen"
%undefine buildroot
%{python_sitearch}/thrift
%{python_sitearch}/thrift-0.8.0-*.egg-info
%else
%{python_sitearch}/thrift
%{python_sitearch}/thrift-0.9.1-*.egg-info
%endif

%if  "%{dist}" == ".xen"
%define buildroot %{_topdir}/BUILDROOT
%endif

%changelog
* Wed Dec 19 2012  <builder@build01> - picassa-1
- Initial build.

