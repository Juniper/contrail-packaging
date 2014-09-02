%define         _relstr      0contrail
%{echo: "Building release %{_relstr}\n"}

%global srcname bottle

Name:           python-%{srcname}
Version:        0.11.6
Release:        %{_relstr}%{?dist}
Summary:        Fast and simple WSGI-framework for small web-applications

Group:          Development/Languages
License:        MIT
URL:            http://bottlepy.org
Source0:        http://pypi.python.org/packages/source/b/%{srcname}/%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools


%description
Bottle is a fast and simple micro-framework for small web-applications. 
It offers request dispatching (Routes) with URL parameter support, Templates, 
a built-in HTTP Server and adapters for many third party WSGI/HTTP-server and 
template engines. All in a single file and with no dependencies other than the 
Python Standard Library.

%prep
%setup -q -n %{srcname}-%{version}
sed -i '/^#!/d' bottle.py

%build
pushd %{_builddir}/bottle-0.11.6
%{__python} setup.py build
popd

%install
pushd %{_builddir}/bottle-0.11.6
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
rm %{buildroot}%{_bindir}/bottle.py
popd

%files
%doc README.rst PKG-INFO
%{python_sitelib}/*


%changelog
* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild
