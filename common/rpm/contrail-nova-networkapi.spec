# contrail-nova-networkapi spec file

%define		_package_name	contrail-nova-networkapi
%if 0%{?_buildTag:1}
%define		_relstr		%{_buildTag}
%else
%define		_relstr		%(date -u +%y%m%d%H%M)
%endif
%if 0%{?_srcVer:1}
%define		_verstr		%{_srcVer}
%else
%define		_verstr		1
%endif

%{echo: "Building rpm package for %{_package_name} release %{_relstr}\n"}

Name:		contrail-nova-networkapi
Version:	%{_verstr}
Release:	%{_relstr}1%{?dist}
Summary:	OpenContrail networking api for nova

Group:		Applications/System
License:	Commercial
URL:		http://www.juniper.net/
Vendor:		Juniper Network Inc

BuildRequires:	python2-devel	
BuildRequires:	python-setuptools
#Requires:	

%description
OpenContrail networking api for nova


%build
	rm -rf %{buildroot}
	(cd %{_builddir}/../; scons contrail-nova-networkapi)


%install
	(cd %{_builddir}/../build/noarch/contrail_nova_networkapi && python setup.py install --root=%{buildroot})


%files
/usr/lib/python2.7/site-packages/*
%doc



%changelog

