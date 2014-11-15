#!/bin/bash

SM=""
WEBUI=""
SMCLIENT=""
HOSTIP=""
SMMON=""
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
    echo "\t--sm-mon=$SMMON"
    echo "\t--hostip=$HOSTIP"
    echo "\t--all"
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
fi

if [ "$SM" != "" ]; then
  echo "SM is $SM"
  # convert https to http, since was not able to get the repos
  sed -i 's/https:/http:/g' /etc/yum.repos.d/epel.repo

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
  echo "module.exports = config;" >> $WEBUI_CONF_FILE
  sed -i "s/config.featurePkg.webController.enable = .*/config.featurePkg.webController.enable = false;/g" $WEBUI_CONF_FILE
  sed -i "s/smConfig.sm.server_ip = .*/smConfig.sm.server_ip = '$HOSTIP';/g" $SM_CONF_FILE
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
fi
