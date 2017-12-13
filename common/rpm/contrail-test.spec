# RPM Spec file for contrail-test.rpm
# view contents of rpm file: rpm -qlp <filename>.rpm

%{echo: "Building release %{_relstr}\n"}
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
%if 0%{?_skuTag:1}
%define         _sku     %{_skuTag}
%else
%define         _sku      None
%endif

Name:		    contrail-test
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail Test %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

# Add all requires for contrail-test
#Requires:	    python-subunit
AutoReqProv: yes

%description
Contrail Test
Sanity and Regression Suite for Contrail

%prep

%build

%install
# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}

# install files
cp -a %{_builddir}/../third_party/contrail-test %{buildroot}/contrail-test
cp -a %{_builddir}/../tools/contrail-test-ci %{buildroot}/contrail-test-ci
rm -rf %{buildroot}/contrail-test/.git*
rm -rf %{buildroot}/contrail-test-ci/.git*
exit 0

%post
# Add post installation scripts if any

%files
%defattr(-, root, root)
/contrail-test
/contrail-test-ci

%changelog
* Tue Dec 12 2017 Nagendra Maynattamai <npchandran@juniper.net>
- Initial Draft for Contrail Test Package
