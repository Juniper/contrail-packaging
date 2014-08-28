%define         _distrothirdpartydir distro/third_party

%define         _relstr     0contrail 
%{echo: "Building release %{_relstr}\n"}

Summary: xmltodict %{?_gitVer}
Name: xmltodict 
Version: 0.7.0
Release: %{_relstr}%{?dist}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

BuildRequires: python-pip
Requires: python-bitarray >= 0.8.0
Requires: python-gevent
Requires: python-pycassa
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
pushd %{_builddir}/
gitrepo=contrail-controller
grep $gitrepo .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "please run rpmbuild from ctrlplane git tree"
    exit -1
fi


%build
pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/xmltodict-0.7.0
%{__python} setup.py install --root=%{buildroot}
%{__python} setup.py sdist
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/xmltodict*

%post
if [ $1 -eq 1 ] ; then
   /bin/systemctl daemon-reload > /dev/null
fi

