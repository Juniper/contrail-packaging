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

Requires: contrail-api-lib
Requires: contrail-web-core
Requires: contrail-web-controller
Requires: contrail-setup

%description
Contrail Package Requirements for WebUI

%post
if [ -d /usr/src/contrail/contrail-webui ] ; then
    rm -rf /usr/src/contrail/contrail-webui
fi

%files

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

