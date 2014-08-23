%define         _distropkgdir tools/packaging/common/control_files
%define         _contrailetc            /etc/contrail
%define         _contrailwebsrc         /usr/src/contrail/contrail-webui
%if 0%{?fedora} >= 17
%define         _servicedir             /usr/lib/systemd/system
%endif
%define         _nodemodules            node_modules/
%define         _config                 contrail-web-core/config
%define         _contrailuitoolsdir     src/tools
%define         _supervisordir /etc/contrail/supervisord_webui_files

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
Release:	    %{_relstr}%{?dist}
Summary: Contrail Openstack Webui %{?_gitVer}
Name: contrail-openstack-webui
Version:	    %{_verstr}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: python-contrail >= %{_verstr}-%{_relstr}
Requires: contrail-web-core >= %{_verstr}-%{_relstr}
Requires: contrail-web-controller >= %{_verstr}-%{_relstr}
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}

%description
Contrail Package Requirements for WebUI

%install
pushd %{_builddir}/..
install -d -m 755 %{buildroot}%{_contrailetc}
#install -d -m 755 %{buildroot}%{_initddir}
install -p -m 755 %{_distropkgdir}/supervisord_webui.conf %{buildroot}%{_contrailetc}/supervisord_webui.conf
#install -p -m 755 %{_distropkgdir}/supervisor-webui.conf %{buildroot}%{_initddir}/supervisor-webui.conf

%files
%defattr(-,root,root)
%config(noreplace) %{_contrailetc}/supervisord_webui.conf
#%config(noreplace) %{_initddir}/supervisor-webui.conf
 
%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

