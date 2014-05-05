# view contents of rpm file: rpm -qlp <filename>.rpm

%define		_base	node
%define		_contrailbase	/opt/contrail
%define     _sbtop      %(pwd | awk '{sub("tools/packaging/common/rpm", "", $1);print}')
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}

Name:		contrail-%{_base}js
Version:	0.8.15
Release:	%{_relstr}%{?dist}
Summary:	Contrail Systems NodeJS Package %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc


Provides:	npm
%if 0%{?fedora} >= 17
BuildRequires:	gcc
BuildRequires:	gcc-c++
%endif
%if 0%{?rhel}
BuildRequires:	devtoolset-1.1-gcc
BuildRequires:	devtoolset-1.1-gcc-c++
%endif
BuildRequires:	make
BuildRequires:	openssl-devel
BuildRequires:	libstdc++-devel
BuildRequires:	zlib-devel

%description
Contrail Systems NodeJS Package

%prep
rm -rf %{_builddir}/%{_base}js-v%{version}

%build
#cp -r -p %{_sourcedir}/contrail-webui/third-party/%{_base}-v%{version} %{_builddir}/
#pushd %{_builddir}/..
cd %{_sbtop}/third_party/%{_base}-v%{version}

./configure \
	--prefix=/usr \
	--shared-openssl \
	--shared-openssl-includes=%{_includedir} \
	--shared-zlib \
	--shared-zlib-includes=%{_includedir}
make binary %{?_smp_mflags}


%install
mkdir  -p %{buildroot}%{_contrailbase}/%{_base}js-v%{version}/bin
mkdir  -p %{buildroot}%{_bindir}
cp -p %{_sbtop}/third_party/%{_base}-v%{version}/out/Release/%{_base} %{buildroot}%{_contrailbase}/%{_base}js-v%{version}/bin/%{_base}js
ln -sf %{_contrailbase}/%{_base}js-v%{version}/bin/%{_base}js %{buildroot}%{_bindir}/%{_base}js-contrail

%files
%defattr(-,root,root,-)
%{_contrailbase}/%{_base}js-v%{version}/bin/*
%{_bindir}

%clean
rm -rf %{buildroot}

%changelog
* Fri Feb 9 2013 - bmandal@contrailsystems.com
-- Initial Version
