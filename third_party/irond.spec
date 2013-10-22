Summary: IFMap server %{?_gitVer}
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}

Name: irond
Version: 1.0
License: Apache License, Version 2.0
Release: %{_relstr}
Group: Contrail
URL: http://trust.inform.fh-hannover.de
Source0: %{name}-%{version}.tar.gz
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildArch: noarch
BuildRequires: ant

Requires: jre >= 1.6
Requires: log4j
Requires: slf4j
Requires: apache-commons-codec

%description

%prep
##if [ ! -d ifmap-server  ]; then
    ##git clone ssh://git@bitbucket.org/contrail_admin/ifmap-server
##else
    ##(cd ifmap-server; git pull)
##fi

%build
pushd %{_builddir}/..
pushd third_party/ifmap-server
ant

%install
pushd %{_builddir}/..
pushd third_party/ifmap-server
install -p -D -m 640 build/irond.jar %{buildroot}%{_libexecdir}/irond.jar
install -d -m 755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} << EOF
#!/bin/sh
java -jar %{_libexecdir}/irond.jar
(cd %{_datadir}/%{name}; /usr/bin/java -Dlog4j.configuration=file:///%{_sysconfdir}/%{name}/log4j.properties -jar /usr/libexec/irond.jar)
EOF

chmod 755 %{buildroot}%{_bindir}/%{name}
install -d -m 755 %{buildroot}%{_datadir}/%{name}/schema
install -d -m 755 %{buildroot}%{_datadir}/%{name}/keystore
install -d -m 755 %{buildroot}%{_datadir}/%{name}/lib
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}/
install -p -D -m 644 schema/*.xsd %{buildroot}%{_datadir}/%{name}/schema
install -p -D -m 644 schema/ifmap-2.0.wsdl %{buildroot}%{_datadir}/%{name}/schema
install -p -D -m 644 ifmap.properties %{buildroot}%{_sysconfdir}/%{name}/ifmap.properties.rpmsave
install -p -D -m 644 log4j.properties %{buildroot}%{_sysconfdir}/%{name}/log4j.properties.rpmsave
install -p -D -m 644 publisher.properties %{buildroot}%{_sysconfdir}/%{name}/publisher.properties.rpmsave
install -p -D -m 644 authorization.properties %{buildroot}%{_sysconfdir}/%{name}/authorization.properties.rpmsave
install -p -D -m 644 basicauthusers.properties %{buildroot}%{_sysconfdir}/%{name}/basicauthusers.properties.rpmsave
install -p -D -m 644 keystore/irond.jks %{buildroot}%{_datadir}/%{name}/keystore
install -p -D -m 644 keystore/irond.pem %{buildroot}%{_datadir}/%{name}/keystore
install -p -D -m 644 keystore/irond.pem %{buildroot}%{_datadir}/%{name}/keystore
install -p -D -m 644 lib/astyanax-0.8.12-SNAPSHOT.jar %{buildroot}%{_datadir}/%{name}/lib
install -p -D -m 644 lib/guava-12.0.jar %{buildroot}%{_datadir}/%{name}/lib
install -p -D -m 644 lib/high-scale-lib-1.1.2.jar %{buildroot}%{_datadir}/%{name}/lib
install -p -D -m 644 lib/httpcore-4.2.jar %{buildroot}%{_datadir}/%{name}/lib
install -p -D -m 644 lib/commons-codec-1.5.jar %{buildroot}%{_datadir}/%{name}/lib/commons-codec.jar
install -p -D -m 644 lib/log4j-1.2.16.jar %{buildroot}%{_datadir}/%{name}/lib/log4j.jar
install -p -D -m 755 ifmap.ini %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/ifmap.ini
install -p -D -m 755 ifmap.kill %{buildroot}%{_sysconfdir}/contrail/supervisord_config_files/ifmap.kill
install -p -D -m 755 ifmap.initd.supervisord %{buildroot}/etc/init.d/ifmap

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc
%{_bindir}/%{name}
%{_libexecdir}/irond.jar
%{_sysconfdir}/%{name}/*.properties.rpmsave
%{_datadir}/%{name}/schema
%{_datadir}/%{name}/keystore
%{_datadir}/%{name}/lib
%{_sysconfdir}/contrail/supervisord_config_files/ifmap.ini
%{_sysconfdir}/contrail/supervisord_config_files/ifmap.kill
/etc/init.d/ifmap

%post
%if 0%{?fedora} >= 17
if [ $1 -eq 1 ] ; then
   /bin/systemctl daemon-reload > /dev/null
fi
%endif

[ -f %{_sysconfdir}/%{name}/ifmap.properties ] || mv %{_sysconfdir}/%{name}/ifmap.properties.rpmsave  %{_sysconfdir}/%{name}/ifmap.properties
[ -f %{_sysconfdir}/%{name}/log4j.properties ] || mv %{_sysconfdir}/%{name}/log4j.properties.rpmsave  %{_sysconfdir}/%{name}/log4j.properties
[ -f %{_sysconfdir}/%{name}/publisher.properties ] || mv %{_sysconfdir}/%{name}/publisher.properties.rpmsave  %{_sysconfdir}/%{name}/publisher.properties
[ -f %{_sysconfdir}/%{name}/authorization.properties ] || mv %{_sysconfdir}/%{name}/authorization.properties.rpmsave  %{_sysconfdir}/%{name}/authorization.properties
[ -f %{_sysconfdir}/%{name}/basicauthusers.properties ] || mv %{_sysconfdir}/%{name}/basicauthusers.properties.rpmsave  %{_sysconfdir}/%{name}/basicauthusers.properties

%changelog
* Wed Dec 12 2012 Pedro Marques <roque@build02> - 
- Initial build.

