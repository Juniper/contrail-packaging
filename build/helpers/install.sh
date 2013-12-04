#!/bin/bash

usage() {
    echo
    echo $"Usage: $0 [all|database|cfgm|collector|webui|control|vrouter]" 1>&2
    exit 2
}

help() {
    echo
    echo $"Usage: $0 [all|database|cfgm|collector|webui|control|vrouter]" 1>&2
    echo
    echo $"Eg: $0 all       ; #To install all the contrail packages in one server." 1>&2
    echo $"Eg: $0 openstack  ; #To install contrail openstack packages in this server." 1>&2
    echo $"Eg: $0 database  ; #To install contrail database packages in this server." 1>&2
    echo $"Eg: $0 cfgm      ; #To install contrail cfgm packages in this server." 1>&2
    echo $"Eg: $0 collector ; #To install contrail collector packages in this server." 1>&2
    echo $"Eg: $0 webui     ; #To install contrail webui packages in this server." 1>&2
    echo $"Eg: $0 control   ; #To install contrail control packages in this server." 1>&2
    echo $"Eg: $0 vrouter   ; #To install contrail vrouter packages in this server." 1>&2
    exit 0
}

[ $# -lt 1 ] && usage

package=$1
if [ $package = "-h" ] || [ $package = "-help" ] || [ $package = "--h" ] || [ $package = "--help" ]; then
    help
fi

case "$package" in
  "openstack" )
      echo
      echo "Installing contrail openstack package"
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack
  ;;
  "database" )
      echo
      echo "Installing contrail database package"
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-database
  ;;
  "cfgm" )
      echo
      echo "Installing contrail cfgm package"
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-cfgm
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-storage
  ;;
  "collector" )
      echo
      echo "Installing contrail collector package"
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-analytics
  ;;
  "control" )
      echo
      echo "Installing contrail control packages"
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-control
  ;;
  "webui" )
      echo
      echo "Installing contrail webui package"
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-webui
  ;;
  "vrouter" )
      echo
      echo "Installing contrail vrouter packages"
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-vrouter
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-storage
  ;;
  "all" )
      echo
      echo "Installing all contrail packages"
      yum -y --disablerepo=* --enablerepo=contrail_install_repo install contrail-openstack-database contrail-openstack-cfgm contrail-openstack-analytics contrail-openstack-control contrail-openstack-webui contrail-openstack-vrouter contrail-openstack-storage
  ;;
  * )
      echo
      echo "Unknown package: Exiting installer."
  ;;

esac
