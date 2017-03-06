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
rm -rf %{_builddir}/usr/share/contrail-tripleo-heat-templates/
install -d -m 0755 %{_builddir}/usr/share/contrail-tripleo-heat-templates/
cp -rp  %{_builddir}/../tools/contrail-tht/* %{_builddir}/usr/share/contrail-tripleo-heat-templates/

%files
%defattr(-, root, root)
/usr/share/contrail-tripleo-heat-templates/*

%changelog

