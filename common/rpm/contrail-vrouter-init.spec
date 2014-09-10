%define         _contrailetc /etc/contrail
%define         _supervisordir /etc/contrail/supervisord_vrouter_files
%define         _distropkgdir tools/packaging/common/control_files
%define 	_opt_bin /opt/contrail/bin 
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

Name:             contrail-vrouter-init
Version:            %{_verstr}
Release:          %{_relstr}%{?dist}
Summary:          Contrail vrouter init %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires: contrail-vrouter >= %{_verstr}-%{_relstr}
Requires: contrail-vrouter-utils >= %{_verstr}-%{_relstr}
Requires: contrail-vrouter-agent >= %{_verstr}-%{_relstr}
Requires: python-contrail-vrouter-api >= %{_verstr}-%{_relstr}
Requires: supervisor
Requires: python-contrail >= %{_verstr}-%{_relstr}

%description
contrail vrouter init packages provides init files 

%install
install -d -m 755 %{buildroot}%{_opt_bin}
install -d -m 755 %{buildroot}%{_supervisordir}
install -d -m 755 %{buildroot}/etc/rc.d/init.d
install -d -m 777 %{buildroot}/var/log/contrail
pushd %{_builddir}/..
install -p -m 755 %{_distropkgdir}/supervisord_vrouter.conf %{buildroot}%{_contrailetc}/supervisord_vrouter.conf
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail-vrouter.kill %{buildroot}%{_supervisordir}/contrail-vrouter.kill
install -p -m 755 %{_distropkgdir}/contrail-vrouter.initd.supervisord %{buildroot}/etc/rc.d/init.d/contrail-vrouter
install -p -m 644 %{_distropkgdir}/contrail-nodemgr-vrouter.ini %{buildroot}%{_supervisordir}
install -p -m 644 %{_distropkgdir}/contrail-vrouter-agent.ini %{buildroot}%{_supervisordir}
install -p -m 644 %{_distropkgdir}/contrail-vrouter.rules %{buildroot}%{_supervisordir}
install -p -m 755 %{_distropkgdir}/vnagent_ExecStartPre.sh  %{buildroot}%{_contrailetc}/vnagent_ExecStartPre.sh
install -p -m 755 %{_distropkgdir}/vnagent_ExecStartPost.sh %{buildroot}%{_contrailetc}/vnagent_ExecStartPost.sh
install -p -m 755 %{_distropkgdir}/vnagent_ExecStopPost.sh  %{buildroot}%{_contrailetc}/vnagent_ExecStopPost.sh
install -p -m 755 %{_distropkgdir}/vnagent_param_setup.sh   %{buildroot}%{_opt_bin}/vnagent_param_setup.sh
install -p -m 755 %{_distropkgdir}/if-vhost0 %{buildroot}%{_opt_bin}/if-vhost0
install -p -m 755 %{_distropkgdir}/vrouter-functions.sh %{buildroot}%{_opt_bin}/vrouter-functions.sh
install -p -m 755 %{_distropkgdir}/contrail_reboot  %{buildroot}/etc/contrail/contrail_reboot
install -p -m 755 %{_distropkgdir}/agent.conf  %{buildroot}/etc/contrail/rpm_agent.conf

%files
/opt/*
/etc/*
/var/*
%dir %attr(0777, contrail, contrail) /var/log/contrail


%post
set -e
kver=`uname -r`
echo "create the agent_param file..."
/opt/contrail/bin/vnagent_param_setup.sh $kver
