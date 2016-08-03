%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:       python-neutronclient
Version:    3.1.0
Release:    2contrail%{?dist}
Summary:    Python API and CLI for OpenStack Neutron

License:    ASL 2.0
URL:        http://launchpad.net/%{name}
#Rebuilding from contrail + upstream
#Source0:    https://pypi.python.org/packages/source/p/%{name}/%{name}-%{version}.tar.gz

BuildArch:  noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-pbr
BuildRequires: python-d2to1

Requires: pyparsing
Requires: python-cliff >= 1.14.0
Requires: python-keystoneclient >= 1.6.0
Requires: python-oslo-i18n >= 1.5.0
Requires: python-oslo-serialization >= 1.4.0
Requires: python-oslo-utils >= 2.0.0
Requires: python-pbr
Requires: python-prettytable >= 0.6
Requires: python-requests >= 2.5.2
Requires: python-setuptools
Requires: python-simplejson
Requires: python-babel
Requires: python-iso8601
Requires: python-netaddr
Requires: python-six >= 1.9.0


%description
Client library and command line utility for interacting with Openstack
Neutron's API.

%prep
#%setup -q -n %{name}-%{upstream_version}

# Let RPM handle the dependencies
rm -f test-requirements.txt requirements.txt

%build
pushd %{_builddir}
pushd python-neutronclient
%{__python2} setup.py build

%install
pushd %{_builddir}
pushd python-neutronclient
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Install other needed files
install -p -D -m 644 tools/neutron.bash_completion \
    %{buildroot}%{_sysconfdir}/bash_completion.d/neutron.bash_completion

# Remove unused files
rm -rf %{buildroot}%{python_sitelib}/neutronclient/tests

%files
#%license LICENSE
#%doc README.rst
%{_bindir}/neutron
%{python2_sitelib}/neutronclient
%{python2_sitelib}/*.egg-info
%{_sysconfdir}/bash_completion.d

%changelog
* Wed Jan 27 2016 Nagendra Maynattamai <npchandran@juniper.net> 3.1.0-2contrail
- Added contrail patches to upstream version 3.1.0

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu May 28 2015 Haikel Guemar <hguemar@fedoraproject.org> 2.4.0-1
- Update to upstream 2.4.0

* Fri Mar 27 2015 Haikel Guemar <hguemar@fedoraproject.org> 2.3.11-1
- Update to upstream 2.3.11
- Add Requires: python-pbr (drop the patch)
- Add Requires: python-oslo-i18n, python-oslo-serialization, python-oslo-utils

* Mon Oct 13 2014 Jakub Ruzicka <jruzicka@redhat.com> 2.3.9-1
- Update to upstream 2.3.9

* Thu Aug 21 2014 Jakub Ruzicka <jruzicka@redhat.com> 2.3.6-2
- Fix listing security group rules

* Mon Aug 04 2014 Jakub Ruzicka <jruzicka@redhat.com> 2.3.6-1
- Update to upstream 2.3.6
- New requirements: python-requests, python-keystoneclient

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Feb 25 2014 Jakub Ruzicka <jruzicka@redhat.com> 2.3.4-1
- Update to upstream 2.3.4

* Mon Jan 13 2014 Jakub Ruzicka <jruzicka@redhat.com> 2.3.3-1
- Update to upstream 2.3.3

* Fri Nov 01 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.3.1-2
- Don't obsolete python-quantumclient (#1025509)

* Tue Oct 08 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.3.1-1
- Update to upstream 2.3.1.

* Mon Sep 09 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.3.0-1
- Update to upstream 2.3.0.

* Wed Aug 28 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.2.6-2
- Remove all pbr deps in the patch instead of this spec file.

* Wed Aug 21 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.2.6-1
- Update to upstream 2.2.6.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 23 2013 Jakub Ruzicka <jruzicka@redhat.com> - 1:2.2.4-1
- Initial package based on python-quantumclient.
- Removed runtime dependency on python-pbr.
