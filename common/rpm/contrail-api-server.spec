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
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Source:     %{name}

######### description #########
%description
Contrail API Server package

######### prep #########
%prep
##Nothing to do

######### setup #########
#%setup -n %{name}

######### prep #########
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

WD=$(pwd)

#install -p -m 755 %{_distropkgdir}%{_initdScriptSrc} %{buildroot}%{_initdScriptFilePath}
#install -p -m 755 %{_distropkgdir}%{_defaultFileSrc} %{buildroot}%{_etcDefaultFilePath}
#install -p -m 755 %{_distropkgdir}%{_systemdFileSrc} %{buildroot}%{_systemdServiceFilePath}

install -p -m 755 %{_distropkgdir}/contrail %{buildroot}%{_initdScriptFilePath}
install -p -m 755 %{_distropkgdir}/contrail_syslog %{buildroot}%{_etcDefaultFilePath}
install -p -m 755 %{_distropkgdir}/contrail.service %{buildroot}%{_systemdServiceFilePath}

#cp -r  %{_srcDir} %{buildroot}%{_homedir}
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
######### pre #########
%pre
######### post #########
%post
[ -f %{_sysconfdir}/sysconfig/contrail ] && . %{_sysconfdir}/sysconfig/contrail

startCONTRAIL() {
  if [ -x /bin/systemctl ] ; then
    /bin/systemctl daemon-reload
        /bin/systemctl start contrail.service
    elif [ -x %{_sysconfdir}/init.d/contrail ] ; then
        %{_sysconfdir}/init.d/contrail start
    elif [ -x %{_sysconfdir}/rc.d/init.d/contrail ] ; then
        %{_sysconfdir}/rc.d/init.d/contrail start
    fi
}

stopCONTRAIL() {
    if [ -x /bin/systemctl ] ; then
        /bin/systemctl stop contrail.service > /dev/null 2>&1 || :
    elif [ -x %{_sysconfdir}/init.d/contrail ] ; then
        %{_sysconfdir}/init.d/contrail stop
    elif [ -x %{_sysconfdir}/rc.d/init.d/contrail ] ; then
        %{_sysconfdir}/rc.d/init.d/contrail stop
    fi
}


# Initial installation: $1 == 1
# Upgrade: $1 == 2, and configured to restart on upgrade
if [ $1 -eq 1 ] ; then
    [ -z "$CONTRAIL_USER" ] && CONTRAIL_USER="contrail"
    [ -z "$CONTRAIL_GROUP" ] && CONTRAIL_GROUP="contrail"
    if ! getent group "$CONTRAIL_GROUP" > /dev/null 2>&1 ; then
    groupadd -r "$CONTRAIL_GROUP"
    fi
    if ! getent passwd "$CONTRAIL_USER" > /dev/null 2>&1 ; then
    useradd -r -g contrail -d %{_exec_prefix}/share/contrail -s /sbin/nologin \
    -c "contrail user" contrail
    fi

  # copy user config files
  if [ ! -f $CONF_FILE ]; then
    cp %{_exec_prefix}/share/contrail/apisrv.yaml $CONF_FILE
  fi

    # Set user permissions on %{_var}/log/grafana, %{_var}/lib/grafana
    mkdir -p %{_var}/log/contrail %{_var}/lib/contrail
    chown -R $CONTRAIL_USER:$CONTRAIL_GROUP %{_var}/log/contrail %{_var}/lib/contrail
    chmod 755 %{_var}/log/contrail %{_var}/lib/contrail

    # configuration files should not be modifiable by contrail user, as this can be a security issue
    chown -Rh root:$CONTRAIL_GROUP %{_sysconfdir}/contrail/*
    chmod 755 %{_sysconfdir}/contrail
    find %{_sysconfdir}/contrail -type f -exec chmod 640 {} ';'
    find %{_sysconfdir}/contrail -type d -exec chmod 755 {} ';'

  if [ -x /bin/systemctl ] ; then
    echo "### NOT starting on installation, please execute the following statements to configure contrail to start automatically using systemd"
    echo " sudo /bin/systemctl daemon-reload"
    echo " sudo /bin/systemctl enable contrail.service"
    echo "### You can start contrail by executing"
    echo " sudo /bin/systemctl start contrail.service"
  elif [ -x /sbin/chkconfig ] ; then
    echo "### NOT starting contrail by default on bootup, please execute"
    echo " sudo /sbin/chkconfig --add contrail"
    echo "### In order to start contrail, execute"
    echo " sudo service contrail start"
  fi
elif [ $1 -ge 2 ] ; then
  if [ "$RESTART_ON_UPGRADE" == "true" ]; then
    stopCONTRAIL
    startCONTRAIL
  fi
fi
######### preun #########
%preun
echo "POSTTRANS: Running script"

[ -f %{_sysconfdir}/sysconfig/contrail ] && . %{_sysconfdir}/sysconfig/contrail

# copy config files if missing
if [ ! -f %{_sysconfdir}/contrail/apisrv.yml ]; then
  echo "POSTTRANS: Config file not found"

  if [ -f %{_sysconfdir}/contrail/apisrv.yml.rpmsave ]; then
    echo "POSTTRANS: %{_sysconfdir}/contrail/apisrv.yml.rpmsave config file found."
    mv %{_sysconfdir}/contrail/apisrv.yaml.rpmsave %{_sysconfdir}/contrail/apisrv.yml
    echo "POSTTRANS: %{_sysconfdir}/contrail/apisrv.yml restored"

    echo "POSTTRANS: Restoring config file permissions"
    chown -Rh root:$contrail_GROUP %{_sysconfdir}/contrail/*
    chmod 755 %{_sysconfdir}/contrail
    find %{_sysconfdir}/contrail -type f -exec chmod 640 {} ';'
    find %{_sysconfdir}/contrail -type d -exec chmod 755 {} ';'
  fi
fi

######### changelog #########
%changelog




