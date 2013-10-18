# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contraildns /etc/contrail/dns
%define         _namedlogdir /var/log/named
%define         _contrailetc /etc/contrail
%define         _supervisordir /etc/contrail/supervisord_dns_files
%define         _distropkgdir tools/packaging/common/control_files

%if 0%{?fedora} >= 17
%define         _servicedir  /usr/lib/systemd/system
%endif
%define         _osVer       %(uname -r)
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

Name:		    contrail-dns
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail Dns %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	    sudo

%description
Contrail DNS package

BuildRequires:  systemd-units

%prep
# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=contrail-controller
grep $gitrepo .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "please run rpmbuild from contrail-controller git tree"
    exit -1
fi


%build

#BUILD_DIR=%_repository_dir
#if [ -z %{?_repository_dir} ]; then
 #  BUILD_DIR=$( cat  %{SOURCE0} )
#fi

#pushd $BUILD_DIR
if [ ! -f build/debug/dns/dnsd ] ; then
    scons  -U --target=%{_target_cpu}  src/dns
    if [ $? -ne 0 ] ; then
        echo " Dnsd build failed"
        exit -1
    fi
fi

#pushd $BUILD_DIR
if [ ! -f build/third_party/bind/bin/named/named ] || [ ! -f build/third_party/bind/bin/rndc/rndc ] ; then
    scons -U --target=%{_target_cpu}  lib/bind
    if [ $? -ne 0 ] ; then
        echo " Bind build failed"
        exit -1
    fi
fi

%install
#BUILD_DIR=%_repository_dir
#if [ -z %{?_repository_dir} ]; then
#   BUILD_DIR=$( cat  %{SOURCE0} )
#fi
#pushd $BUILD_DIR


# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_contraildns}
install -d -m 755 %{buildroot}%{_supervisordir}
%if 0%{?fedora} >= 17
install -d -m 755 %{buildroot}%{_servicedir}
%endif
%if 0%{?rhel}
install -d -m 755 %{buildroot}%{_initddir}
%endif
install -d -m 755 %{buildroot}%{_namedlogdir}

# ND - how to get here ??
pushd %{_builddir}/..
# install bin files
install -p -m 755 build/third_party/bind/bin/named/named  %{buildroot}%{_bindir}/named
install -p -m 755 build/third_party/bind/bin/rndc/rndc    %{buildroot}%{_bindir}/rndc
install -p -m 755 build/debug/dns/dnsd                    %{buildroot}%{_bindir}/dnsd

# install etc files
install -p -m 644 %{_distropkgdir}/rndc.conf                %{buildroot}%{_contraildns}/rndc.conf
install -p -m 644 %{_distropkgdir}/named.conf               %{buildroot}%{_contraildns}/named.conf
%if 0%{?fedora} >= 17
install -p -m 755 %{_distropkgdir}/supervisor-dns.service     %{buildroot}%{_servicedir}/supervisor-dns.service
%endif
%if 0%{?rhel}
install -p -m 755 %{_distropkgdir}/supervisor-dns.initd     %{buildroot}%{_initddir}/supervisor-dns
install -p -m 755 %{_distropkgdir}/contrail-dns.initd.supervisord %{buildroot}%{_initddir}/contrail-dns
install -p -m 755 %{_distropkgdir}/contrail-named.initd.supervisord %{buildroot}%{_initddir}/contrail-named
%endif

#install .ini files for supervisord
install -p -m 755 %{_distropkgdir}/supervisord_dns.conf %{buildroot}%{_contrailetc}/supervisord_dns.conf  
install -p -m 755 %{_distropkgdir}/contrail-dns.ini %{buildroot}%{_supervisordir}/contrail-dns.ini
install -p -m 755 %{_distropkgdir}/contrail-named.ini %{buildroot}%{_supervisordir}/contrail-named.ini


%post
%if 0%{?fedora} >= 17
/bin/systemctl daemon-reload
%endif

%preun
%if 0%{?fedora} >= 17
/bin/systemctl stop supervisor-dns.service
if [ $1 = 0 ] ; then
    /bin/systemctl --no-reload disable supervisor-dns.service
fi
/bin/systemctl stop supervisor-named.service
if [ $1 = 0 ] ; then
    /bin/systemctl --no-reload disable supervisor-named.service
fi
%endif
exit 0

%postun
%if 0%{?fedora} >= 17
if [ $1 = 0 ] ; then
    /bin/systemctl daemon-reload
fi
%endif
exit 0

%files
%defattr(-, root, root)
%{_bindir}/named
%{_bindir}/rndc
%{_bindir}/dnsd
%{_contraildns}
%{_namedlogdir}

%{_contraildns}/named.conf
%{_contraildns}/rndc.conf
%{_supervisordir}/contrail-named.ini
%{_supervisordir}/contrail-dns.ini
%{_contrailetc}/supervisord_dns.conf
%if 0%{?fedora} >= 17
%{_servicedir}/supervisor-dns.service
%endif
%if 0%{?rhel}
%{_initddir}
%endif

%changelog
