%define         _distrothirdpartydir distro/third_party

Summary: gevent http client library %{?_gitVer}
%define upstream_name geventhttpclient
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif

%if 0%(grep -c Xen /etc/redhat-release)
%define		dist	.xen
%endif
Name: python-%{upstream_name}
Version: 1.0a
Release: %{_relstr}%{?dist}
License: MIT
Group: Applications/System
URL: https://github.com/gwik/geventhttpclient

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
pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/geventhttpclient-1.0a
CFLAGS="%{optflags}" %{__python} setup.py build 

%install
pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/geventhttpclient-1.0a
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%files
%defattr(-,root,root,-)
%if 0%{?rhel} >= 7
    /usr/lib64/python2.7/site-packages/%{upstream_name}
    /usr/lib64/python2.7/site-packages/%{upstream_name}-%{version}-*.egg-info
%else
    /usr/lib64/python2.6/site-packages/%{upstream_name}
    /usr/lib64/python2.6/site-packages/%{upstream_name}-%{version}-*.egg-info
%endif


%changelog
* Wed Dec 19 2012  <builder@build01> - 
- Initial build.

