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

%define         _installdir  /usr/share/contrail-tripleo-heat-templates/

%{echo: "Building release %{_relstr}\n"}

Name:           contrail-tripleo-heat-templates
Version:        %{_verstr}
Release:        %{_relstr}%{?dist}
Summary:        heat templates for tripleo composable roles deployment%{?_gitVer}
Group:          Applications/System
License:        Commercial
URL:            http://www.juniper.net
Vendor:         Juniper Networks Inc

BuildArch:      noarch
    
%description
Contrail heat templates for tripleo composable roles deployment
    
%install
rm -rf %{buildroot}%{_installdir}
install -d -m 0755 %{buildroot}%{_installdir}
cp -rp  %{_builddir}/../tools/contrail-tht/* %{buildroot}%{_installdir}

%files
%defattr(-, root, root)
%{_installdir}*

%changelog

