#!/bin/bash
set -x
set -e

datetime_string=$(date +%Y_%m_%d__%H_%M_%S)
mkdir -p /tmp/centos-mirrors/logs/
log_file=/tmp/centos-mirrors/logs/centos6_mirror_update_$datetime_string.log
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

# FOR CENTOS 6 #############################
# Server Repos
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/centos/6/extras/ --baseurl=http://mirror.centos.org/centos/6/extras/x86_64/
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/centos/6/updates/ --baseurl=http://mirror.centos.org/centos/6/updates/x86_64/
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/centos/6/os/ --baseurl=http://mirror.centos.org/centos/6/os/x86_64/

# Openstack Repos
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/openstack/openstack-icehouse/epel-6/ --baseurl=https://repos.fedorapeople.org/repos/openstack/openstack-icehouse/epel-6/

# Epel Repos
retry pakrat --repoversion=$snapshot --name=x86_64 --outdir=/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/epel/6/ --baseurl=http://download.fedoraproject.org/pub/epel/6/x86_64
