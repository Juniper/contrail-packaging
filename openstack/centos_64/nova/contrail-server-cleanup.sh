#!/usr/bin/env bash

#
# Remove OpenStack configuration from a server.
#

CONF_DIR=/etc/contrail


function error_exit
{
#   ----------------------------------------------------------------
#   Function for exit due to fatal program error
#       Accepts 1 argument:
#               string containing descriptive error message
#   ----------------------------------------------------------------


    echo "${PROGNAME}: ${1:-''} ${2:-'Unknown Error'}" 1>&2
    exit ${3:-1}
}

if [ -n "$MYSQL_ROOT_PW" ]; then
    MYSQL_TOKEN=$MYSQL_ROOT_PW
elif [ -f $CONF_DIR/mysql.token ]; then
    MYSQL_TOKEN=$(cat $CONF_DIR/mysql.token)
fi

if [ -z "$MYSQL_TOKEN" ]; then
    echo "Please provide MySQL root password"
    exit 1
fi
echo show databases |mysql -u root -p${MYSQL_TOKEN} &> /dev/null || \
        error_exit ${LINENO} "MySQL root password not working from token file, reset and retry"

# shutdown all the services
for svc in zookeeper ifmap contrail-api contrail-schema quantum-server; do
    /bin/systemctl --no-reload disable $svc.service > /dev/null 2>&1
    /bin/systemctl stop $svc.service > /dev/null 2>&1
done

for svc in api objectstore compute scheduler cert consoleauth novncproxy; do
    svc=openstack-nova-$svc
    /bin/systemctl --no-reload disable $svc.service > /dev/null 2>&1
    /bin/systemctl stop $svc.service > /dev/null 2>&1
done

for svc in api registry; do
    svc=openstack-glance-$svc
    /bin/systemctl --no-reload disable $svc.service > /dev/null 2>&1
    /bin/systemctl stop $svc.service > /dev/null 2>&1
done

for svc in api scheduler; do
    svc=openstack-cinder-$svc
    /bin/systemctl --no-reload disable $svc.service > /dev/null 2>&1
    /bin/systemctl stop $svc.service > /dev/null 2>&1
done

for svc in keystone nova glance cinder; do
    openstack-db -y --drop --service $svc --rootpw "$MYSQL_TOKEN"
done

rm -rf /etc/keystone/ssl
rm -f /etc/contrail/service.token
rm -f /etc/contrail/keystonerc
rm -f /etc/contrail/openstackrc

if [ -n "$DISABLE_MYSQL" ]; then
    rm -f /etc/contrail/mysql.token

    mysqladmin --password="$MYSQL_TOKEN" password ""
    /bin/systemctl --no-reload disable mysqld.service > /dev/null 2>&1
    /bin/systemctl stop mysqld.service > /dev/null 2>&1
fi

# TODO: determine what needs to be removed
for subdir in keys buckets images; do
    ls /var/lib/nova/$subdir
done

for file in $(ls /var/lib/glance/images); do
    rm -f $file
done

# Remove keystone keys
for svc in nova glance quantum; do
    rm -f /var/lib/$svc/keystone-signing/*.pem
done

rm -f /var/lib/cinder/*.pem
