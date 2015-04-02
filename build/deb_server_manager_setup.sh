#!/bin/bash
set -x
datetime_string=`date +%Y_%m_%d__%H_%M_%S`
mkdir -p /var/log/contrail/install_logs/
exec > /var/log/contrail/install_logs/install_$datetime_string.log
# copy files over

space="    "

ALL=""
SM=""
SMCLIENT=""
HOSTIP=""
SMMON=""
WEBUI=""
WEBCORE=""
DOMAIN=""
APPARMOR=""
PASSENGER=""
BINDLOGGING=""
HOST_IP_LIST=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp'`
LOCALHOSTIP=`echo $HOST_IP_LIST | cut -d' ' -f1`
echo $LOCALHOSTIP

function usage()
{
    echo "Usage"
    echo ""
    echo "$0"
    echo "\t-h --help"
    echo "\t--sm=$SM"
    echo "\t--sm-client=$SMCLIENT"
    echo "\t--webui=$WEBUI"
    echo "\t--sm-mon=$SMMON"
    echo "\t--hostip=$HOSTIP"
    echo "\t--domain=$DOMAIN"
    echo "\t--all"
    echo "\t*extra options* --bind_apparmor --no_passenger"
    echo ""
}

if [ "$#" -eq 0 ]; then
   usage
   exit
fi

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        -h | --help)
            usage
            exit
            ;;
        --all)
            ALL="all"
            ;;
        --sm)
            SM=$VALUE
            ;;
        --webui)
            WEBUI=$VALUE
            ;;
        --sm-mon)
            SMMON=$VALUE
            ;;
        --sm-client)
            SMCLIENT=$VALUE
            ;;
        --hostip)
            HOSTIP=$VALUE
            rm -rf ./IP.txt
            echo $HOSTIP >> ./IP.txt
            ;;
        --domain)
            DOMAIN=$VALUE
            ;;
        --no_passenger)
            PASSENGER="no"
            ;;
        --bind_logging)
            BINDLOGGING="yes"
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

if [ "$ALL" != "" ]; then
   output="$(find ./ -name "contrail-*.deb")"
   printf "%s\n" "${output}" >> temp.txt
   while read line;
   do
     if [[ "$line" == *client* ]];
     then
       SMCLIENT=$line
     elif [[ "$line" == *monitoring* ]];
     then
       SMMON=$line
     elif [[ "$line" == *web-server-manager* ]];
     then
       WEBUI=$line
     elif [[ "$line" == *web-core* ]];
     then
       WEBCORE=$line
     elif [[ "$line" != *client*  &&  "$line" != *monitoring*  &&  "$line" != *web* ]];
     then
       SM=$line
     fi
   done < temp.txt
   rm temp.txt
fi

cd /etc/apt/
# create repo with only local packages
datetime_string=`date +%Y_%m_%d__%H_%M_%S`
cp sources.list sources.list.$datetime_string
echo "deb file:/opt/contrail/contrail_server_manager ./" > local_repo

#modify /etc/apt/soruces.list/ to add local repo on the top
grep "deb file:/opt/contrail/contrail_server_manager ./" sources.list

if [ $? != 0 ]; then
     cat local_repo sources.list > new_sources.list
     mv new_sources.list sources.list
     apt-get update --yes
fi

# Allow unauthenticated pacakges to get installed.
# Do not over-write apt.conf. Instead just append what is necessary
# retaining other useful configurations such as http::proxy info.
apt_auth="APT::Get::AllowUnauthenticated \"true\";"
grep --quiet "$apt_auth" apt.conf
if [ "$?" != "0" ]; then
    echo "$apt_auth" >> apt.conf
fi

#scan pkgs in local repo and create Packages.gz
cd /opt/contrail/contrail_server_manager
apt-get -y install dpkg-dev
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
apt-get update --yes

# install base packages and fabric utils
#DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install contrail-setup
#pip install --upgrade --no-deps --index-url='' /opt/contrail/python_packages/ecdsa-0.10.tar.gz

apt-get -y install gdebi-core

cd /opt/contrail/contrail_server_manager


function save_cobbler_state()
{
  echo "$space### Begin: Saving Cobbler State"
  mkdir -p /cobbler_save_state
  cp /etc/mail/sendmail.cf /cobbler_save_state/
  cp /etc/ntp.conf /cobbler_save_state/
  cp /etc/contrail_smgr/tags.ini /cobbler_save_state/
  cp -r /etc/cobbler/* /cobbler_save_state/
  cp /etc/bind/named.conf.options /cobbler_save_state/
  echo "$space### End: Saving Cobbler State"
}

function replace_cobbler_state()
{
  echo "$space### Begin: Replacing Cobbler State"
  cp /cobbler_save_state/named.conf.options /etc/bind/
  cp /cobbler_save_state/dhcp.template /etc/cobbler/
  cp /cobbler_save_state/named.template /etc/cobbler/
  cp /cobbler_save_state/zone.template /etc/cobbler/
  cp /cobbler_save_state/settings /etc/cobbler/
  cp /cobbler_save_state/modules.conf /etc/cobbler/
  cp -r /cobbler_save_state/zone_templates /etc/cobbler/
  cp /cobbler_save_state/sendmail.cf /etc/mail/
  cp /cobbler_save_state/ntp.conf /etc/
  cp /cobbler_save_state/tags.ini /etc/contrail_smgr/
  echo "$space### End: Replacing Cobbler State"
}


function passenger_install()
{
  rel=`lsb_release -r`
  rel=( $rel )
  if [ ${rel[1]} == "14.04"  ]; then
    passenger_install_14
  else
    passenger_install_12
  fi
}
function passenger_install_14()
{
  apt-get -y install libcurl4-openssl-dev libssl-dev zlib1g-dev apache2-threaded-dev ruby-dev libapr1-dev libaprutil1-dev
  gem install rack
  gem install passenger --version 4.0.59
  apt-get -y install puppetmaster-passenger="3.7.3-1puppetlabs1"
  service apache2 stop
  if [ -e /etc/apt/preferences.d/00-puppet.pref ]; then
    rm /etc/apt/preferences.d/00-puppet.pref
  fi
  echo -e "# /etc/apt/preferences.d/00-puppet.pref\nPackage: puppet puppet-common puppetmaster-passenger\nPin: version 3.7.3\nPin-Priority: 501" >> /etc/apt/preferences.d/00-puppet.pref
  passenger-install-apache2-module --auto --languages 'ruby,python,nodejs' &> /dev/null
  mkdir -p /usr/share/puppet/rack/puppetmasterd
  mkdir -p /usr/share/puppet/rack/puppetmasterd/public /usr/share/puppet/rack/puppetmasterd/tmp
  cp /usr/share/puppet/ext/rack/config.ru /usr/share/puppet/rack/puppetmasterd/
  chown puppet:puppet /usr/share/puppet/rack/puppetmasterd/config.ru
  if [ -e /etc/apache2/sites-available/puppetmaster.conf ]; then
    mv /etc/apache2/sites-available/puppetmaster.conf /etc/apache2/sites-available/puppetmaster.conf.save
  fi
  cp ./puppetmaster /etc/apache2/sites-available/puppetmaster.conf
  # passenger version is hard coded at puppetmasterd, hence the following change
  rel=`passenger --version`
  rel=( $rel )
  sed -i "s|LoadModule passenger_module /var/lib/gems/1.8/gems/passenger-4.0.53/buildout/apache2/mod_passenger.so|LoadModule passenger_module /var/lib/gems/1.9.1/gems/passenger-${rel[3]}/buildout/apache2/mod_passenger.so|g" /etc/apache2/sites-available/puppetmaster.conf
  sed -i "s|PassengerRoot /var/lib/gems/1.8/gems/passenger-4.0.53|PassengerRoot /var/lib/gems/1.9.1/gems/passenger-${rel[3]}|g" /etc/apache2/sites-available/puppetmaster.conf
  sed -i "s|PassengerDefaultRuby /usr/bin/ruby1.8|PassengerDefaultRuby /usr/bin/ruby1.9.1|g" /etc/apache2/sites-available/puppetmaster.conf
  a2ensite puppetmaster
  host=`echo $HOSTNAME | awk '{print tolower($0)}'`
  if [ "$DOMAIN" != "" ]; then
    output="$(find /var/lib/puppet/ssl/certs/ -name "${host}.${DOMAIN}*.pem")"
    output=( $output )
    sed -i "s|SSLCertificateFile.*|SSLCertificateFile      ${output[0]}|g" /etc/apache2/sites-available/puppetmaster.conf
    output="$(find /var/lib/puppet/ssl/private_keys/ -name "${host}.${DOMAIN}*.pem")"
    output=( $output )
    sed -i "s|SSLCertificateKeyFile.*|SSLCertificateKeyFile   ${output[0]}|g" /etc/apache2/sites-available/puppetmaster.conf
    sed -i "s|ErrorLog .*|ErrorLog /var/log/apache2/${host}.${DOMAIN}_ssl_error.log|g" /etc/apache2/sites-available/puppetmaster.conf
    sed -i "s|CustomLog .*|CustomLog /var/log/apache2/${host}.${DOMAIN}_ssl_access.log combined|g" /etc/apache2/sites-available/puppetmaster.conf
  else
    output="$(find /var/lib/puppet/ssl/certs/ -name "${host}*.pem")"
    output=( $output )
    sed -i "s|SSLCertificateFile.*|SSLCertificateFile      ${output[0]}|g" /etc/apache2/sites-available/puppetmaster.conf
    output="$(find /var/lib/puppet/ssl/private_keys/ -name "${host}*.pem")"
    output=( $output )
    sed -i "s|SSLCertificateKeyFile.*|SSLCertificateKeyFile   ${output[0]}|g" /etc/apache2/sites-available/puppetmaster.conf
    sed -i "s|ErrorLog .*|ErrorLog /var/log/apache2/${host}_ssl_error.log|g" /etc/apache2/sites-available/puppetmaster.conf
    sed -i "s|CustomLog .*|CustomLog /var/log/apache2/${host}_ssl_access.log combined|g" /etc/apache2/sites-available/puppetmaster.conf
  fi
  /etc/init.d/puppetmaster start
  /etc/init.d/puppetmaster stop
  /etc/init.d/apache2 restart
  update-rc.d -f puppetmaster remove
  sed -i "s|START=.*|START=no|g" /etc/default/puppetmaster
  echo "$space### End: Install Passenger"
}

function passenger_install_12()
{
    echo "$space### Begin: Install Passenger"
    apt-get -y install apache2 ruby1.8-dev rubygems libcurl4-openssl-dev libssl-dev zlib1g-dev apache2-threaded-dev libapr1-dev libaprutil1-dev
    a2enmod ssl
    a2enmod headers
    gem install rack passenger
    passenger-install-apache2-module --auto --languages 'ruby,python,nodejs' &> /dev/null
    mkdir -p /usr/share/puppet/rack/puppetmasterd
    mkdir -p /usr/share/puppet/rack/puppetmasterd/public /usr/share/puppet/rack/puppetmasterd/tmp
    cp /usr/share/puppet/ext/rack/config.ru /usr/share/puppet/rack/puppetmasterd/
    chown puppet:puppet /usr/share/puppet/rack/puppetmasterd/config.ru
    if [ -e /etc/apache2/sites-available/puppetmasterd ]; then
      mv /etc/apache2/sites-available/puppetmasterd /etc/apache2/sites-available/puppetmasterd.save
    fi
    cp ./puppetmaster /etc/apache2/sites-available/puppetmasterd
    # passenger version is hard coded at puppetmasterd, hence the following change
    rel=`passenger --version`
    rel=( $rel )
    sed -i "s|LoadModule passenger_module /var/lib/gems/1.8/gems/passenger-4.0.53/buildout/apache2/mod_passenger.so|LoadModule passenger_module /var/lib/gems/1.8/gems/passenger-${rel[3]}/buildout/apache2/mod_passenger.so|g" /etc/apache2/sites-available/puppetmasterd
    sed -i "s|PassengerRoot /var/lib/gems/1.8/gems/passenger-4.0.53|PassengerRoot /var/lib/gems/1.8/gems/passenger-${rel[3]}|g" /etc/apache2/sites-available/puppetmasterd
    a2ensite puppetmasterd
    host=`echo $HOSTNAME | awk '{print tolower($0)}'`
    if [ "$DOMAIN" != "" ]; then
      output="$(find /var/lib/puppet/ssl/certs/ -name "${host}.${DOMAIN}*.pem")"
      output=( $output )
      sed -i "s|SSLCertificateFile.*|SSLCertificateFile      ${output[0]}|g" /etc/apache2/sites-available/puppetmasterd
      output="$(find /var/lib/puppet/ssl/private_keys/ -name "${host}.${DOMAIN}*.pem")"
      output=( $output )
      sed -i "s|SSLCertificateKeyFile.*|SSLCertificateKeyFile   ${output[0]}|g" /etc/apache2/sites-available/puppetmasterd
      sed -i "s|ErrorLog .*|ErrorLog /var/log/apache2/${host}.${DOMAIN}_ssl_error.log|g" /etc/apache2/sites-available/puppetmasterd
      sed -i "s|CustomLog .*|CustomLog /var/log/apache2/${host}.${DOMAIN}_ssl_access.log combined|g" /etc/apache2/sites-available/puppetmasterd
    else
      output="$(find /var/lib/puppet/ssl/certs/ -name "${host}*.pem")"
      output=( $output )
      sed -i "s|SSLCertificateFile.*|SSLCertificateFile      ${output[0]}|g" /etc/apache2/sites-available/puppetmasterd
      output="$(find /var/lib/puppet/ssl/private_keys/ -name "${host}*.pem")"
      output=( $output )
      sed -i "s|SSLCertificateKeyFile.*|SSLCertificateKeyFile   ${output[0]}|g" /etc/apache2/sites-available/puppetmasterd
      sed -i "s|ErrorLog .*|ErrorLog /var/log/apache2/${host}_ssl_error.log|g" /etc/apache2/sites-available/puppetmasterd
      sed -i "s|CustomLog .*|CustomLog /var/log/apache2/${host}_ssl_access.log combined|g" /etc/apache2/sites-available/puppetmasterd
    fi
    /etc/init.d/puppetmaster start
    /etc/init.d/puppetmaster stop
    /etc/init.d/apache2 restart
    update-rc.d -f puppetmaster remove
    sed -i "s|START=.*|START=no|g" /etc/default/puppetmaster
    echo "$space### End: Install Passenger"
}

function install_cobbler()
{
  rel=`lsb_release -r`
  rel=( $rel )
  if [ ${rel[1]} == "14.04"  ]; then
    install_cobbler_14
  else
    install_cobbler_12
  fi
}

function install_cobbler_12()
{
  echo "$space### Begin: Install Cobbler"
  apt-get -y install apache2 libapache2-mod-wsgi tftpd-hpa python-urlgrabber python-django selinux-utils python-simplejson python-dev
  apt-get -y install python-software-properties debmirror
  wget -qO - http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_12.04/Release.key | apt-key add -
  add-apt-repository "deb http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_12.04/ ./"
  apt-get update --yes
  apt-get -y install cobbler="2.6.3-1"
  a2enmod proxy
  a2enmod proxy_http
  a2enmod version
  a2enmod wsgi
  setenforce 0
  cp -r /srv/www/cobbler /var/www/cobbler
  cp -r /srv/www/cobbler_webui_content /var/www/cobbler_webui_content
  cp ./cobbler.conf /etc/apache2/conf.d/
  cp ./cobbler_web.conf /etc/apache2/conf.d/
  cp ./cobbler.conf /etc/cobbler/
  cp ./cobbler_web.conf /etc/cobbler/
  sed -i "s/django.conf.urls /django.conf.urls.defaults /g" /usr/share/cobbler/web/cobbler_web/urls.py
  chmod 777 /var/lib/cobbler/webui_sessions/
  service cobblerd restart
  service apache2 restart
  echo "$space### End: Install Cobbler"
}

function install_cobbler_14()
{
  echo "$space### Begin: Install Cobbler"
  apt-get -y install apache2 libapache2-mod-wsgi tftpd-hpa python-urlgrabber python-django selinux-utils python-simplejson python-dev
  apt-get -y install python-software-properties debmirror
  wget -qO - http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_14.04/Release.key | apt-key add -
  add-apt-repository "deb http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_14.04/ ./"
  apt-get update --yes
  apt-get -y install cobbler="2.6.3-1"
  mkdir -p /etc/apache2/conf-available/
  cp ./cobbler_14.conf /etc/apache2/conf.d/cobbler.conf
  cp ./cobbler_web_14.conf /etc/apache2/conf.d/cobbler_web.conf
  cp ./cobbler_14.conf /etc/cobbler/cobbler.conf
  cp ./cobbler_web_14.conf /etc/cobbler/cobbler_web.conf
  cp /etc/apache2/conf.d/cobbler.conf /etc/apache2/conf-available/
  cp /etc/apache2/conf.d/cobbler_web.conf /etc/apache2/conf-available/
  a2enconf cobbler cobbler_web
  a2enmod proxy
  a2enmod proxy_http
  a2enmod wsgi
  cp -r /srv/www/cobbler /var/www/cobbler
  cp -r /srv/www/cobbler_webui_content /var/www/cobbler_webui_content
  chmod 777 /var/lib/cobbler/webui_sessions/
  SECRET_KEY=$(python -c 'import re;from random import choice; import sys; sys.stdout.write(re.escape("".join([choice("abcdefghijklmnopqrstuvwxyz0123456789^&*(-_=+)") for i in range(100)])))')
  sudo sed --in-place "s/^SECRET_KEY = .*/SECRET_KEY = '${SECRET_KEY}'/" /usr/share/cobbler/web/settings.py
  service cobblerd restart
  service apache2 restart
  echo "$space### End: Install Cobbler"
}

function bind_logging()
{
  mkdir /var/log/named
  touch /var/log/named/debug.log
  touch /var/log/named/query.log
  echo "logging {

    channel debug_log {
         file "/var/log/named/debug.log";
        severity debug 3;
        print-category yes;
        print-severity yes;
        print-time yes;
    };

    channel query_log {
        file "/var/log/named/query.log";
        severity dynamic;
        print-category yes;
        print-severity yes;
        print-time yes;
    };

    category resolver { debug_log; };
    category security { debug_log; };
    category queries { query_log; };

};" >> /etc/bind/named.conf
}


if [ "$SM" != "" ]; then
  echo "### Begin: Installing Server Manager"
  echo "SM is $SM"
  rel=`lsb_release -r`
  rel=( $rel )
  if [ ${rel[1]} == "14.04"  ]; then
    wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb
    gdebi -n puppetlabs-release-trusty.deb
    apt-get update --yes
    apt-get -y install puppet-common="3.7.3-1puppetlabs1"
    apt-get -y install puppetmaster-common="3.7.3-1puppetlabs1"
    apt-get -y install puppetmaster="3.7.3-1puppetlabs1"
    service puppetmaster stop
    service apache2 start
    gdebi -n nodejs_0.8.15-1contrail1_amd64.deb
  else
    wget https://apt.puppetlabs.com/puppetlabs-release-precise.deb
    gdebi -n puppetlabs-release-precise.deb
    apt-get update --yes
    apt-get -y install puppet-common="3.7.3-1puppetlabs1"
    apt-get -y install puppetmaster-common="3.7.3-1puppetlabs1"
    apt-get -y install puppetmaster="3.7.3-1puppetlabs1"
    gdebi -n nodejs_0.8.15-1contrail1_amd64.deb
  fi

  if [ -e /etc/init.d/apparmor ]; then
    /etc/init.d/apparmor stop
    update-rc.d -f apparmor remove
    apt-get --purge remove apparmor apparmor-utils libapparmor-perl libapparmor1 --yes
  fi

  apt-get -y install software-properties-common
  # Check if this is an upgrade
  check=`dpkg --list | grep "contrail-server-manager "`
  if [ "$check" != ""  ]; then
    # Upgrade
    save_cobbler_state
    cv=`cobbler --version`
    cv=( $cv  )
    if [ "${cv[1]}" != "2.6.3" ]; then
      dpkg -P --force-all python-cobbler
      dpkg -P --force-all cobbler-common
      dpkg -P --force-all cobbler-web
      dpkg -P --force-all cobbler
      dpkg -P --force-all contrail-server-manager
    fi
    install_cobbler
    if [ -e /etc/apache2/sites-enabled/puppetmasterd ]; then
      rm /etc/apache2/sites-enabled/puppetmasterd
    fi
    gdebi -n $SM
    replace_cobbler_state
  else
    install_cobbler
    gdebi -n $SM
  fi

  if [ "$HOSTIP" == "" ]; then
     HOSTIP=$LOCALHOSTIP
  fi
  sed -i "s/listen_ip_addr = .*/listen_ip_addr = $HOSTIP/g" /opt/contrail/server_manager/sm-config.ini

  # Adding server and Public DNS to /etc/resolv.conf if not present
  grep "nameserver $LOCALHOSTIP" /etc/resolv.conf
  if [ $? != 0 ]; then
    echo "nameserver $LOCALHOSTIP" >> /etc/resolv.conf
  fi
  grep "nameserver 8.8.8.8" /etc/resolv.conf
  if [ $? != 0 ]; then
    echo "nameserver 8.8.8.8" >> /etc/resolv.conf
  fi
  grep "bind_master: $LOCALHOSTIP" /etc/cobbler/settings
  if [ $? != 0 ]; then
    echo "bind_master: $LOCALHOSTIP" >> /etc/cobbler/settings
  fi

  if [ "$PASSENGER" != "no"  ]; then
    passenger_install
  fi

  if [ "$BINDLOGGING" == "yes" ]; then
    bind_logging
  fi

  if [ "$DOMAIN" != "" ]; then
    grep "manage_forward_zones: ['$DOMAIN']" /etc/cobbler/settings
    if [ $? != 0 ]; then
      sed -i "s/manage_forward_zones:.*/manage_forward_zones: ['$DOMAIN']/g" /etc/cobbler/settings
    fi
  fi
  echo "### End: Installing Server Manager"
  echo "IMPORTANT: CONFIGURE /ETC/COBBLER/DHCP.TEMPLATE, NAMED.TEMPLATE, SETTINGS TO BRING UP SERVER MANAGER."
  echo "Install log is at /var/log/contrail/install_logs/"
fi

if [ "$SMCLIENT" != "" ]; then
  echo "### Begin: Installing Server Manager Client"
  echo "SMCLIENT is $SMCLIENT"
  gdebi -n $SMCLIENT
  if [ "$HOSTIP" == "" ]; then
     HOSTIP=$LOCALHOSTIP
  fi
  sed -i "s/listen_ip_addr = .*/listen_ip_addr = $HOSTIP/g" /opt/contrail/server_manager/client/sm-client-config.ini
  echo "### End: Installing Server Manager Client"
fi

if [ "$WEBUI" != "" ]; then
  echo "### Begin: Installing Server Manager Web UI"
  echo "WEBUI is $WEBUI"
  # install webui
  if [ $WEBCORE!="" ]; then
    add-apt-repository ppa:rwky/redis --yes
    apt-get update --yes
    gdebi -n $WEBCORE
  fi
  gdebi -n $WEBUI
  # Modify webui config file
  WEBUI_CONF_FILE=/etc/contrail/config.global.js
  SM_CONF_FILE=/usr/src/contrail/contrail-web-server-manager/webroot/common/api/sm.config.js
  WEBUI_PATH=/usr/src/contrail/contrail-web-server-manager
  grep "config.featurePkg" $WEBUI_CONF_FILE
  if [ $? != 0 ]; then
     echo "config.featurePkg = {};" >> $WEBUI_CONF_FILE
     echo "config.featurePkg.serverManager = {};" >> $WEBUI_CONF_FILE
  fi
  grep "config.featurePkg.serverManager" $WEBUI_CONF_FILE
  if [ $? != 0 ]; then
     echo "config.featurePkg.serverManager = {};" >> $WEBUI_CONF_FILE
  fi
  grep "config.featurePkg.serverManager.path" $WEBUI_CONF_FILE
  if [ $? == 0  ]; then
     sed -i "s|config.featurePkg.serverManager.path = .*|config.featurePkg.serverManager.path = '$WEBUI_PATH';|g" $WEBUI_CONF_FILE
  else
     echo "config.featurePkg.serverManager.path = '$WEBUI_PATH';" >> $WEBUI_CONF_FILE
  fi
  grep "config.featurePkg.serverManager.enable" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s/config.featurePkg.serverManager.enable = .*/config.featurePkg.serverManager.enable = true;/g" $WEBUI_CONF_FILE
  else
    echo "config.featurePkg.serverManager.enable = true;" >> $WEBUI_CONF_FILE
  fi
  if [ "$HOSTIP" == "" ]; then
     HOSTIP=$LOCALHOSTIP
  fi
  grep "config.orchestration" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s/config.orchestration = .*/config.orchestration = {};/g" $WEBUI_CONF_FILE
  else
    echo "config.orchestration = {};" >> $WEBUI_CONF_FILE
  fi
  grep "config.orchestration.Manager" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s/config.orchestration.Manager = .*/config.orchestration.Manager = 'none'/g" $WEBUI_CONF_FILE
  else
    echo "config.orchestration.Manager = 'none';" >> $WEBUI_CONF_FILE
  fi
  grep "config.discoveryService" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s/config.discoveryService = .*/config.discoveryService = {};/g" $WEBUI_CONF_FILE
  else
    echo "config.discoveryService = {};" >> $WEBUI_CONF_FILE
  fi
  grep "config.discoveryService.enable" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s/config.discoveryService.enable = .*/config.discoveryService.enable = false;/g" $WEBUI_CONF_FILE
  else
    echo "config.discoveryService.enable = false;" >> $WEBUI_CONF_FILE
  fi
  grep "config.multi_tenancy" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s/config.multi_tenancy = .*/config.multi_tenancy = {};/g" $WEBUI_CONF_FILE
  else
    echo "config.multi_tenancy = {};" >> $WEBUI_CONF_FILE
  fi
  grep "config.multi_tenancy.enabled" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s/config.multi_tenancy.enabled = .*/config.multi_tenancy.enabled = false;/g" $WEBUI_CONF_FILE
  else
    echo "config.multi_tenancy.enabled = false;" >> $WEBUI_CONF_FILE
  fi
  grep "module.exports" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s|module.exports =.*||g" $WEBUI_CONF_FILE
  fi
  echo "module.exports = config;" >> $WEBUI_CONF_FILE
  sed -i "s/config.featurePkg.webController.enable = .*/config.featurePkg.webController.enable = false;/g" $WEBUI_CONF_FILE
  sed -i "s/smConfig.sm.server_ip = .*/smConfig.sm.server_ip = '$HOSTIP';/g" $SM_CONF_FILE
  sed -i "s/smConfig.sm.server_port = .*/smConfig.sm.server_port = 9001;/g" $SM_CONF_FILE
  sed -i "s/smConfig.sm.introspect_ip = .*/smConfig.sm.introspect_ip = '$HOSTIP';/g" $SM_CONF_FILE
  sed -i "s/smConfig.sm.introspect_port = .*/smConfig.sm.introspect_port = 8106;/g" $SM_CONF_FILE
  # start redis and supervisord
  service redis-server restart
  service supervisor restart

  # start webui
  mkdir -p /var/log/contrail/
  service supervisor-webui restart
  echo "### End: Installing Server Manager Web UI"
fi

if [ "$SMMON" != "" ]; then
  echo "### Begin: Installing Server Manager Monitoring"
  echo "SMMON is $SMMON"
  gdebi -n $SMMON
  echo "### End: Installing Server Manager Monitoring"
  echo "IMPORTANT: CONFIGURE /ETC/COBBLER/DHCP.TEMPLATE, NAMED.TEMPLATE, SETTINGS TO BRING UP SERVER MANAGER."
  echo "Install log is at /var/log/contrail/install_logs/"
fi
