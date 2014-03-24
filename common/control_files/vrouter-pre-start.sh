#! /bin/bash

set -x

function error_exit
{
#   ----------------------------------------------------------------
#   Function for exit due to fatal program error
#       Accepts 3 arguments:
#               line #
#               string containing descriptive error message
#               exit code
#   ----------------------------------------------------------------


    echo "${PROGNAME}: ${1:-''} ${2:-'Unknown Error'}" 1>&2
    exit ${3:-1}
}

function find_dev_by_mac () {
mac=$1;
[ -z "$mac" ] || for dev in /sys/class/net/*; do
    [ $mac = $(cat $dev/address) ] && [ $(basename $dev) != vhost0 ] && \
         echo $(basename $dev) && return 
done
}


[ -f /etc/contrail/default_pmac ] || error_exit $LINENO "Did you run setup?"
[ -f /etc/contrail/agent_param ] || error_exit $LINENO "Did you run setup?"

source /opt/contrail/bin/vrouter-function.sh

function create_virtual_gateway() {

    echo "$(date): Adding intreface vgw for virtual gateway"
    #    sysctl -w net.ipv4.ip_forward=1
    echo 1 > /proc/sys/net/ipv4/ip_forward
    vif --create vgw --mac 00:01:00:5e:00:00
    if [ $? != 0 ]
    then
        echo "$(date): Error adding intreface vgw"
    fi
 
    ifconfig vgw up
    vgw_subnet=$vgw_subnet_ip"/"$vgw_subnet_mask
    route add -net $vgw_subnet dev vgw
    
}

insert_vrouter &>> $LOG
echo "$(date): Value $vgw_subnet_ip" &>> $LOG
if [ $vgw_subnet_ip != __VGW_SUBNET_IP__ ] 
then
    echo "$(date): Creating VGW Intreface as VGW Subnet is present" &>> $LOG
    create_virtual_gateway &>>$LOG
fi

