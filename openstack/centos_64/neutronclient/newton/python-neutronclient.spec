%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
Name:       python-neutronclient
Version:    6.0.0 
Release:    2contrail1%{?dist}
Summary:    Python API and CLI for OpenStack Neutron

License:    ASL 2.0
URL:        http://launchpad.net/python-neutronclient/
#Source0:    https://pypi.python.org/packages/source/p/%{name}/%{name}-%{version}%{?milestone}.tar.gz

BuildArch:  noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-pbr

Requires: python-babel >= 2.3.4
Requires: python-cliff >= 1.15.0
Requires: python-iso8601 >= 0.1.11
Requires: python-netaddr >= 0.7.12
Requires: python-os-client-config >= 1.13.1
Requires: python-oslo-i18n >= 2.1.0
Requires: python-oslo-serialization >= 1.10.0
Requires: python-oslo-utils >= 3.16.0
Requires: python-pbr
Requires: python-requests >= 2.10.0
Requires: python-simplejson >= 2.2.0
Requires: python-six >= 1.9.0
Requires: python-debtcollector
Requires: python-osc-lib
Requires: python-keystoneauth1

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
* Wed Nov 23 2016 Atul Moghe <amoghe@juniper.net> 6.0.0-2.1contrail1
- Rebuilt with patches for Opencontrail

* Mon Sep 12 2016 Haikel Guemar <hguemar@fedoraproject.org> 6.0.0-1
- Update to 6.0.0
