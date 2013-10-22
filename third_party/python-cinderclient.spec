%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}

Name:             python-cinderclient
Version:          1.0.2
Release:          %{_relstr}
Summary:          Python API and CLI for OpenStack cinder %{?_gitVer}

Group:            Development/Languages
License:          ASL 2.0
URL:              http://github.com/openstack/python-cinderclient
#Source0:          http://tarballs.openstack.org/%{name}/%{name}-%{version}.tar.gz

#
# patches_base=0.2
#

BuildArch:        noarch
BuildRequires:    python-setuptools

Requires:         python-httplib2
Requires:         python-prettytable
Requires:         python-setuptools

%description
This is a client for the OpenStack cinder API. There's a Python API (the
cinderclient module), and a command-line script (cinder). Each implements
100% of the OpenStack cinder API.

%prep
## if [ -d python-cinderclient ]; then
   ## (cd python-cinderclient; git pull)
## else
   ## git clone git@bitbucket.org:contrail_admin/python-cinderclient.git
## fi


%build
pushd %{_builddir}/..
pushd third_party/python-cinderclient
rm -rf python_cinderclient.egg-info
%{__python} setup.py build

%install
pushd %{_builddir}/..
pushd third_party/python-cinderclient
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

install -p -D -m 644 tools/cinder.bash_completion %{buildroot}%{_sysconfdir}/bash_completion.d/cinder.bash_completion

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

%files
%{_sysconfdir}/bash_completion.d/cinder.bash_completion
## %doc python-cinderclient/README.rst
## %doc python-cinderclient/LICENSE
%{_bindir}/cinder
%{python_sitelib}/cinderclient
%{python_sitelib}/*.egg-info

%changelog
* Mon Jan 14 2013 Eric Harney <eharney@redhat.com> 1.0.2-1
- Add bash completion support
- Update to latest client

* Mon Sep 25 2012 Pádraig Brady <P@draigBrady.com> 0.2.26-1
- Update to latest client to support latest cinder

* Mon Sep  3 2012 Pádraig Brady <P@draigBrady.com> 0.2-2
- Initial release
