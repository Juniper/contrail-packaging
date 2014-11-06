#!/bin/bash

SM=""
WEBUI=""
CLIENT=""
HOSTIP=""
LOCALHOSTIP=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp' | awk 'NR==1'`
 
function usage()
{
    echo "Usage"
    echo ""
    echo "$0"
    echo "\t-h --help"
    echo "\t--sm=$SM"
    echo "\t--webui=$WEBUI"
    echo "\t--sm-client=$SMCLIENT"
    echo "\t--hostip=$HOSTIP"
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
        --sm)
            SM=$VALUE
            ;;
        --webui)
            WEBUI=$VALUE
            ;;
        --sm-client)
            SMCLIENT=$VALUE
            ;;
        --hostip)
            HOSTIP=$VALUE
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
   yum -y install $PKGS/epel-release-6-8.noarch.rpm
fi

if [ "$SM" != "" ]; then
  echo "SM is $SM" 
  # convert https to http, since was not able to get the repos
  sed -i 's/https:/http:/g' /etc/yum.repos.d/epel.repo
  yum -y install $PKGS/puppetlabs-release-el-6.noarch.rpm

  # Install server manager
  yum -y install $SM
  if [ "$HOSTIP" == "" ]; then
     HOSTIP=$LOCALHOSTIP
  fi
  sed -i "s/listen_ip_addr = .*/listen_ip_addr = $HOSTIP/g" /opt/contrail/server_manager/sm-config.ini
  echo "Configure /etc/cobbler/ dhcp.template, named.template, settings to bring up server manager"
fi

if [ "$WEBUI" != "" ]; then
  echo "WEBUI is $WEBUI"
  # install webui
  yum -y install $WEBUI
  # Modify webui config file
  WEBUI_CONF_FILE=/etc/contrail/config.global.js
  grep "config.featurePkg.serverManager = {};" $WEBUI_CONF_FILE
  if [ $? != 0 ]; then
     echo "config.featurePkg.serverManager = {};" >> $WEBUI_CONF_FILE
  fi

  grep "config.featurePkg.serverManager.path = '/usr/src/contrail/contrail-web-server-manager';" $WEBUI_CONF_FILE
  if [ $? != 0 ]; then
     echo "config.featurePkg.serverManager.path = '/usr/src/contrail/contrail-web-server-manager';" >> $WEBUI_CONF_FILE
  fi

  grep "config.featurePkg.serverManager.enable " $WEBUI_CONF_FILE
  if [ $? != 0 ]; then
    echo "config.featurePkg.serverManager.enable = true;" >> $WEBUI_CONF_FILE
  fi

  sed -i "s/config.orchestration.Manager = .*/config.orchestration.Manager = 'none'/g" $WEBUI_CONF_FILE
  sed -i "s/config.discoveryService.enable = .*/config.discoveryService.enable = false;/g" $WEBUI_CONF_FILE
  sed -i "s/config.featurePkg.webController.enable = .*/config.featurePkg.webController.enable = false;/g" $WEBUI_CONF_FILE
  sed -i "s/config.featurePkg.serverManager.enable = .*/config.featurePkg.serverManager.enable = true;/g" $WEBUI_CONF_FILE

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
