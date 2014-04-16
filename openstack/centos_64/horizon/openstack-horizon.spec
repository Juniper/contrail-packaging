
%define mod_name openstack_dashboard
%define script_name /dashboard
%define httpd_conf openstack-dashboard.conf
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}


Name:       django-horizon

Version:    2013.1.4
Release:    %{_relstr}
Summary:    Django application for talking to Openstack %{?_gitVer}

Group:      Development/Libraries
License:    ASL 2.0
URL:        http://horizon.openstack.org
BuildArch:  noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: nodejs

#Source0:    http://launchpad.net/horizon/%{release_name}/%{release_name}-%{milestone}/+download/horizon-%{version}~%{release_letter}%{milestone}.tar.gz
#Source1:    openstack_dashboard.conf

# This was supposed to be in essex-3 but came 2 patches too late
# Patch1:     django-horizon-drop-openstackx.patch
# Dep is for testing only, so not required for a first run
# Patch2:     django-horizon-remove-test-dep.patch
# Place sqlite DB in /var/lib/openstack_dashboard
# Patch3:     django-horizon-db-var-path.patch

Requires:   Django >= 1.4
Requires:   nodejs
Requires:   python-django-openstack-auth
Requires:   python-django-compressor
Requires:   django-staticfiles
Requires:   python-dateutil
Requires:   python-cinderclient
Requires:   python-glanceclient
Requires:   python-keystoneclient
Requires:   python-novaclient
Requires:   python-quantumclient
Requires:   python-swiftclient
Requires:   pytz

%description
Horizon is a Django application for providing Openstack UI components.
It allows performing site administrator (viewing account resource usage,
configuring users, accounts, quotas, flavors, etc.) and end user
operations (start/stop/delete instances, create/restore snapshots, view
instance VNC console, etc.)


%package -n openstack-dashboard
Summary:    Openstack web user interface reference implementation  %{?_gitVer}
Group:      Applications/System

Requires:   httpd
Requires:   mod_wsgi
Requires:   django-horizon
Requires:   Django >= 1.4
Requires:   nodejs
Requires:   python-django-openstack-auth
Requires:   python-django-compressor
Requires:   django-staticfiles
Requires:   python-dateutil
Requires:   python-cinderclient
Requires:   python-glanceclient
Requires:   python-keystoneclient
Requires:   python-novaclient
Requires:   python-quantumclient
Requires:   python-swiftclient
Requires:   pytz


BuildRequires: python2-devel

%description -n openstack-dashboard
Openstack Dashboard is a web user interface for Openstack. The package
provides a reference implementation using the django-horizon project,
mostly consisting of javascript and theming to tie it act as a standalone
site.


%package doc
Summary:    Documentation for Django Horizon  %{?_gitVer}
Group:      Documentation

Requires:   %{name} = %{version}-%{release}

BuildRequires: python-sphinx

# Doc building basically means we have to mirror Requires:
#BuildRequires: openstack-glance
#BuildRequires: python-cloudfiles >= 1.7.9.3
#BuildRequires: python-dateutil
#BuildRequires: python-keystoneclient
#BuildRequires: python-novaclient >= 2012.1
#BuildRequires: python-quantumclient


%description doc
Documentation for the Django Horizon application for talking with Openstack


%prep
#%setup -q -n horizon-%{version}
#%patch1 -p1
#%patch2 -p1
#%patch3 -p1
## if [ -d horizon ]; then
   ## (cd horizon; git stash; git pull)
## else
   ## git clone git@bitbucket.org:contrail_admin/horizon.git
## fi


%build
pushd horizon
#%{__python} setup.py build

echo 'WSGISocketPrefix run/wsgi' > %{httpd_conf}
echo '<VirtualHost *:80>' >> %{httpd_conf}
echo '    WSGIScriptAlias %{script_name} %{python_sitelib}/%{mod_name}/wsgi/django.wsgi' >> %{httpd_conf}
echo '    Alias /static/%{mod_name} %{python_sitelib}/%{mod_name}/static/openstack_dashboard' >> %{httpd_conf}
echo '    WSGIDaemonProcess dashboard' >> %{httpd_conf}
echo '    WSGIProcessGroup dashboard' >> %{httpd_conf}
echo '    #DocumentRoot %HORIZON_DIR%/.blackhole/' >> %{httpd_conf}
echo '    <Directory %{script_name}>' >> %{httpd_conf}
echo '        Options FollowSymLinks' >> %{httpd_conf}
echo '        AllowOverride None' >> %{httpd_conf}
echo '    </Directory>' >> %{httpd_conf}
echo '    <Directory %{python_sitelib}/%{mod_name}/>' >> %{httpd_conf}
echo '        Options Indexes FollowSymLinks MultiViews' >> %{httpd_conf}
echo '        AllowOverride None' >> %{httpd_conf}
echo '        Order allow,deny' >> %{httpd_conf}
echo '        allow from all' >> %{httpd_conf}
echo '    </Directory>' >> %{httpd_conf}
echo '    ErrorLog logs/error_log' >> %{httpd_conf}
echo '    LogLevel crit' >> %{httpd_conf}
echo '    CustomLog access_log combine' >> %{httpd_conf}
echo '</VirtualHost>' >> %{httpd_conf}
popd

%install
pushd horizon
%{__python} setup.py install --root %{buildroot}

install -m 0644 -D -p %{httpd_conf} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{httpd_conf}


sed -e 's|^STATIC_ROOT = .*|STATIC_ROOT = os.path.join\("/var/www/html", "static"\)|' -i %{buildroot}%{python_sitelib}/openstack_dashboard/settings.py

# This is needed for docs building
cp openstack_dashboard/local/local_settings.py.example \
   openstack_dashboard/local/local_settings.py

export PYTHONPATH="$( pwd ):$PYTHONPATH"
#sphinx-build -b horizon/html docs/source html

# Fix hidden-file-or-dir warnings
rm -fr horizon/html/.doctrees horizon/html/.buildinfo

install -d -m 755 %{buildroot}%{_sysconfdir}/openstack_dashboard
#rm openstack_dashboard/local/local_settings.py
cp openstack_dashboard/local/local_settings.py \
   %{buildroot}%{_sysconfdir}/openstack_dashboard/local_settings
#ln -s %{buildroot}%{_sysconfdir}/openstack_dashboard/local_settings \
#      %{buildroot}%{_sysconfdir}/oopenstack_dashboard/local/local_settings.py

cp openstack_dashboard/local/local_settings.py \
   %{buildroot}%{python_sitelib}/%{mod_name}/local/local_settings.py

rm -rf %{buildroot}%{python_sitelib}/horizon/test

install -d -m 755 %{buildroot}/var/www/html/static

%files
%{python_sitelib}/horizon
%{python_sitelib}/horizon*.egg-info


%files -n openstack-dashboard
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{httpd_conf}
%config(noreplace) %{_sysconfdir}/openstack_dashboard/local_settings
%config(noreplace) %{python_sitelib}/openstack_dashboard/local/local_settings.py
%{python_sitelib}/openstack_dashboard
%{python_sitelib}/bin/less
%{python_sitelib}/bin/lib/less
%dir %attr(0755, apache, root) /var/www/html/static

%post -n openstack-dashboard
runuser -p apache -c "echo yes | django-admin collectstatic --settings=settings --pythonpath=%{python_sitelib}/openstack_dashboard"

#%files doc
#%doc horizon/html
