%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}

%define         _distrothirdpartydir distro/third_party

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif

%if 0%(grep -c XenServer /etc/redhat-release)
%define dist .xen
%endif

Name: python-thrift
Summary: Python Thrift Package %{?_gitVer}
Version: 0.9.1
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
pushd %{_distrothirdpartydir}/thrift-0.9.1
#pushd third_party/thrift-0.8.0/lib/py
CFLAGS="%{optflags}" %{__python} setup.py build

%install
pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/thrift-0.9.1
#pushd third_party/thrift-0.8.0/lib/py
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitearch}/thrift
%{python_sitearch}/thrift-0.9.1-*.egg-info


%changelog
* Wed Dec 19 2012  <builder@build01> - picassa-1
- Initial build.

