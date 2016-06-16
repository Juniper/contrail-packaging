#!/bin/bash
set -e
set -x

datetime_string=$(date +%Y_%m_%d__%H_%M_%S)
mkdir -p /tmp/ubuntu-mirrors/logs/
log_file=/tmp/ubuntu-mirrors/logs/ubuntu_mirror_update_$datetime_string.log
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
        echo "Refer Log file $log_file for complete errrors"
        exit 2
    fi
}

echo "Log file - $log_file"
sleep 5

# Update all available mirrors excluding precise/node repos 
# as they're no more supported
aptly mirror list -raw | grep -v precise | grep -v node | xargs -n 1 aptly mirror update
echo "All Mirrors are updated"

# Create snapshots
mirror_list=$(aptly mirror list --raw | grep -v precise | grep -v node)
for mirror in $mirror_list; do
    aptly snapshot create $mirror-$SNAPSHOT_TAG from mirror $mirror
done
echo "All Snapshots are created"


# Publish trusty multi-components
echo Publish trusty repos as multi-components

aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=trusty trusty-main-$SNAPSHOT_TAG trusty-universe-$SNAPSHOT_TAG trusty/$SNAPSHOT_TAG
aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=trusty-updates trusty-updates-main-$SNAPSHOT_TAG trusty-updates-universe-$SNAPSHOT_TAG trusty-updates/$SNAPSHOT_TAG
aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=trusty-security trusty-security-main-$SNAPSHOT_TAG trusty-security-universe-$SNAPSHOT_TAG  trusty-security/$SNAPSHOT_TAG

# Publish trusty openstack repos
aptly publish snapshot -passphrase=OpenContrail trusty-updates-juno-main-$SNAPSHOT_TAG trusty-updates-juno/$SNAPSHOT_TAG
aptly publish snapshot -passphrase=OpenContrail trusty-updates-kilo-main-$SNAPSHOT_TAG trusty-updates-kilo/$SNAPSHOT_TAG
aptly publish snapshot -passphrase=OpenContrail trusty-updates-liberty-main-$SNAPSHOT_TAG trusty-updates-liberty/$SNAPSHOT_TAG
aptly publish snapshot -passphrase=OpenContrail trusty-updates-mitaka-main-$SNAPSHOT_TAG trusty-updates-mitaka/$SNAPSHOT_TAG


echo Publish local repos to AWS

# Publish trusty repos to AWS

retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=trusty trusty-main-$SNAPSHOT_TAG trusty-universe-$SNAPSHOT_TAG s3:aws-contrail-mirrors:trusty/$SNAPSHOT_TAG
retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=trusty-updates trusty-updates-main-$SNAPSHOT_TAG trusty-updates-universe-$SNAPSHOT_TAG s3:aws-contrail-mirrors:trusty-updates/$SNAPSHOT_TAG
retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=trusty-security trusty-security-main-$SNAPSHOT_TAG trusty-security-universe-$SNAPSHOT_TAG  s3:aws-contrail-mirrors:trusty-security/$SNAPSHOT_TAG

# Publish trusty openstack repos to AWS
retry aptly publish snapshot -passphrase=OpenContrail trusty-updates-juno-main-$SNAPSHOT_TAG s3:aws-contrail-mirrors:trusty-updates-juno/$SNAPSHOT_TAG
retry aptly publish snapshot -passphrase=OpenContrail trusty-updates-kilo-main-$SNAPSHOT_TAG s3:aws-contrail-mirrors:trusty-updates-kilo/$SNAPSHOT_TAG
retry aptly publish snapshot -passphrase=OpenContrail trusty-updates-liberty-main-$SNAPSHOT_TAG s3:aws-contrail-mirrors:trusty-updates-liberty/$SNAPSHOT_TAG
retry aptly publish snapshot -passphrase=OpenContrail trusty-updates-liberty-mitaka-$SNAPSHOT_TAG s3:aws-contrail-mirrors:trusty-updates-mitaka/$SNAPSHOT_TAG

# Publish precise multi-components
#aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=precise precise-main-$SNAPSHOT_TAG precise-universe-$SNAPSHOT_TAG $SNAPSHOT_TAG
#aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=precise-updates precise-updates-main-$SNAPSHOT_TAG precise-updates-universe-$SNAPSHOT_TAG $SNAPSHOT_TAG
#aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=precise-security precise-security-main-$SNAPSHOT_TAG precise-security-universe-$SNAPSHOT_TAG  $SNAPSHOT_TAG

# Publish precise openstack repos
#aptly publish snapshot -passphrase=OpenContrail precise-updates-havana-main-$SNAPSHOT_TAG $SNAPSHOT_TAG
#aptly publish snapshot -passphrase=OpenContrail precise-updates-icehouse-main-$SNAPSHOT_TAG $SNAPSHOT_TAG

# Publish precise repos to AWS

#retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=precise precise-main-$SNAPSHOT_TAG precise-universe-$SNAPSHOT_TAG s3:aws-contrail-mirrors:precise/$SNAPSHOT_TAG
#retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=precise-updates precise-updates-main-$SNAPSHOT_TAG precise-updates-universe-$SNAPSHOT_TAG s3:aws-contrail-mirrors:precise-updates/$SNAPSHOT_TAG
#retry aptly publish snapshot -passphrase=OpenContrail -component=main,universe -distribution=precise-security precise-security-main-$SNAPSHOT_TAG precise-security-universe-$SNAPSHOT_TAG  s3:aws-contrail-mirrors:precise-security/$SNAPSHOT_TAG

# Publish precise openstack repos to AWS
#retry aptly publish snapshot -passphrase=OpenContrail precise-updates-havana-main-$SNAPSHOT_TAG s3:aws-contrail-mirrors:precise-updates-havana/$SNAPSHOT_TAG
#retry aptly publish snapshot -passphrase=OpenContrail precise-updates-icehouse-main-$SNAPSHOT_TAG s3:aws-contrail-mirrors:precise-updates-icehouse/$SNAPSHOT_TAG

# Publish trusty node repos
#aptly publish snapshot -passphrase=OpenContrail -component=main -distribution=trusty node-trusty-main-$SNAPSHOT_TAG node/$SNAPSHOT_TAG

# Publish trusty node repos to AWS
#retry aptly publish snapshot -passphrase=OpenContrail node-trusty-main-$SNAPSHOT_TAG node/$SNAPSHOT_TAG
