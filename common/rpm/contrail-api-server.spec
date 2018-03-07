# view contents of rpm file: rpm -qlp <filename>.rpm

%define     _distropkgdir      build/package-build/SOURCES/
%define     _contrailetc        %{_sysconfdir}/contrail
############# contrail paths ##############
%define     _homedir                %{_exec_prefix}/share/contrail
%define     _binPath                %{_exec_prefix}/sbin
%define     _configDir              %{_sysconfdir}/contrail
%define     _etcDefaultPath         %{_sysconfdir}/sysconfig
%define     _etcDefaultFilePath     %{_sysconfdir}/sysconfig/contrail
%define     _initdScriptFilePath    %{_sysconfdir}/init.d/contrail
%define     _servicedir             %{_exec_prefix}/lib/systemd/system
%define     _systemdServiceFilePath %{_exec_prefix}/lib/systemd/system/contrail.service

%define     _initdScriptSrc         /packaging/rpm/init.d/contrail
%define     _defaultFileSrc         /packaging/rpm/sysconfig/contrail
%define     _systemdFileSrc         /packaging/rpm/systemd/contrail.service

%define     _initd                  %{_sysconfdir}/init.d
%define     _srcDir                 ../go/src/github.com/Juniper/contrail
############# contrail paths ends##############

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

Name:       contrail-api-server
Version:    %{_verstr}
Release:    %{_relstr}
Summary:    Contrail API Server %{?_gitVer}

Group:              Applications/System
License:            Apache 2.0
URL:                https://github.com/Juniper/contrail
Vendor:             Juniper Networks Inc

Source:     %{name}

######### description #########
%description
Contrail API Server package


######### pre #########
%pre
[ -z "$CONTRAIL_USER" ] && CONTRAIL_USER="contrail"
[ -z "$CONTRAIL_GROUP" ] && CONTRAIL_GROUP="contrail"
if ! getent group "$CONTRAIL_GROUP" > /dev/null 2>&1 ; then
groupadd -r "$CONTRAIL_GROUP"
fi
if ! getent passwd "$CONTRAIL_USER" > /dev/null 2>&1 ; then
useradd -r -g contrail -d %{_exec_prefix}/share/contrail -s /sbin/nologin \
-c "contrail user" contrail
fi

######### build #########
%build
WD=$(pwd)

## Get the dependencies and make the binaries

export GOPATH=$WD/../go
export PATH=$PATH:$WD/../go/bin
cd %{_srcDir}

make deps
make binaries

cd $WD

######### install #########
%install
echo "BUILD ROOT"+%{buildroot}
echo "DISTRO ROOT"+%{_distropkgdir}
echo $(pwd)
rm -rf %{buildroot}%{_homedir}
rm -rf %{buildroot}%{_configDir}

mkdir -p %{buildroot}%{_homedir}
mkdir -p %{buildroot}%{_configDir}
mkdir -p %{buildroot}%{_initd}
mkdir -p %{buildroot}%{_etcDefaultPath}
mkdir -p %{buildroot}%{_servicedir}
mkdir -p %{buildroot}%{_binPath}
mkdir -p %{buildroot}%{_var}/log/contrail
mkdir -p %{buildroot}%{_var}/lib/contrail

WD=$(pwd)

install -p -m 755 %{_distropkgdir}/contrail %{buildroot}%{_initdScriptFilePath}
install -p -m 755 %{_distropkgdir}/contrail_syslog %{buildroot}%{_etcDefaultFilePath}
install -p -m 755 %{_distropkgdir}/contrail.service %{buildroot}%{_systemdServiceFilePath}

cp -r %{_srcDir}/dist %{buildroot}%{_homedir}/dist
cp -r %{_srcDir}/dist/contrail_linux_amd64 %{buildroot}%{_binPath}/contrail
cp -r -p %{_srcDir}/public %{buildroot}%{_homedir}
install -p %{_srcDir}/tools/init.sql %{buildroot}%{_homedir}
install -p %{_srcDir}/packaging/apisrv.yml  %{buildroot}%{_configDir}
rm -rf %{buildroot}%{_homedir}/bin

######### clean #########
%clean
rm -rf %{_specdir}/contrail-api-server.spec

######### files #########
%files
%{_exec_prefix}/sbin/contrail
%{_exec_prefix}/share/contrail/
%{_sysconfdir}/init.d/contrail
%{_sysconfdir}/sysconfig/contrail
%{_exec_prefix}/lib/systemd/system/contrail.service
%{_sysconfdir}/contrail/apisrv.yml

%attr(755,contrail,contrail) %{_var}/log/contrail
%attr(755,contrail,contrail) %{_var}/lib/contrail
%attr(755,root,contrail) %{_sysconfdir}/contrail/*

%config(noreplace) %{_sysconfdir}/contrail/apisrv.yml

######### post #########
%post
[ -f %{_sysconfdir}/sysconfig/contrail ] && . %{_sysconfdir}/sysconfig/contrail

# Initial installation: $1 == 1
if [ $1 -eq 1 ] ; then

    # copy user config files
    if [ ! -f $CONF_FILE ]; then
      cp %{_exec_prefix}/share/contrail/apisrv.yaml $CONF_FILE
    fi

    find %{_sysconfdir}/contrail -type f -exec chmod 640 {} ';'
    find %{_sysconfdir}/contrail -type d -exec chmod 755 {} ';'

fi

######### changelog #########
%changelog




