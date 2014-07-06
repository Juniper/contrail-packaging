#
# Latest keystoneclient
#
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}


Name:       python-keystoneclient
Version:    0.2.1
Release:    %{_relstr}
Summary:    Python API and CLI for OpenStack Keystone %{?_gitVer}

Group:      Development/Languages
License:    ASL 2.0
URL:        https://github.com/openstack/python-keystoneclient
BuildArch:  noarch

#Source0:    https://launchpad.net/%{name}/trunk/%{version}/+download/%{name}-%{version}.tar.gz
#Source0:    http://tarballs.openstack.org/%{name}/%{name}-%{version}.tar.gz

#
# patches_base=0.2.1
#

Requires:   python-httplib2 >= 0.7
Requires:   python-prettytable
Requires:   python-setuptools
Requires:   python-simplejson
Requires:   python-keyring
Requires:   python-requests

BuildRequires: make
BuildRequires: python2-devel
BuildRequires: python-setuptools

%description
Client library and command line utility for interacting with Openstack
Keystone's API.

%package doc
Summary:    Documentation for OpenStack Keystone API Client %{?_gitVer}
Group:      Documentation

BuildRequires: python-sphinx

%description doc
Documentation for the client library for interacting with Openstack
Keystone's API.

%prep
## if [ -d python-keystoneclient ]; then
    ## (cd python-keystoneclient; git pull)
## else
    ## git clone git@bitbucket.org:contrail_admin/python-keystoneclient.git
## fi

%build
pushd %{_builddir}/..
pushd third_party/python-keystoneclient
%{__python} setup.py build

%install
pushd %{_builddir}/..
pushd third_party/python-keystoneclient
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
%{__python} setup.py sdist
mv %{buildroot}/usr/keystoneclient/versioninfo %{buildroot}%{python_sitelib}/keystoneclient/versioninfo
install -p -D -m 644 tools/keystone.bash_completion %{buildroot}%{_sysconfdir}/bash_completion.d/keystone.bash_completion

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
make html
popd
# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
%clean
%files
## %doc python-keystoneclient/README.rst
%{_bindir}/keystone
%{_sysconfdir}/bash_completion.d/keystone.bash_completion
%{python_sitelib}/keystoneclient
%{python_sitelib}/*.egg-info

%files doc
## %doc python-keystoneclient/LICENSE python-keystoneclient/doc/build/html

%changelog
* Wed Jan 2 2013 Dan Prince <dprince@redhat.com> 0.2-0.1.g2
- Add dependency on python-requests.

* Fri Dec 21 2012 Alan Pevec <apevec@redhat.com> 0.2.1-1
- New upstream release.
- Add bash completion support

* Wed Dec 19 2012 Dan Prince <dprince@redhat.com> 0.2-0.1.g2
- Add missing build dependency for make.

* Fri Dec 14 2012 Dan Prince <dprince@redhat.com> 0.2-0.1.g2
- Add python-keyring RPM dependency.

* Fri Nov 23 2012 Alan Pevec <apevec@redhat.com> 0.2.0-1
- New upstream release.
- Identity API v3 support
- add service_id column to endpoint-list
- avoid ValueError exception for 400 or 404 lp#1067512
- use system default CA certificates lp#106483
- keep original IP lp#1046837
- avoid exception for an expected empty catalog lp#1070493
- fix keystoneclient against Rackspace Cloud Files lp#1074784
- blueprint solidify-python-api
- blueprint authtoken-to-keystoneclient-repo
- fix auth_ref initialization lp#1078589
- warn about bypassing auth on CLI lp#1076225
- check creds before token/endpoint lp#1076233
- check for auth URL before password lp#1076235
- fix scoped auth for non-admins lp#1081192

* Tue Oct 16 2012 Alan Pevec <apevec@redhat.com> 0.1.3.27-1
- Allow empty description for tenants (lp#1025929)
- Documentation updates
- change default  wrap for tokens from 78 characters to 0 (lp#1061514)
- bootstrap a keystone user in one cmd
- Useful message when missing catalog (lp#949904)

* Thu Sep 27 2012 Alan Pevec <apevec@redhat.com> 1:0.1.3.9-1
- Handle "503 Service Unavailable" exception (lp#1028799)
- add --wrap option for long PKI tokens (lp#1053728)
- remove deprecated Diablo options
- add --os-token and --os-endpoint options to match
  http://wiki.openstack.org/UnifiedCLI/Authentication

* Sun Sep 23 2012 Alan Pevec <apevec@redhat.com> 1:0.1.3-1
- Change underscores in new cert options to dashes (lp#1040162)

* Wed Aug 22 2012 Alan Pevec <apevec@redhat.com> 1:0.1.2-1
- Add dependency on python-setuptools (#850842)
- New upstream release.

* Mon Jul 23 2012 Alan Pevec <apevec@redhat.com> 1:0.1.1-1
- New upstream release.

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2012.2-0.2.f1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Apr 05 2012 Alan Pevec <apevec@redhat.com> 2012.1-1
- Essex release

* Thu Apr 05 2012 Alan Pevec <apevec@redhat.com> 2012.1-0.8.rc2
- essex rc2

* Sat Mar 24 2012 Alan Pevec <apevec@redhat.com> 2012.1-0.7.rc1
- update to final essex rc1

* Wed Mar 21 2012 Alan Pevec <apevec@redhat.com> 2012.1-0.6.rc1
- essex rc1

* Thu Mar 01 2012 Alan Pevec <apevec@redhat.com> 2012.1-0.5.e4
- essex-4 milestone

* Tue Feb 28 2012 Alan Pevec <apevec@redhat.com> 2012.1-0.4.e4
- Endpoints: Add create, delete, list support
  https://review.openstack.org/4594

* Fri Feb 24 2012 Alan Pevec <apevec@redhat.com> 2012.1-0.3.e4
- Improve usability of CLI. https://review.openstack.org/4375

* Mon Feb 20 2012 Alan Pevec <apevec@redhat.com> 2012.1-0.2.e4
- pre essex-4 snapshot, for keystone rebase

* Thu Jan 26 2012 Cole Robinson <crobinso@redhat.com> - 2012.1-0.1.e3
- Initial package
