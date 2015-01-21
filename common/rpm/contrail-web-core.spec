# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _distropkgdir tools/packaging/common/control_files
%define		_contrailetc 		/etc/contrail
%define		_contrailwebsrc 	/usr/src/contrail/contrail-web-core
%if 0%{?fedora} >= 17
%define		_servicedir  		/usr/lib/systemd/system
%endif
%define		_nodemodules		node_modules/
%define		_config			contrail-web-core/config
%define		_contrailuitoolsdir	src/tools
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

Name:		contrail-web-core
Version:	%{_verstr}
Release:	%{_relstr}
Summary:	Contrail Web UI %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	redis
Requires:	nodejs >= 0.8.15-1%{?dist}
Requires:	supervisor

Obsoletes:      contrail-webui

Source:		%{name}

%description
Contrail Web UI package

%prep

#%setup -n %{name}
%build
##cd %{_sourcedir}/%{name}/contrail-ui
##make package

%install
rm -rf %{buildroot}%{_contrailwebsrc}
%if 0%{?fedora} >= 17
rm -rf %{buildroot}%{_servicedir}
%endif
%if 0%{?rhel}
install -d -m 755 %{buildroot}%{_initddir}
%endif
rm -rf %{buildroot}%{_libdir}/node_modules
rm -rf %{buildroot}%{_contrailetc}

mkdir -p %{buildroot}%{_contrailwebsrc}
%if 0%{?fedora} >= 17
mkdir -p %{buildroot}%{_servicedir}
%endif
mkdir -p %{buildroot}%{_libdir}/node_modules
mkdir -p %{buildroot}%{_contrailetc}

#cp -r -p %{_sourcedir}/%{name}/contrail-ui/* %{buildroot}%{_contrailwebsrc}/
pushd %{_builddir}/..
cp -r -p contrail-web-core/* %{buildroot}%{_contrailwebsrc}/

%if 0%{?fedora} >= 17
cp -p %{_distropkgdir}/supervisor-webui.service  %{buildroot}%{_servicedir}/supervisor-webui.service
%endif
%if 0%{?rhel}
install -p -m 755 %{_distropkgdir}/supervisor-webui.initd %{buildroot}%{_initddir}/supervisor-webui
install -p -m 755 %{_distropkgdir}/contrail-webui.initd.supervisord          %{buildroot}%{_initddir}/contrail-webui
install -p -m 755 %{_distropkgdir}/contrail-webui-middleware.initd.supervisord %{buildroot}%{_initddir}/contrail-webui-middleware
%endif
cp -p %{_distropkgdir}/contrailWebServer.sh %{buildroot}%{_contrailwebsrc}/
cp -p %{_distropkgdir}/contrailWebMiddleware.sh %{buildroot}%{_contrailwebsrc}/
#cp -r -p %{_distropkgdir}/%{name}/%{_nodemodules}/* %{buildroot}%{_libdir}/node_modules
cp -r -p %{buildroot}%{_contrailwebsrc}/%{_nodemodules}/* %{buildroot}%{_libdir}/node_modules
rm -rf  %{buildroot}%{_contrailwebsrc}/node_modules
ln -s %{_libdir}/node_modules %{buildroot}%{_contrailwebsrc}/node_modules
rm %{buildroot}%{_contrailwebsrc}/config/config.global.js
cp -p %{_config}/config.global.js %{buildroot}%{_contrailetc}/
ln -s %{_contrailetc}/config.global.js %{buildroot}%{_contrailwebsrc}/config/config.global.js
perl -pi -e '{ s/opencontrail-logo/juniper-networks-logo/g; }' %{buildroot}%{_contrailetc}/config.global.js
perl -pi -e '{ s/opencontrail-favicon/juniper-networks-favicon/g; }' %{buildroot}%{_contrailetc}/config.global.js
rm %{buildroot}%{_contrailwebsrc}/config/userAuth.js
cp -p %{_config}/userAuth.js %{buildroot}%{_contrailetc}/contrail-webui-userauth.js
ln -s %{_contrailetc}/contrail-webui-userauth.js %{buildroot}%{_contrailwebsrc}/config/userAuth.js

#install .ini files for supervisord
install -d -m 755 %{buildroot}%{_supervisordir}
install -p -m 755 %{_distropkgdir}/supervisord_webui.conf %{buildroot}%{_contrailetc}/supervisord_webui.conf
install -p -m 755 %{_distropkgdir}/contrail-webui.ini %{buildroot}%{_supervisordir}/contrail-webui.ini
install -p -m 755 %{_distropkgdir}/contrail-webui-middleware.ini %{buildroot}%{_supervisordir}/contrail-webui-middleware.ini

%clean
rm -rf %{buildroot}
rm -rf %{_distropkgdir}/contrailWebServer.sh
rm -rf %{_distropkgdir}/contrailWebMiddleware.sh
rm -rf %{_distropkgdir}/contrail-webui.service
rm -rf %{_distropkgdir}/contrail-webui-middleware.service
rm -rf %{_specdir}/contrail-webui.spec

%files
%defattr(-,root,root)
%{_contrailwebsrc}/*
%if 0%{?fedora} >= 17
%{_servicedir}/*
%endif
%if 0%{?rhel}
%{_initddir}/*
%endif
%{_libdir}/*
%config(noreplace) %{_contrailetc}/config.global.js
%config(noreplace) %{_contrailetc}/contrail-webui-userauth.js
%config(noreplace) %{_supervisordir}/*
%config(noreplace) %{_contrailetc}/supervisord_webui.conf

%post
%if 0%{?rhel}
%else
/bin/systemctl daemon-reload
%endif

%preun
if [ $1 = 1 ] ; then 
	echo "Upgrading contrail-webui Package"
%if 0%{?rhel}
	/etc/init.d/supervisor-webui restart
%else
	/bin/systemctl restart supervisor-webui.service
%endif
elif [ $1 = 0 ] ; then
	echo "Removing contrail-webui Package"
%if 0%{?rhel}
	/etc/init.d/supervisor-webui stop
%else
	/bin/systemctl stop supervisor-webui.service
	/bin/systemctl --no-reload disable supervisor-webui.service
%endif
fi
exit 0

%changelog
* Tue Jan 30 2013 - bmandal@contrailsystems.com
- Added log file in package.
* Fri Jan 18 2013 - bmandal@contrailsystems.com
- first release

