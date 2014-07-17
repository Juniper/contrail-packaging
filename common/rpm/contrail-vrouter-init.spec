%define         _contrailetc /etc/contrail
%define         _supervisordir /etc/contrail/supervisord_vrouter_files
%define         _supervisoropenstackdir /etc/contrail/supervisord_openstack_files
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

Requires: contrail-vrouter
Requires: contrail-vrouter-utils
Requires: contrail-vrouter-agent
Requires: python-contrail-vrouter-api
Requires: supervisor
Requires: python-contrail

%description
contrail vrouter init packages provides init files 

%install
install -d -m 755 %{buildroot}%{_opt_bin}
install -d -m 755 %{buildroot}%{_supervisordir}
install -d -m 755 %{buildroot}/etc/rc.d/init.d
install -d -m 755 %{buildroot}/var/log/contrail
pushd %{_builddir}/..
install -p -m 755 %{_distropkgdir}/supervisord_vrouter.conf %{buildroot}%{_contrailetc}/supervisord_vrouter.conf
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail-vrouter.kill %{buildroot}%{_supervisordir}/contrail-vrouter.kill
install -p -m 644 %{_distropkgdir}/contrail-vrouter.initd.supervisord %{buildroot}/etc/rc.d/init.d/contrail-vrouter
install -p -m 644 %{_distropkgdir}/contrail-vrouter.ini %{buildroot}%{_supervisordir}
install -p -m 644 %{_distropkgdir}/contrail-vrouter.rules %{buildroot}%{_supervisordir}
install -p -m 755 %{_distropkgdir}/vnagent_ExecStartPre.sh  %{buildroot}%{_contrailetc}/vnagent_ExecStartPre.sh
install -p -m 755 %{_distropkgdir}/vnagent_ExecStartPost.sh %{buildroot}%{_contrailetc}/vnagent_ExecStartPost.sh
install -p -m 755 %{_distropkgdir}/vnagent_ExecStopPost.sh  %{buildroot}%{_contrailetc}/vnagent_ExecStopPost.sh
install -p -m 755 %{_distropkgdir}/vnagent_param_setup.sh   %{buildroot}%{_opt_bin}/vnagent_param_setup.sh
install -p -m 755 %{_distropkgdir}/if-vhost0 %{buildroot}%{_opt_bin}/if-vhost0
install -p -m 755 %{_distropkgdir}/vrouter-functions.sh %{buildroot}%{_opt_bin}/vrouter-functions.sh
install -p -m 755 %{_distropkgdir}/contrail_reboot  %{buildroot}/etc/contrail/contrail_reboot
install -p -m 755 %{_distropkgdir}/agent.conf  %{buildroot}/etc/contrail/rpm_agent.conf
# Install supervisord nova config files and directories
install -d -m 755 %{buildroot}%{_supervisoropenstackdir}
install -D -m 755 %{_distropkgdir}/supervisor-openstack.upstart %{buildroot}/etc/init/supervisor-openstack.conf.upstart_vrouter
install -p -m 755 %{_distropkgdir}/nova-compute.initd.supervisord %{buildroot}/etc/rc.d/init.d/nova-compute.initd.supervisord
install -p -m 755 %{_distropkgdir}/supervisord_openstack.conf %{buildroot}/etc/contrail/supervisord_openstack.conf.supervisord_vrouter
install -p -m 755 %{_distropkgdir}/nova-compute.ini %{buildroot}%{_supervisoropenstackdir}/nova-compute.ini

%files
/opt/*
/etc/*
/var/*

%post
set -e
kver=`uname -r`
echo "create the agent_param file..."
/opt/contrail/bin/vnagent_param_setup.sh $kver
# switch to supervisord
for svc in openstack-nova_compute; do
    if [ -e /etc/init/$svc.conf ]; then
        service $svc stop || true
        mv /etc/init/$svc.conf /etc/rc.d/init/$svc.conf.backup
        mv /etc/rc.d/init.d/$svc /etc/rc.d/init.d/$svc.backup
        cp /etc/rc.d/init.d/$svc.initd.supervisord /etc/rc.d/init.d/$svc
    fi
done

if [ ! -f /etc/init/supervisor-openstack.conf ]; then
    mv /etc/init/supervisor-openstack.conf.upstart_vrouter /etc/init/supervisor-openstack.conf
else
    rm /etc/init/supervisor-openstack.conf.upstart_vrouter
fi
if [ ! -f /etc/contrail/supervisord_openstack.conf ]; then
    mv /etc/contrail/supervisord_openstack.conf.supervisord_vrouter /etc/contrail/supervisord_openstack.conf
else
    rm /etc/contrail/supervisord_openstack.conf.supervisord_vrouter
fi
