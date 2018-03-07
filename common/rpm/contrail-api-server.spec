# view contents of rpm file: rpm -qlp <filename>.rpm

%define     _distropkgdir	   build/package-build/SOURCES/ 
%define     _contrailetc        /etc/contrail
%if 0%{?fedora} >= 17

%endif
############# contrail paths ##############
%define     _packageType            rpm
%define     _homedir                /usr/share/contrail
%define     _binPath                /usr/bin
%define     _configDir              /etc/contrail
%define     _etcDefaultPath         /etc/sysconfig
%define     _etcDefaultFilePath     /etc/sysconfig/contrail
%define     _initdScriptFilePath    /etc/init.d/contrail
%define     _servicedir             /usr/lib/systemd/system
%define     _systemdServiceFilePath /usr/lib/systemd/system/contrail.service

%define     _postinstSrc            /packaging/rpm/control/postinst
%define     _initdScriptSrc         /packaging/rpm/init.d/contrail
%define     _defaultFileSrc         /packaging/rpm/sysconfig/contrail
%define     _systemdFileSrc         /packaging/rpm/systemd/contrail.service

%define     _initd                  /etc/init.d
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

#Requires:   go >= go1.9.4
Requires: mysql

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
##Nothing to do

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

## Get the dependencies and make the binaries

export GOPATH=$WD/../go
export PATH=$PATH:$WD/../go/bin
cd %{_srcDir}
#TODO uncomment below
make deps
make binaries

cd $WD

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
##TODO check what needs to be cleaned
rm -rf %{_specdir}/contrail-api-server.spec

######### files #########
%files
/usr/bin/contrail
/usr/share/contrail/
/etc/init.d/contrail
/etc/sysconfig/contrail
/usr/lib/systemd/system/contrail.service
/etc/contrail/apisrv.yml
######### pre #########
%pre
######### post #########
%post
[ -f /etc/sysconfig/contrail ] && . /etc/sysconfig/contrail

startCONTRAIL() {
  if [ -x /bin/systemctl ] ; then
    /bin/systemctl daemon-reload
        /bin/systemctl start contrail.service
    elif [ -x /etc/init.d/contrail ] ; then
        /etc/init.d/contrail start
    elif [ -x /etc/rc.d/init.d/contrail ] ; then
        /etc/rc.d/init.d/contrail start
    fi
}

stopCONTRAIL() {
    if [ -x /bin/systemctl ] ; then
        /bin/systemctl stop contrail.service > /dev/null 2>&1 || :
    elif [ -x /etc/init.d/contrail ] ; then
        /etc/init.d/contrail stop
    elif [ -x /etc/rc.d/init.d/contrail ] ; then
        /etc/rc.d/init.d/contrail stop
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
    useradd -r -g contrail -d /usr/share/contrail -s /sbin/nologin \
    -c "contrail user" contrail
    fi

  # copy user config files
  if [ ! -f $CONF_FILE ]; then
    cp /usr/share/contrail/apisrv.yaml $CONF_FILE
  fi

    # Set user permissions on /var/log/grafana, /var/lib/grafana
    mkdir -p /var/log/contrail /var/lib/contrail
    chown -R $CONTRAIL_USER:$CONTRAIL_GROUP /var/log/contrail /var/lib/contrail
    chmod 755 /var/log/contrail /var/lib/contrail

    # configuration files should not be modifiable by contrail user, as this can be a security issue
    chown -Rh root:$CONTRAIL_GROUP /etc/contrail/*
    chmod 755 /etc/contrail
    find /etc/contrail -type f -exec chmod 640 {} ';'
    find /etc/contrail -type d -exec chmod 755 {} ';'

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

[ -f /etc/sysconfig/contrail ] && . /etc/sysconfig/contrail

# copy config files if missing
if [ ! -f /etc/contrail/apisrv.yml ]; then
  echo "POSTTRANS: Config file not found"

  if [ -f /etc/contrail/apisrv.yml.rpmsave ]; then
    echo "POSTTRANS: /etc/contrail/apisrv.yml.rpmsave config file found."
    mv /etc/contrail/apisrv.yaml.rpmsave /etc/contrail/apisrv.yml
    echo "POSTTRANS: /etc/contrail/apisrv.yml restored"

    echo "POSTTRANS: Restoring config file permissions"
    chown -Rh root:$contrail_GROUP /etc/contrail/*
    chmod 755 /etc/contrail
    find /etc/contrail -type f -exec chmod 640 {} ';'
    find /etc/contrail -type d -exec chmod 755 {} ';'
  fi
fi

######### changelog #########
%changelog




