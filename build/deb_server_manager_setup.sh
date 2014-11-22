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
LOCALHOSTIP=`ifconfig | sed -n -e 's/:127\.0\.0\.1 //g' -e 's/ *inet addr:\([0-9.]\+\).*/\1/gp' | awk 'NR==1'`

function usage()
{
    echo "Usage"
    echo ""
    echo "$0"
    echo "\t-h --help"
    echo "\t--sm=$SM"
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

if [ "$SMMON" != "" ]; then
  echo "SMMON is $SMMON"
  gdebi $SMMON
fi
