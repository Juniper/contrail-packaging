# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_fileList:1}
%define         _flist      %{_fileList}
%else
%define         _flist      None
%endif
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
%if 0%{?_skuTag:1}
%define         _sku     %{_skuTag}
%else
%define         _sku      None
%endif
%if 0%{?_osVer:1}
%define         _osver   %(echo %{_osVer} | sed 's,[-|.],,g')
%else
%define         _osver   %(PYTHONPATH=%{PYTHONPATH}:%{_builddir}/../tools/packaging/build/ python -c "import package_utils; print package_utils.get_platform()")
%endif
%if 0%{?_pkgSrcDirs:1}
%define         _pkgDirs  %{_pkgSrcDirs}
%else
%define         _pkgDirs  /cs-shared/builder/cache/%{_osver}/%{_sku}
%endif
%if 0%{?_pkgFile:1}
%define         _pkgfile %{_pkgFile}
%else
%define         _pkgfile  %{_builddir}/../tools/packaging/package_configs/%{_osver}-%{_sku}-thirdparty
%endif


Name:		    contrail-thirdparty-packages
Version:	    %{_verstr}
Release:	    %{_relstr}~%{_sku}%{?dist}
Summary:	    Contrail Installer %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc



%description
Contrail Thirdparty Packages - Container of Contrail Thirdparty RPMs

%install

# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_packages
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_thirdparty_repo

# install files
pushd %{_builddir}/..
install -p -m 755 tools/packaging/build/thirdparty_setup_centos.sh %{buildroot}%{_contrailopt}/contrail_packages/thirdparty_setup.sh
%{_builddir}/../tools/packaging/build/copy_thirdparty_packages.py --package-file %{_pkgfile} \
                                                                  --destination-dir %{buildroot}%{_contrailopt}/contrail_thirdparty_repo/ \
                                                                  --source-dirs %{_pkgDirs}
#create repo
createrepo %{buildroot}%{_contrailopt}/contrail_thirdparty_repo/

%files
%defattr(-, root, root)
%{_contrailopt}/contrail_thirdparty_repo/*
%{_contrailopt}/contrail_packages/thirdparty_setup.sh

%changelog

