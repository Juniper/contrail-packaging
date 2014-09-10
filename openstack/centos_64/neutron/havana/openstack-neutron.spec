#
# This is 2013.2 havana
#
%define         _relstr     2contrail 
%{echo: "Building release %{_relstr}\n"}

Name:		openstack-neutron
Version:	2013.2
Release:        %{_relstr}
#Provides:	openstack-quantum = %{version}-%{release}
#Obsoletes:	openstack-quantum < 2013.2-0.4.b3
Summary:	Virtual network service for OpenStack (neutron) %{?_gitVer}

Group:		Applications/System
License:	ASL 2.0
URL:		http://launchpad.net/neutron/

#Source0:	http://launchpad.net/neutron/%{release_name}/%{version}/+download/neutron-%{version}.tar.gz
#Source0:    http://launchpad.net/neutron/%{release_name}/%{release_name}-1/+download/neutron-%{version}.b3.tar.gz
Source1:	neutron.logrotate
Source2:	neutron-sudoers
Source5:	neutron-node-setup
Source6:	neutron-dhcp-setup
Source7:	neutron-l3-setup
%if 0%{?fedora} >= 17
Source10:	neutron-server.service
%endif
%if 0%{?rhel}
Source10:	neutron-server.initd
%endif
#
# patches_base=2013.2.b3
#

BuildArch:	noarch

BuildRequires:	python2-devel
BuildRequires:	python-setuptools
%if 0%{?fedora} >= 17
BuildRequires:	systemd-units
%endif
BuildRequires:  python-pbr
BuildRequires:  python-d2to1

Requires:	python-neutron = %{version}-%{release}
Requires:	openstack-utils
Requires:	python-pbr

# dnsmasq is not a hard requirement, but is currently the only option
# when neutron-dhcp-agent is deployed.
Requires:	dnsmasq

Requires(pre):	shadow-utils
%if 0%{?fedora} >= 17
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%endif


%description
Neutron is a virtual network service for Openstack. Just like
OpenStack Nova provides an API to dynamically request and configure
virtual servers, Quantum provides an API to dynamically request and
configure virtual networks. These networks connect "interfaces" from
other OpenStack services (e.g., virtual NICs from Nova VMs). The
Quantum API supports extensions to provide advanced network
capabilities (e.g., QoS, ACLs, network monitoring, etc.)


%package -n python-neutron
Summary:	Quantum Python libraries
Group:		Applications/System

Requires:	MySQL-python
Requires:	python-alembic
Requires:	python-amqplib
Requires:	python-anyjson
Requires:	python-eventlet
Requires:	python-greenlet
Requires:	python-httplib2
Requires:	python-iso8601
Requires:	python-kombu
Requires:	python-netaddr
Requires:	python-oslo-config
Requires:	python-paste-deploy
Requires:	python-qpid
Requires:	python-neutronclient >= 2.1.10
Requires:	python-routes
Requires:	python-sqlalchemy
Requires:	python-webob
Requires:	sudo



%description -n python-neutron
Quantum provides an API to dynamically request and configure virtual
networks.

This package contains the neutron Python library.


#%package -n openstack-neutron-bigswitch
#Summary:	Quantum Big Switch plugin
#Group:		Applications/System

#Provides:	openstack-quantum-bigswitch = %{version}-%{release}
#Obsoletes:	openstack-quantum-bigswitch < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-bigswitch
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using the FloodLight Openflow Controller or the Big Switch
#Networks Controller.


#%package -n openstack-neutron-brocade
#Summary:	Quantum Brocade plugin
#Group:		Applications/System

#Provides:	openstack-quantum-brocade = %{version}-%{release}
#Obsoletes:	openstack-quantum-brocade < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-brocade
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using Brocade VCS switches running NOS.


#%package -n openstack-neutron-cisco
#Summary:	Quantum Cisco plugin
#Group:		Applications/System
#
#Provides:	openstack-quantum-cisco = %{version}-%{release}
#Obsoletes:	openstack-quantum-cisco < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}
#Requires:	python-configobj


#%description -n openstack-neutron-cisco
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using Cisco UCS and Nexus.


#%package -n openstack-neutron-hyperv
#Summary:	Quantum Hyper-V plugin
#Group:		Applications/System

#Provides:	openstack-quantum-hyperv = %{version}-%{release}
#Obsoletes:	openstack-quantum-hyperv < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-hyperv
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using Microsoft Hyper-V.


#%package -n openstack-neutron-linuxbridge
#Summary:	Quantum linuxbridge plugin
#Group:		Applications/System

#Provides:	openstack-quantum-linuxbridge = %{version}-%{release}
#Obsoletes:	openstack-quantum-linuxbridge < 2013.2-0.4.b3

#Requires:	bridge-utils
#Requires:	openstack-neutron = %{version}-%{release}
#Requires:	python-pyudev


#%description -n openstack-neutron-linuxbridge
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks as VLANs using Linux bridging.


#%package -n openstack-neutron-midonet
#Summary:	Quantum MidoNet plugin
#Group:		Applications/System

#Provides:	openstack-quantum-midonet = %{version}-%{release}
#Obsoletes:	openstack-quantum-midonet < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-midonet
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using MidoNet from Midokura.


#%package -n openstack-neutron-ml2
#Summary:    Quantum ML2 plugin
#Group:      Applications/System

#Provides:	openstack-quantum-ml2 = %{version}-%{release}
#Obsoletes:	openstack-quantum-ml2 < 2013.2-0.4.b3

#Requires:   openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-ml2
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains a neutron plugin that allows the use of drivers
#to support separately extensible sets of network types and the mechanisms
#for accessing those types.


#%package -n openstack-neutron-mellanox
#Summary:    Quantum Mellanox plugin
#Group:      Applications/System

#Provides:	openstack-quantum-mellanox = %{version}-%{release}
#Obsoletes:	openstack-quantum-mellanox < 2013.2-0.4.b3

#Requires:      openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-mellanox
#This plugin implements Quantum v2 APIs with support for Mellanox embedded
#switch functionality as part of the VPI (Ethernet/InfiniBand) HCA.
#

#%package -n openstack-neutron-nicira
#Summary:	Quantum Nicira plugin
#Group:		Applications/System

#Provides:	openstack-quantum-nicira = %{version}-%{release}
#Obsoletes:	openstack-quantum-nicira < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-nicira
#Quantum provides an API to dynamically request and configure virtual
#networks.
#
#This package contains the neutron plugin that implements virtual
#networks using Nicira NVP.


#%package -n openstack-neutron-openvswitch
#Summary:	Quantum openvswitch plugin
#Group:		Applications/System

#Provides:	openstack-quantum-openvswitch = %{version}-%{release}
#Obsoletes:	openstack-quantum-openvswitch < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}
#Requires:	openvswitch


#%description -n openstack-neutron-openvswitch
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using Open vSwitch.


#%package -n openstack-neutron-plumgrid
#Summary:	Quantum PLUMgrid plugin
#Group:		Applications/System

#Provides:	openstack-quantum-plumgrid = %{version}-%{release}
#Obsoletes:	openstack-quantum-plumgrid < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-plumgrid
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using the PLUMgrid platform.


#%package -n openstack-neutron-ryu
#Summary:	Quantum Ryu plugin
#Group:		Applications/System

#Provides:	openstack-quantum-ryu = %{version}-%{release}
#Obsoletes:	openstack-quantum-ryu < 2013.2-0.4.b3

#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-ryu
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using the Ryu Network Operating System.


#%package -n openstack-neutron-nec
#Summary:	Quantum NEC plugin
#Group:		Applications/System
#
#Provides:	openstack-quantum-nec = %{version}-%{release}
#Obsoletes:	openstack-quantum-nec < 2013.2-0.4.b3
#
#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-nec
#Quantum provides an API to dynamically request and configure virtual
#networks.

#This package contains the neutron plugin that implements virtual
#networks using the NEC OpenFlow controller.


#%package -n openstack-neutron-metaplugin
#Summary:	Quantum meta plugin
#Group:		Applications/System

#Provides:	openstack-quantum-metaplugin = %{version}-%{release}
#Obsoletes:	openstack-quantum-metaplugin < 2013.2-0.4.b3
#
#Requires:	openstack-neutron = %{version}-%{release}


#%description -n openstack-neutron-metaplugin
#xQuantum provides an API to dynamically request and configure virtual
#xnetworks.
#
#This package contains the neutron plugin that implements virtual
#xnetworks using multiple other neutron plugins.


#%package -n openstack-neutron-meetering-agent
#Summary:	Neutron bandwidth metering agent
#Group:		Applications/System
#
#Requires:   openstack-neutron = %{version}-%{release}
#
#%description -n openstack-neutron-meetering-agent
#Neutron provides an API to measure bandwidth utilization
#
#This package contains the neutron agent responsible for generating bandwidth
#utilization notifications.
#
#%package -n openstack-neutron-vpn-agent
#Summary:	Neutron VPNaaS agent
#Group:		Applications/System

#Requires:   openstack-neutron = %{version}-%{release}
#
#%description -n openstack-neutron-vpn-agent
#Neutron provides an API to implement VPN as a service
#
#This package contains the neutron agent responsible for implenting VPNaaS with
#IPSec.

%prep
#%setup -q -n neutron-%{version}

pushd neutron

find neutron -name \*.py -exec sed -i '/\/usr\/bin\/env python/d' {} \;

# let RPM handle deps
sed -i '/setuptools_git/d' setup.py

# Adjust configuration file content
sed -i 's/debug = True/debug = False/' etc/neutron.conf
sed -i 's/\# auth_strategy = keystone/auth_strategy = keystone/' etc/neutron.conf

%build
pushd neutron
#%{__python} setup.py build


%install
pushd neutron
%{__python} setup.py install -O1 --root %{buildroot}

# Remove unused files
rm -rf %{buildroot}%{python_sitelib}/bin
rm -rf %{buildroot}%{python_sitelib}/doc
rm -rf %{buildroot}%{python_sitelib}/tools
rm -rf %{buildroot}%{python_sitelib}/neutron/tests
rm -rf %{buildroot}%{python_sitelib}/neutron/plugins/*/tests
rm -f %{buildroot}%{python_sitelib}/neutron/plugins/*/run_tests.*
rm %{buildroot}/usr/etc/init.d/neutron-server

#install -p -D -m 755 bin/neutron-server %{buildroot}%{_bindir}/neutron-server

# Move rootwrap files to proper location
install -d -m 755 %{buildroot}%{_datarootdir}/neutron/rootwrap
mv %{buildroot}/usr/etc/neutron/rootwrap.d/*.filters %{buildroot}%{_datarootdir}/neutron/rootwrap

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron
cp -ar %{buildroot}/usr/etc/neutron/* %{buildroot}%{_sysconfdir}/neutron

chmod 640  %{buildroot}%{_sysconfdir}/neutron/plugins/*/*.ini

# Configure agents to use neutron-rootwrap
sed -i 's/^# root_helper.*/root_helper = sudo neutron-rootwrap \/etc\/neutron\/rootwrap.conf/g' %{buildroot}%{_sysconfdir}/neutron/neutron.conf

# Configure neutron-dhcp-agent state_path
sed -i 's/state_path = \/opt\/stack\/data/state_path = \/var\/lib\/neutron/' %{buildroot}%{_sysconfdir}/neutron/dhcp_agent.ini

# remove hyperv plugin ini file
rm -f %{buildroot}%{_sysconfdir}/quantum/plugins/hyperv/hyperv_quantum_plugin.ini
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/cisco/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/bigswitch/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/brocade/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/linuxbridge/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/metaplugin/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/midonet/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/nec/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/nicira/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/openvswitch/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/plumgrid/
rm -rf %{buildroot}%{_sysconfdir}/quantum/plugins/ryu/
rm -f  %{buildroot}%{_sysconfdir}/quantum/dhcp_agent.ini
rm -f  %{buildroot}%{_sysconfdir}/quantum/l3_agent.ini
rm -f  %{buildroot}%{_sysconfdir}/quantum/lbaas_agent.ini
rm -f  %{buildroot}%{_sysconfdir}/quantum/metadata_agent.ini
rm -f  %{buildroot}%{_sysconfdir}/quantum/rootwrap.d/dhcp.filters
rm -f  %{buildroot}%{_sysconfdir}/quantum/rootwrap.d/iptables-firewall.filters
rm -f  %{buildroot}%{_sysconfdir}/quantum/rootwrap.d/l3.filters
rm -f  %{buildroot}%{_sysconfdir}/quantum/rootwrap.d/lbaas-haproxy.filters
rm -f  %{buildroot}%{_sysconfdir}/quantum/rootwrap.d/linuxbridge-plugin.filters
rm -f  %{buildroot}%{_sysconfdir}/quantum/rootwrap.d/nec-plugin.filters
rm -f  %{buildroot}%{_sysconfdir}/quantum/rootwrap.d/openvswitch-plugin.filters
rm -f  %{buildroot}%{_sysconfdir}/quantum/rootwrap.d/ryu-plugin.filters

rm -f  %{buildroot}%{_sysconfdir}/neutron/metering_agent.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/bigswitch/restproxy.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/brocade/brocade.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/cisco/cisco_plugins.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/hyperv/hyperv_neutron_plugin.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/linuxbridge/linuxbridge_conf.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/metaplugin/metaplugin.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/midonet/midonet.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/ml2/ml2_conf.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/ml2/ml2_conf_arista.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/ml2/ml2_conf_cisco.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/mlnx/mlnx_conf.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/nec/nec.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/nicira/nvp.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/openvswitch/ovs_neutron_plugin.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/plumgrid/plumgrid.ini

rm -f  %{buildroot}%{_sysconfdir}/neutron/plugins/ryu/ryu.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/vpn_agent.ini
rm -f  %{buildroot}%{_sysconfdir}/neutron/fwaas_driver.ini
rm -f  %{buildroot}%{_bindir}/quantum-check-nvp-config
rm -f  %{buildroot}%{_bindir}/quantum-metadata-agent
rm -f  %{buildroot}%{_bindir}/quantum-ns-metadata-proxy
rm -f  %{buildroot}%{_bindir}/quantum-ovs-cleanup

rm -f  %{buildroot}%{_bindir}/neutron-check-nvp-config
rm -f  %{buildroot}%{_bindir}/neutron-hyperv-agent
rm -f  %{buildroot}%{_bindir}/neutron-linuxbridge-agent
rm -f  %{buildroot}%{_bindir}/neutron-metering-agent
rm -f  %{buildroot}%{_bindir}/neutron-mlnx-agent
rm -f  %{buildroot}%{_bindir}/neutron-nec-agent
rm -f  %{buildroot}%{_bindir}/neutron-openvswitch-agent
rm -f  %{buildroot}%{_bindir}/neutron-ovs-cleanup
rm -f  %{buildroot}%{_bindir}/neutron-ryu-agent
rm -f  %{buildroot}%{_bindir}/neutron-vpn-agent
rm -f  %{buildroot}%{_bindir}/quantum-hyperv-agent
rm -f  %{buildroot}%{_bindir}/quantum-linuxbridge-agent
rm -f  %{buildroot}%{_bindir}/quantum-mlnx-agent
rm -f  %{buildroot}%{_bindir}/quantum-nec-agent
rm -f  %{buildroot}%{_bindir}/quantum-openvswitch-agent
rm -f  %{buildroot}%{_bindir}/quantum-ryu-agent
rm -f  %{buildroot}/usr/share/neutron/rootwrap/debug.filters
rm -f  %{buildroot}/usr/share/neutron/rootwrap/linuxbridge-plugin.filters
rm -f  %{buildroot}/usr/share/neutron/rootwrap/nec-plugin.filters
rm -f  %{buildroot}/usr/share/neutron/rootwrap/openvswitch-plugin.filters
rm -f  %{buildroot}/usr/share/neutron/rootwrap/ryu-plugin.filters
rm -f  %{buildroot}/usr/share/neutron/rootwrap/vpnaas.filters

rm -f  %{buildroot}/usr/etc/neutron/api-paste.ini
rm -f  %{buildroot}/usr/etc/neutron/dhcp_agent.ini
rm -f  %{buildroot}/usr/etc/neutron/l3_agent.ini
rm -f  %{buildroot}/usr/etc/neutron/lbaas_agent.ini
rm -f  %{buildroot}/usr/etc/neutron/metadata_agent.ini
rm -f  %{buildroot}/usr/etc/neutron/metering_agent.ini
rm -f  %{buildroot}/usr/etc/neutron/neutron.conf
rm -f  %{buildroot}/usr/etc/neutron/plugins/bigswitch/restproxy.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/brocade/brocade.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/cisco/cisco_plugins.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/hyperv/hyperv_neutron_plugin.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/linuxbridge/linuxbridge_conf.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/metaplugin/metaplugin.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/midonet/midonet.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/ml2/ml2_conf.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/ml2/ml2_conf_arista.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/ml2/ml2_conf_cisco.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/mlnx/mlnx_conf.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/nec/nec.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/nicira/nvp.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/plumgrid/plumgrid.ini
rm -f  %{buildroot}/usr/etc/neutron/plugins/ryu/ryu.ini
rm -f  %{buildroot}/usr/etc/neutron/policy.json
rm -f  %{buildroot}/usr/etc/neutron/rootwrap.conf
rm -f  %{buildroot}/usr/etc/neutron/vpn_agent.ini
rm -f  %{buildroot}/usr/etc/neutron/fwaas_driver.ini

#  Install logrotate
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-neutron

# Install sudoers
install -p -D -m 440 %{SOURCE2} %{buildroot}%{_sysconfdir}/sudoers.d/neutron

# Install systemd units
%if 0%{?fedora} >= 17
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/neutron-server.service
%endif
%if 0%{?rhel}
install -p -D -m 755 %{SOURCE10} %{buildroot}%{_initddir}/neutron-server
%endif
#install -p -D -m 644 %{SOURCE15} %{buildroot}%{_unitdir}/neutron-dhcp-agent.service
#install -p -D -m 644 %{SOURCE16} %{buildroot}%{_unitdir}/neutron-l3-agent.service
#install -p -D -m 644 %{SOURCE17} %{buildroot}%{_unitdir}/neutron-metadata-agent.service
#install -p -D -m 644 %{SOURCE18} %{buildroot}%{_unitdir}/neutron-ovs-cleanup.service
#install -p -D -m 644 %{SOURCE19} %{buildroot}%{_unitdir}/neutron-lbaas-agent.service

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/neutron
install -d -m 755 %{buildroot}%{_localstatedir}/log/neutron
install -d -m 755 %{buildroot}%{_localstatedir}/run/neutron

# Install setup helper scripts
install -p -D -m 755 %{SOURCE5} %{buildroot}%{_bindir}/neutron-node-setup
install -p -D -m 755 %{SOURCE6} %{buildroot}%{_bindir}/neutron-dhcp-setup
install -p -D -m 755 %{SOURCE7} %{buildroot}%{_bindir}/neutron-l3-setup

# Install version info file
cat > %{buildroot}%{_sysconfdir}/neutron/release <<EOF
[Quantum]
vendor = Fedora Project
product = OpenStack Quantum
package = %{release}
EOF

%pre
getent group neutron >/dev/null || groupadd -o -r neutron --gid 164
getent passwd neutron >/dev/null || \
    useradd -o --uid 164 -r -g neutron -d %{_sharedstatedir}/neutron -s /sbin/nologin \
    -c "OpenStack Quantum Daemons" neutron
exit 0


%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable neutron-server.service > /dev/null 2>&1 || :
    /bin/systemctl stop neutron-server.service > /dev/null 2>&1 || :
#    /bin/systemctl --no-reload disable neutron-dhcp-agent.service > /dev/null 2>&1 || :
#    /bin/systemctl stop neutron-dhcp-agent.service > /dev/null 2>&1 || :
#    /bin/systemctl --no-reload disable neutron-l3-agent.service > /dev/null 2>&1 || :
#    /bin/systemctl stop neutron-l3-agent.service > /dev/null 2>&1 || :
#    /bin/systemctl --no-reload disable neutron-metadata-agent.service > /dev/null 2>&1 || :
#    /bin/systemctl stop neutron-metadata-agent.service > /dev/null 2>&1 || :
#    /bin/systemctl --no-reload disable neutron-lbaas-agent.service > /dev/null 2>&1 || :
#    /bin/systemctl stop neutron-lbaas-agent.service > /dev/null 2>&1 || :
fi


%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
#    /bin/systemctl try-restart neutron-server.service >/dev/null 2>&1 || :
#    /bin/systemctl try-restart neutron-dhcp-agent.service >/dev/null 2>&1 || :
#    /bin/systemctl try-restart neutron-l3-agent.service >/dev/null 2>&1 || :
#    /bin/systemctl try-restart neutron-metadata-agent.service >/dev/null 2>&1 || :
#    /bin/systemctl try-restart neutron-lbaas-agent.service >/dev/null 2>&1 || :
fi

%files
%doc neutron/LICENSE
%doc neutron/README.rst
%{_bindir}/quantum-db-manage
%{_bindir}/quantum-debug
%{_bindir}/quantum-dhcp-agent
%{_bindir}/quantum-l3-agent
%{_bindir}/quantum-lbaas-agent
%{_bindir}/quantum-netns-cleanup
%{_bindir}/quantum-rootwrap
%{_bindir}/quantum-rootwrap-xen-dom0
%{_bindir}/quantum-server
%{_bindir}/quantum-usage-audit

%{_bindir}/neutron-db-manage
%{_bindir}/neutron-debug
%{_bindir}/neutron-dhcp-agent
%{_bindir}/neutron-dhcp-setup
%{_bindir}/neutron-l3-agent
%{_bindir}/neutron-l3-setup
%{_bindir}/neutron-lbaas-agent
%{_bindir}/neutron-metadata-agent
%{_bindir}/neutron-netns-cleanup
%{_bindir}/neutron-node-setup
%{_bindir}/neutron-ns-metadata-proxy
%{_bindir}/neutron-rootwrap
%{_bindir}/neutron-rootwrap-xen-dom0
%{_bindir}/neutron-server
%{_bindir}/neutron-usage-audit

#%{_unitdir}/neutron-dhcp-agent.service
#%{_unitdir}/neutron-l3-agent.service
#%{_unitdir}/neutron-lbaas-agent.service
#%{_unitdir}/neutron-metadata-agent.service
%if 0%{?fedora} >= 17
%{_unitdir}/neutron-server.service
%endif
%if 0%{?rhel}
%{_initddir}/neutron-server
%endif
%dir %{_sysconfdir}/neutron
%{_sysconfdir}/neutron/release
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/api-paste.ini
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/dhcp_agent.ini
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/l3_agent.ini
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/metadata_agent.ini
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/lbaas_agent.ini
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/policy.json
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/neutron.conf
%config(noreplace) %{_sysconfdir}/neutron/rootwrap.conf
%dir %{_sysconfdir}/neutron/plugins
%config(noreplace) %{_sysconfdir}/logrotate.d/*
%config(noreplace) %{_sysconfdir}/sudoers.d/neutron
%dir %attr(0755, neutron, neutron) %{_sharedstatedir}/neutron
%dir %attr(0755, neutron, neutron) %{_localstatedir}/log/neutron
%dir %attr(0755, neutron, neutron) %{_localstatedir}/run/neutron
%dir %{_datarootdir}/neutron
%dir %{_datarootdir}/neutron/rootwrap
%{_datarootdir}/neutron/rootwrap/dhcp.filters
%{_datarootdir}/neutron/rootwrap/iptables-firewall.filters
%{_datarootdir}/neutron/rootwrap/l3.filters
%{_datarootdir}/neutron/rootwrap/lbaas-haproxy.filters


%files -n python-neutron
%doc neutron/LICENSE
%doc neutron//README.rst
%{python_sitelib}/quantum
%{python_sitelib}/neutron
%exclude %{python_sitelib}/neutron/plugins/bigswitch
%exclude %{python_sitelib}/neutron/plugins/brocade
%exclude %{python_sitelib}/neutron/plugins/cisco
%exclude %{python_sitelib}/neutron/plugins/hyperv
%exclude %{python_sitelib}/neutron/plugins/linuxbridge
%exclude %{python_sitelib}/neutron/plugins/metaplugin
%exclude %{python_sitelib}/neutron/plugins/midonet
%exclude %{python_sitelib}/neutron/plugins/ml2
%exclude %{python_sitelib}/neutron/plugins/mlnx
%exclude %{python_sitelib}/neutron/plugins/nec
%exclude %{python_sitelib}/neutron/plugins/nicira
%exclude %{python_sitelib}/neutron/plugins/openvswitch
%exclude %{python_sitelib}/neutron/plugins/plumgrid
%exclude %{python_sitelib}/neutron/plugins/ryu
%{python_sitelib}/neutron-%%{version}*.egg-info

%changelog
* Fri Sep 13  2013 Dan Prince <dprince@redhat.com> - 2013.2-0.8.b3
- Drop b3 from release name.

* Tue Sep 10 2013 Terry Wilson <twilson@redhat.com> - 2013.2-0.8.b3
- Add python-pbr dependency (for now)

* Mon Sep 09 2013 Terry Wilson <twilson@redhat.com> - 2013.2-0.6.b3
- Update to havana milestone 3 release

* Mon Aug 26 2013 Terry Wilson <twilson@redhat.com> - 2013.2-0.5.b2
- Add provides/obsoletes for subpackages

* Mon Aug 19 2013 Terry Wilson <twilson@redhat.com> - 2013.2-0.4.b2
- Updated to havana milestone 2 release
- Renamed quantum to neutron

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2013.2-0.3.b1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 21 2013 Terry Wilson <twilson@redhat.com> - 2013.2-0.2.b1
- Update to havana milestone 1 release

* Fri Jun 07 2013 Terry Wilson <twilson@redhat.com> - 2013.1.2-1
- Update to grizzly 2013.1.2 release

* Fri May 24 2013 Pádraig Brady <P@draigBrady.com> - 2013.1.1-5
- Fix inclusion of db migrations

* Thu May 23 2013 Gary Kotton <gkotton@redhat.com> - 2013.1.1-4
- Fix rootwrap (bug 947793)

* Mon May 20 2013 Terry Wilson <twilson@redhat.com> - 2013.1.1-3
- Fix swapped l3-agent and lbaas-agent service definitions

* Mon May 13 2013 Gary Kotton <gkotton@redhat.com> - 2013.1.1-2
- Update to grizzly release
- Update install scripts to configure security groups
- Update install scripts to remove virtual interface configurations

* Wed Apr  3 2013 Gary Kotton <gkotton@redhat.com> - 2013.1-1
- Update to grizzly release

* Wed Apr  3 2013 Gary Kotton <gkotton@redhat.com> - 2013.1-0.7.rc3
- Update to grizzly rc3
- Update rootwrap (bug 947793)
- Update l3-agent-setup to support qpid (bug 947532)
- Update l3-agent-setup to support metadata-agent credentials
- Update keystone authentication details (bug 947776)

* Tue Mar 26 2013 Terry Wilson <twilson@redhat.com> - 2013.1-0.6.rc2
- Update to grizzly rc2

* Tue Mar 12 2013 Pádraig Brady <P@draigBrady.Com> - 2013.1-0.5.g3
- Relax the dependency requirements on sqlalchemy

* Mon Feb 25 2013 Robert Kukura <rkukura@redhat.com> - 2013.1-0.4.g3
- Update to grizzly milestone 3
- Add brocade, hyperv, midonet, and plumgrid plugins as sub-packages
- Remove cisco files that were eliminated
- Add quantum-check-nvp-config
- Include patch for https://code.launchpad.net/bugs/1132889
- Require python-oslo-config
- Require compatible version of python-sqlalchemy
- Various spec file improvements

* Thu Feb 14 2013 Robert Kukura <rkukura@redhat.com> - 2013.1-0.3.g2
- Update to grizzly milestone 2
- Add quantum-db-manage, quantum-metadata-agent,
  quantum-ns-metadata-proxy, quantum-ovs-cleanup, and
  quantum-usage-audit executables
- Add systemd units for quantum-metadata-agent and quantum-ovs-cleanup
- Fix /etc/quantum/policy.json permissions (bug 877600)
- Require dnsmasq (bug 890041)
- Add the version info file
- Remove python-lxml dependency
- Add python-alembic dependency

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2013.1-0.2.g1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Dec  5 2012 Robert Kukura <rkukura@redhat.com> - 2013.1-0.1.g1
- Update to grizzly milestone 1
- Require python-quantumclient >= 1:2.1.10
- Remove unneeded rpc control_exchange patch
- Add bigswitch plugin as sub-package
- Work around bigswitch conf file missing from setup.py

* Mon Dec  3 2012 Robert Kukura <rkukura@redhat.com> - 2012.2.1-1
- Update to folsom stable 2012.2.1
- Turn off PrivateTmp for dhcp_agent and l3_agent (bug 872689)
- Add upstream patch: Fix rpc control_exchange regression.
- Remove workaround for missing l3_agent.ini

* Fri Sep 28 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-1
- Update to folsom final
- Require python-quantumclient >= 1:2.1.1

* Sun Sep 23 2012 Gary Kotton <gkotton@redhat.com> - 2012.2-0.9.rc2
- Update to folsom rc2

* Sun Sep 16 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.9.rc1
- Fix setting admin_user in quantum_l3_setup

* Fri Sep 14 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.8.rc1
- Setup script fixes from garyk
- Fix openvswitch service config file path
- Make log file names consistent with service names

* Thu Sep 13 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.7.rc1
- Fix various issues in setup scripts
- Configure quantum-dhcp-agent to store files under /var/lib/quantum
- Make config files with passwords world-unreadable
- Replace bug workarounds with upstream patches

* Wed Sep 12 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.6.rc1
- Require python-quantumclient >= 2.0.22
- Add bug references for work-arounds
- Use /usr/share/quantum/rootwrap instead of /usr/share/quantum/filters

* Wed Sep 12 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.5.rc1
- Update to folsom rc1
- Fix command lines in agent systemd units
- Fix setup scripts
- Fix configuration of agents to use quantum-rootwrap
- Set "debug = False" and "auth_strategy = noauth" in quantum.conf
- Symlink /etc/quantum/plugin.ini to plugin's config file
- Add "--config-file /etc/quantum/plugin.ini" to ExecStart in quantum-server.service

* Tue Sep 11 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.4.rc1.20120911.1224
- Update to folsom rc1 snapshot
- Add support for new agents, plugins and rootwrap

* Wed Aug 22 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.3.f2
- Fix helper scripts to setup the database config correctly (#847785)

* Tue Aug  7 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.2.f2
- Include quantum module no longer provided by python-quantumclient
- Update description text
- Disable setuptools_git dependency

* Tue Aug  7 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.1.f2
- Update to folsom milestone 2

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2012.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon May 28 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-2
- Fix helper scripts to use the always available openstack-config util

* Mon Apr  9 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-1
- Update to essex release

* Thu Apr  5 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.7.rc2
- Update to essex rc2 milestone
- Use PrivateTmp for services

* Wed Mar 21 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.6.rc1
- Update to official essex rc1 milestone
- Add quantum-server-setup and quantum-node-setup scripts
- Use hand-coded agent executables rather than easy-install scripts
- Make plugin config files mode 640 and group quantum to protect passwords

* Mon Mar 19 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.5.e4
- Update to essex possible RC1 tarball
- Remove patches incorporated upstream
- Don't package test code
- Remove dependencies only needed by test code

* Wed Mar 14 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.4.e4
- Upstream patch: add root_helper to quantum agents
- Add sudoers file enabling quantum-rootwrap for quantum user
- Configure plugin agents to use quantum-rootwrap
- Run plugin agents as quantum user

* Fri Mar  9 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.3.e4
- Add upstream patch: remove pep8 and strict lxml version from setup.py
- Remove old fix for pep8 dependency
- Add upstream patch: Bug #949261 Removing nova drivers for Linux Bridge Plugin
- Add openvswitch dependency

* Mon Mar  5 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.2.e4
- Update to essex milestone 4
- Move plugins to sub-packages
- Systemd units for agents

* Mon Jan 30 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.1.e3
- Update to essex milestone 3 for F17

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2011.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Nov  17 2011 Robert Kukura <rkukura@redhat.com> - 2011.3-1
- Initial package for Fedora
