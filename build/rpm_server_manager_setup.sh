#!/bin/bash

SM=""
WEBUI=""
SMCLIENT=""
HOSTIP=""
SMMON=""
DOMAIN=""
HOST_IP_LIST=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp'`
LOCALHOSTIP=`echo $HOST_IP_LIST | cut -d' ' -f1`
echo $LOCALHOSTIP
yum clean all

function usage()
{
    echo "Usage"
    echo ""
    echo "$0"
    echo "\t-h --help"
    echo "\t--sm=$SM"
    echo "\t--webui=$WEBUI"
    echo "\t--sm-client=$SMCLIENT"
    echo "\t--sm-mon=$SMMON"
    echo "\t--hostip=$HOSTIP"
    echo "\t--domain=$DOMAIN"
    echo "\toptions: --no_passenger"
    echo "\t--all"
    echo ""
}

function passenger_install()
{

  gem install rack passenger
  passenger-install-apache2-module --auto --languages 'ruby,python,nodejs'
  mkdir -p /usr/share/puppet/rack/puppetmasterd
  mkdir -p /usr/share/puppet/rack/puppetmasterd/public /usr/share/puppet/rack/puppetmasterd/tmp
  cp /usr/share/puppet/ext/rack/config.ru /usr/share/puppet/rack/puppetmasterd/
  chown puppet:puppet /usr/share/puppet/rack/puppetmasterd/config.ru
  if [ -e /etc/httpd/conf.d/puppetmaster.conf ]; then
    mv /etc/httpd/conf.d/puppetmaster.conf /etc/httpd/conf.d/puppetmaster.conf.save
  fi
  cp ./puppetmaster.conf /etc/httpd/conf.d/puppetmaster.conf
  rel=`passenger --version`
  rel=( $rel )
  sed -i "s|LoadModule passenger_module /usr/lib/ruby/gems/1.8/gems/passenger-4.0.53/buildout/apache2/mod_passenger.so|LoadModule passenger_module /usr/lib/ruby/gems/1.8/gems/passenger-${rel[3]}/buildout/apache2/mod_passenger.so|g" /etc/httpd/conf.d/puppetmaster.conf
  sed -i "s|PassengerRoot /usr/lib/ruby/gems/1.8/gems/passenger-4.0.53|PassengerRoot /usr/lib/ruby/gems/1.8/gems/passenger-${rel[3]}|g" /etc/httpd/conf.d/puppetmaster.conf
  host=`echo $HOSTNAME | awk '{print tolower($0)}'`
  if [ "$DOMAIN" != "" ]; then
    output="$(find /var/lib/puppet/ssl/certs/ -name "${host}.${DOMAIN}*.pem")"
    output=( $output )
    sed -i "s|SSLCertificateFile.*|SSLCertificateFile      ${output[0]}|g" /etc/httpd/conf.d/puppetmaster.conf
    output="$(find /var/lib/puppet/ssl/private_keys/ -name "${host}.${DOMAIN}*.pem")"
    output=( $output )
    sed -i "s|SSLCertificateKeyFile.*|SSLCertificateKeyFile   ${output[0]}|g" /etc/httpd/conf.d/puppetmaster.conf
    sed -i "s|ErrorLog .*|ErrorLog /var/log/httpd/${host}.${DOMAIN}_ssl_error.log|g" /etc/httpd/conf.d/puppetmaster.conf
    sed -i "s|CustomLog .*|CustomLog /var/log/httpd/${host}.${DOMAIN}_ssl_access.log combined|g" /etc/httpd/conf.d/puppetmaster.conf
  else
    output="$(find /var/lib/puppet/ssl/certs/ -name "${host}*.pem")"
    output=( $output )
    sed -i "s|SSLCertificateFile.*|SSLCertificateFile      ${output[0]}|g" /etc/httpd/conf.d/puppetmaster.conf
    output="$(find /var/lib/puppet/ssl/private_keys/ -name "${host}*.pem")"
    output=( $output )
    sed -i "s|SSLCertificateKeyFile.*|SSLCertificateKeyFile   ${output[0]}|g" /etc/httpd/conf.d/puppetmaster.conf
    sed -i "s|ErrorLog .*|ErrorLog /var/log/httpd/${host}_ssl_error.log|g" /etc/httpd/conf.d/puppetmaster.conf
    sed -i "s|CustomLog .*|CustomLog /var/log/httpd/${host}_ssl_access.log combined|g" /etc/httpd/conf.d/puppetmaster.conf
  fi
  service puppetmaster start
  service puppetmaster stop
  /etc/init.d/httpd restart
  chkconfig puppetmaster off
  chkconfig httpd on

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
            output="$(find packages/ -name "contrail-*.rpm")"
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
              elif [[ "$line" != *client*  &&  "$line" != *monitoring*  &&  "$line" != *web* ]];
              then
                SM=$line
              fi
            done < temp.txt
            rm temp.txt
            ;;
        --sm)
            SM=$VALUE
            ;;
        --sm-mon)
            SMMON=$VALUE
            ;;
        --webui)
            WEBUI=$VALUE
            ;;
        --sm-client)
            SMCLIENT=$VALUE
            ;;
        --hostip)
            HOSTIP=$VALUE
            rm -rf ./IP.txt
            echo $HOSTIP >> IP.txt
            ;;
        --domain)
            DOMAIN=$VALUE
            ;;
        --no_passenger)
            PASSENGER="no"
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done
PKGS=./packages

if [ "$SM" != ""  -o  "$WEBUI" != "" ]; then
   # Get the epel and puupetlab repo packages
   wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
   wget http://yum.puppetlabs.com/puppetlabs-release-el-6.noarch.rpm
   # Install epel repo
   yum -y install ./epel-release-6-8.noarch.rpm
   rm -rf ./epel-release-6-8.noarch.rpm
   yum clean all
fi

if [ "$SM" != "" ]; then
  echo "SM is $SM"
  # convert https to http, since was not able to get the repos
  sed -i 's/https:/http:/g' /etc/yum.repos.d/epel.repo
  # Install the puppetlabs-release repo
  yum -y install ./puppetlabs-release-el-6.noarch.rpm
  rm -rf ./puppetlabs-release-el-6.noarch.rpm
  yum clean all
  # Install server manager
  yum -y install $SM
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

  if [ "$PASSENGER" != "no"  ]; then
    passenger_install
  fi

  if [ "$DOMAIN" != "" ]; then
    grep "manage_forward_zones: ['$DOMAIN']" /etc/cobbler/settings
    if [ $? != 0 ]; then
      sed -i "s/manage_forward_zones:.*/manage_forward_zones: ['$DOMAIN']/g" >> /etc/cobbler/settings
    fi
  fi

  echo "IMPORTANT: CONFIGURE /ETC/COBBLER/DHCP.TEMPLATE, NAMED.TEMPLATE, SETTINGS TO BRING UP SERVER MANAGER."

fi

if [ "$WEBUI" != "" ]; then
  echo "WEBUI is $WEBUI"
  # install webui
  yum -y install $WEBUI
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
    sed -i "s/config.featurePkg.serverManager.enable = .*/config.featurePkg.serverManager.enable = true;/g" >> $WEBUI_CONF_FILE
  else
    echo "config.featurePkg.serverManager.enable = true;" >> $WEBUI_CONF_FILE
  fi
  if [ "$HOSTIP" == "" ]; then
     HOSTIP=$LOCALHOSTIP
  fi
  grep "config.orchestration" $WEBUI_CONF_FILE
  if [ $? == 0 ]; then
    sed -i "s/config.orchestration = .*/config.orchestration = {};/g" >> $WEBUI_CONF_FILE
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
  service redis restart
  service supervisord restart

  # start webui
  mkdir -p /var/log/contrail/
  service supervisor-webui restart
fi

if [ "$SMCLIENT" != "" ]; then
  echo "SMCLIENT is $SMCLIENT"
  yum -y install $SMCLIENT
  if [ "$HOSTIP" == "" ]; then
     HOSTIP=$LOCALHOSTIP
  fi
  sed -i "s/listen_ip_addr = .*/listen_ip_addr = $HOSTIP/g" /opt/contrail/server_manager/client/sm-client-config.ini
fi

if [ "$SMMON" != "" ]; then
  echo "SMMON is $SMMON"
  yum -y install $SMMON
  echo "IMPORTANT: CONFIGURE /ETC/COBBLER/DHCP.TEMPLATE, NAMED.TEMPLATE, SETTINGS TO BRING UP SERVER MANAGER."
fi
