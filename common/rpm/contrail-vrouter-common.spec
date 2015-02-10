%define         _contrailetc /etc/contrail
%define         _servicedir  /usr/lib/systemd/system
%define         _supervisordir /etc/contrail/supervisord_vrouter_files
%define         _distropkgdir tools/packaging/common/control_files
%define         _controllersrcdir controller/src

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
Summary: Contrail vRouter Common %{?_gitVer}
Name: contrail-vrouter-common
Version:	    %{_verstr}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-vrouter >= %{_verstr}-%{_relstr}
Requires: abrt
# abrt-addon-vmcore might be needed for centos. Add when package is available
%if 0%{?fedora} >= 17
Requires: abrt-addon-vmcore
Requires: kexec-tools
Requires: kernel = 3.6.6-1.fc17
%endif
Requires: python-thrift >= 0.9.1
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}
Requires: contrail-nodemgr >= %{_verstr}-%{_relstr}
Requires: contrail-vrouter-init >= %{_verstr}-%{_relstr}

%if 0%{?centos}
Requires: python-opencontrail-vrouter-netns >= %{_verstr}-%{_relstr}
%endif

%if 0%{?rhel}
Requires: tunctl
%endif

%description
Contrail Package Requirements for Contrail vRouter

%install
# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_servicedir}
%if 0%(if [ "%{dist}" != ".xen" ]; then echo 1; fi)
install -d -m 755 %{buildroot}%{_supervisordir}
%endif
install -d -m 755 %{buildroot}/lib/modules/%{_osVer}/extra/net/vrouter

# install etc files
pushd %{_builddir}/..
if [ "%{?dist}" != ".xen" ]; then
install -p -m 755 %{_distropkgdir}/contrail_reboot          %{buildroot}%{_contrailetc}/contrail_reboot
fi

%if 0%(if [ "%{dist}" != ".xen" ]; then echo 1; fi)
install -d -m 755 %{buildroot}/bin
install -p -m 755 %{_controllersrcdir}/vnsw/agent/uve/mock_generator.py %{buildroot}/bin/mock_generator
install -p -m 755 %{_controllersrcdir}/vnsw/agent/uve/run_mock_generator %{buildroot}/bin/run_mock_generator
%endif

%post
%if 0%{?fedora} >= 17
/bin/systemctl daemon-reload
%endif

%if 0%{?fedora} >= 17 || 0%{?rhel}
# patch ifup-eth
#if [ $1 -eq 1 ]; then
# create the agent_param file
#/etc/contrail/vnagent_param_setup.sh %{_osVer}
#fi
%endif

%preun
%if 0%{?fedora} >= 17
/bin/systemctl stop supervisor-vrouter.service
if [ $1 = 0 ] ; then
    /usr/sbin/rmmod vrouter
    /bin/systemctl --no-reload disable supervisor-vrouter.service
fi
%endif
exit 0

%postun
if [ $1 = 0 ] ; then
    /bin/systemctl daemon-reload || true
    cp /etc/sysconfig/network-scripts/ifup-eth.rpmsave /etc/sysconfig/network-scripts/ifup-eth
    phydev=`cat /etc/contrail/agent_param | grep dev | sed 's/dev=//g'`
    phydev_save_file=/etc/sysconfig/network-scripts/ifcfg-${phydev}.rpmsave
    phydev_file=/etc/sysconfig/network-scripts/ifcfg-${phydev}
    [ -f ${phydev_save_file} ] && mv ${phydev_save_file} ${phydev_file} || rm -f /etc/sysconfig/network-scripts/ifcfg-${phydev}
    rm -f /etc/sysconfig/network-scripts/ifcfg-vhost0
fi
exit 0

%files
%defattr(-, root, root)
%if  "%{dist}" == ".xen"
%undefine buildroot
%endif
%if 0%(if [ "%{dist}" == ".xen" ]; then echo 1; fi)
%{_sysconfdir}/init.d/contrail-vrouter-agent
%else
%{_contrailetc}/contrail_reboot
/bin/mock_generator
/bin/run_mock_generator
%endif
%if 0%{?rhel}
%endif
%if 0%{?fedora} >= 17
%endif

%if  "%{dist}" == ".xen"
%define buildroot  %{_topdir}/BUILDROOT
%endif

%changelog
* Fri Nov  14 2014 <ijohnson@juniper.net>
* Initial build.

