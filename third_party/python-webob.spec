%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif

Name:           python-webob
Summary:        WSGI request and response object
Version:        1.2.3
Release:        %{_relstr}
Summary:	    python webob %{?_gitVer}
License:        MIT
Group:          System Environment/Libraries
URL:            http://pythonpaste.org/webob/
Source0:        WebOb-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-setuptools-devel
BuildRequires:  python-nose
BuildRequires:  python-webtest
Requires:       contrail-api-venv

%description
WebOb provides wrappers around the WSGI request environment, and an object to 
help create WSGI responses. The objects map much of the specified behavior of 
HTTP, including header parsing and accessors for other standard parts of the 
environment.

%prep
%setup -q -n WebOb-%{version}

# Disable performance_test, which requires repoze.profile, which isn't
# in Fedora.
%{__rm} -f tests/performance_test.py


%build
%{__python} setup.py build


%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}
%{__python} setup.py sdist
install -p -D -m 644 dist/WebOb-1.2.3.tar.gz %{buildroot}/opt/contrail/api-venv/archive/WebOb-1.2.3.tar.gz


%check
PYTHONPATH=$(pwd) nosetests


%files
%defattr(-,root,root,-)
%doc docs/*
%{python_sitelib}/webob/
%{python_sitelib}/WebOb*.egg-info/
/opt/contrail/api-venv/archive/WebOb-1.2.3.tar.gz
%changelog
* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec 14 2011 Luke Macken <lmacken@redhat.com> - 1.1.1-1
- Update to the latest stable release
- Remove wsgiproxy, tempita, and dtopt from our build requirements

* Wed Aug 17 2011 Nils Philippsen <nils@redhat.com> - 1.0.8-1
- Update to 1.0.8 for TurboGears 2.1.1 which needs 1.0.7 (#663117)

* Mon Mar 21 2011 Luke Macken <lmacken@redhat.com> - 1.0.5-1
- Update to 1.0.5, which restores Python 2.4 support

* Thu Feb 24 2011 Luke Macken <lmacken@redhat.com> - 1.0.3-1
- Update to 1.0.3

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Dec 14 2010 Ricky Zhou <ricky@fedoraproject.org> - 1.0-1
- Upstream released new version.

* Sun Jul 25 2010 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 0.9.8-4
- Reenable tests since python-webtest is now available

* Sun Jul 25 2010 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 0.9.8-3
- Disable tests. We need to bootstrap against python-webtest

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 0.9.8-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Wed May 05 2010 Luke Macken <lmacken@redhat.com> - 0.9.8-1
- Latest upstream release
- Get the test suite running

* Tue Jan 19 2010 Ricky Zhou <ricky@fedoraproject.org> - 0.9.7.1-1
- Upstream released new version.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Apr 14 2009 Ricky Zhou <ricky@fedoraproject.org> - 0.9.6.1-2
- Change define to global.
- Remove unnecessary BuildRequires on python-devel.

* Tue Mar 10 2009 Ricky Zhou <ricky@fedoraproject.org> - 0.9.6.1-1
- Upstream released new version.

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jan 06 2009 Luke Macken <lmacken@redhat.com> 0.9.5-1
- Update to 0.9.5

* Sat Dec 06 2008 Ricky Zhou <ricky@fedoraproject.org> 0.9.4-1
- Upstream released new version.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.9.3-3
- Rebuild for Python 2.6

* Tue Sep 30 2008 Ricky Zhou <ricky@fedoraproject.org> 0.9.3-2
- Add BuildRequires on python-tempita.

* Tue Sep 30 2008 Ricky Zhou <ricky@fedoraproject.org> 0.9.3-1
- Upstream released new version.

* Thu Jul 17 2008 Ricky Zhou <ricky@fedoraproject.org> 0.9.2-2
- Remove conftest from the tests.

* Fri Jun 27 2008 Ricky Zhou <ricky@fedoraproject.org> 0.9.2-1
- Upstream released new version.
- Rename to python-webob, as mentioned in the Python package naming
  guidelines.
- Clean up spec.
- Add %%check section.

* Sat Mar 15 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.9-1
- Initial package for Fedora
