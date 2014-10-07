%define         _cloudstackutils  /opt/contrail/cloudstack-utils
%define         _utils  /opt/contrail/utils
%define         _distroprovdir    %{_builddir}/../tools/provisioning
%define         _distrocloudstackprovdir  %{_builddir}/../tools/provisioning/cloudstack

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_fileList:1}
%define         _flist      %{_fileList}
%else
%define         _flist      None
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

Name: contrail-cloudstack-utils
Version:            %{_verstr}
Release:            %{_relstr}%{?dist}
Summary:            Contrail Cloudstack Utils %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires: python
Requires: bash

%description
Contrail Cloudstack utilities package

%prep 

%build 

%install
rm -rf %{buildroot}%{_cloudstackutils}

#create cloudstack utils dir
install -d -m 755 %{buildroot}%{_cloudstackutils}
install -d -m 755 %{buildroot}%{_cloudstackutils}/setup_files/

#get all cloudstack utils
install -m 755 %{_distrocloudstackprovdir}/*.sh   %{buildroot}%{_cloudstackutils}
install -m 755 %{_distrocloudstackprovdir}/*.py   %{buildroot}%{_cloudstackutils}
install -m 755 %{_distrocloudstackprovdir}/LICENSE   %{buildroot}%{_cloudstackutils}
install -m 755 %{_distrocloudstackprovdir}/README.md   %{buildroot}%{_cloudstackutils}
install -m 755 %{_distrocloudstackprovdir}/setup_files/* %{buildroot}%{_cloudstackutils}/setup_files/

#Install some other helper scripts in this directory
install -m 755 %{_distroprovdir}/contrail_provisioning/collector/scripts/collector-server-setup.sh %{buildroot}%{_cloudstackutils}
install -m 755 %{_distroprovdir}/contrail_provisioning/webui/scripts/webui-server-setup.sh %{buildroot}%{_cloudstackutils}

# Install the template files necessary for cloudstack
install -d -m 755 %{buildroot}%{_cloudstackutils}/config_templates/
install -m 755 %{_distroprovdir}/templates/* %{buildroot}%{_cloudstackutils}/config_templates/

# TODO: below should be in separate package (We now have contrail-setup package that we can pull)
install -d -m 755 %{buildroot}/opt/contrail/utils
install -m 755 %{_builddir}/src/config/utils/* %{buildroot}/opt/contrail/utils/


%clean
#rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_cloudstackutils}
%{_utils}

%doc


%changelog

