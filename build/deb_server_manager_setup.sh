#!/bin/bash
# copy files over
cd /opt/contrail/contrail_server_manager;
tar -xvf contrail_server_manager_packages.tgz

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
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
apt-get update

# install base packages and fabric utils
#DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes --allow-unauthenticated install contrail-setup
#pip install --upgrade --no-deps --index-url='' /opt/contrail/python_packages/ecdsa-0.10.tar.gz

apt-get install gdebi-core

cd /opt/contrail/contrail_server_manager

SM=""
SMCLIENT=""
HOSTIP=""
SMMON=""
WEBUI=""
LOCALHOSTIP=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp' | awk 'NR==1'`

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
              elif [[ "$line" != *client*  &&  "$line" != *monitoring*  &&  "$line" != *web* ]];
              then
                SM=$line
              fi
            done < temp.txt
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
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

rm temp.txt

if [ "$SM" != "" ]; then
  echo "SM is $SM"
  wget http://apt.puppetlabs.com/pool/stable/main/p/puppet/puppet-common_2.7.25-1puppetlabs1_all.deb
  gdebi puppet-common_2.7.25-1puppetlabs1_all.deb

  wget http://apt.puppetlabs.com/pool/stable/main/p/puppet/puppetmaster-common_2.7.25-1puppetlabs1_all.deb
  gdebi puppetmaster-common_2.7.25-1puppetlabs1_all.deb

  wget http://apt.puppetlabs.com/pool/stable/main/p/puppet/puppetmaster_2.7.25-1puppetlabs1_all.deb
  gdebi puppetmaster_2.7.25-1puppetlabs1_all.deb

  # Install server manager
  gdebi $SM
  if [ "$HOSTIP" == "" ]; then
     HOSTIP=$LOCALHOSTIP
  fi
  sed -i "s/listen_ip_addr = .*/listen_ip_addr = $HOSTIP/g" /opt/contrail/server_manager/sm-config.ini
  echo "Configure /etc/cobbler/ dhcp.template, named.template, settings to bring up server manager"
fi

if [ "$SMCLIENT" != "" ]; then
  echo "SMCLIENT is $SMCLIENT"
  gdebi $SMCLIENT
  if [ "$HOSTIP" == "" ]; then
     HOSTIP=$LOCALHOSTIP
  fi
  sed -i "s/listen_ip_addr = .*/listen_ip_addr = $HOSTIP/g" /opt/contrail/server_manager/client/sm-client-config.ini
fi

if [ "$WEBUI" != "" ]; then
  echo "WEBUI is $WEBUI"
  # install webui
  gdebi $WEBUI
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

if [ "$SMMON" != "" ]; then
  echo "SMMON is $SMMON"
  gdebi $SMMON
fi
