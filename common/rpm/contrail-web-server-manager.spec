# view contents of rpm file: rpm -qlp <filename>.rpm

%define		_contrailwebsrc 	/usr/src/contrail/contrail-web-server-manager

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

Requires:	redis
Requires:	supervisor
Requires:	contrail-web-core >= %{_verstr}-%{_relstr}

Obsoletes:      contrail-webui

Source:		%{name}

%description
Contrail Web Server Manager UI package

%prep

#%setup -n %{name}
%build
##cd %{_sourcedir}/%{name}/contrail-ui
##make package

%install
rm -rf %{buildroot}%{_contrailwebsrc}
mkdir -p %{buildroot}%{_contrailwebsrc}

pushd %{_builddir}/..
cp -r -p contrail-web-server-manager/* %{buildroot}%{_contrailwebsrc}/

ln -s %{_libdir}/node_modules %{buildroot}%{_contrailwebsrc}/node_modules

%clean
rm -rf %{buildroot}
rm -rf %{_specdir}/contrail-web-server-manager.spec

%files
%defattr(-,root,root)
%{_contrailwebsrc}/*

%post
%if 0%{?rhel}
%else
/bin/systemctl daemon-reload
%endif

%preun
if [ $1 = 1 ] ; then 
	echo "Upgrading contrail-web-server-manager Package"
%if 0%{?rhel}
	/etc/init.d/supervisor-webui restart
%else
	/bin/systemctl restart supervisor-webui.service
%endif
elif [ $1 = 0 ] ; then
	echo "Removing contrail-web-server-manager Package"
%if 0%{?rhel}
	/etc/init.d/supervisor-webui stop
%else
	/bin/systemctl stop supervisor-webui.service
	/bin/systemctl --no-reload disable supervisor-webui.service
%endif
fi
exit 0

%changelog
* Wed Sep 24 2014 - czanpure@juniper.net
- first release

