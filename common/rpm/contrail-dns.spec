# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contraildns /etc/contrail/dns
%define         _supervisordir /etc/contrail/supervisord_control_files
%define         _distropkgdir tools/packaging/common/control_files

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
scons  -U --target=%{_target_cpu}  src/dns
if [ $? -ne 0 ] ; then
    echo "contrail-dns build failed"
    exit -1
fi

#pushd $BUILD_DIR
scons -U --target=%{_target_cpu}  lib/bind
if [ $? -ne 0 ] ; then
    echo " Bind build failed"
    exit -1
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
%if 0%{?rhel}
install -d -m 755 %{buildroot}%{_initddir}
%endif

# ND - how to get here ??
pushd %{_builddir}/..
# install bin files
install -p -m 755 build/third_party/bind/bin/named/contrail-named  %{buildroot}%{_bindir}/contrail-named
install -p -m 755 build/third_party/bind/bin/rndc/contrail-rndc    %{buildroot}%{_bindir}/contrail-rndc
install -p -m 755 build/third_party/bind/bin/confgen/contrail-rndc-confgen    %{buildroot}%{_bindir}/contrail-rndc-confgen
install -p -m 755 build/debug/dns/contrail-dns            %{buildroot}%{_bindir}/contrail-dns

# install etc files
install -p -m 644 %{_distropkgdir}/contrail-rndc.conf       %{buildroot}%{_contraildns}/contrail-rndc.conf
install -p -m 644 %{_distropkgdir}/contrail-named.conf      %{buildroot}%{_contraildns}/contrail-named.conf
install -p -m 644 build/third_party/bind/COPYRIGHT          %{buildroot}%{_contraildns}/COPYRIGHT
%if 0%{?rhel}
install -p -m 755 %{_distropkgdir}/contrail-dns.initd.supervisord %{buildroot}%{_initddir}/contrail-dns
install -p -m 755 %{_distropkgdir}/contrail-named.initd.supervisord %{buildroot}%{_initddir}/contrail-named
%endif

#install .ini files for supervisord
install -p -m 755 %{_distropkgdir}/contrail-dns.ini %{buildroot}%{_supervisordir}/contrail-dns.ini
install -p -m 755 %{_distropkgdir}/contrail-named.ini %{buildroot}%{_supervisordir}/contrail-named.ini
perl -pi -e '{ s/user=contrail\s*//g; }' %{buildroot}%{_supervisordir}/contrail-named.ini
perl -pi -e '{ s/\/usr\/bin\/authbind //g; }' %{buildroot}%{_supervisordir}/contrail-named.ini

%post
%if 0%{?fedora} >= 17
/bin/systemctl daemon-reload
%endif

%preun
%if 0%{?fedora} >= 17
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
%{_bindir}/contrail-named
%{_bindir}/contrail-rndc
%{_bindir}/contrail-rndc-confgen
%{_bindir}/contrail-dns
%{_contraildns}

%{_contraildns}/contrail-named.conf
%{_contraildns}/contrail-rndc.conf
%{_contraildns}/COPYRIGHT
%{_supervisordir}/contrail-named.ini
%{_supervisordir}/contrail-dns.ini
%if 0%{?rhel}
%{_initddir}
%endif

%changelog
