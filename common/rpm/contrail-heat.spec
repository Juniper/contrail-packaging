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

install -d -m 755 %{buildroot}/usr/lib/heat/resources
install -d -m 755 %{buildroot}/usr/lib/heat/template
for s in resources template ; do
    for f in %{_builddir}/../openstack/contrail-heat/contrail_heat/$s/* ; do
	install -p -m 755 $f %{buildroot}/usr/lib/heat/$s
    done
done

%files
%defattr(-,root,root,-)
%{python_sitelib}/contrail_heat*
/usr/lib/heat

%post
