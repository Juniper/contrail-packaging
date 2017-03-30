# view contents of rpm file: rpm -qlp <filename>.rpm

%define		_contrailwebsrc 	/usr/src/contrail/contrail-web-server-manager
%define     _contrailetc    /etc/contrail
%define     _distropkgdir tools/packaging/common/control_files
%define     _supervisordir /etc/contrail/supervisord_webui_sm_files

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

Name:		contrail-web-server-manager
Version:	%{_verstr}
Release:	%{_relstr}
Summary:	Contrail Web Server Manager UI %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	supervisor >= 3.0-9.2
Requires:	contrail-web-core >= %{_verstr}-%{_relstr}


Source:		%{name}

%description
Contrail Web Server Manager UI package

%prep

%build

%install
rm -rf %{buildroot}%{_contrailwebsrc}
mkdir -p %{buildroot}%{_contrailwebsrc}
mkdir -p %{buildroot}%{_contrailetc}
mkdir -p %{buildroot}%{_servicedir}
mkdir -p %{buildroot}%{_initddir}

pushd %{_builddir}/..
cp -r -p contrail-web-server-manager/* %{buildroot}%{_contrailwebsrc}/
install -p -m 755 contrail-web-core/config/config.global.js %{buildroot}%{_contrailetc}/config.global.sm.js

%if 0%{?fedora} >= 17
install -p -m 755 %{_distropkgdir}/supervisor-webui-sm.service  %{buildroot}%{_servicedir}/supervisor-webui-sm.service
%endif
%if 0%{?rhel}
install -p -m 755 %{_distropkgdir}/supervisor-webui-sm.initd %{buildroot}%{_initddir}/supervisor-webui-sm
install -p -m 755 %{_distropkgdir}/contrail-webui-sm.initd.supervisord          %{buildroot}%{_initddir}/contrail-webui-sm
install -p -m 755 %{_distropkgdir}/contrail-webui-middleware-sm.initd.supervisord %{buildroot}%{_initddir}/contrail-webui-middleware-sm    
%endif

ln -s %{_libdir}/node_modules %{buildroot}%{_contrailwebsrc}/node_modules
#install .ini files for supervisord
install -d -m 755 %{buildroot}%{_supervisordir}
install -p -m 755 %{_distropkgdir}/supervisord_webui_sm.conf %{buildroot}%{_contrailetc}/supervisord_webui_sm.conf
install -p -m 755 %{_distropkgdir}/contrail-webui-sm.ini %{buildroot}%{_supervisordir}/contrail-webui-sm.ini
install -p -m 755 %{_distropkgdir}/contrail-webui-middleware-sm.ini %{buildroot}%{_supervisordir}/contrail-webui-middleware-sm.ini

%clean
rm -rf %{buildroot}
rm -rf %{_specdir}/contrail-web-server-manager.spec

%files
%defattr(-,root,root)
%{_contrailwebsrc}/*
%config(noreplace) %{_contrailetc}/*
%{_initddir}/*
%config(noreplace) %{_supervisordir}/*

%post
mkdir -p /var/log/contrail/

exit 0

%changelog
* Wed Sep 24 2014 - czanpure@juniper.net
- first release

