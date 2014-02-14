%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif

%if 0%(grep -c Xen /etc/redhat-release)
%define		dist	.xen
%endif

%{echo: "Building release %{_relstr}\n"}

Name:		    contrail-nova-vif
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail nova vif driver %{?_gitVer} 

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

%description
Contrail Nova Vif driver package

%build
scons -U nova-contrail-vif

%install
pushd %{_builddir}/../build/noarch/nova_contrail_vif
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/nova_contrail_vif*


