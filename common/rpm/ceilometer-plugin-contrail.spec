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

Name:		    ceilometer-plugin-contrail
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Ceilometer Contrail Plugin%{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch
BuildRequires: python-devel
Requires: python-ceilometer

%description
Ceilometer Contrail Plugin Package

%install
pushd %{_builddir}/../openstack/ceilometer_plugin
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/ceilometer_plugin_contrail*

%post
