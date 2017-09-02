%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global sname neutronclient

%if 0%{?fedora}
%global with_python3 1
%endif

Name:       python-neutronclient
Version:    6.1.0
Release:    1contrail1%{?dist}
Provides:    python2-neutronclient = %{version}-%{release}
Summary:    Python API and CLI for OpenStack Neutron

License:    ASL 2.0
URL:        http://launchpad.net/python-neutronclient/
#Source0:    https://tarballs.openstack.org/%{name}/%{name}-%{upstream_version}.tar.gz

BuildArch:  noarch

Obsoletes:  python-%{sname}-tests <= 4.1.1-3

Requires: python-babel >= 2.3.4
Requires: python-cliff >= 2.3.0
Requires: python-iso8601 >= 0.1.11
Requires: python-netaddr >= 0.7.12
Requires: python-os-client-config >= 1.22.0
Requires: python-oslo-i18n >= 2.1.0
Requires: python-oslo-serialization >= 1.10.0
Requires: python-oslo-utils >= 3.18.0
Requires: python-pbr
Requires: python-requests >= 2.10.0
Requires: python-simplejson >= 2.2.0
Requires: python-six >= 1.9.0
Requires: python-debtcollector
Requires: python-osc-lib >= 1.2.0
Requires: python-keystoneauth1 >= 2.18.0
Requires: python-keystoneclient >= 1:3.8.0
BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-pbr
%description
Client library and command line utility for interacting with OpenStack
Neutron's API.

%if 0%{?with_python3}
%package -n python3-%{sname}
Summary:    Python API and CLI for OpenStack Neutron
%{?python_provide:%python_provide python3-neutronclient}

BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: python3-pbr

Requires: python3-babel >= 2.3.4
Requires: python3-cliff >= 2.3.0
Requires: python3-iso8601 >= 0.1.11
Requires: python3-netaddr >= 0.7.12
Requires: python3-os-client-config >= 1.22.0
Requires: python3-oslo-i18n >= 2.1.0
Requires: python3-oslo-serialization >= 1.10.0
Requires: python3-oslo-utils >= 3.18.0
Requires: python3-pbr
Requires: python3-requests >= 2.10.0
Requires: python3-simplejson >= 2.2.0
Requires: python3-six >= 1.9.0
Requires: python3-debtcollector
Requires: python3-osc-lib >= 1.2.0
Requires: python3-keystoneauth1 >= 2.18.0
Requires: python3-keystoneclient >= 1:3.8.0

%description -n python3-%{sname}
Client library and command line utility for interacting with OpenStack
Neutron's API.
%endif

#%package doc
#Summary:          Documentation for OpenStack Neutron API Client

#BuildRequires:    python-sphinx
#BuildRequires:    python-oslo-sphinx
#BuildRequires:    python-reno

#%description      doc
#Client library and command line utility for interacting with OpenStack
#Neutron's API.

%prep
#%setup -q -n %{name}-%{upstream_version}

# Let RPM handle the dependencies
rm -f test-requirements.txt requirements.txt

%build
#CFLAGS="%{optflags}" %{__python} setup.py %{?py_setup_args} build --executable="%{__python2} -s"
#%if 0%{?with_python3}
#%py3_build
#%endif
pushd %{_builddir}
pushd python-neutronclient
%{__python2} setup.py build

%install
%if 0%{?with_python3}
%py3_install
mv %{buildroot}%{_bindir}/neutron %{buildroot}%{_bindir}/neutron-%{python3_version}
ln -s ./neutron-%{python3_version} %{buildroot}%{_bindir}/neutron-3
# Delete tests
rm -fr %{buildroot}%{python3_sitelib}/neutronclient/tests
%endif
#CFLAGS="%{optflags}" %{__python} setup.py %{?py_setup_args} install -O1 --skip-build --root %{buildroot}

pushd %{_builddir}
pushd python-neutronclient
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}
install -p -D -m 644 tools/neutron.bash_completion %{buildroot}%{_sysconfdir}/bash_completion.d/neutron.bash_completion
mv %{buildroot}%{_bindir}/neutron %{buildroot}%{_bindir}/neutron-%{python2_version}
ln -s ./neutron-%{python2_version} %{buildroot}%{_bindir}/neutron-2
ln -s ./neutron-2 %{buildroot}%{_bindir}/neutron

# Delete tests
rm -fr %{buildroot}%{python2_sitelib}/neutronclient/tests

export PYTHONPATH="$( pwd ):$PYTHONPATH"
#sphinx-build -b html doc/source html


%files -n python-%{sname}
#%doc README.rst
#%license LICENSE
%{python2_sitelib}/neutronclient
%{python2_sitelib}/*.egg-info
%{_bindir}/neutron
%{_bindir}/neutron-2
%{_bindir}/neutron-%{python2_version}
%{_sysconfdir}/bash_completion.d/neutron.bash_completion

%if 0%{?with_python3}
%files -n python3-%{sname}
%license LICENSE
%doc README.rst
%{python3_sitelib}/%{sname}
%{python3_sitelib}/*.egg-info
%{_bindir}/neutron-3
%{_bindir}/neutron-%{python3_version}
%endif

#%files doc
#%doc html
#%license LICENSE

%changelog
* Tue Aug 29 2017 Alexey Morlang <amorlang@juniper.net> 6.1.0-1contrail1
- Rebuilt version 6.1.0-1contrail with contrail patches for OpenContrail

* Wed Feb 08 2017 Alfredo Moralejo <amoralej@redhat.com> 6.1.0-1
- Update to 6.1.0

