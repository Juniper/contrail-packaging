%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
Name:       python-neutronclient
Version:    4.1.1
Release:    2contrail1%{?dist}
Summary:    Python API and CLI for OpenStack Neutron

License:    ASL 2.0
URL:        http://launchpad.net/python-neutronclient/
#Source0:    https://pypi.python.org/packages/source/p/%{name}/%{name}-%{version}%{?milestone}.tar.gz

BuildArch:  noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-pbr

Requires: python-babel >= 1.3
Requires: python-cliff >= 1.14.0
Requires: python-iso8601 >= 0.1.9
Requires: python-keystoneclient >= 1.6.0
Requires: python-netaddr >= 0.7.12
Requires: python-os-client-config >= 1.13.1
Requires: python-oslo-i18n >= 1.5.0
Requires: python-oslo-serialization >= 1.4.0
Requires: python-oslo-utils >= 2.0.0
Requires: python-pbr
Requires: python-requests >= 2.5.2
Requires: python-simplejson >= 2.2.0
Requires: python-six >= 1.9.0


%description
Client library and command line utility for interacting with OpenStack
Neutron's API.


%package tests
Summary:	OpenStack Neutron client tests
Requires:	%{name} = %{version}-%{release}


%description tests
Client library and command line utility for interacting with OpenStack
Neutron's API.

This package contains client test files.


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

%files
#%license LICENSE
#%doc README.rst
%{_bindir}/neutron
%{python2_sitelib}/neutronclient
%{python2_sitelib}/*.egg-info
%{_sysconfdir}/bash_completion.d
%exclude %{python2_sitelib}/neutronclient/tests

#%files tests
#%license LICENSE
#%{python2_sitelib}/neutronclient/tests

%changelog
* Wed Jun 29 2016 Nagendra Maynattamai <npchandran@juniper.net> 4.1.1-2.1contrail1
- Rebuilt with patches for Opencontrail

* Wed Mar 23 2016 RDO <rdo-list@redhat.com> 4.1.1-0.1
-  Rebuild for Mitaka 4.1.1
