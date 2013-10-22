%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}

Name:             python-novaclient
Version:          2.10.0
Release:          %{_relstr}
Summary:	      Python API and CLI for OpenStack Nova %{?_gitVer}
Epoch:            1

Group:            Development/Languages
License:          ASL 2.0
URL:              http://pypi.python.org/pypi/python-novaclient
Source0:          http://tarballs.openstack.org/%{name}/%{name}-%{version}.tar.gz

BuildArch:        noarch
BuildRequires:    python-setuptools

Requires:         python-argparse
Requires:         python-simplejson
Requires:         python-httplib2
Requires:         python-prettytable
Requires:         python-setuptools
Requires:         python-iso8601
Requires:         contrail-api-venv

%description
This is a client for the OpenStack Nova API. There's a Python API (the
novaclient module), and a command-line script (nova). Each implements 100% of
the OpenStack Nova API.

%package doc
Summary:          Documentation for OpenStack Nova API Client %{?_gitVer}
Group:            Documentation

BuildRequires:    python-sphinx

%description      doc
This is a client for the OpenStack Nova API. There's a Python API (the
novaclient module), and a command-line script (nova). Each implements 100% of
the OpenStack Nova API.

This package contains auto-generated documentation.

%prep
#%setup -q
## if [ -d python-novaclient ]; then
   ## (cd python-novaclient; git pull)
## else
   ## git clone git@bitbucket.org:contrail_admin/python-novaclient.git
## fi

##pushd python-novaclient

# TODO: Have the following handle multi line entries

%build
pushd %{_builddir}/..
pushd third_party/python-novaclient
sed -i '/setup_requires/d; /install_requires/d; /dependency_links/d' setup.py
%{__python} setup.py build

%install
pushd %{_builddir}/..
pushd third_party/python-novaclient
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
%{__python} setup.py sdist

install -p -D -m 644 dist/python-novaclient-3776fe9.tar.gz %{buildroot}/opt/contrail/api-venv/archive/python-novaclient-3776fe9.tar.gz
mkdir -p %{buildroot}%{_sysconfdir}/bash_completion.d
install -pm 644 tools/nova.bash_completion %{buildroot}%{_sysconfdir}/bash_completion.d/nova

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

export PYTHONPATH="$( pwd ):$PYTHONPATH"
sphinx-build -b html doc/source html

# Fix hidden-file-or-dir warnings
rm -fr html/.doctrees html/.buildinfo

%files
## TODO - doc/sphinx has errors. need to fix
##%doc python-novaclient/README.rst
##%doc python-novaclient/LICENSE
%{_bindir}/nova
%{python_sitelib}/novaclient
%{python_sitelib}/*.egg-info
%{_sysconfdir}/bash_completion.d
/opt/contrail/api-venv/archive/python-novaclient-3776fe9.tar.gz

%files doc
## %doc python-novaclient/html

%changelog
* Thu Mar 28 2013 Dan Prince <dprince@redhat.com> 2.10.0-2
- Remove versioninfo file.

* Fri Dec 21 2012 Alan Pevec <apevec@redhat.com> 2.10.0-2
- Include bash_completion file (#872544) (Alvaro Lopez Ortega)
- Add dependency on python-iso8601 (#881515)

* Mon Dec 03 2012 Alan Pevec <apevec@redhat.com> 2.10.0-1
- Update to latest upstream release

* Thu Sep 27 2012 Pádraig Brady <P@draigBrady.com> 1:2.9.0-1
- Update to latest upstream release (aligned with Folsom)

* Tue Sep 25 2012 Pádraig Brady <P@draigBrady.com> 1:2.8.0.26-2
- Update to latest upstream release

* Wed Aug 22 2012 Pádraig Brady <P@draigBrady.com> 2012.2-0.3.f1
- Add dependency on python-setuptools (#849477)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2012.2-0.2.f1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun 13 2012 Pádraig Brady <P@draigBrady.com> 2012.2-0.1.f1
- Update to folsom-1 release

* Sun Apr  8 2012 Pádraig Brady <P@draigBrady.com> 2012.1-1
- Update to essex release
- Include LICENSE (#732695)

* Thu Mar 22 2012 Pádraig Brady <P@draigBrady.com> 2012.1-0.4.rc1
- Avoid a horizon issue trying to write to /var/www (#801202)

* Wed Mar 21 2012 Pádraig Brady <P@draigBrady.com> 2012.1-0.3.rc1
- Update to essex-rc1

* Tue Mar 06 2012 Alan Pevec <apevec@redhat.com> 2012.1-0.2.e4
- Update to essex-4

* Fri Jan 27 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.1.e3
- Update to essex milestone 3

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.1-0.5.89bzr
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Aug 24 2011 Mark McLoughlin <markmc@redhat.com> - 2.6.1-0.4.89bzr
- Update to latest upstream snapshot
- Don't use %%setup -n (#732694)

* Mon Aug 22 2011 Mark McLoughlin <markmc@redhat.com> - 2.6.1-0.3.83bzr
- Remove python-devel BR
- Remove the openstack-novaclient sub-package

* Fri Aug 19 2011 Mark McLoughlin <markmc@redhat.com> - 2.6.1-0.2.83bzr
- Remove argparse from egg requires.txt; no egg info for argparse available

* Wed Aug 17 2011 Mark McLoughlin <markmc@redhat.com> - 2.6.1-0.1.83bz
- Update to latest upstream

* Wed Aug 10 2011 Mark McLoughlin <markmc@redhat.com> - 2.6.1-0.1.74bzr
- Update to latest upstream

* Mon Aug  8 2011 Mark McLoughlin <markmc@redhat.com> - 2.5.1-1
- Initial package from Alexander Sakhnov <asakhnov@mirantis.com>
  with cleanups by Mark McLoughlin
