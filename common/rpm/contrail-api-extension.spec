%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif

Release:	    %{_relstr}%{?dist}
Summary: Contrail API Extensions%{?_gitVer}
Name: contrail-api-extension
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-api-venv
%define _venv_root    /opt/contrail/api-venv
%define _venvtr       --prefix=%{_venv_root}

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
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi


%build
scons -U src/config/vnc_openstack

%define _build_dist %{_builddir}/../build/debug
%install
install -d -m 755 %{buildroot}%{_venv_root}

mkdir -p build/python_dist
pushd build/python_dist

tar zxf %{_build_dist}/config/vnc_openstack/dist/vnc_openstack-0.1dev.tar.gz
pushd vnc_openstack-0.1dev
%{__python} setup.py install --root=%{buildroot} %{?_venvtr}
popd

%files
%defattr(-,root,root,-)
%{_venv_root}%{_pysitepkg}/vnc_openstack
%{_venv_root}%{_pysitepkg}/vnc_openstack-*

%post

%changelog
* Mon Sep 9 2013 Praneet Bachheti <praneetb@juniper.net>
- Initial build.

