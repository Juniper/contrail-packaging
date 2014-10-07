%if 0%{?fedora} >= 17
%define         _servicedir  /usr/lib/systemd/system
%endif

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

Name:             contrail-monitoring
Version:            %{_verstr}
Release:          %{_relstr}%{?dist}
Summary:          Contrail monitoring %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	  python-importlib
Requires:	  python-bottle >= 0.11.6

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages

BuildRequires:    make
BuildRequires:    gcc

%description
Contrail Monitoring package

%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}

# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=contrail-controller
grep $gitrepo %{_builddir}/.git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi

%build
scons -U ipmi:sdist

if [ $? -ne 0 ] ; then
    echo "build failed"
    exit -1
fi

%install

# Setup directories

pushd %{_builddir}/..

# install pysandesh files
%define _build_dist %{_builddir}/../build/noarch
install -d -m 755 %{buildroot}

popd
mkdir -p build/python_dist
pushd build/python_dist

tar zxf %{_build_dist}/monitoring/dist/contrail-ipmi-monitoring-0.1dev.tar.gz
pushd contrail-ipmi-monitoring-0.1dev
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/ipmi*
%{python_sitelib}/contrail_ipmi_monitor*

%post
if [ -x /bin/systemctl ]; then
   /bin/systemctl --system daemon-reload
fi

%changelog
