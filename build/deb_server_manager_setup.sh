#!/bin/bash
set -e

start_time=$(date +"%s")
datetime_string=`date +%Y_%m_%d__%H_%M_%S`
mkdir -p /var/log/contrail/install_logs/
log_file=/var/log/contrail/install_logs/install_$datetime_string.log
exec &> >(tee -a "$log_file")

space="    "
arrow="---->"
install_str=" Installing package "

echo "$arrow This install is being logged at: $log_file"

ALL=""
SM=""
SMCLIENT=""
HOSTIP=""
SMMON=""
NOSMMON=""
WEBUI=""
NOWEBUI=""
WEBCORE=""
CERT_NAME=""
SMLITE=""
HOST_IP_LIST=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp'`
HOSTIP=`echo $HOST_IP_LIST | cut -d' ' -f1`
rel=`lsb_release -r`
rel=( $rel )


function usage()
{
    echo "Usage:"
    echo ""
    echo "-h --help"
    echo "--smlite"
    echo "--nowebui"
    echo "--nosm-mon"
    echo "--sm"
    echo "--sm-client"
    echo "--webui"
    echo "--sm-mon"
    echo "--hostip=<HOSTIP>"
    echo "--cert-name=<PUPPET CERTIFICATE NAME>"
    echo "--all"
    echo ""
}

function cleanup_smgr_repos()
{

  echo "$space$arrow Cleaning up existing sources.list and Server Manager sources file"
  local_repo="deb file:/opt/contrail/contrail_server_manager ./"
  sed -i "s|$local_repo||g" /etc/apt/sources.list
  if [ -f /etc/apt/sources.list.d/smgr_sources.list ]; then
    rm /etc/apt/sources.list.d/smgr_sources.list
  fi

}

function setup_smgr_repos()
{
  # Push this to makefile - Copy only the file we need into installer.
  if [ ${rel[1]} == "14.04"  ]; then
    cp /opt/contrail/contrail_server_manager/ubuntu_14_04_1_sources.list /etc/apt/sources.list.d/smgr_sources.list
  elif [ ${rel[1]} == "12.04"  ]; then
    cp /opt/contrail/contrail_server_manager/ubuntu_12_04_3_sources.list /etc/apt/sources.list.d/smgr_sources.list
  else
    echo "$space$arrow This version of Ubuntu ${rel[1]} is not supported"
    exit
  fi

  echo "$space$arrow Setting up the repositories for Server Manager Install"
  apt-get update >> $log_file 2>&1

  echo "$space$arrow Installing dependent packages for Setting up repos"
  #scan pkgs in local repo and create Packages.gz
  apt-get --no-install-recommends -y install dpkg-dev >> $log_file 2>&1
  # Dependencies to add apt-repos
  apt-get --no-install-recommends -y install python-software-properties debmirror >> $log_file 2>&1
  apt-get --no-install-recommends -y install software-properties-common >> $log_file 2>&1

  pushd /opt/contrail/contrail_server_manager >> $log_file 2>&1
  dpkg-scanpackages . | gzip -9c > Packages.gz | >> $log_file 2>&1
  popd >> $log_file 2>&1
 
  echo "deb file:/opt/contrail/contrail_server_manager ./" > /tmp/local_repo
  cat /tmp/local_repo /etc/apt/sources.list.d/smgr_sources.list > /tmp/new_smgr_sources.list
  mv /tmp/new_smgr_sources.list /etc/apt/sources.list.d/smgr_sources.list

  # Allow unauthenticated pacakges to get installed.
  # Do not over-write apt.conf. Instead just append what is necessary
  # retaining other useful configurations such as http::proxy info.
  apt_auth="APT::Get::AllowUnauthenticated \"true\";"
  set +e
  grep --quiet "$apt_auth" /etc/apt/apt.conf
  exit_status=$?
  set -e
  if [ $exit_status != "0" ]; then
    echo "$apt_auth" >> /etc/apt/apt.conf
  fi

  puppet_list_file="/etc/apt/sources.list.d/puppet.list"
  passenger_list_file="/etc/apt/sources.list.d/passenger.list"
  dist='precise'
  if [ ${rel[1]} == "14.04"  ]; then
      dist='trusty'
  fi
  # Add puppet sources
  if [ ! -f "$puppet_list_file" ]; then
      echo "deb http://apt.puppetlabs.com $dist main" >> $puppet_list_file
      echo "deb-src http://apt.puppetlabs.com $dist main" >> $puppet_list_file
      echo "deb http://apt.puppetlabs.com $dist dependencies" >> $puppet_list_file
      echo "deb-src http://apt.puppetlabs.com $dist dependencies" >> $puppet_list_file
  fi

  # Add passenger's sources
  if [ ! -f "$passenger_list_file" ]; then
      echo "deb https://oss-binaries.phusionpassenger.com/apt/passenger $dist main" >> $passenger_list_file
  fi

  # Repo to add for redis - required for contrail-web-core
  add-apt-repository ppa:rwky/redis --yes >> $log_file 2>&1

  # Cobbler repo to be added if this is not an SMLITE install
  if [ "$SMLITE" == "" ]; then
    if [ ${rel[1]} == "14.04"  ]; then
      wget -qO - http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_14.04/Release.key | apt-key add - >> $log_file 2>&1
      add-apt-repository "deb http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_14.04/ ./" >> $log_file 2>&1
    elif [ ${rel[1]} == "12.04"  ]; then
      wget -qO - http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_12.04/Release.key | apt-key add - >> $log_file 2>&1
      add-apt-repository "deb http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_12.04/ ./" >> $log_file 2>&1
    fi
  fi
  apt-get update >> $log_file 2>&1

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
            exit 1
            ;;
        --all)
            ALL="all"
	    SM="contrail-server-manager"
	    WEBUI="contrail-web-server-manager"
	    WEBCORE="contrail-web-core"
	    SMCLIENT="contrail-server-manager-client"
	    SMMON="contrail-server-manager-monitoring"
            ;;
	--smlite)
	    SMLITE="smlite"
	    ;;
	--nowebui)
	    NOWEBUI="nowebui"
	    ;;
	--nosm-mon)
	    NOSMMON="nosm-mon"
	    ;;
        --sm)
	    SM="contrail-server-manager"
            ;;
        --webui)
	    WEBUI="contrail-web-server-manager"
	    WEBCORE="contrail-web-core"
            ;;
        --sm-mon)
	    SMMON="contrail-server-manager-monitoring"
            ;;
        --sm-client)
	    SMCLIENT="contrail-server-manager-client"
            ;;
        --hostip)
            HOSTIP=$VALUE
            rm -rf /opt/contrail/contrail-server-manager/IP.txt
            echo $HOSTIP >> /opt/contrail/contrail-server-manager/IP.txt 
            ;;
        --cert-name)
            CERT_NAME=$VALUE
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

cleanup_smgr_repos
setup_smgr_repos

if [ "$SM" != "" ]; then
  echo "$arrow Server Manager"

  # Removing the existing puppet agent certs, so that puppet master certs can take its place
  # Check if below logic will work in pre-install of contrail-smgr
  puppetmaster_installed=`dpkg -l | grep "puppetmaster-passenger" || true`

  if [[ -d /var/lib/puppet/ssl && $puppetmaster_installed == "" ]]; then
      datetime_string=`date +%Y_%m_%d__%H_%M_%S`
      echo "$space$arrow Puppet agent certificates have been moved to /var/lib/puppet/ssl_$datetime_string"
      mv /var/lib/puppet/ssl /var/lib/puppet/ssl_$datetime_string
  fi
  #To be Removed after local repo additions
  if [ ${rel[1]} == "14.04"  ]; then
    apt-get --no-install-recommends -y install libpython2.7=2.7.6-8ubuntu0.2 >> $log_file 2>&1
  fi
  apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install puppet-common="3.7.3-1puppetlabs1" puppetmaster-common="3.7.3-1puppetlabs1" >> $log_file 2>&1
  apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install nodejs=0.8.15-1contrail1 >> $log_file 2>&1
  if [ "$CERT_NAME" != "" ]; then
    host=$CERT_NAME
    echo "$space$arrow Creating puppet certificate with name $host"
  else
    host=$(hostname -f)
    echo "$space$arrow Using default puppet certificate name $host"
  fi
  set +e
  puppet cert list --all 2>&1 | grep -v $(hostname -f) && puppet cert generate $host >> $log_file 2>&1
  set -e
  #To be Removed after local repo additions
  echo "$space$arrow$install_str Puppetmaster Passenger"
  apt-get --no-install-recommends -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install puppetmaster-passenger="3.7.3-1puppetlabs1" >> $log_file 2>&1
  service apache2 restart >> $log_file 2>&1

  if [ -e /etc/init.d/apparmor ]; then
    /etc/init.d/apparmor stop >> $log_file 2>&1
    update-rc.d -f apparmor remove >> $log_file 2>&1
  fi

  # Check if this is an upgrade
  if [ "$SMLITE" != "" ]; then
      check_upgrade=`dpkg --list | grep "contrail-server-manager-lite " || true`
  else
      check_upgrade=`dpkg --list | grep "contrail-server-manager " || true`
  fi

  if [ "$check_upgrade" != ""  ]; then
    # Upgrade
    echo "$space$arrow Upgrading Server Manager"
    if [ "$SMLITE" != "" ]; then
       echo "$space$arrow$install_str Server Manager Lite"
       apt-get -y install contrail-server-manager-lite >> $log_file 2>&1
       apt-get -y install -f >> $log_file 2>&1
       echo "$space$space$arrow Starting Server Manager Lite Service"
       service contrail-server-manager restart
       sleep 5
       service contrail-server-manager status
    else
       cv=`cobbler --version`
       cv=( $cv  )
       if [ "${cv[1]}" != "2.6.3" ]; then
          dpkg -P --force-all python-cobbler >> $log_file 2>&1
          dpkg -P --force-all cobbler-common >> $log_file 2>&1
          dpkg -P --force-all cobbler-web >> $log_file 2>&1
          dpkg -P --force-all cobbler >> $log_file 2>&1
          dpkg -P --force-all contrail-server-manager >> $log_file 2>&1
       fi
       echo "$space$arrow$install_str Server Manager"
       apt-get -y install cobbler="2.6.3-1" >> $log_file 2>&1 # TODO : Remove after local repo pinning
       apt-get -y install contrail-server-manager >> $log_file 2>&1
       apt-get -y install -f >> $log_file 2>&1
    fi
  else
    if [ "$SMLITE" != "" ]; then
       echo "$space$arrow$install_str Server Manager Lite"
       apt-get -y install contrail-server-manager-lite >> $log_file 2>&1
       echo "$space$space$arrow Starting Server Manager Lite Service"
       service contrail-server-manager restart
       sleep 5
       service contrail-server-manager status
    else
      echo "$space$arrow$install_str Server Manager"
      apt-get -y install cobbler="2.6.3-1" >> $log_file 2>&1 # TODO : Remove after local repo pinning
      apt-get -y install contrail-server-manager >> $log_file 2>&1
    fi
    apt-get -y install -f >> $log_file 2>&1
  fi

  echo "$arrow Completed Installing Server Manager"
fi

if [ "$SMCLIENT" != "" ]; then
  echo "$arrow Server Manager Client"
  echo "$space$arrow$install_str Server Manager Client"
  apt-get -y install contrail-server-manager-client >> $log_file 2>&1
  apt-get -y install -f >> $log_file 2>&1
  echo "$arrow Completed Installing Server Manager Client"
fi

if [ "$WEBUI" != "" ] && [ "$NOWEBUI" == "" ]; then
  echo "$arrow Web Server Manager"
  # install webui
  echo "$space$arrow$install_str Contrail Web Core"
  apt-get -y install contrail-web-core >> $log_file 2>&1
  echo "$space$arrow$install_str Contrail Web Server Manager"
  apt-get -y install contrail-web-server-manager >> $log_file 2>&1
  apt-get -y install -f >> $log_file 2>&1
  echo "$arrow Completed Installing Web Server Manager"
fi

if [ "$SMMON" != "" ] && [ "$NOSMMON" == "" ]; then
  echo "$arrow Server Manager Monitoring"
  echo "$space$arrow$install_str Server Manager Monitoring"
  apt-get -y install contrail-server-manager-monitoring >> $log_file 2>&1
  apt-get -y install -f >> $log_file 2>&1
  if [ "$check_upgrade" != ""  ]; then
      echo "Sample Configurations for Monitoring and Inventory are available at /opt/contrail/server_manager/sm-monitoring-config.ini and /opt/contrail/server_manager/sm-inventory-config.ini."
      echo "Sample Configurations for Sandesh is available at /opt/contrail/server_manager/sm-sandesh-config.ini."
      echo "Please add these to the main server manager configuration at /opt/contrail/server_manager/sm-config.ini to activate these features."
  else
      cat /opt/contrail/server_manager/sm-sandesh-config.ini >> /opt/contrail/server_manager/sm-config.ini
      cat /opt/contrail/server_manager/sm-monitoring-config.ini >> /opt/contrail/server_manager/sm-config.ini
      cat /opt/contrail/server_manager/sm-inventory-config.ini >> /opt/contrail/server_manager/sm-config.ini
  fi
  echo "$arrow Completed Installing Server Manager Monitoring"
fi

# Should we remove Puppet/Passenger sources.list.d files also?
echo "$arrow Reverting Repos to old state"
rm -f /etc/apt/sources.list.d/puppet.list >> $log_file 2>&1 
rm -f /etc/apt/sources.list.d/passenger.list >> $log_file 2>&1
rm -f /etc/apt/sources.list.d/smgr_sources.list >> $log_file 2>&1
apt-get update >> $log_file 2>&1

sm_installed=`dpkg -l | grep "contrail-server-manager " || true`
if [ "$sm_installed" != "" ]; then
  echo "IMPORTANT: CONFIGURE /ETC/COBBLER/DHCP.TEMPLATE, NAMED.TEMPLATE, SETTINGS TO BRING UP SERVER MANAGER."
  echo "If your install has failed, please make sure the /etc/apt/sources.list file reflects the default sources.list for your version of Ubuntu."
  echo "Sample sources.list files are available at /opt/contrail/contrail_server_manager/."
  echo "Install log is at /var/log/contrail/install_logs/"
fi

end_time=$(date +"%s")
diff=$(($end_time-$start_time))
echo "SM installation took $(($diff / 60)) minutes and $(($diff % 60)) seconds."
