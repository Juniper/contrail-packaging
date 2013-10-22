%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}

Name:             python-glanceclient
# Since folsom-2 OpenStack clients follow their own release plan
# and restarted version numbering from 0.1.1
# https://lists.launchpad.net/openstack/msg14248.html
Epoch:            1
Version:          0.7.0
Release:          %{_relstr}
Summary:          Python API and CLI for OpenStack Glance %{?_gitVer}

Group:            Development/Languages
License:          ASL 2.0
URL:              http://github.com/openstack/python-glanceclient
#Source0:          http://launchpad.net/glance/folsom/folsom-1/+download/python-glanceclient-2012.2~f1.tar.gz

BuildArch:        noarch
BuildRequires:    python-setuptools
#BuildRequires:    python-setuptools_git

BuildArch:        noarch
#BuildRequires:    python-setuptools

Requires:         python-httplib2
Requires:         python-keystoneclient
Requires:         python-prettytable
Requires:         python-setuptools
Requires:         python-warlock

%description
This is a client for the OpenStack Glance API. There's a Python API (the
glanceclient module), and a command-line script (glance). Each implements
100% of the OpenStack Glance API.

%prep
##if [ ! -d python-glanceclient ]; then
    ##git clone ssh://git@bitbucket.org/contrail_admin/python-glanceclient
##else
   ##(cd python-glanceclient; git pull)
##fi

##pushd python-glanceclient

%build
pushd %{_builddir}/..
pushd third_party/python-glanceclient
sed -e 's|^prettytable.*|prettytable|' -i tools/pip-requires
sed -e 's|^python-keystoneclient.*|python-keystoneclient|' -i tools/pip-requires

# Remove bundled egg-info
rm -rf python_glanceclient.egg-info
# let RPM handle deps
sed -i '/setup_requires/d; /install_requires/d; /dependency_links/d' setup.py

%{__python} setup.py build

%install
pushd %{_builddir}/..
pushd third_party/python-glanceclient
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

%files
#%doc README.rst
#%doc LICENSE
%{_bindir}/glance
%{python_sitelib}/glanceclient
%{python_sitelib}/*.egg-info

%changelog
* Mon Feb 18 2013 Dan Prince <dprince@redhat.com> 1:0.7.0-2
- Remove versioninfo move command from spec.

* Wed Jan 30 2013 Alan Pevec <apevec@redhat.com> 1:0.7.0-1
- Update to 0.7.0

* Fri Nov 23 2012 Alan Pevec <apevec@redhat.com> 1:0.6.0-1
- Update to 0.6.0

* Sat Sep 15 2012 Alan Pevec <apevec@redhat.com> 1:0.5.1-1
- Update to 0.5.1

* Wed Aug 22 2012 Alan Pevec <apevec@redhat.com> 1:0.4.1-1
- Add dependency on python-setuptools (#850844)
- Revert client script rename, old glance client is now deprecated.
- New upstream release.

* Fri Aug 03 2012 Alan Pevec <apevec@redhat.com> 2012.2-0.3.f1
- rename client script to avoid conflict with old glance client

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2012.2-0.2.f1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun 06 2012 Pádraig Brady <P@draigBrady.com> 2012.2-0.1.f1
- Initial (folsom-1) release
