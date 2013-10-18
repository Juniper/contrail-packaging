# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailetc /etc/contrail
%define         _distropkgdir tools/packaging/common/control_files

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif

%if 0%(grep -c Xen /etc/redhat-release)
%define		dist	.xen
%endif

%if 0%(grep -c CentOS /etc/redhat-release)
%define     dist    .centos
%endif

%{echo: "Building release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif

BuildArch: noarch

Name:		    contrail-interface-name
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail Consistent Interface Naming Scheme %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	    sudo
Requires:	    patch

%if 0%{?rhel}
Requires:           NetworkManager
%endif

%description
Contrail Consistent Interface Naming Scheme

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

%install

# Setup directories
rm -rf %{buildroot}

# install etc files
pushd %{_builddir}/..
if [ "%{?dist}" != ".xen" ]; then
install -D -m 755 %{_distropkgdir}/contrail_ifrename.sh      %{buildroot}%{_contrailetc}/contrail_ifrename.sh
if [ "%{?dist}" = ".centos" ];then
install -D -m 755 %{_distropkgdir}/72-contrail-net.rules     %{buildroot}/lib/udev/rules.d/72-contrail-net.rules
else
install -D -m 755 %{_distropkgdir}/72-contrail-net.rules     %{buildroot}/usr/lib/udev/rules.d/72-contrail-net.rules
fi
fi

%files
%defattr(-, root, root)

%if "%{?dist}%{!?dist:0}" != ".xen" 
%{_contrailetc}/contrail_ifrename.sh
%if "%{?dist}%{!?dist:0}" == ".centos" 
/lib/udev/rules.d/72-contrail-net.rules
%else
/usr/lib/udev/rules.d/72-contrail-net.rules
%endif
%endif

%changelog

