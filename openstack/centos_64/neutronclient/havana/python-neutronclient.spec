#
# This is 2.3.0 havana
#
%define         _relstr     3contrail
%{echo: "Building release %{_relstr}\n"}

Name:       python-neutronclient
Version:    2.3.0
#Epoch:      2
Release:    %{_relstr}
Summary:    Python API and CLI for OpenStack Neutron

Group:      Development/Languages
License:    ASL 2.0
URL:        http://launchpad.net/python-neutronclient/
#Source0:    https://pypi.python.org/packages/source/p/%{name}/%{name}-%{version}.tar.gz

#
# patches_base=2.3.0
#
#Patch0001: 0001-Remove-runtime-dependency-on-python-pbr.patch

Obsoletes:  python-quantumclient < 2:2.2.4

BuildArch:  noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-pbr
BuildRequires: python-d2to1

Requires: pyparsing
Requires: python-httplib2
Requires: python-cliff >= 1.0
Requires: python-prettytable >= 0.6
Requires: python-setuptools
Requires: python-simplejson
Requires: python-pbr

%description
Client library and command line utility for interacting with Openstack
Neutron's API.

%prep
pushd %{_builddir}
pushd python-neutronclient
#%setup -q -n %{name}-%{version}
#%patch0001 -p1
# We provide version like this in order to remove runtime dep on pbr.
#sed -i s/REDHATNEUTRONCLIENTVERSION/%{version}/ neutronclient/version.py
sed -i 's/Babel>=0.9.6/Babel/' requirements.txt

%build
pushd %{_builddir}
pushd python-neutronclient
%{__python} setup.py build

%install
pushd %{_builddir}
pushd python-neutronclient
%{__python} setup.py install -O1 --skip-build --root %{buildroot} %{?_venvtr}
%{__python} setup.py sdist

# Install other needed files
# rhbz 888939#c7: bash-completion is not in RHEL
install -p -D -m 644 tools/neutron.bash_completion \
    %{buildroot}%{_sysconfdir}/profile.d/neutron.sh
popd

# Remove unused files
rm -rf %{buildroot}%{python_sitelib}/neutronclient/tests

%files
#%doc LICENSE
#%doc README.rst
%{_bindir}/neutron
%{python_sitelib}/neutronclient
%{python_sitelib}/*.egg-info
%{_sysconfdir}/profile.d/neutron.sh
#/opt/contrail/api-venv/archive/python-neutronclient.tar.gz

%changelog
* Tue Sep 09 2014 Atul Moghe <amoghe@juniper.net> - 2.3.0-3contrail
- Fixed python-pbr dependency issue.

* Mon Sep 09 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.3.0-1
- Update to upstream 2.3.0.

* Wed Aug 28 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.2.6-2
- Remove all pbr deps in the patch instead of this spec file.

* Tue Aug 27 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.2.6-1
- Update to upstream 2.2.6.

* Tue Jul 23 2013 Jakub Ruzicka <jruzicka@redhat.com> - 1:2.2.4-1
- Initial package based on python-quantumclient.
- Removed runtime dependency on python-pbr.
