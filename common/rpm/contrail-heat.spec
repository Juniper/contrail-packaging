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

Name:		    contrail-heat
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail Heat Resources and Templates%{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

%description
Contrail Heat Resources and Templates package

%install
pushd %{_builddir}/../openstack/contrail-heat
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/contrail_heat*
/usr/lib/heat

%post
