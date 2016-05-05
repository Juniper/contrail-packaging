#!/bin/bash
set -e
set -x

datetime_string=$(date +%Y_%m_%d__%H_%M_%S)
mkdir -p /tmp/ubuntu-mirrors/logs/
log_file=/tmp/ubuntu-mirrors/logs/ubuntu_security_mirror_update_$datetime_string.log
exec &> >(tee -a "$log_file")
SNAPSHOT_TAG=$(date "+%m%d%Y")

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
        echo "Refer log file $log_file for complete errors"
        exit 2
    fi
}

echo "Log file - $log_file"
sleep 5

# Publish trusty multi-components
mirror=trusty-security
aptly mirror update trusty-security-main
aptly mirror update trusty-security-universe
aptly snapshot create trusty-security-main-$SNAPSHOT_TAG from mirror trusty-security-main
aptly snapshot create trusty-security-universe-$SNAPSHOT_TAG from mirror trusty-security-universe
aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=trusty-security trusty-security-main-$SNAPSHOT_TAG trusty-security-universe-$SNAPSHOT_TAG  trusty-security/$SNAPSHOT_TAG
retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=trusty-security trusty-security-main-$SNAPSHOT_TAG trusty-security-universe-$SNAPSHOT_TAG  s3:aws-contrail-mirrors:trusty-security/$SNAPSHOT_TAG

# Publish precise multi-components
#mirror=precise-security
#aptly mirror update precise-security-main
#aptly mirror update precise-security-universe
#aptly snapshot create precise-security-main-$SNAPSHOT_TAG from mirror precise-security-main
#aptly snapshot create precise-security-universe-$SNAPSHOT_TAG from mirror precise-security-universe
#aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=precise-security precise-security-main-$SNAPSHOT_TAG precise-security-universe-$SNAPSHOT_TAG  precise-security/$SNAPSHOT_TAG
#retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=precise-security precise-security-main-$SNAPSHOT_TAG precise-security-universe-$SNAPSHOT_TAG  s3:aws-contrail-mirrors:precise-security/$SNAPSHOT_TAG
