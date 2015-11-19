# view contents of rpm file: rpm -qlp <filename>.rpm

%define		_contrailwebsrc 	/usr/src/contrail/contrail-web-controller

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

Name:		contrail-web-controller
Version:	%{_verstr}
Release:	%{_relstr}
Summary:	Contrail Web UI %{?_gitVer}

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
Contrail Web UI package

%prep
command -v node >/dev/null 2>&1 || {
    command -v nodejs >/dev/null 2>&1 || {
        echo >&2 "contrail-web-controller build requires node/nodejs.  Aborting.";
        exit 1;
    }
}
command -v npm >/dev/null 2>&1 || {
    echo >&2 "contrail-web-core UT requires npm. Aborting.";
    exit 1;
}

#%setup -n %{name}
%build
##cd %{_sourcedir}/%{name}/contrail-ui
##make package

%install
rm -rf %{buildroot}%{_contrailwebsrc}
mkdir -p %{buildroot}%{_contrailwebsrc}

pushd %{_builddir}/..
cp -r -p contrail-web-controller/* %{buildroot}%{_contrailwebsrc}/

ln -s %{_libdir}/node_modules %{buildroot}%{_contrailwebsrc}/node_modules

%clean
rm -rf %{buildroot}
rm -rf %{_specdir}/contrail-web-controller.spec

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
	echo "Upgrading contrail-web-controller Package"
%if 0%{?rhel}
	/etc/init.d/supervisor-webui restart
%else
	/bin/systemctl restart supervisor-webui.service
%endif
elif [ $1 = 0 ] ; then
	echo "Removing contrail-web-controller Package"
%if 0%{?rhel}
	/etc/init.d/supervisor-webui stop
%else
	/bin/systemctl stop supervisor-webui.service
	/bin/systemctl --no-reload disable supervisor-webui.service
%endif
fi
exit 0

%changelog
* Mon May 26 2013 - bmandal@juniper.net
- first release

