%define         _distrothirdpartydir distro/third_party

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}

Summary: xmltodict %{?_gitVer}
Name: xmltodict 
Version: 0.1
Release: %{_relstr}%{?dist}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

BuildRequires: python-pip
Requires: python-bitarray
Requires: python-gevent
Requires: python-pycassa
Requires: python-keystone
Requires: python-requests
Requires: python-zope-interface

Requires:           contrail-analytics-venv
Requires:           contrail-api-venv
%define             _venv_archv        /opt/contrail/api-venv/archive
%define             _anl_venv_archv    /opt/contrail/analytics-venv/archive
%define             _vrouter_venv_archv    /opt/contrail/vrouter-venv/archive
%define             _control_venv_archv    /opt/contrail/control-venv/archive

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
install -D -m 644 dist/xmltodict-0.7.0.tar.gz %{buildroot}%{_venv_archv}/xmltodict-0.7.0.tar.gz
install -D -m 644 dist/xmltodict-0.7.0.tar.gz %{buildroot}%{_anl_venv_archv}/xmltodict-0.7.0.tar.gz
install -D -m 644 dist/xmltodict-0.7.0.tar.gz %{buildroot}%{_control_venv_archv}/xmltodict-0.7.0.tar.gz
install -D -m 644 dist/xmltodict-0.7.0.tar.gz %{buildroot}%{_vrouter_venv_archv}/xmltodict-0.7.0.tar.gz
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/xmltodict*
%{_venv_archv}/xmltodict-0.7.0.tar.gz
%{_anl_venv_archv}/xmltodict-0.7.0.tar.gz
%{_vrouter_venv_archv}/xmltodict-0.7.0.tar.gz
%{_control_venv_archv}/xmltodict-0.7.0.tar.gz

%post
if [ $1 -eq 1 ] ; then
   /bin/systemctl daemon-reload > /dev/null
fi

