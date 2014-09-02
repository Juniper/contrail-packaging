%define         _distrothirdpartydir distro/third_party

%define         _relstr      2contrail
%{echo: "Building release %{_relstr}\n"}
%if 0%(grep -c Xen /etc/redhat-release)
%define		dist	.xen
%endif

Summary: redis-py %{?_gitVer}
Name: redis-py 
Version: 0.1
Release: %{_relstr}%{?dist}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

BuildRequires: python-pip
Requires: python-bitarray >= 0.8.0
Requires: python-gevent
Requires: python-keystone
Requires: python-requests
Requires: python-zope-interface

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages
%description

%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}

# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=contrail-controller
grep $gitrepo .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "please run rpmbuild from ctrlplane git tree"
    exit -1
fi


%build
pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/redis-2.8.0
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/redis
%{python_sitelib}/redis*egg-info

%post
if [ $1 -eq 1 ] ; then
   /bin/systemctl daemon-reload > /dev/null
fi

%changelog
* Mon Dec 17 2012 Pedro Marques <roque@build01> - config-1
- Initial build.

