%define         _contrailetc /etc/contrail
%define         _contrailcontrol /opt/contrail/control-node
%define         _supervisordir /etc/contrail/supervisord_control_files
%define         _distropkgdir tools/packaging/common/control_files

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
Summary: Contrail Openstack Control %{?_gitVer}
Name: contrail-openstack-control
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-control
Requires: contrail-lib
Requires: contrail-dns
Requires: contrail-setup
Requires: contrail-nodemgr
Requires: python-contrail

%description
Contrail Package Requirements for Control Node

%install
# Setup directories
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_contrailcontrol}
install -d -m 755 %{buildroot}%{_supervisordir}

pushd %{_builddir}/..

install -D -m 755 %{_distropkgdir}/supervisor-control.initd %{buildroot}%{_initddir}/supervisor-control
install -D -m 755 %{_distropkgdir}/contrail-control.initd.supervisord %{buildroot}%{_initddir}/contrail-control
%if 0%{?rhel}
install -D -m 755 %{_distropkgdir}/supervisor-control.initd %{buildroot}%{_initddir}/supervisor-control
install -D -m 755 %{_distropkgdir}/contrail-control.initd.supervisord %{buildroot}%{_initddir}/contrail-control
%endif

#install nstall .ini files for supervisord
install -p -m 755 %{_distropkgdir}/supervisord_control.conf %{buildroot}%{_contrailetc}/supervisord_control.conf
install -p -m 755 %{_distropkgdir}/contrail-control.ini %{buildroot}%{_supervisordir}/contrail-control.ini

install -D -m 644 %{_distropkgdir}/control_param %{buildroot}/etc/contrail/control_param
install -p -m 755 %{_distropkgdir}/contrail-control.rules %{buildroot}%{_supervisordir}/contrail-control.rules

%files
%defattr(-,root,root,-)
%{_supervisordir}
%config(noreplace) %{_contrailetc}/supervisord_control.conf
%if 0%{?rhel}
%{_initddir}/supervisor-control
%{_initddir}/contrail-control
%endif

%config(noreplace) /etc/contrail/control_param
%config(noreplace) %{_supervisordir}/contrail-control.ini

%post
(umask 007; /bin/echo "HOSTNAME=$(hostname)" >> /etc/contrail/control_param)
if [ -x /bin/systemctl ]; then
   /bin/systemctl --system daemon-reload
fi

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

