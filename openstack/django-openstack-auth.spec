%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}

Name:             python-django-openstack-auth
Epoch:            1
Version:          1.0.6
Release:          %{_relstr}
Summary:          A Django authentication backend %{?_gitVer}

Group:            Development/Languages
License:          BSD
URL:              http://pypi.python.org/pypi/django_openstack_auth/1.0.6
#Source1:          git_root_auth
Source0:          django_openstack_auth-1.0.6.tar.gz

BuildArch:        noarch
BuildRequires:    python-setuptools

%description
A Django authentication backend for use with the OpenStack Keystone Identity
backend

%prep
# start from git root_auth .. run this
#       git rev-parse --show-toplevel > ~/rpmbuild/SOURCES/git_root_auth
pwd

#pushd $( cat %{SOURCE1} )

# make sure we are in django-openstack-auth repo
##gitrepo=django-openstack-auth.git
##/bin/grep -- $gitrepo .git/config &> /dev/null
##if [ $? -ne 0 ]; then
    ##echo "please run rpmbuild from django-openstack-auth git tree"
    ##exit -1
##fi

##popd

echo untar-ing
%setup -q -n django_openstack_auth-1.0.6
echo untared

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

%files
#%doc README.rst
#%doc LICENSE
%{python_sitelib}/openstack_auth/
%{python_sitelib}/*.egg-info

%changelog
* Mon Jan 7 2013 Praneet <praneet@localhost> 
- Initial Checkin
