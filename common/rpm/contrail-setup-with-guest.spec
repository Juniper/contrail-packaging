# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail
%define         _provdir      %{_builddir}/../tools/provisioning

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


Name:		    contrail-setup
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail Setup %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	    tar
Requires:	    python-netifaces

%description
Contrail Setup package with scripts for provisioning

BuildRequires:  systemd-units

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
pushd %{_builddir}/build
#%{__python} tools/provisioning/create_installer.py --embed_vrouter --embed_guest
%{__python} %{_provdir}/create_installer.py --embed_guest
popd

pushd src/config
tar cvfz ../../build/cfgm_utils.tgz utils
popd

%install
pushd %{_builddir}/build

# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_contrailopt}

# install etc files
install -p -m 644 contrail_installer.tgz  %{buildroot}%{_contrailopt}/contrail_installer.tgz
install -p -m 644 cfgm_utils.tgz  %{buildroot}%{_contrailopt}/cfgm_utils.tgz

%post

cd %{_contrailopt}
tar xzvf contrail_installer.tgz

%files
%defattr(-, root, root)
%{_contrailopt}/contrail_installer.tgz
%{_contrailopt}/cfgm_utils.tgz

%changelog

