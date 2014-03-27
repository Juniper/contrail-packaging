%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}


Name:             openstack-cinder
Version:          2013.1
Release:          %{_relstr}
Summary:          OpenStack Volume (cinder) %{?_gitVer}

Group:            Applications/System
License:          ASL 2.0
URL:              http://www.openstack.org/software/openstack-storage/
#Source0:          https://launchpad.net/cinder/grizzly/grizzly-2/+download/cinder-2013.1~g2.tar.gz
Source1:          cinder.conf
Source2:          cinder.logrotate
Source3:          cinder-tgt.conf

%if 0%{?fedora} >= 17
Source10:         openstack-cinder-api.service
Source11:         openstack-cinder-scheduler.service
Source12:         openstack-cinder-volume.service
%endif
%if 0%{?rhel}
Source10:         openstack-cinder-api.initd
Source11:         openstack-cinder-scheduler.initd
Source12:         openstack-cinder-volume.initd
%endif

Source20:         cinder-sudoers

#
# patches_base=grizzly-2
#
Patch0001: 0001-Ensure-we-don-t-access-the-net-when-building-docs.patch

BuildArch:        noarch
BuildRequires:    intltool
BuildRequires:    python-sphinx
BuildRequires:    python-setuptools
BuildRequires:    python-netaddr
BuildRequires:    openstack-utils

Requires:         openstack-utils
Requires:         python-cinder = %{version}-%{release}

# as convenience
Requires:         python-cinderclient

%if 0%{?fedora} >= 17
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%endif
Requires(pre):    shadow-utils

Requires:         lvm2
Requires:         scsi-target-utils

%description
OpenStack Volume (codename Cinder) provides services to manage and
access block storage volumes for use by Virtual Machine instances.


%package -n       python-cinder
Summary:          OpenStack Volume Python libraries %{?_gitVer}
Group:            Applications/System

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
Requires:         python-cheetah

Requires:         python-sqlalchemy
Requires:         python-migrate

Requires:         python-paste-deploy
Requires:         python-routes
Requires:         python-webob

Requires:         python-glanceclient >= 1:0
Requires:         python-oslo-config

%description -n   python-cinder
OpenStack Volume (codename Cinder) provides services to manage and
access block storage volumes for use by Virtual Machine instances.

This package contains the cinder Python library.

%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Volume %{?_gitVer}
Group:            Documentation

Requires:         %{name} = %{version}-%{release}

BuildRequires:    openstack-utils
%if 0%{?fedora} >= 17
BuildRequires:    systemd-units
%endif
BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python-eventlet
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-webob
# while not strictly required, quiets the build down when building docs.
BuildRequires:    python-migrate, python-iso8601

%description      doc
OpenStack Volume (codename Cinder) provides services to manage and
access block storage volumes for use by Virtual Machine instances.

This package contains documentation files for cinder.
%endif

%prep
#%setup -q -n cinder-%{version}
## if [ ! -d cinder ]; then
   ## git clone ssh://git@bitbucket.org/contrail_admin/cinder
## else
   ## (cd cinder; git pull)
## fi

#%patch0001 -p1
pushd cinder

find . \( -name .gitignore -o -name .placeholder \) -delete

find cinder -name \*.py -exec sed -i '/\/usr\/bin\/env python/{d;q}' {} +

# TODO: Have the following handle multi line entries
sed -i '/setup_requires/d; /install_requires/d; /dependency_links/d' setup.py

%build
pushd cinder

# Move authtoken configuration out of paste.ini
openstack-config --del etc/cinder/api-paste.ini filter:authtoken admin_tenant_name
openstack-config --del etc/cinder/api-paste.ini filter:authtoken admin_user
openstack-config --del etc/cinder/api-paste.ini filter:authtoken admin_password
openstack-config --del etc/cinder/api-paste.ini filter:authtoken auth_host
openstack-config --del etc/cinder/api-paste.ini filter:authtoken auth_port
openstack-config --del etc/cinder/api-paste.ini filter:authtoken auth_protocol

%{__python} setup.py build

%install
pushd cinder
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# docs generation requires everything to be installed first
export PYTHONPATH="$( pwd ):$PYTHONPATH"

pushd doc

pwd

%if 0%{?with_doc}
SPHINX_DEBUG=1 sphinx-build -b html source build/html
# Fix hidden-file-or-dir warnings
pwd
rm -fr build/html/.doctrees build/html/.buildinfo
%endif

# Create dir link to avoid a sphinx-build exception
rm -fr build/man/.doctrees
mkdir -p build/man/.doctrees/
ln -s .  build/man/.doctrees/man
SPHINX_DEBUG=1 sphinx-build -b man -c source source/man build/man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/

popd

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/cinder
install -d -m 755 %{buildroot}%{_sharedstatedir}/cinder/tmp
install -d -m 755 %{buildroot}%{_localstatedir}/log/cinder

# Install config files
install -d -m 755 %{buildroot}%{_sysconfdir}/cinder
install -p -D -m 640 %{SOURCE1} %{buildroot}%{_sysconfdir}/cinder/cinder.conf
install -d -m 755 %{buildroot}%{_sysconfdir}/cinder/volumes
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/tgt/conf.d/cinder.conf
install -p -D -m 640 etc/cinder/rootwrap.conf %{buildroot}%{_sysconfdir}/cinder/rootwrap.conf
install -p -D -m 640 etc/cinder/api-paste.ini %{buildroot}%{_sysconfdir}/cinder/api-paste.ini
install -p -D -m 640 etc/cinder/policy.json %{buildroot}%{_sysconfdir}/cinder/policy.json

# Remove auth config from api-paste.ini
openstack-config --del %{buildroot}%{_sysconfdir}/cinder/api-paste.ini filter:authtoken admin_tenant_name
openstack-config --del %{buildroot}%{_sysconfdir}/cinder/api-paste.ini filter:authtoken admin_user
openstack-config --del %{buildroot}%{_sysconfdir}/cinder/api-paste.ini filter:authtoken admin_password

# Install initscripts for services
%if 0%{?fedora} >= 17
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/openstack-cinder-api.service
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_unitdir}/openstack-cinder-scheduler.service
install -p -D -m 644 %{SOURCE12} %{buildroot}%{_unitdir}/openstack-cinder-volume.service
%endif
%if 0%{?rhel}
install -p -D -m 755 %{SOURCE10} %{buildroot}%{_initddir}/openstack-cinder-api
install -p -D -m 755 %{SOURCE11} %{buildroot}%{_initddir}/openstack-cinder-scheduler
install -p -D -m 755 %{SOURCE12} %{buildroot}%{_initddir}/openstack-cinder-volume
%endif

# Install sudoers
install -p -D -m 440 %{SOURCE20} %{buildroot}%{_sysconfdir}/sudoers.d/cinder

# Install logrotate
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-cinder

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/cinder

# Install rootwrap files in /usr/share/cinder/rootwrap
mkdir -p %{buildroot}%{_datarootdir}/cinder/rootwrap/
install -p -D -m 644 etc/cinder/rootwrap.d/* %{buildroot}%{_datarootdir}/cinder/rootwrap/

install -D -m 644 cinder/db/sqlalchemy/migrate_repo/migrate.cfg %{buildroot}%{python_sitelib}/cinder/db/sqlalchemy/migrate_repo

# Remove unneeded in production stuff
rm -f %{buildroot}%{_bindir}/cinder-debug
rm -fr %{buildroot}%{python_sitelib}/cinder/tests/
rm -fr %{buildroot}%{python_sitelib}/run_tests.*
rm -f %{buildroot}/usr/share/doc/cinder/README*

%pre
#TODO:reserve 165 in the setup package
getent group cinder >/dev/null || groupadd -r cinder --gid 165
if ! getent passwd cinder >/dev/null; then
  useradd -u 165 -r -g cinder -G cinder,nobody -d %{_sharedstatedir}/cinder -s /sbin/nologin -c "OpenStack Cinder Daemons" cinder
fi
exit 0

%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    for svc in volume api scheduler; do
        /bin/systemctl --no-reload disable openstack-cinder-${svc}.service > /dev/null 2>&1 || :
        /bin/systemctl stop openstack-cinder-${svc}.service > /dev/null 2>&1 || :
    done
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in volume api scheduler; do
        /bin/systemctl try-restart openstack-cinder-${svc}.service >/dev/null 2>&1 || :
    done
fi

%files
%doc cinder/LICENSE

%dir %{_sysconfdir}/cinder
%config(noreplace) %attr(-, root, cinder) %{_sysconfdir}/cinder/cinder.conf
%config(noreplace) %attr(-, root, cinder) %{_sysconfdir}/cinder/api-paste.ini
%config(noreplace) %attr(-, root, cinder) %{_sysconfdir}/cinder/rootwrap.conf
%config(noreplace) %attr(-, root, cinder) %{_sysconfdir}/cinder/policy.json
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-cinder
%config(noreplace) %{_sysconfdir}/sudoers.d/cinder
%config(noreplace) %{_sysconfdir}/tgt/conf.d/cinder.conf

%dir %attr(0755, cinder, root) %{_localstatedir}/log/cinder
%dir %attr(0755, cinder, root) %{_localstatedir}/run/cinder
%dir %attr(0755, cinder, root) %{_sysconfdir}/cinder/volumes

%{_bindir}/cinder-*
%if 0%{?fedora} >= 17
%{_unitdir}/*.service
%endif
%if 0%{?rhel}
%{_initddir}/openstack-cinder-api
%{_initddir}/openstack-cinder-scheduler
%{_initddir}/openstack-cinder-volume
%endif
%{_datarootdir}/cinder
%{_mandir}/man1/cinder*.1.gz

%defattr(-, cinder, cinder, -)
%dir %{_sharedstatedir}/cinder
%dir %{_sharedstatedir}/cinder/tmp

%files -n python-cinder
%defattr(-,root,root,-)
%doc cinder/LICENSE
%{python_sitelib}/cinder
%{python_sitelib}/cinder-%{version}*.egg-info

%if 0%{?with_doc}
%files doc
%doc cinder/LICENSE cinder/doc/build/html
%endif

%changelog
* Tue Feb 19 2013 Dan Prince <dprince@redhat.com> - 2013.1-0.1.g2
- Add dependency on python-oslo-config.

* Thu Jan 10 2013 Eric Harney <eharney@redhat.com> - 2013.1-0.1.g2
- Update to Grizzly milestone 2

* Thu Nov 29 2012 Eric Harney <eharney@redhat.com> - 2013.1-0.1.g1
- Update to Grizzly milestone 1

* Wed Nov 14 2012 Eric Harney <eharney@redhat.com> - 2012.2-2
- Remove unused dependency on python-daemon

* Thu Sep 27 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-1
- Update to Folsom final

* Fri Sep 21 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.5.rc1
- Update to Folsom RC1

* Fri Sep 21 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.4.f3
- Fix to ensure that tgt configuration is honored

* Mon Sep 17 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.3.f3
- Move user config out of /etc/cinder/api-paste.ini
- Require python-cinderclient

* Mon Sep  3 2012 Pádraig Brady <P@draigBrady.com> - 2012.2-0.2.f3
- Initial release
