#
# This is 2.3.4 icehouse
#
%define         _relstr      3contrail
%{echo: "Building release %{_relstr}\n"}

Name:       python-neutronclient
Version:    2.3.4
#Epoch:      2
Release:    %{_relstr}
Summary:    Python API and CLI for OpenStack Neutron

Group:      Development/Languages
License:    ASL 2.0
URL:        http://launchpad.net/python-neutronclient/

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

%changelog
* Tue Sep 9 2014 Atul Moghe <amoghe@juniper.net> 2.3.4-3contrail
- Added 3contrail, added python-pbr dependency

* Tue Aug 12 2014 Atul Moghe <amoghe@juniper.net> 2.3.4-1
- Added epoch for contrail/juniper

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

* Tue Aug 27 2013 Jakub Ruzicka <jruzicka@redhat.com> - 2.2.6-1
- Update to upstream 2.2.6.

* Tue Jul 23 2013 Jakub Ruzicka <jruzicka@redhat.com> - 1:2.2.4-1
- Initial package based on python-quantumclient.
- Removed runtime dependency on python-pbr.
