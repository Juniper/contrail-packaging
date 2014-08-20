# Sample initial data for Keystone using python-keystoneclient
#
# This script is based on the original DevStack keystone_data.sh script.
#
# It demonstrates how to bootstrap Keystone with an administrative user
# using the SERVICE_TOKEN and SERVICE_ENDPOINT environment variables
# and the administrative API.  It will get the admin_token (SERVICE_TOKEN)
# and admin_port from keystone.conf if available.
#
# There are two environment variables to set passwords that should be set
# prior to running this script.  Warnings will appear if they are unset.
# * ADMIN_PASSWORD is used to set the password for the admin and demo accounts.
# * SERVICE_PASSWORD is used to set the password for the service accounts.
#
# Enable the Swift and Quantum accounts by setting ENABLE_SWIFT and/or
# ENABLE_QUANTUM environment variables.
#
# Enable creation of endpoints by setting ENABLE_ENDPOINTS environment variable.
# Works with Catalog SQL backend. Do not use with Catalog Templated backend
# (default).
#
#
# Tenant               User      Roles
# -------------------------------------------------------
# admin                admin     admin
# service              glance    admin
# service              nova      admin
# service              quantum   admin        # if enabled
# service              swift     admin        # if enabled
# demo                 admin     admin
# demo                 demo      Member,sysadmin,netadmin
# invisible_to_admin   demo      Member

ENABLE_ENDPOINTS=yes
#ENABLE_QUANTUM=yes

if [ -z $ADMIN_PASSWORD ]; then
    echo ADMIN_PASSWORD must be defined
    exit 1;
fi

if [ -z $SERVICE_PASSWORD ]; then
    echo SERVICE_PASSWORD must be defined
    exit 1;
fi

CONTROLLER=$1
if [ -z $CONTROLLER ]; then
    $CONTROLLER="localhost"
fi

function get_id () {
    echo `"$@" | grep ' id ' | awk '{print $4}'`
}

function is_keystone_up() {
    for i in {1..36} {
    do
       keystone tenant-list
       if [ $? == 0 ]; then
           return 0
       fi
       echo "Keystone is not up, retrying in 5 secs"
       sleep 5
    done
    return 1
}

function get_tenant() {
    id=$(keystone tenant-list | grep ' '$1' ' | awk '{print $2;}')
    if [ -z "$id" ]; then
	id=$(keystone tenant-create --name=$1 | grep ' id ' | awk '{print $4}')
    fi
    echo $id
}

# Tenants
is_keystone_up
if [ $? != 0 ]; then
    echo "Keystone is not up, Exiting..."
    exit 1
fi
ADMIN_TENANT=$(get_tenant admin)
SERVICE_TENANT=$(get_tenant service)
DEMO_TENANT=$(get_tenant demo)
INVIS_TENANT=$(get_tenant invisible_to_admin)

# Users
function get_user() {
    id=$(keystone user-list | grep $1 | awk '{print $2;}')
    EMAIL="@example.com"
    if [ -z $id ]; then
	id=$(keystone user-create --name=$1 --pass="$ADMIN_PASSWORD" \
	         --email=$1$EMAIL | grep ' id ' | awk '{print $4;}')
    fi
    echo $id
}

ADMIN_USER=$(get_user admin)
DEMO_USER=$(get_user demo)

# Roles

function get_role() {
    id=$(keystone role-list | grep ' '$1' ' | awk '{print $2;}')
    if [ -z $id ]; then
	id=$(keystone role-create --name=$1 | grep ' id ' | awk '{print $4;}')
    fi
    echo $id
}

ADMIN_ROLE=$(get_role admin)
MEMBER_ROLE=$(get_role Member)
KEYSTONEADMIN_ROLE=$(get_role KeystoneAdmin)
KEYSTONESERVICE_ROLE=$(get_role KeystoneServiceAdmin)
SYSADMIN_ROLE=$(get_role sysadmin)
NETADMIN_ROLE=$(get_role netadmin)

function user_role_lookup() {
    echo $(keystone user-role-list --user-id $1 --tenant-id $2 \
	| grep ' '$3' ' | awk '{print $4;}')
}

# Add Roles to Users in Tenants
if [ -z $(user_role_lookup $ADMIN_USER $ADMIN_TENANT admin) ]; then
keystone user-role-add --user-id $ADMIN_USER --role-id $ADMIN_ROLE --tenant-id $ADMIN_TENANT
fi

if [ -z $(user_role_lookup $DEMO_USER $DEMO_TENANT Member) ]; then
keystone user-role-add --user-id $DEMO_USER --role-id $MEMBER_ROLE --tenant-id $DEMO_TENANT
fi

if [ -z $(user_role_lookup $DEMO_USER $DEMO_TENANT sysadmin) ]; then
keystone user-role-add --user-id $DEMO_USER --role-id $SYSADMIN_ROLE --tenant-id $DEMO_TENANT
fi

if [ -z $(user_role_lookup $DEMO_USER $DEMO_TENANT netadmin) ]; then
keystone user-role-add --user-id $DEMO_USER --role-id $NETADMIN_ROLE --tenant-id $DEMO_TENANT
fi

if [ -z $(user_role_lookup $DEMO_USER $INVIS_TENANT Member) ]; then
keystone user-role-add --user-id $DEMO_USER --role-id $MEMBER_ROLE --tenant-id $INVIS_TENANT
fi

if [ -z $(user_role_lookup $ADMIN_USER $DEMO_TENANT admin) ]; then
keystone user-role-add --user-id $ADMIN_USER --role-id $ADMIN_ROLE --tenant-id $DEMO_TENANT
fi

# TODO(termie): these two might be dubious
if [ -z $(user_role_lookup $ADMIN_USER $ADMIN_TENANT KeystoneAdmin) ]; then
keystone user-role-add --user-id $ADMIN_USER --role-id $KEYSTONEADMIN_ROLE --tenant-id $ADMIN_TENANT
fi
if [ -z $(user_role_lookup $ADMIN_USER $ADMIN_TENANT KeystoneServiceAdmin) ]; then
keystone user-role-add --user-id $ADMIN_USER --role-id $KEYSTONESERVICE_ROLE --tenant-id $ADMIN_TENANT
fi

# Services
function get_service() {
    id=$(keystone service-list | grep ' '$1' ' | awk '{print $2;}')
    if [ -z $id ]; then
	id=$(get_id keystone service-create --name=$1 \
                        --type=$2 --description=$2)
    fi
    echo $id
}

function get_service_user() {
    id=$(keystone user-list | grep $1 | awk '{print $2;}')
    EMAIL="@example.com"
    if [ -z $id ]; then
	id=$(keystone user-create --name=$1 --pass="$SERVICE_PASSWORD" \
	         --tenant-id $SERVICE_TENANT \
	         --email=$1$EMAIL | grep ' id ' | awk '{print $4;}')
    fi
    echo $id
}

function endpoint_lookup() {
    echo $(keystone endpoint-list | grep ' '$1' ' | awk '{print $2;}' )
}

NOVA_SERVICE=$(get_service nova compute "Nova Compute Service")
NOVA_USER=$(get_service_user nova)

if [ -z $(user_role_lookup $NOVA_USER $SERVICE_TENANT admin) ]; then
keystone user-role-add --tenant-id $SERVICE_TENANT \
                       --user-id $NOVA_USER \
                       --role-id $ADMIN_ROLE
fi

if [[ -n "$ENABLE_ENDPOINTS" ]]; then
    if [ -z $(endpoint_lookup $NOVA_SERVICE) ]; then
    keystone endpoint-create --region RegionOne --service-id $NOVA_SERVICE \
        --publicurl 'http://'$CONTROLLER':$(compute_port)s/v1.1/$(tenant_id)s' \
        --adminurl 'http://'$CONTROLLER:'$(compute_port)s/v1.1/$(tenant_id)s' \
        --internalurl 'http://'$CONTROLLER:'$(compute_port)s/v1.1/$(tenant_id)s'
    fi
fi

EC2_SERVICE=$(get_service ec2 ec2 "EC2 Compatibility Layer")
if [[ -n "$ENABLE_ENDPOINTS" ]]; then
    if [ -z $(endpoint_lookup $EC2_SERVICE) ]; then
    keystone endpoint-create --region RegionOne --service-id $EC2_SERVICE \
        --publicurl http://localhost:8773/services/Cloud \
        --adminurl http://localhost:8773/services/Admin \
        --internalurl http://localhost:8773/services/Cloud
    fi
fi

GLANCE_SERVICE=$(get_service glance image "Glance Image Service")
GLANCE_USER=$(get_service_user glance)

if [ -z $(user_role_lookup $GLANCE_USER $SERVICE_TENANT admin) ]; then
keystone user-role-add --tenant-id $SERVICE_TENANT \
                       --user-id $GLANCE_USER \
                       --role-id $ADMIN_ROLE
fi

if [[ -n "$ENABLE_ENDPOINTS" ]]; then
    if [ -z $(endpoint_lookup $GLANCE_SERVICE) ]; then
    keystone endpoint-create --region RegionOne --service-id $GLANCE_SERVICE \
        --publicurl http://$CONTROLLER:9292/v1 \
        --adminurl http://$CONTROLLER:9292/v1 \
        --internalurl http://$CONTROLLER:9292/v1
    fi
fi

KEYSTONE_SERVICE=$(get_service keystone identity "Keystone Identity Service")
if [[ -n "$ENABLE_ENDPOINTS" ]]; then
    if [ -z $(endpoint_lookup $KEYSTONE_SERVICE) ]; then
    keystone endpoint-create --region RegionOne --service-id $KEYSTONE_SERVICE \
        --publicurl 'http://'$CONTROLLER':$(public_port)s/v2.0' \
        --adminurl 'http://'$CONTROLLER':$(admin_port)s/v2.0' \
        --internalurl 'http://'$CONTROLLER':$(admin_port)s/v2.0'
    fi
fi

CINDER_SERVICE=$(get_service "cinder" volume "Cinder Service")
CINDER_USER=$(get_service_user cinder)

if [ -z $(user_role_lookup $CINDER_USER $SERVICE_TENANT admin) ]; then
keystone user-role-add --tenant-id $SERVICE_TENANT \
                       --user-id $CINDER_USER \
                       --role-id $ADMIN_ROLE
fi

if [[ -n "$ENABLE_ENDPOINTS" ]]; then
    if [ -z $(endpoint_lookup $CINDER_SERVICE) ]; then
    keystone endpoint-create --region RegionOne --service-id $CINDER_SERVICE \
        --publicurl 'http://'$CONTROLLER':8776/v1/$(tenant_id)s' \
        --adminurl 'http://'$CONTROLLER':8776/v1/$(tenant_id)s' \
        --internalurl 'http://'$CONTROLLER':8776/v1/$(tenant_id)s'
    fi
fi

HORIZON_SERVICE=$(get_service "horizon" dashboard "OpenStack Dashboard")

if [[ -n "$ENABLE_SWIFT" ]]; then
    SWIFT_SERVICE=$(get_id \
    keystone service-create --name=swift \
                            --type="object-store" \
                            --description="Swift Service")
    SWIFT_USER=$(get_id keystone user-create --name=swift \
                                             --pass="$SERVICE_PASSWORD" \
                                             --tenant-id $SERVICE_TENANT \
                                             --email=swift@example.com)
    keystone user-role-add --tenant-id $SERVICE_TENANT \
                           --user-id $SWIFT_USER \
                           --role-id $ADMIN_ROLE
    if [[ -n "$ENABLE_ENDPOINTS" ]]; then
        keystone endpoint-create --region RegionOne --service-id $SWIFT_SERVICE \
            --publicurl   'http://localhost:8080/v1/AUTH_$(tenant_id)s' \
            --adminurl    'http://localhost:8080/v1/AUTH_$(tenant_id)s' \
            --internalurl 'http://localhost:8080/v1/AUTH_$(tenant_id)s'
    fi
fi

if [[ -n "$ENABLE_QUANTUM" ]]; then
    QUANTUM_SERVICE=$(get_service quantum network "Quantum Service")
    QUANTUM_USER=$(get_service_user quantum)
    if [ -z $(user_role_lookup $QUANTUM_USER $SERVICE_TENANT admin) ]; then
    keystone user-role-add --tenant-id $SERVICE_TENANT \
                           --user-id $QUANTUM_USER \
                           --role-id $ADMIN_ROLE
    fi

    if [[ -n "$ENABLE_ENDPOINTS" ]]; then
	if [ -z $(endpoint_lookup $QUANTUM_SERVICE) ]; then
        keystone endpoint-create --region RegionOne --service-id $QUANTUM_SERVICE \
            --publicurl http://localhost:9696 \
            --adminurl http://localhost:9696 \
            --internalurl http://localhost:9696
	fi
    fi
fi

# A set of EC2-compatible credentials is created for both admin and demo
# users and placed in etc/ec2rc.
EC2RC=${EC2RC:-/etc/contrail/ec2rc}


# create ec2 creds and parse the secret and access key returned
RESULT=$(keystone ec2-credentials-create --tenant-id=$ADMIN_TENANT --user-id=$ADMIN_USER)
ADMIN_ACCESS=`echo "$RESULT" | grep access | awk '{print $4}'`
ADMIN_SECRET=`echo "$RESULT" | grep secret | awk '{print $4}'`

RESULT=$(keystone ec2-credentials-create --tenant-id=$DEMO_TENANT --user-id=$DEMO_USER)
DEMO_ACCESS=`echo "$RESULT" | grep access | awk '{print $4}'`
DEMO_SECRET=`echo "$RESULT" | grep secret | awk '{print $4}'`

# write the secret and access to ec2rc
cat > $EC2RC <<EOF
ADMIN_ACCESS=$ADMIN_ACCESS
ADMIN_SECRET=$ADMIN_SECRET
DEMO_ACCESS=$DEMO_ACCESS
DEMO_SECRET=$DEMO_SECRET
EOF

