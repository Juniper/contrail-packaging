#!/bin/bash
set -e
set -x

#### Mirror Creation - Already done - Added only for info
# aptly mirror create -architectures="amd64" xenial-main http://nova.clouds.archive.ubuntu.com/ubuntu/ xenial main
# aptly mirror create -architectures="amd64" xenial-universe http://nova.clouds.archive.ubuntu.com/ubuntu/ xenial universe
# aptly mirror create -architectures="amd64" xenial-updates-main http://nova.clouds.archive.ubuntu.com/ubuntu/ xenial-updates main
# aptly mirror create -architectures="amd64" xenial-updates-universe http://nova.clouds.archive.ubuntu.com/ubuntu/ xenial-updates universe
# aptly mirror create -architectures="amd64" xenial-security-main http://nova.clouds.archive.ubuntu.com/ubuntu/ xenial-security main
# aptly mirror create -architectures="amd64" xenial-security-universe http://nova.clouds.archive.ubuntu.com/ubuntu/ xenial-security universe
# aptly mirror create -architectures="amd64" xenial-updates-newton http://ubuntu-cloud.archive.canonical.com/ubuntu/ xenial-updates/newton main
# aptly mirror update xenial-main
# aptly mirror update xenial-universe
# aptly mirror update xenial-updates-main
# aptly mirror update xenial-updates-universe
# aptly mirror update xenial-security-main
# aptly mirror update xenial-security-universe
# aptly mirror update xenial-updates-newton
##########################################################

datetime_string=$(date +%Y_%m_%d__%H_%M_%S)
mkdir -p /tmp/ubuntu-mirrors/logs/
log_file=/tmp/ubuntu-mirrors/logs/ubuntu_mirror_update_$datetime_string.log
exec &> >(tee -a "$log_file")
SNAPSHOT_TAG=$(date "+%m%d%Y")
CODENAME=xenial

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
        echo "Refer Log file $log_file for complete errrors"
        exit 2
    fi
}

echo "Log file - $log_file"
sleep 5

# Update all available mirrors excluding precise/node repos 
# as they're no more supported
mirror_list="${CODENAME} ${CODENAME}-updates ${CODENAME}-security ${CODENAME}-updates-newton"
for mirror in $mirror_list; do
    # update mirror
    aptly mirror update $mirror
    echo "Mirror ( $mirror ) is updated"

    # Create snapshot
    aptly snapshot create $mirror-$SNAPSHOT_TAG from mirror $mirror
    echo "Snapshot ( $mirror-$SNAPSHOT_TAG ) from Mirror ( $mirror ) is created"
done


# Publish multi-components
echo Publish ${CODENAME} repos as multi-components

aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=${CODENAME} ${CODENAME}-main-$SNAPSHOT_TAG ${CODENAME}-universe-$SNAPSHOT_TAG ${CODENAME}/$SNAPSHOT_TAG
aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=${CODENAME}-updates ${CODENAME}-updates-main-$SNAPSHOT_TAG ${CODENAME}-updates-universe-$SNAPSHOT_TAG ${CODENAME}-updates/$SNAPSHOT_TAG
aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=${CODENAME}-security ${CODENAME}-security-main-$SNAPSHOT_TAG ${CODENAME}-security-universe-$SNAPSHOT_TAG  ${CODENAME}-security/$SNAPSHOT_TAG

# Publish openstack repos
aptly publish snapshot -passphrase=OpenContrail ${CODENAME}-updates-newton-main-$SNAPSHOT_TAG ${CODENAME}-updates-newton/$SNAPSHOT_TAG


echo Publish local repos to AWS

# Publish repos to AWS

retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=${CODENAME} ${CODENAME}-main-$SNAPSHOT_TAG ${CODENAME}-universe-$SNAPSHOT_TAG s3:aws-contrail-mirrors:${CODENAME}/$SNAPSHOT_TAG
retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=${CODENAME}-updates ${CODENAME}-updates-main-$SNAPSHOT_TAG ${CODENAME}-updates-universe-$SNAPSHOT_TAG s3:aws-contrail-mirrors:${CODENAME}-updates/$SNAPSHOT_TAG
retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=${CODENAME}-security ${CODENAME}-security-main-$SNAPSHOT_TAG ${CODENAME}-security-universe-$SNAPSHOT_TAG  s3:aws-contrail-mirrors:${CODENAME}-security/$SNAPSHOT_TAG

# Publish openstack repos to AWS
retry aptly publish snapshot -passphrase=OpenContrail ${CODENAME}-updates-liberty-newton-$SNAPSHOT_TAG s3:aws-contrail-mirrors:${CODENAME}-updates-newton/$SNAPSHOT_TAG
