%define mod_name contrail-openstack-dashboard
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif

%{echo: "Building release %{_relstr}\n"}


Name:       contrail-openstack-dashboard
Version:    2013.2
Release:    %{_relstr}
Summary:    Horizon Plugin for Contrail Neutron implementation %{?_gitVer}

Group:      Development/Libraries
License:    ASL 2.0
URL:        http://github.com/Juniper/contrail-horizon
BuildArch:  noarch

Requires:   openstack-dashboard

%description
Horizon Plugin for Contrail Neutron implementation

%build

%install

install -d -m 755 %{buildroot}%{python_sitelib}/contrail_openstack_dashboard

# Copy everything to /usr/share
cp *.py %{buildroot}%{python_sitelib}/contrail_openstack_dashboard
cp -prf openstack_dashboard %{buildroot}%{python_sitelib}/contrail_openstack_dashboard


%files -n contrail-openstack-dashboard
%dir %{python_sitelib}/contrail_openstack_dashboard
%{python_sitelib}/contrail_openstack_dashboard/*.py*
%{python_sitelib}/contrail_openstack_dashboard/openstack_dashboard

%post -n %{mod_name}
if [ -e /usr/share/openstack-dashboard/static ] ; then
  cp -prf %{python_sitelib}/contrail_openstack_dashboard/openstack_dashboard/static/*    /usr/share/openstack-dashboard/static
fi

%postun -n %{mod_name}
if [ -e /usr/share/openstack-dashboard/static/dashboard/js/contrail.networktopology.js ] ; then
  rm -f /usr/share/openstack-dashboard/static/dashboard/js/contrail.networktopology.js
fi
