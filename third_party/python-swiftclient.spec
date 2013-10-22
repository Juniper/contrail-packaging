%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}

Name:       python-swiftclient
Version:    2012.2
Release:    %{_relstr}
Summary:    Python API and CLI for OpenStack Swift %{?_gitVer}

Group:      Development/Languages
License:    ASL 2.0
URL:        https://github.com/openstack/python-swiftclient

# Source URL is https://github.com/openstack/python-swiftclient/tarball/1.0
# which produces  Content-Disposition: attachment; filename=XXXXXX.tar.gz.
# But wait! The extracted directory name is different from tarball name.
#Source0:    openstack-python-swiftclient-1.0-0-gc9dfd14.tar.gz

BuildArch:  noarch
BuildRequires: python2-devel
BuildRequires: python-setuptools

Requires: python-keystoneclient

%description
Client library and command line utility for interacting with Openstack
Swift object storage service.

%prep
#%setup -q
## if [ ! -d python-swiftclient ]; then
    ## git clone ssh://git@bitbucket.org/contrail_admin/python-swiftclient
## else
   ## (cd python-swiftclient; git stash; git pull)
## fi

%build
pushd %{_builddir}/..
pushd third_party/python-swiftclient
%{__python} setup.py build

%install
pushd %{_builddir}/..
pushd third_party/python-swiftclient
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%files
## %doc python-swiftclient/LICENSE python-swiftclient/README.rst
%{_bindir}/swift
%{python_sitelib}/swiftclient
# XXX Do we actually need the egg? The package is installed with RPM.
%{python_sitelib}/*.egg-info

%changelog
* Mon Aug 4 2012 Dan Prince <dprince@redhat.com>
- Add dependency on python-keystoneclient

* Mon Jul 30 2012 Dan Prince <dprince@redhat.com>
- Don't exclude openstack-common (we need it!)

* Thu May 31 2012 Pete Zaitcev <zaitcev@redhat.com>
- 1.0-1
- Initial revision
