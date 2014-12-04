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
mkdir -p /var/log/contrail/

exit 0

%changelog
* Wed Sep 24 2014 - czanpure@juniper.net
- first release

