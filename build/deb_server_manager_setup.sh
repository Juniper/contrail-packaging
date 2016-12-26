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
SMCLIFFCLIENT=""
HOSTIP=""
WEBUI=""
NOWEBUI=""
WEBCORE=""
CERT_NAME=""
SMLITE=""
NOEXTERNALREPOS=""
HOST_IP_LIST=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp'`
HOSTIP=`echo $HOST_IP_LIST | cut -d' ' -f1`
rel=`lsb_release -r`
rel=( $rel )

function create_pip_repo()
{
  echo "Installing pip2pi ..."
  pip install pip2pi
  echo "Create pip repo for required thirdparty packages ..."

  #mkdir -p /var/www/html/thirdparty_packages/pip_repo
  #mv /var/www/html/thirdparty_packages/*.tar.gz /var/www/html/thirdparty_packages/pip_repo

  sed -i "s/HOSTIP/$HOSTIP/" /opt/contrail/server_manager/ansible/playbooks/files/pip.conf
  dir2pi /var/www/html/thirdparty_packages/pip_repo
}

function ansible_and_docker_configs()
{
  echo "Configuring Ansible"
  sed -i "/callback_plugin/c\callback_plugins = \/opt\/contrail\/server_manager\/ansible\/plugins" /etc/ansible/ansible.cfg
  ansible-galaxy install -r /opt/contrail/server_manager/ansible/playbooks/requirements.yml
  echo "Starting docker registry"

  NUM_CONT=`docker ps -qa | wc -l`
  if [ $NUM_CONT != "0" ]; then
      docker rm -f `docker ps -qa`
  fi

  echo "DOCKER_OPTS=\"--insecure-registry $HOSTIP:5000\"" >> /etc/default/docker
  service docker restart >> $log_file 2>&1
  docker run -d -p 5000:5000 --restart=always --name registry registry:2

  #echo "Cleaning up docker images"
  #docker rmi -f `docker images -a | grep -v registry | grep -v REPOSITORY | awk '{print $3}'`
}


function usage()
{
    echo "Usage:"
    echo ""
    echo "-h --help"
    echo "--smlite"
    echo "--nowebui"
    echo "--sm"
    echo "--sm-client"
    echo "--sm-cliff-client"
    echo "--webui"
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

function setup_apt_conf()
{
  echo "$space$arrow Allow Install of Unauthenticated APT packages"
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

  set +e
  apt-get update >> $log_file 2>&1
  set -e
}


function setup_smgr_repos()
{

  echo "$space$arrow Installing dependent packages for Setting up Smgr repos"
  #scan pkgs in local repo and create Packages.gz
  apt-get --no-install-recommends -y install dpkg-dev >> $log_file 2>&1

  pushd /opt/contrail/contrail_server_manager >> $log_file 2>&1
  dpkg-scanpackages . | gzip -9c > Packages.gz | >> $log_file 2>&1
  popd >> $log_file 2>&1

  echo "deb file:/opt/contrail/contrail_server_manager ./" > /tmp/local_repo
  cat /tmp/local_repo /etc/apt/sources.list.d/smgr_sources.list > /tmp/new_smgr_sources.list
  mv /tmp/new_smgr_sources.list /etc/apt/sources.list.d/smgr_sources.list

  set +e
  apt-get update >> $log_file 2>&1
  set -e

}

function setup_internet_repos()
{
  echo "$space$arrow Setting up Internet Repos"
  # Push this to makefile - Copy only the file we need into installer.
  if [ ${rel[1]} == "14.04"  ]; then
    cp /opt/contrail/contrail_server_manager/ubuntu_14_04_1_sources.list /etc/apt/sources.list.d/smgr_sources.list
  elif [ ${rel[1]} == "12.04"  ]; then
    cp /opt/contrail/contrail_server_manager/ubuntu_12_04_3_sources.list /etc/apt/sources.list.d/smgr_sources.list
  else
    echo "$space$arrow This version of Ubuntu ${rel[1]} is not supported"
    exit
  fi

  set +e
  apt-get update >> $log_file 2>&1
  set -e

  # Dependencies to add apt-repos
  apt-get --no-install-recommends -y install python-software-properties debmirror >> $log_file 2>&1
  apt-get --no-install-recommends -y install software-properties-common >> $log_file 2>&1

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

  set +e
  apt-get update >> $log_file 2>&1
  set -e

}

function cleanup_passenger()
{
  echo "$space$arrow Cleaning up passenger for Server Manager Ugrade"
  if [ -f /etc/apache2/mods-enabled/passenger.conf ]; then
    a2dismod passenger >> $log_file 2>&1
  fi
  service apache2 restart >> $log_file 2>&1
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
	    SMCLIFFCLIENT="contrail-server-manager-cliff-client"
            ;;
	--smlite)
	    SMLITE="smlite"
	    ;;
	--nowebui)
	    NOWEBUI="nowebui"
	    ;;
        --sm)
	    SM="contrail-server-manager"
            ;;
        --webui)
	    WEBUI="contrail-web-server-manager"
	    WEBCORE="contrail-web-core"
            ;;
        --sm-client)
	    SMCLIENT="contrail-server-manager-client"
            ;;
        --sm-cliff-client)
	    SMCLIFFCLIENT="contrail-server-manager-cliff-client"
            ;;
        --hostip)
            HOSTIP=$VALUE
            rm -rf /opt/contrail/contrail_server_manager/IP.txt
            echo $HOSTIP >> /opt/contrail/contrail_server_manager/IP.txt
            ;;
        --cert-name)
            CERT_NAME=$VALUE
            ;;
        --no-external-repos)
            NOEXTERNALREPOS="TRUE"
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
setup_apt_conf
if [ "$NOEXTERNALREPOS" == "" ]; then
  setup_internet_repos
else
  touch /etc/apt/sources.list.d/smgr_sources.list
fi
setup_smgr_repos

RESTART_SERVER_MANAGER=""
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
  # Check if this is an upgrade
  if [ "$SMLITE" != "" ]; then
      installed_version=`dpkg -l | grep "contrail-server-manager-lite " | awk '{print $3}'`
  else
      installed_version=`dpkg -l | grep "contrail-server-manager " | awk '{print $3}'`
  fi
  check_upgrade=1
  if [ "$installed_version" != ""  ]; then
      version_to_install=`ls /opt/contrail/contrail_server_manager/contrail-server-manager_* | cut -d'_' -f 4`
      set +e
      comparison=`dpkg --compare-versions $version_to_install gt $installed_version`
      check_upgrade=`echo $?`
      set -e
      if [ $check_upgrade == 0 ]; then
          echo "$space$arrow Upgrading Server Manager to version $version_to_install"
      else
          echo "$space$arrow Cannot upgrade Server Manager to version $version_to_install"
          exit
      fi
  fi

  if [ $check_upgrade == 0 ]; then
    #  Cleanup old Passenger Manual Install so that it doesn't collide with new package
    passenger_upgrade_version="2.22"
    contrail_server_manager_version=`dpkg -l | grep "contrail-server-manager " | awk '{print $3}' | cut -d'-' -f 1`
    awk -v n1=$passenger_upgrade_version -v n2=$contrail_server_manager_version 'BEGIN{ if (n1>n2) cleanup_passenger}'
  fi

  #TODO: To be Removed after local repo additions
  if [ ${rel[1]} == "14.04"  ]; then
    apt-get --no-install-recommends -y install libpython2.7=2.7.6-8ubuntu0.2 >> $log_file 2>&1
  fi
  apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install puppet-common="3.7.3-1puppetlabs1" puppetmaster-common="3.7.3-1puppetlabs1" >> $log_file 2>&1
  cp /opt/contrail/contrail_server_manager/puppet.conf /etc/puppet/
  apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install nodejs=0.10.35-1contrail1 >> $log_file 2>&1

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

  if [ $check_upgrade == 0 ]; then
    # Upgrade
    echo "$space$arrow Upgrading Server Manager"
    RESTART_SERVER_MANAGER="1"
    if [ "$SMLITE" != "" ]; then
       echo "$space$arrow$install_str Server Manager Lite"
       dpkg -P --force-all contrail-server-manager-monitoring >> $log_file 2>&1
       apt-get -y install contrail-server-manager-lite >> $log_file 2>&1
       apt-get -y install -f >> $log_file 2>&1
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
       dpkg -P --force-all contrail-server-manager-monitoring >> $log_file 2>&1
       apt-get -y install contrail-server-manager >> $log_file 2>&1
       apt-get -y install -f >> $log_file 2>&1
       # Stopping webui service that uses old name
       if [ -f /etc/init.d/supervisor-webui ]; then
         old_webui_status=`service supervisor-webui status | awk '{print $2}' | cut -d'/' -f 1`
         if [ $old_webui_status != "stop"  ]; then
            service supervisor-webui stop >> $log_file 2>&1 # TODO : Remove for 3.0 release
         fi
       fi
    fi
  else
    if [ "$SMLITE" != "" ]; then
       echo "$space$arrow$install_str Server Manager Lite"
       apt-get -y install contrail-server-manager-lite >> $log_file 2>&1
       RESTART_SERVER_MANAGER="1"
    else
      echo "$space$arrow$install_str Server Manager"
      apt-get -y install cobbler="2.6.3-1" >> $log_file 2>&1 # TODO : Remove after local repo pinning
      apt-get -y install contrail-server-manager >> $log_file 2>&1
      cp /etc/contrail_smgr/cobbler/bootup_dhcp.template.u /etc/cobbler/dhcp.template
    fi
    apt-get -y install -f >> $log_file 2>&1
  fi

  ansible_and_docker_configs
  create_pip_repo
  echo "$arrow Completed Installing Server Manager"
fi

if [ "$SMCLIENT" != "" ]; then
  echo "$arrow Server Manager Client"
  echo "$space$arrow$install_str Server Manager Client"
  apt-get -y install contrail-server-manager-client >> $log_file 2>&1
  apt-get -y install -f >> $log_file 2>&1
  echo "$arrow Completed Installing Server Manager Client"
fi

if [ "$SMCLIFFCLIENT" != "" ]; then
  echo "$arrow Server Manager Cliff Client"
  echo "$space$arrow$install_str Server Manager Cliff Client"
  apt-get -y install contrail-server-manager-cliff-client >> $log_file 2>&1
  apt-get -y install -f >> $log_file 2>&1
  echo "$arrow Completed Installing Server Manager Cliff Client"
fi

if [ "$WEBUI" != "" ] && [ "$NOWEBUI" == "" ]; then
  echo "$arrow Web Server Manager"
  # install webui
  echo "$space$arrow$install_str Contrail Web Core"
  apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install contrail-web-core >> $log_file 2>&1
  echo "$space$arrow$install_str Contrail Web Server Manager"
  apt-get -y --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install contrail-web-server-manager >> $log_file 2>&1
  apt-get -y install -f >> $log_file 2>&1
  echo "$arrow Completed Installing Web Server Manager"
fi

if [ "x$RESTART_SERVER_MANAGER" == "x1" ]; then
  if [ "$SMLITE" != "" ]; then
    echo "$space$space$arrow Starting Server Manager Lite Service"
  else
    echo "$space$space$arrow Starting Server Manager Service"
  fi
  service contrail-server-manager restart >> $log_file 2>&1
  sleep 5
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
