#!/bin/bash
set -e

start_time=$(date +"%s")
datetime_string=`date +%Y_%m_%d__%H_%M_%S`
mkdir -p /var/log/contrail/install_logs/
log_file=/var/log/contrail/install_logs/install_$datetime_string.log
exec &> >(tee -a "$log_file")
# copy files over

space="    "

ALL=""
SM=""
SMCLIENT=""
HOSTIP=""
SMMON=""
NOSMMON=""
WEBUI=""
NOWEBUI=""
WEBCORE=""
# REVISIT : Do we need this option:
#DOMAIN=""
#HOSTNAME=""
SMLITE=""
HOST_IP_LIST=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp'`
HOSTIP=`echo $HOST_IP_LIST | cut -d' ' -f1`
echo $HOSTIP
rel=`lsb_release -r`
rel=( $rel )


function usage()
{
    echo "Usage"
    echo ""
    echo "$0"
    echo "\t-h --help"
    echo "\t--smlite"
    echo "\t--nowebui"
    echo "\t--nosm-mon"
    echo "\t--sm"
    echo "\t--sm-client"
    echo "\t--webui"
    echo "\t--sm-mon"
    echo "\t--hostip=$HOSTIP"
    #echo "\t--domain=$DOMAIN"
    #echo "\t--hostname=$HOSTNAME"
    echo "\t--all"
    echo ""
}

function setup_smgr_repos()
{

  # Push this to makefile - Copy only the file we need into installer.
  if [ ${rel[1]} == "14.04"  ]; then
    cp /opt/contrail/contrail_server_manager/ubuntu_14_04_1_sources.list /etc/apt/sources.list.d/smgr_sources.list
  elif [ ${rel[1]} == "12.04"  ]; then
    cp /opt/contrail/contrail_server_manager/ubuntu_12_04_3_sources.list /etc/apt/sources.list.d/smgr_sources.list
  else
    echo "This version of Ubuntu ${rel[1]} is not supported"
    exit
  fi

  echo "Setting up the repositories for Server Manager Install"
  apt-get update &> /dev/null

  echo "Installing dependent packages for Setting up repos"
  #scan pkgs in local repo and create Packages.gz
  apt-get --no-install-recommends -y install dpkg-dev &> /dev/null
  # Dependencies to add apt-repos
  apt-get --no-install-recommends -y install python-software-properties debmirror &> /dev/null
  apt-get --no-install-recommends -y install software-properties-common &> /dev/null

  pushd /opt/contrail/contrail_server_manager
  dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz &> /dev/null
  popd
 
  echo "deb file:/opt/contrail/contrail_server_manager ./" > /tmp/local_repo
  cat /tmp/local_repo /etc/apt/sources.list.d/smgr_sources.list > /tmp/new_smgr_sources.list
  mv /tmp/new_smgr_sources.list /etc/apt/sources.list.d/smgr_sources.list

  # Allow unauthenticated pacakges to get installed.
  # Do not over-write apt.conf. Instead just append what is necessary
  # retaining other useful configurations such as http::proxy info.
  apt_auth="APT::Get::AllowUnauthenticated \"true\";"
  set +e
  grep --quiet "$apt_auth" /etc/apt/apt.conf
  set -e
  exit_status=$?
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
  add-apt-repository ppa:rwky/redis --yes &> /dev/null

  # Cobbler repo to be added if this is not an SMLITE install
  if [ "$SMLITE" == "" ]; then
    if [ ${rel[1]} == "14.04"  ]; then
      wget -qO - http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_14.04/Release.key | apt-key add -
      add-apt-repository "deb http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_14.04/ ./"
    elif [ ${rel[1]} == "12.04"  ]; then
      wget -qO - http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_12.04/Release.key | apt-key add -
      add-apt-repository "deb http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_12.04/ ./"
    fi
  fi
  apt-get update &> /dev/null

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
            rm -rf ./IP.txt
            echo $HOSTIP >> ./IP.txt
            ;;
        #--domain)
        #    DOMAIN=$VALUE
        #    ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

setup_smgr_repos

if [ "$SM" != "" ]; then
  echo "### Begin: Installing Server Manager"

  # Removing the existing puppet agent certs, so that puppet master certs can take its place
  # Check if below logic will work in pre-install of contrail-smgr
  puppetmaster_installed=`dpkg -l | grep "puppetmaster-passenger" || true`

  if [[ -d /var/lib/puppet/ssl && $puppetmaster_installed == "" ]]; then
      rm -rf /var/lib/puppet/ssl
  fi
  #To be Removed after local repo additions
  echo "Installing Server Manager Dependent Packages"
  if [ ${rel[1]} == "14.04"  ]; then
  apt-get --no-install-recommends -y install libpython2.7=2.7.6-8ubuntu0.2 &> /dev/null
  fi
  apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install puppet-common="3.7.3-1puppetlabs1" puppetmaster-common="3.7.3-1puppetlabs1" &> /dev/null
  apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install nodejs=0.8.15-1contrail1 &> /dev/null
  host=$(hostname -f)
  puppet cert list --all 2>&1 | grep -v $(hostname -f) && puppet cert generate $host
  #To be Removed after local repo additions
  apt-get --no-install-recommends -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install puppetmaster-passenger="3.7.3-1puppetlabs1" &> /dev/null
  service apache2 restart

  if [ -e /etc/init.d/apparmor ]; then
    /etc/init.d/apparmor stop
    update-rc.d -f apparmor remove
  fi

  # Check if this is an upgrade
  if [ "$SMLITE" != "" ]; then
      check_upgrade=`dpkg --list | grep "contrail-server-manager-lite " || true`
  else
      check_upgrade=`dpkg --list | grep "contrail-server-manager " || true`
  fi

  if [ "$check_upgrade" != ""  ]; then
    # Upgrade
    echo "Upgrading Server Manager"
    if [ "$SMLITE" != "" ]; then
       # To be tested
       echo "Installing Server Manager Lite Package"
       apt-get -y install contrail-server-manager-lite
       apt-get -y install -f
    else
       cv=`cobbler --version`
       cv=( $cv  )
       if [ "${cv[1]}" != "2.6.3" ]; then
          dpkg -P --force-all python-cobbler
          dpkg -P --force-all cobbler-common
          dpkg -P --force-all cobbler-web
          dpkg -P --force-all cobbler
          dpkg -P --force-all contrail-server-manager
       fi
       # Install server manager package
       echo "Installing Server Manager Package"
       apt-get -y install cobbler="2.6.3-1" &> /dev/null
       apt-get -y install contrail-server-manager
       apt-get -y install -f
    fi
  else
  # Not tested
    if [ "$SMLITE" != "" ]; then
       # To be tested
  echo "Installing Server Manager Lite Package"
       apt-get -y install contrail-server-manager-lite
    else
      #To be Removed after local repo additions
  echo "Installing Server Manager Package"
      apt-get -y install cobbler="2.6.3-1" &> /dev/null
      apt-get -y install contrail-server-manager
    fi
    apt-get -y install -f
  fi

  echo "### End: Installing Server Manager"
fi

if [ "$SMCLIENT" != "" ]; then
  echo "### Begin: Installing Server Manager Client"
  apt-get -y install contrail-server-manager-client
  apt-get -y install -f
  echo "### End: Installing Server Manager Client"
fi

if [ "$WEBUI" != "" ] && [ "$NOWEBUI" == "" ]; then
  echo "### Begin: Installing Server Manager Web UI"
  # install webui
  apt-get -y install contrail-web-core
  apt-get -y install contrail-web-server-manager
  apt-get -y install -f
  echo "### End: Installing Server Manager Web UI"
fi

if [ "$SMMON" != "" ]; then
  echo "### Begin: Installing Server Manager Monitoring"
  if [ "$check_upgrade" != ""  ]; then
      apt-get -y install contrail-server-manager-monitoring
      apt-get -y install -f
      echo "Sample Configurations for Monitoring and Inventory are available at /opt/contrail/server_manager/sm-monitoring-config.ini and /opt/contrail/server_manager/sm-inventory-config.ini."
      echo "Sample Configurations for Sandesh is available at /opt/contrail/server_manager/sm-sandesh-config.ini."
      echo "Please add these to the main server manager configuration at /opt/contrail/server_manager/sm-config.ini to activate these features."
  else
      apt-get -y install contrail-server-manager-monitoring
      apt-get install -f
      cat /opt/contrail/server_manager/sm-sandesh-config.ini >> /opt/contrail/server_manager/sm-config.ini
      cat /opt/contrail/server_manager/sm-monitoring-config.ini >> /opt/contrail/server_manager/sm-config.ini
      cat /opt/contrail/server_manager/sm-inventory-config.ini >> /opt/contrail/server_manager/sm-config.ini
  fi
  echo "### End: Installing Server Manager Monitoring"
  echo "Install log is at /var/log/contrail/install_logs/"
fi

# Should we remove Puppet/Passenger sources.list.d files also?

rm -f /etc/apt/sources.list.d/puppet.list
rm -f /etc/apt/sources.list.d/passenger.list
rm -f /etc/apt/sources.list.d/smgr_sources.list
apt-get update &> /dev/null

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
