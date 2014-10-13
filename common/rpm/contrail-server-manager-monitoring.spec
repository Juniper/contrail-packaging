
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

Name:            contrail-server-manager-monitoring
Version:            %{_verstr}
Release:          %{_relstr}%{?dist}
Summary:          contrail-server-manager-monitoring %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

#Requires:	  python-contrail >= %{_verstr}-%{_relstr}
Requires:	  python-contrail


BuildRequires:    make
BuildRequires:    gcc

%description
Contrail Server-Manager Monitoring package

%prep
gitrepo=contrail-controller
grep $gitrepo %{_builddir}/.git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi

%build
scons -U install_contrail_sm_monitoring --root=%{buildroot}

if [ $? -ne 0 ] ; then
    echo "build failed"
    exit -1
fi

%files
%defattr(-,root,root,-)
%{python_sitelib}/contrail_sm_monitoring*

%post
if [ -x /bin/systemctl ]; then
   /bin/systemctl --system daemon-reload
fi

%changelog
