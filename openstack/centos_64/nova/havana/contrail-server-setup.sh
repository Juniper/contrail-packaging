#!/usr/bin/env bash

# Copyright 2012 OpenStack LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


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

is_enabled=$(systemctl is-enabled mysqld.service 2>/dev/null)
if [ -z "$is_enabled" ]; then
    error_exit ${LINENO} "MySQL is not installed"
fi

if [ "$is_enabled" = 'disabled' ]; then
    service mysqld enable
fi

is_active=$(systemctl is-active mysqld.service 2>/dev/null)
if [ "$is_active" = 'inactive' ]; then
    service mysqld start
fi

# Use MYSQL_ROOT_PW from the environment or generate a new password
if [ ! -f $CONF_DIR/mysql.token ]; then
    if [ -n "$MYSQL_ROOT_PW" ]; then
	MYSQL_TOKEN=$MYSQL_ROOT_PW
    else
	MYSQL_TOKEN=$(openssl rand -hex 10)
    fi
    echo show databases |mysql -u root &> /dev/null
    if [ $? -eq 0 ] ; then
        mysqladmin password $MYSQL_TOKEN
    else
        error_exit ${LINENO} "MySQL root password unknown, reset and retry"
    fi
    echo $MYSQL_TOKEN > $CONF_DIR/mysql.token
    chmod 400 $CONF_DIR/mysql.token
else
    MYSQL_TOKEN=$(cat $CONF_DIR/mysql.token)
    echo show databases |mysql -u root -p${MYSQL_TOKEN} &> /dev/null || \
        error_exit ${LINENO} "MySQL root password not working from token file, reset and retry"
fi

KEYSTONE_CONF=${KEYSTONE_CONF:-/etc/keystone/keystone.conf}

# Please set these, they are ONLY SAMPLE PASSWORDS!
ADMIN_PASSWORD=${ADMIN_PASSWORD:-contrail123}
if [[ "$ADMIN_PASSWORD" == "secrete" ]]; then
    echo "The default admin password has been detected.  Please consider"
    echo "setting an actual password in environment variable ADMIN_PASSWORD"
fi

if [ ! "${SERVICE_PASSWORD+defined}" ]; then
    if [ -f $CONF_DIR/service.token ]; then
	SERVICE_PASSWORD=$(cat $CONF_DIR/service.token)
    else
	SERVICE_PASSWORD=$(openssl rand -hex 10)
	echo $SERVICE_PASSWORD > $CONF_DIR/service.token
	chmod 400 $CONF_DIR/service.token
    fi
fi

if [ -f $CONF_DIR/keystonerc ]; then
    SERVICE_TOKEN=$(awk '/SERVICE_TOKEN/{split($2, fields, "="); print fields[2];}' $CONF_DIR/keystonerc)
else
    SERVICE_TOKEN=$(openssl rand -hex 10)
    openstack-config --set /etc/keystone/keystone.conf DEFAULT admin_token $SERVICE_TOKEN

    # Stop keystone if it is already running (to reload the new admin token)
    service openstack-keystone status >/dev/null 2>&1 &&
    service openstack-keystone stop

fi

# Start and enable the Keystone service
service openstack-keystone start
chkconfig openstack-keystone on

/usr/bin/openstack-keystone-db-setup --rootpw "$MYSQL_TOKEN"

if [ ! -d /etc/keystone/ssl ]; then
    keystone-manage pki_setup
    chown -R keystone.keystone /etc/keystone/ssl
fi

# Set up a keystonerc file with admin password
export SERVICE_ENDPOINT=${SERVICE_ENDPOINT:-http://127.0.0.1:${CONFIG_ADMIN_PORT:-35357}/v2.0}

cat > $CONF_DIR/openstackrc <<EOF
export OS_USERNAME=admin
export OS_PASSWORD=$ADMIN_PASSWORD
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://127.0.0.1:5000/v2.0/
EOF

cat > $CONF_DIR/keystonerc <<EOF
export OS_USERNAME=admin
export SERVICE_TOKEN=$SERVICE_TOKEN
export OS_SERVICE_ENDPOINT=$SERVICE_ENDPOINT
EOF

# wait for the keystone service to start
tries=0
while [ $tries -lt 10 ]; do
    $(source $CONF_DIR/keystonerc; keystone user-list >/dev/null 2>&1)
    if [ $? -eq 0 ]; then break; fi;
    tries=$(($tries + 1))
    sleep 1
done

ROOT_PW=${ROOT_PW:-$SERVICE_PASSWORD}
for APP in nova glance cinder; do
  openstack-db -y --init --service $APP --rootpw "$MYSQL_TOKEN"
done

export ADMIN_PASSWORD
export SERVICE_PASSWORD

$(source $CONF_DIR/keystonerc; bash contrail-keystone-setup.sh)

# Update all config files with service username and password
for svc in nova quantum cinder; do
    openstack-config --set /etc/$svc/$svc.conf keystone_authtoken admin_tenant_name service
    openstack-config --set /etc/$svc/$svc.conf keystone_authtoken admin_user $svc
    openstack-config --set /etc/$svc/$svc.conf keystone_authtoken admin_password $SERVICE_PASSWORD
done

openstack-config --set /etc/nova/nova.conf DEFAULT quantum_admin_tenant_name service
openstack-config --set /etc/nova/nova.conf DEFAULT quantum_admin_username quantum
openstack-config --set /etc/nova/nova.conf DEFAULT quantum_admin_password $SERVICE_PASSWORD

for cfg in api registry; do
    openstack-config --set /etc/glance/glance-$cfg.conf DEFAULT flavor keystone
    openstack-config --set /etc/glance/glance-$cfg.conf keystone_authtoken admin_tenant_name service
    openstack-config --set /etc/glance/glance-$cfg.conf keystone_authtoken admin_user glance
    openstack-config --set /etc/glance/glance-$cfg.conf keystone_authtoken admin_password $SERVICE_PASSWORD
done

echo "======= Enabling the services ======"

for svc in qpidd libvirtd httpd; do
    chkconfig $svc on
done

for svc in zookeeper ifmap contrail-api contrail-schema quantum-server; do
    chkconfig $svc on
done

for svc in api registry; do
    chkconfig openstack-glance-$svc on
done

for svc in api objectstore compute scheduler cert consoleauth novncproxy; do
    chkconfig openstack-nova-$svc on
done

for svc in api scheduler; do
    chkconfig openstack-cinder-$svc on
done

echo "======= Starting the services ======"

for svc in qpidd libvirtd httpd; do
    service $svc start
done

for svc in zookeeper ifmap; do
    service $svc start
done

# TODO: move dependency to service script
tries=0
while [ $tries -lt 10 ]; do
    wget -O- http://localhost:8443 >/dev/null 2>&1
    if [ $? -eq 0 ]; then break; fi
    tries=$(($tries + 1))
    sleep 1
done

service contrail-api start
service contrail-schema start


# TODO: move dependency to service script
tries=0
while [ $tries -lt 10 ]; do
    wget -O- http://localhost:8082 >/dev/null 2>&1
    if [ $? -eq 0 ]; then break; fi
    tries=$(($tries + 1))
    sleep 1
done
service quantum-server start

for svc in api registry; do
    service openstack-glance-$svc start
done

for svc in api objectstore compute scheduler cert consoleauth novncproxy; do
    service openstack-nova-$svc start
done

for svc in api scheduler; do
    service openstack-cinder-$svc start
done


