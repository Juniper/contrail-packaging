%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}


Name:             openstack-nova
Version:          2013.2
Release:          %{_relstr}
Summary:          OpenStack Compute (nova) %{?_gitVer}

Group:            Applications/System
License:          ASL 2.0
URL:              http://openstack.org/projects/compute/
#Source0:	  https://launchpad.net/nova/havana/havana-3/+download/nova-%{version}.b3.tar.gz

Source1:          nova-dist.conf
Source6:          nova.logrotate

%if 0%{?fedora} >= 17
Source10:         openstack-nova-api.service
Source11:         openstack-nova-cert.service
Source12:         openstack-nova-compute.service
#Source13:         openstack-nova-network.service
Source14:         openstack-nova-objectstore.service
Source15:         openstack-nova-scheduler.service
Source18:         openstack-nova-xvpvncproxy.service
Source19:         openstack-nova-console.service
Source20:         openstack-nova-consoleauth.service
Source25:         openstack-nova-metadata-api.service
Source26:         openstack-nova-conductor.service
Source27:         openstack-nova-cells.service
Source28:         openstack-nova-spicehtml5proxy.service
Source29:         openstack-nova-novncproxy.service
%endif
%if 0%{?rhel}
Source10:         openstack-nova-api.initd
Source11:         openstack-nova-cert.initd
Source12:         openstack-nova-compute.initd
Source15:         openstack-nova-scheduler.initd
Source20:         openstack-nova-consoleauth.initd
Source26:         openstack-nova-conductor.initd
Source29:         openstack-nova-novncproxy.initd
%endif
Source21:         nova-polkit.pkla
Source23:         nova-polkit.rules
Source22:         nova-ifc-template
Source24:         nova-sudoers
Source30:         openstack-nova-novncproxy.sysconfig
Source31:         contrail-server-setup.sh
Source32:         contrail-keystone-setup.sh
Source33:         contrail-server-cleanup.sh
Source34:         nova_havana.conf

#
# patches_base=2013.2.b3
#
Patch0001: 0001-Ensure-we-don-t-access-the-net-when-building-docs.patch
Patch0002: 0002-remove-runtime-dep-on-python-pbr.patch
Patch0003: 0003-Revert-Use-oslo.sphinx-and-remove-local-copy-of-doc-.patch
Patch0004: 0004-Fix-compute_node_get_all-for-Nova-Baremetal.patch

BuildArch:        noarch
BuildRequires:    intltool
BuildRequires:    python-sphinx
BuildRequires:    python-setuptools
BuildRequires:    python-netaddr
BuildRequires:    openstack-utils
BuildRequires:    python-pbr
BuildRequires:    python-oslo-sphinx

Requires:         openstack-nova-compute = %{version}-%{release}
Requires:         openstack-nova-cert = %{version}-%{release}
Requires:         openstack-nova-scheduler = %{version}-%{release}
Requires:         openstack-nova-api = %{version}-%{release}
#Requires:         openstack-nova-network = %{version}-%{release}
Requires:         openstack-nova-objectstore = %{version}-%{release}
Requires:         openstack-nova-conductor = %{version}-%{release}
Requires:         openstack-nova-console = %{version}-%{release}
Requires:         openstack-nova-cells = %{version}-%{release}
Requires:         openstack-nova-novncproxy = %{version}-%{release}


%description
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

%package common
Summary:          Components common to all OpenStack Nova services
Group:            Applications/System

Requires:         python-nova = %{version}-%{release}

%if 0%{?fedora} >= 17
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%endif
Requires(pre):    shadow-utils

%description common
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains scripts, config and dependencies shared
between all the OpenStack nova services.


%package compute
Summary:          OpenStack Nova Virtual Machine control service
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}
Requires:         curl
Requires:         iscsi-initiator-utils
Requires:         iptables iptables-ipv6
Requires:         vconfig
Requires:         python-libguestfs
Requires:         libvirt >= 0.9.6
Requires:         libvirt-python
Requires:         openssh-clients
Requires:         rsync
Requires:         lvm2
Requires:         python-cinderclient
Requires(pre):    qemu-kvm
Requires:         sysfsutils
Requires:         genisoimage

%description compute
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the Nova service for controlling Virtual Machines.


#%package network
#Summary:          OpenStack Nova Network control service
#Group:            Applications/System

#Requires:         openstack-nova-common = %{version}-%{release}
#Requires:         vconfig
#Requires:         radvd
#Requires:         bridge-utils
#Requires:         dnsmasq
#Requires:         dnsmasq-utils
#Requires:         ebtables

#%description network
#OpenStack Compute (codename Nova) is open source software designed to
#provision and manage large networks of virtual machines, creating a
#redundant and scalable cloud computing platform. It gives you the
#software, control panels, and APIs required to orchestrate a cloud,
#including running instances, managing networks, and controlling access
#through users and projects. OpenStack Compute strives to be both
#hardware and hypervisor agnostic, currently supporting a variety of
#standard hardware configurations and seven major hypervisors.

#This package contains the Nova service for controlling networking.


%package scheduler
Summary:          OpenStack Nova VM distribution service
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}

%description scheduler
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the service for scheduling where
to run Virtual Machines in the cloud.


%package cert
Summary:          OpenStack Nova certificate management service
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}

%description cert
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the Nova service for managing certificates.


%package api
Summary:          OpenStack Nova API services
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}

%description api
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the Nova services providing programmatic access.

%package conductor
Summary:          OpenStack Nova Conductor services
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}

%description conductor
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the Nova services providing database access for
the compute service

%package objectstore
Summary:          OpenStack Nova simple object store service
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}

%description objectstore
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the Nova service providing a simple object store.


%package console
Summary:          OpenStack Nova console access services
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}
Requires:         python-websockify

%description console
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the Nova services providing
console access services to Virtual Machines.

%package cells
Summary:          OpenStack Nova Cells services
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}

%description cells
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the Nova Cells service providing additional 
scaling and (geographic) distribution for compute services.

%package novncproxy
Summary:          OpenStack Nova noVNC proxy service
Group:            Applications/System

Requires:         openstack-nova-common = %{version}-%{release}
Requires:         novnc
Requires: 	  python-websockify


%description novncproxy
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

This package contains the Nova noVNC Proxy service that can proxy 
VNC traffic over browser websockets connections.

%package -n       python-nova
Summary:          Nova Python libraries
Group:            Applications/System

Requires:         openssl
# Require openssh for ssh-keygen
Requires:         openssh
Requires:         sudo

Requires:         MySQL-python

Requires:         python-paramiko

Requires:         python-qpid
Requires:         python-kombu
Requires:         python-amqplib

Requires:         python-eventlet
Requires:         python-greenlet
Requires:         python-iso8601
Requires:         python-netaddr
Requires:         python-lxml
Requires:         python-anyjson
Requires:         python-boto
Requires:         python-cheetah
Requires:         python-ldap
Requires:         python-stevedore

Requires:         python-memcached

Requires:         python-sqlalchemy
Requires:         python-migrate

Requires:         python-paste-deploy
Requires:         python-routes
Requires:         python-webob

Requires:         python-glanceclient >= 1:0
Requires:         python-neutronclient
Requires:         python-novaclient
Requires:         python-oslo-config
Requires:         python-pyasn1
Requires:         python-six
Requires:         python-babel
Requires:         python-jinja2
#Requires:         python-oslo-messaging

%description -n   python-nova
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform.

This package contains the nova Python library.

%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Compute
Group:            Documentation

%if 0%{?fedora} >= 17
BuildRequires:    systemd-units
%endif
BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python-boto
BuildRequires:    python-eventlet
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-webob
# while not strictly required, quiets the build down when building docs.
BuildRequires:    python-migrate, python-iso8601

%description      doc
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform.

This package contains documentation files for nova.
%endif

%prep
# Remove the requirements file so that pbr hooks don't add it 
# to distutils requiers_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

%build
pushd nova
%{__python} setup.py build

# Move authtoken configuration out of paste.ini
openstack-config --del etc/nova/api-paste.ini filter:authtoken admin_tenant_name
openstack-config --del etc/nova/api-paste.ini filter:authtoken admin_user
openstack-config --del etc/nova/api-paste.ini filter:authtoken admin_password
openstack-config --del etc/nova/api-paste.ini filter:authtoken auth_host
openstack-config --del etc/nova/api-paste.ini filter:authtoken auth_port
openstack-config --del etc/nova/api-paste.ini filter:authtoken auth_protocol
openstack-config --del etc/nova/api-paste.ini filter:authtoken signing_dir
openstack-config --del etc/nova/api-paste.ini filter:authtoken auth_version


echo '
#
# Options to be passed to keystoneclient.auth_token middleware
# NOTE: These options are not defined in nova but in keystoneclient
#
[keystone_authtoken]

# the name of the admin tenant (string value)
#admin_tenant_name=

# the keystone admin username (string value)
#admin_user=

# the keystone admin password (string value)
#admin_password=

# the keystone host (string value)
#auth_host=

# the keystone port (integer value)
#auth_port=

# protocol to be used for auth requests http/https (string value)
#auth_protocol=

# Workaround for https://bugs.launchpad.net/nova/+bug/1154809
#auth_version=

# signing_dir is configurable, but the default behavior of the authtoken
# middleware should be sufficient.  It will create a temporary directory
# in the home directory for the user the nova process is running as.
#signing_dir=/var/lib/nova/keystone-signing
' >> etc/nova/nova.conf.sample

# Programmatically update defaults in sample config
# which is installed at /etc/nova/nova.conf
# TODO: Make this more robust
# Note it only edits the first occurance, so assumes a section ordering in sample
# and also doesn't support multi-valued variables like dhcpbridge_flagfile.
while read name eq value; do
  test "$name" && test "$value" || continue
  sed -i "0,/^# *$name=/{s!^# *$name=.*!#$name=$value!}" etc/nova/nova.conf.sample
done < %{SOURCE1}

%install
pushd nova
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# docs generation requires everything to be installed first
export PYTHONPATH="$( pwd ):$PYTHONPATH"

pushd doc

%if 0%{?with_doc}
SPHINX_DEBUG=1 sphinx-build -b html source build/html
# Fix hidden-file-or-dir warnings
rm -fr build/html/.doctrees build/html/.buildinfo
%endif

# Create dir link to avoid a sphinx-build exception
mkdir -p build/man/.doctrees/
if [ ! -L build/man/.doctrees/man ]; then
    ln -s .  build/man/.doctrees/man
fi
SPHINX_DEBUG=1 sphinx-build -b man -c source source/man build/man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/

popd

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/buckets
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/instances
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/keys
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/networks
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/tmp
install -d -m 755 %{buildroot}%{_localstatedir}/log/nova

# Setup ghost CA cert
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/CA
install -p -m 755 nova/CA/*.sh %{buildroot}%{_sharedstatedir}/nova/CA
install -p -m 644 nova/CA/openssl.cnf.tmpl %{buildroot}%{_sharedstatedir}/nova/CA
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/CA/{certs,crl,newcerts,projects,reqs}
touch %{buildroot}%{_sharedstatedir}/nova/CA/{cacert.pem,crl.pem,index.txt,openssl.cnf,serial}
install -d -m 750 %{buildroot}%{_sharedstatedir}/nova/CA/private
touch %{buildroot}%{_sharedstatedir}/nova/CA/private/cakey.pem

# Install config files
install -d -m 755 %{buildroot}%{_sysconfdir}/nova
install -p -D -m 640 %{SOURCE1} %{buildroot}%{_datadir}/nova/nova-dist.conf
install -p -D -m 640 %{SOURCE34}  %{buildroot}%{_sysconfdir}/nova/nova.conf
install -p -D -m 640 etc/nova/rootwrap.conf %{buildroot}%{_sysconfdir}/nova/rootwrap.conf
install -p -D -m 640 etc/nova/api-paste.ini %{buildroot}%{_sysconfdir}/nova/api-paste.ini
install -p -D -m 640 etc/nova/policy.json %{buildroot}%{_sysconfdir}/nova/policy.json

# Move authtoken configuration out of paste.ini
openstack-config --del %{buildroot}%{_sysconfdir}/nova/api-paste.ini filter:authtoken admin_tenant_name
openstack-config --del %{buildroot}%{_sysconfdir}/nova/api-paste.ini filter:authtoken admin_user
openstack-config --del %{buildroot}%{_sysconfdir}/nova/api-paste.ini filter:authtoken admin_password
openstack-config --del %{buildroot}%{_sysconfdir}/nova/api-paste.ini filter:authtoken auth_host
openstack-config --del %{buildroot}%{_sysconfdir}/nova/api-paste.ini filter:authtoken auth_port
openstack-config --del %{buildroot}%{_sysconfdir}/nova/api-paste.ini filter:authtoken auth_protocol
openstack-config --del %{buildroot}%{_sysconfdir}/nova/api-paste.ini filter:authtoken signing_dirname

# Install version info file
cat > %{buildroot}%{_sysconfdir}/nova/release <<EOF
[Nova]
vendor = Fedora Project
product = OpenStack Nova
package = %{release}
EOF

# Install initscripts for Nova services
%if 0%{?fedora} >= 17
install -p -D -m 755 %{SOURCE10} %{buildroot}%{_unitdir}/openstack-nova-api.service
install -p -D -m 755 %{SOURCE11} %{buildroot}%{_unitdir}/openstack-nova-cert.service
install -p -D -m 755 %{SOURCE12} %{buildroot}%{_unitdir}/openstack-nova-compute.service
#install -p -D -m 755 %{SOURCE13} %{buildroot}%{_unitdir}/openstack-nova-network.service
install -p -D -m 755 %{SOURCE14} %{buildroot}%{_unitdir}/openstack-nova-objectstore.service
install -p -D -m 755 %{SOURCE15} %{buildroot}%{_unitdir}/openstack-nova-scheduler.service
install -p -D -m 755 %{SOURCE18} %{buildroot}%{_unitdir}/openstack-nova-xvpvncproxy.service
install -p -D -m 755 %{SOURCE19} %{buildroot}%{_unitdir}/openstack-nova-console.service
install -p -D -m 755 %{SOURCE20} %{buildroot}%{_unitdir}/openstack-nova-consoleauth.service
install -p -D -m 755 %{SOURCE25} %{buildroot}%{_unitdir}/openstack-nova-metadata-api.service
install -p -D -m 755 %{SOURCE26} %{buildroot}%{_unitdir}/openstack-nova-conductor.service
install -p -D -m 755 %{SOURCE27} %{buildroot}%{_unitdir}/openstack-nova-cells.service
install -p -D -m 755 %{SOURCE28} %{buildroot}%{_unitdir}/openstack-nova-spicehtml5proxy.service
install -p -D -m 755 %{SOURCE29} %{buildroot}%{_unitdir}/openstack-nova-novncproxy.service
%endif
%if 0%{?rhel}
install -p -D -m 755 %{SOURCE10} %{buildroot}%{_initddir}/openstack-nova-api
install -p -D -m 755 %{SOURCE11} %{buildroot}%{_initddir}/openstack-nova-cert
install -p -D -m 755 %{SOURCE12} %{buildroot}%{_initddir}/openstack-nova-compute
install -p -D -m 755 %{SOURCE15} %{buildroot}%{_initddir}/openstack-nova-scheduler
install -p -D -m 755 %{SOURCE20} %{buildroot}%{_initddir}/openstack-nova-consoleauth
install -p -D -m 755 %{SOURCE26} %{buildroot}%{_initddir}/openstack-nova-conductor
install -p -D -m 755 %{SOURCE29} %{buildroot}%{_initddir}/openstack-nova-novncproxy
%endif
# contrail scripts
install -p -D -m 755 %{SOURCE31} %{buildroot}%{_bindir}/contrail-server-setup.sh
install -p -D -m 755 %{SOURCE32} %{buildroot}%{_bindir}/contrail-keystone-setup.sh
install -p -D -m 755 %{SOURCE33} %{buildroot}%{_bindir}/contrail-server-cleanup.sh

# Install sudoers
install -p -D -m 440 %{SOURCE24} %{buildroot}%{_sysconfdir}/sudoers.d/nova

# Install logrotate
install -p -D -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-nova

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/nova

# Install template files
install -p -D -m 644 nova/cloudpipe/client.ovpn.template %{buildroot}%{_datarootdir}/nova/client.ovpn.template
install -p -D -m 644 %{SOURCE22} %{buildroot}%{_datarootdir}/nova/interfaces.template

# Install rootwrap files in /usr/share/nova/rootwrap
mkdir -p %{buildroot}%{_datarootdir}/nova/rootwrap/
install -p -D -m 644 etc/nova/rootwrap.d/* %{buildroot}%{_datarootdir}/nova/rootwrap/

# Older format. Remove when we no longer want to support Fedora 17 with master branch packages
install -d -m 755 %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d
install -p -D -m 644 %{SOURCE21} %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d/50-nova.pkla
# Newer format since Fedora 18
install -d -m 755 %{buildroot}%{_sysconfdir}/polkit-1/rules.d
install -p -D -m 644 %{SOURCE23} %{buildroot}%{_sysconfdir}/polkit-1/rules.d/50-nova.rules

# Install novncproxy service options template
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 0644 %{SOURCE30} %{buildroot}%{_sysconfdir}/sysconfig/openstack-nova-novncproxy

# Remove unneeded in production stuff
rm -f %{buildroot}%{_bindir}/nova-debug
rm -fr %{buildroot}%{python_sitelib}/nova/tests/
rm -fr %{buildroot}%{python_sitelib}/run_tests.*
rm -f %{buildroot}%{_bindir}/nova-combined
rm -f %{buildroot}/usr/share/doc/nova/README*

%pre common
getent group nova >/dev/null || groupadd -r nova --gid 162
if ! getent passwd nova >/dev/null; then
  useradd -u 162 -r -g nova -G nova,nobody -d %{_sharedstatedir}/nova -s /sbin/nologin -c "OpenStack Nova Daemons" nova
fi
exit 0

%pre compute
usermod -a -G qemu nova
exit 0

%post compute
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
#%post network
#if [ $1 -eq 1 ] ; then
#    # Initial installation
#    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
#fi
%post scheduler
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%post cert
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%post api
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%post conductor
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%post objectstore
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%post console
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%post cells
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun compute
if [ $1 -eq 0 ] ; then
    for svc in compute; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi
#%preun network
#if [ $1 -eq 0 ] ; then
#    for svc in network; do
#        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
#        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
#    done
#fi
%preun scheduler
if [ $1 -eq 0 ] ; then
    for svc in scheduler; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi
%preun cert
if [ $1 -eq 0 ] ; then
    for svc in cert; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi
%preun api
if [ $1 -eq 0 ] ; then
    for svc in api metadata-api; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi
%preun objectstore
if [ $1 -eq 0 ] ; then
    for svc in objectstore; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi
%preun conductor
if [ $1 -eq 0 ] ; then
    for svc in conductor; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi
%preun console
if [ $1 -eq 0 ] ; then
    for svc in console consoleauth xvpvncproxy; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi
%preun cells
if [ $1 -eq 0 ] ; then
    for svc in cells; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi
%preun novncproxy
if [ $1 -eq 0 ] ; then
    for svc in novncproxy; do
        /bin/systemctl --no-reload disable openstack-nova-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-nova-${svc}.service > /dev/null 2>&1 || :
    done
fi

%postun compute
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in compute; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi
#%postun network
#/bin/systemctl daemon-reload >/dev/null 2>&1 || :
#if [ $1 -ge 1 ] ; then
#    # Package upgrade, not uninstall
#    for svc in network; do
#        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
#    done
#fi
%postun scheduler
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in scheduler; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi
%postun cert
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in cert; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi
%postun api
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in api metadata-api; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi
%postun objectstore
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in objectstore; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi
%postun conductor
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in conductor; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi
%postun console
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in console consoleauth xvpvncproxy; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi
%postun cells
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in cells; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi
%postun novncproxy
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in novncproxy; do
        /bin/systemctl try-restart openstack-nova-${svc}.service >/dev/null 2>&1 || :
    done
fi

%files
%doc nova/LICENSE
%{_bindir}/nova-all
%{_bindir}/contrail-server-setup.sh
%{_bindir}/contrail-keystone-setup.sh
%{_bindir}/contrail-server-cleanup.sh

%files common
%doc nova/LICENSE
%dir %{_sysconfdir}/nova
%{_sysconfdir}/nova/release
%attr(-, root, nova) %{_datadir}/nova/nova-dist.conf
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/nova.conf
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/api-paste.ini
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/rootwrap.conf
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/policy.json
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-nova
%config(noreplace) %{_sysconfdir}/sudoers.d/nova
%config(noreplace) %{_sysconfdir}/polkit-1/localauthority/50-local.d/50-nova.pkla
%config(noreplace) %{_sysconfdir}/polkit-1/rules.d/50-nova.rules

%dir %attr(0755, nova, root) %{_localstatedir}/log/nova
%dir %attr(0755, nova, root) %{_localstatedir}/run/nova

%{_bindir}/nova-clear-rabbit-queues
# TODO. zmq-receiver may need its own service?
%{_bindir}/nova-rpc-zmq-receiver
%{_bindir}/nova-manage
%{_bindir}/nova-rootwrap

%{_datarootdir}/nova
%{_mandir}/man1/nova*.1.gz

%defattr(-, nova, nova, -)
%dir %{_sharedstatedir}/nova
%dir %{_sharedstatedir}/nova/buckets
%dir %{_sharedstatedir}/nova/instances
%dir %{_sharedstatedir}/nova/keys
%dir %{_sharedstatedir}/nova/networks
%dir %{_sharedstatedir}/nova/tmp

%files compute
%{_bindir}/nova-compute
%{_bindir}/nova-baremetal-deploy-helper
%{_bindir}/nova-baremetal-manage
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-compute.service
%endif
%if 0%{?rhel}
%{_initddir}/openstack-nova-compute
%endif
%{_datarootdir}/nova/rootwrap/compute.filters

#%files network
%{_bindir}/nova-network
%{_bindir}/nova-dhcpbridge
#%{_unitdir}/openstack-nova-network.service
#%{_datarootdir}/nova/rootwrap/network.filters

%files scheduler
%{_bindir}/nova-scheduler
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-scheduler.service
%endif
%if 0%{?rhel}
%{_initddir}/openstack-nova-scheduler
%endif

%files cert
%{_bindir}/nova-cert
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-cert.service
%endif
%if 0%{?rhel}
%{_initddir}/openstack-nova-cert
%endif
%defattr(-, nova, nova, -)
%dir %{_sharedstatedir}/nova/CA/
%dir %{_sharedstatedir}/nova/CA/certs
%dir %{_sharedstatedir}/nova/CA/crl
%dir %{_sharedstatedir}/nova/CA/newcerts
%dir %{_sharedstatedir}/nova/CA/projects
%dir %{_sharedstatedir}/nova/CA/reqs
%{_sharedstatedir}/nova/CA/*.sh
%{_sharedstatedir}/nova/CA/openssl.cnf.tmpl
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/cacert.pem
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/crl.pem
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/index.txt
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/openssl.cnf
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/serial
%dir %attr(0750, -, -) %{_sharedstatedir}/nova/CA/private
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/private/cakey.pem

%files api
%{_bindir}/nova-api*
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-*api.service
%endif
%if 0%{?rhel}
%{_initddir}/openstack-nova-*api
%endif
%{_datarootdir}/nova/rootwrap/api-metadata.filters

%files conductor
%{_bindir}/nova-conductor
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-conductor.service
%endif
%if 0%{?rhel}
%{_initddir}/openstack-nova-conductor
%endif

%files objectstore
%{_bindir}/nova-objectstore
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-objectstore.service
%endif

%files console
%{_bindir}/nova-console*
%{_bindir}/nova-xvpvncproxy
%{_bindir}/nova-spicehtml5proxy
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-console*.service
%{_unitdir}/openstack-nova-xvpvncproxy.service
%{_unitdir}/openstack-nova-spicehtml5proxy.service
%endif
%if 0%{?rhel}
%{_initddir}/openstack-nova-consoleauth
%endif

%files cells
%{_bindir}/nova-cells
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-cells.service
%endif

%files novncproxy
%{_bindir}/nova-novncproxy
%if 0%{?fedora} >= 17
%{_unitdir}/openstack-nova-novncproxy.service
%endif
%if 0%{?rhel}
%{_initddir}/openstack-nova-novncproxy
%endif
%config(noreplace) %{_sysconfdir}/sysconfig/openstack-nova-novncproxy

%files -n python-nova
%defattr(-,root,root,-)
%doc nova/LICENSE
%{python_sitelib}/nova
%{python_sitelib}/nova-%{version}*.egg-info

%if 0%{?with_doc}
%files doc
%doc nova/LICENSE nova/doc/build/html
%endif

%changelog
* Wed Sep 11 2013 Dan Prince <dprince@redhat.com> - 2013.2-0.19.b3
- Rebase on downstream packages.
- Drop b3 from package name.
- Comment out patches.
- Drop build dependency on python-d2to1.
- Add compute dependency on genisoimage (for Cloud Drive support)
- Add compute dependency on sysfsutils  (for volume support)
- Add dependency on python-oslo-messaging (in preparation for I)
- Add build dep on python-oslo-sphinx (patch removed).

* Mon Sep 09 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.2-0.19.b3
- Fix compute_node_get_all() for Nova Baremetal

* Mon Sep 09 2013 Pádraig Brady <pbrady@redhat.com> - 2013.2-0.18.b3
- Avoid deprecated options in distribution config files

* Mon Sep 09 2013 Dan Prince <dprince@redhat.com> - 2013.2-0.17.b3
- Add dependency on python-babel
- Add dependency on python-jinja2

* Mon Sep 09 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.2-0.16.b3
- Update to Havana milestone 3

* Tue Aug 27 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.2-0.15.b2
- Fix the tarball download link (SOURCE0)

* Tue Aug 27 2013 Xavier Queralt <xqueralt@redhat.com> - 2013.2-0.14.b2
- Set auth_version=v2.0 in nova-dist.conf to avoid http://pad.lv/1154809

* Tue Aug 27 2013 Xavier Queralt <xqueralt@redhat.com> - 2013.2-0.13.b2
- Remove Folsom release deprecated config options from nova-dist.conf

* Tue Aug 27 2013 Xavier Queralt <xqueralt@redhat.com> - 2013.2-0.12.b2
- Add the second dhcpbridge-flagfile to nova-dist.conf 

* Tue Aug 27 2013 Xavier Queralt <xqueralt@redhat.com> - 2013.2-0.11.b2
- Change the default config to poll for DB connection indefinitely

* Wed Aug 07 2013 Xavier Queralt <xqueralt@redhat.com> - 2013.2-0.10.b2
- Create a nova-dist.conf file with default values under /usr/share

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2013.2-0.9.b2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Jul 22 2013 Pádraig Brady <pbrady@redhat.com> - 2013.2-0.8.b2
- Update to Havana milestone 2

* Mon Jun 24 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.2-0.6.b1
- Add the novncproxy subpackage (moved from the novnc package)

* Mon Jun 24 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.2-0.4.h1
- Remove requirements file to be more flexible with dep versions

* Fri Jun 14 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.2-0.3.h1
- Fix an issue with the version string

* Mon Jun 10 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.2-0.2.h1
- Add a runtime dep on python-six
- Fix verision reporting

* Fri Jun 07 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.2-0.1.h1
- Update to Havana milestone 1
- Add a build-time dep on python-d2to1
- Add a build-time dep on python-pbr

* Fri May 17 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.1-2
- Check QCOW2 image size during root disk creation (CVE-2013-2096)

* Mon May 13 2013 Pádraig Brady <pbrady@redhat.com> - 2013.1.1-1
- Update to stable/grizzly 2013.1.1 release

* Fri May 10 2013 Pádraig Brady <pbrady@redhat.com> - 2013.1-3
- Make openstack-nova-network depend on ebtables #961567

* Thu Apr 11 2013 Pádraig Brady <pbrady@redhat.com> - 2013.1-2
- Fix nova network dnsmasq invocation failure #951144

* Mon Apr 08 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.1-1
- Update to Grizzly final

* Tue Apr 02 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.1-0.12.rc2
- Update to Grizzly rc2

* Fri Mar 22 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.1-0.11.rc1
- Update to Grizzly rc1

* Wed Mar 20 2013 Pádraig Brady - 2013.1-0.10.g3
- Remove /etc/tgt/conf.d/nova.conf which was invalid for grizzly

* Tue Mar 12 2013 Pádraig Brady - 2013.1-0.9.g3
- Allow openstack-nova-doc to be installed in isolation

* Thu Feb 28 2013 Dan Prince <dprince@redhat.com> - 2013.1-0.8.g3
- Use LIBGUESTFS_ATTACH_METHOD=appliance to allow injection to work

* Tue Feb 26 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.1-0.7.g3
- Fix dependency issues caused by the Milestone 3 update

* Mon Feb 25 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.1-0.6.g3
- Update to Grizzly milestone 3

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2013.1-0.5.g2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan 11 2013 Nikola Đipanov <ndipanov@redhat.com> - 2013.1-0.4.g2
- Update to Grizzly milestone 2
- Add the version info file
- Add python-stevedore dependency
- Add the cells subpackage and service file

* Thu Dec 06 2012 Nikola Đipanov <ndipanov@redhat.com> - 2013.1-0.3.g1
- signing_dir renamed from incorrect signing_dirname in default nova.conf

* Thu Nov 29 2012 Nikola Đipanov <ndipanov@redhat.com> 2013.1-0.2.g1
-Fix a few spec file issues introduced by the Grizzly update

* Wed Nov 28 2012 Nikola Đipanov <ndipanov@redhat.com> 2013.1-0.1.g1
- Update to Grizzly milestone 1
- Remove volume subpackage - removed from Grizzly
- Add the conductor subpackage - new service added in Grizzly
- Depend on python-libguestfs instead of libguestfs-mount
- Don't add the nova user to the group fuse
- Removes openstack-utils from requirements for nova-common

* Thu Sep 27 2012 Pádraig Brady <pbrady@redhat.com> - 2012.2-1
- Update to folsom final

* Wed Sep 26 2012 Pádraig Brady <pbrady@redhat.com> - 2012.2-0.11.rc1
- Support newer polkit config format to allow communication with libvirtd
- Fix to ensure that tgt configuration is honored

* Fri Sep 21 2012 Pádraig Brady <pbrady@redhat.com> - 2012.2-0.8.rc1
- Update to folsom rc1

* Mon Sep 17 2012 Alan Pevec <apevec@redhat.com> - 2012.2-0.7.f3
- Remove user config from paste ini files

* Mon Aug 27 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.6.f3
- Update to folsom milestone 3

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2012.2-0.4.f1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun 08 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.3.f1
- Enable libguestfs image inspection

* Wed Jun 06 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.2.f1
- Fix up protocol case handling for security groups (CVE-2012-2654)

* Tue May 29 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.1.f1
- Update to folsom milestone 1

* Wed May 16 2012 Alan Pevec <apevec@redhat.com> - 2012.1-6
- Remove m2crypto and other dependencies no loner needed by Essex

* Wed May 16 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-5
- Sync up with Essex stable branch
- Handle updated qemu-img info output
- Remove redundant and outdated openstack-nova-db-setup

* Wed May 09 2012 Alan Pevec <apevec@redhat.com> - 2012.1-4
- Remove the socat dependency no longer needed by Essex

* Wed Apr 27 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-3
- Reference new Essex services at installation

* Wed Apr 18 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-2
- Sync up with Essex stable branch
- Support more flexible guest image file injection
- Enforce quota on security group rules (#814275, CVE-2012-2101)
- Provide startup scripts for the Essex VNC services
- Provide a startup script for the separated metadata api service

* Sun Apr  8 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-1
- Update to Essex release

* Thu Mar 29 2012 Russell Bryant <rbryant@redhat.com> 2012.1-0.10.rc1
- Remove the outdated nova-debug tool
- CVE-2012-1585 openstack-nova: Long server names grow nova-api log files significantly

* Mon Mar 26 2012 Mark McLoughlin <markmc@redhat.com> - 2012.1-0.9.rc1
- Avoid killing dnsmasq on network service shutdown (#805947)

* Tue Mar 20 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.8.rc1
- Update to Essex release candidate 1

* Fri Mar 16 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.8.e4
- Include an upstream fix for errors logged when syncing power states
- Support non blocking libvirt operations
- Fix an exception when querying a server through the API (#803905)
- Suppress deprecation warnings with db sync at install (#801302)
- Avoid and cater for missing libvirt instance images (#801791)

* Fri Mar  6 2012 Alan Pevec <apevec@redhat.com> - 2012.1-0.7.e4
- Fixup permissions on nova config files

* Fri Mar  6 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.6.e4
- Depend on bridge-utils
- Support fully transparent handling of the new ini config file

* Fri Mar  2 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.5.e4
- Update to Essex milestone 4.
- explicitly select the libvirt firewall driver in default nova.conf.
- Add dependency on python-iso8601.
- Enable --force_dhcp_release.
- Switch to the new ini format config file.

* Mon Feb 13 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.4.e3
- Support --force_dhcp_release (#788485)

* Thu Feb  2 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.3.e3
- Suppress a warning from `nova-manage image convert`
- Add the openstack-nova-cert service which now handles the CA folder
- Change the default message broker from rabbitmq to qpid
- Enable the new rootwrap helper, to minimize sudo config

* Fri Jan 27 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.2.e3
- Suppress erroneous output to stdout on package install (#785115)
- Specify a connection_type in nova.conf, needed by essex-3
- Depend on python-carrot, currently needed by essex-3
- Remove the rabbitmq-server dependency as it's now optional
- Have python-nova depend on the messaging libs, not openstack-nova

* Thu Jan 26 2012 Pádraig Brady <P@draigBrady.com> - 2012.1-0.1.e3
- Update to essex milestone 3

* Mon Jan 23 2012 Pádraig Brady <P@draigBrady.com> - 2011.3.1-2
- Fix a REST API v1.0 bug causing a regression with deltacloud

* Fri Jan 20 2012 Pádraig Brady <P@draigBrady.com> - 2011.3.1-1
- Update to 2011.3.1 release
- Allow empty mysql root password in mysql setup script
- Enable mysqld at boot in mysql setup script

* Wed Jan 18 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3.1-0.4.10818%{?dist}
- Update to latest 2011.3.1 release candidate
- Re-add nova-{clear-rabbit-queues,instance-usage-audit}

* Tue Jan 17 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3.1-0.3.10814
- nova-stack isn't missing after all

* Tue Jan 17 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3.1-0.2.10814
- nova-{stack,clear-rabbit-queues,instance-usage-audit} temporarily removed because of lp#917676

* Tue Jan 17 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3.1-0.1.10814
- Update to 2011.3.1 release candidate
- Only adds 4 patches from upstream which we didn't already have

* Wed Jan 11 2012 Pádraig Brady <P@draigBrady.com> - 2011.3-19
- Fix libguestfs support for specified partitions
- Fix tenant bypass by authenticated users using API (#772202, CVE-2012-0030)

* Fri Jan  6 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3-18
- Fix up recent patches which don't apply

* Fri Jan  6 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3-17
- Backport tgtadm off-by-one fix from upstream (#752709)

* Fri Jan  6 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3-16
- Rebase to latest upstream stable/diablo, pulling in ~50 patches

* Fri Jan  6 2012 Mark McLoughlin <markmc@redhat.com> - 2011.3-15
- Move recent patches into git (no functional changes)

* Fri Dec 30 2011 Pádraig Brady <P@draigBrady.com> - 2011.3-14
- Don't require the fuse group (#770927)
- Require the fuse package (to avoid #767852)

* Tue Dec 14 2011 Pádraig Brady <P@draigBrady.com> - 2011.3-13
- Sanitize EC2 manifests and image tarballs (#767236, CVE 2011-4596)
- update libguestfs support

* Tue Dec 06 2011 Russell Bryant <rbryant@redhat.com> - 2011.3-11
- Add --yes, --rootpw, and --novapw options to openstack-nova-db-setup.

* Wed Nov 30 2011 Pádraig Brady <P@draigBrady.com> - 2011.3-10
- Add libguestfs support

* Tue Nov 29 2011 Pádraig Brady <P@draigBrady.com> - 2011.3-9
- Update the libvirt dependency from 0.8.2 to 0.8.7
- Ensure we don't access the net when building docs

* Tue Nov 29 2011 Russell Bryant <rbryant@redhat.com> - 2011.3-8
- Change default database to mysql. (#735012)

* Mon Nov 14 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-7
- Add ~20 significant fixes from upstream stable branch

* Wed Oct 26 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-6
- Fix password leak in EC2 API (#749385, CVE 2011-4076)

* Mon Oct 24 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-5
- Fix block migration (#741690)

* Mon Oct 17 2011 Bob Kukura <rkukura@redhat.com> - 2011.3-4
- Add dependency on python-amqplib (#746685)

* Wed Sep 28 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-3
- Fix lazy load exception with security groups (#741307)
- Fix issue with nova-network deleting the default route (#741686)
- Fix errors caused by MySQL connection pooling (#741312)

* Mon Sep 26 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-2
- Manage the package's patches in git; no functional changes.

* Thu Sep 22 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-1
- Update to Diablo final.
- Drop some upstreamed patches.
- Update the metadata-accept patch to what's proposed for essex.
- Switch rpc impl from carrot to kombu.

* Mon Sep 19 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.10.d4
- Use tgtadm instead of ietadm (#737046)

* Wed Sep 14 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.9.d4
- Remove python-libguestfs dependency (#738187)

* Mon Sep  5 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.8.d4
- Add iptables rule to allow EC2 metadata requests (#734347)

* Sat Sep  3 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.7.d4
- Add iptables rules to allow requests to dnsmasq (#734347)

* Wed Aug 31 2011 Angus Salkeld <asalkeld@redhat.com> - 2011.3-0.6.d4
- Add the one man page provided by nova.
- Start services with --flagfile rather than --flag-file (#735070)

* Tue Aug 30 2011 Angus Salkeld <asalkeld@redhat.com> - 2011.3-0.5.d4
- Switch from SysV init scripts to systemd units (#734345)

* Mon Aug 29 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.4.d4
- Don't generate root CA during %%post (#707199)
- The nobody group shouldn't own files in /var/lib/nova
- Add workaround for sphinx-build segfault

* Fri Aug 26 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.3.d4
- Update to diablo-4 milestone
- Use statically assigned uid:gid 162:162 (#732442)
- Collapse all sub-packages into openstack-nova; w/o upgrade path
- Reduce use of macros
- Rename stack to nova-stack
- Fix openssl.cnf.tmpl script-without-shebang rpmlint warning
- Really remove ajaxterm
- Mark polkit file as %%config

* Mon Aug 22 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.2.1449bzr
- Remove dependency on python-novaclient

* Wed Aug 17 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.1.1449bzr
- Update to latest upstream.
- nova-import-canonical-imagestore has been removed
- nova-clear-rabbit-queues was added

* Tue Aug  9 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.2.1409bzr
- Update to newer upstream
- nova-instancemonitor has been removed
- nova-instance-usage-audit added

* Tue Aug  9 2011 Mark McLoughlin <markmc@redhat.com> - 2011.3-0.1.bzr1130
- More cleanups
- Change release tag to reflect pre-release status

* Wed Jun 29 2011 Matt Domsch <mdomsch@fedoraproject.org> - 2011.3-1087.1
- Initial package from Alexander Sakhnov <asakhnov@mirantis.com>
  with cleanups by Matt Domsch
