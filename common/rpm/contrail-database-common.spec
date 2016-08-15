%define         _distropkgdir tools/packaging/common/control_files
%define         _centos %([ -e /etc/redhat-release ] && egrep -i centos /etc/redhat-release >> /dev/null && echo centos || echo "")
%define         _rhel %([ -e /etc/redhat-release ] && egrep -i "Red Hat" /etc/redhat-release > /dev/null && echo rhel || echo "")

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
Release:	    %{_relstr}%{?dist}
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

Summary: Contrail Database Common %{?_gitVer}
Name: contrail-database-common
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-database >= %{_verstr}-%{_relstr}
Requires: sysstat
Requires: datastax-agent

# Packaging zookeeper-3.4.8-0contrail1 for all rhel version
%if "%{_rhel}" == "rhel"
Requires: zookeeper >= 3.4.8-0contrail1
%endif

# Packaging zookeeper-3.4.8-0contrail1 from mitaka onwards
%if "%{_centos}" == "centos" && ( "%{_sku}" == "liberty" || "%{_sku}" == "kilo" || "%{_sku}" == "juno" )
Requires: zookeeper
%else
Requires: zookeeper >= 3.4.8-0contrail1
%endif


%description
Contrail Package Requirements for Contrail Database Common

%install
# zookeeper.initd will be brought in by zookeeper-3.4.8-0contrail1 packaged in centos/mitaka onwards
%if "%{_centos}" == "centos" && ( "%{_sku}" == "liberty" || "%{_sku}" == "kilo" || "%{_sku}" == "juno" )
pushd %{_builddir}/..
install -D -m 755 %{_distropkgdir}/zookeeper.initd %{buildroot}%{_initddir}/zookeeper
popd
%endif

%files
# zookeeper.initd will be brought in by zookeeper-3.4.8-0contrail1 packaged in centos/mitaka onwards
%if "%{_centos}" == "centos" && ( "%{_sku}" == "liberty" || "%{_sku}" == "kilo" || "%{_sku}" == "juno" )
%{_initddir}
%endif

%changelog
* Fri Aug 12 2016 Nagendra Maynattamai <npchandran@juniper.net>
- Adding dependency to zookeeper >= 3.4.8-0contrail1 for centos based platforms from mitaka onwards

* Sat Aug 06 2016 Nagendra Maynattamai <npchandran@juniper.net>
- Adding dependency to zookeeper >= 3.4.8-0contrail1 for rhel based platforms

* Fri Jul  15 2016 <ijohnson@juniper.net>
* Initial build.

