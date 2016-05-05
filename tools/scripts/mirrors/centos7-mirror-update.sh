#!/bin/bash
set -x
set -e

datetime_string=$(date +%Y_%m_%d__%H_%M_%S)
mkdir -p /tmp/centos-mirrors/logs/
log_file=/tmp/centos-mirrors/logs/centos7_mirror_update_$datetime_string.log
exec &> >(tee -a "$log_file")

snapshot=$(date +%m%d%Y)

retry () {
    cmd=$@
    retries=12
    pass=0
    for count in $(seq 1 $retries); do
        eval $cmd
        if [ $? == 0 ]; then
            pass=1
            break;
        else
            echo "Attempt $count failed; Retrying..."
        fi
    done
    if [ $pass == 1 ]; then
        echo "Command ( $cmd ) passed at $count attempt"
    else
        echo "Command ( $cmd ) failed at $count attempt; Exiting..."
        echo "Refer log file - $log_file for complete errors"
        exit 2
    fi
}

echo "Log file - $log_file"
sleep 5

# FOR CENTOS 7 ###############################
# Server Repos
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/centos/7/extras/ --baseurl=http://mirror.centos.org/centos/7/extras/x86_64/
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/centos/7/updates/ --baseurl=http://mirror.centos.org/centos/7/updates/x86_64/
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/centos/7/os/ --baseurl=http://mirror.centos.org/centos/7/os/x86_64/

# Epel Repos
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/epel/7/ --baseurl=http://download.fedoraproject.org/pub/epel/7/x86_64

# Openstack Repos
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/openstack/openstack-liberty/el7/ --baseurl=http://mirror.centos.org/centos/7/cloud/x86_64/openstack-liberty/
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/openstack/openstack-kilo/el7/ --baseurl=https://repos.fedorapeople.org/repos/openstack/openstack-kilo/el7/

#### RETIRED ###
#pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/openstack/openstack-icehouse/epel-7/ --baseurl=https://repos.fedorapeople.org/repos/openstack/openstack-icehouse/epel-7/
#pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/openstack/openstack-juno/epel-7/ --baseurl=https://repos.fedorapeople.org/repos/openstack/openstack-juno/epel-7/
