#! /bin/bash


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

function pkt_setup () {
    for f in /sys/class/net/$1/queues/rx-*
    do
        q="$(echo $f | cut -d '-' -f2)"
        ((mask=1<<$q))
        echo "obase=16;$mask" | bc > $f/rps_cpus
    done
}

[ -f /etc/contrail/default_pmac ] || error_exit $LINENO "Did you run setup?"
[ -f /etc/contrail/agent_param ] || error_exit $LINENO "Did you run setup?"

source /etc/contrail/agent_param

source $VHOST_CFG

function insert_vrouter() {
    insmod $kmod
    if [ $? != 0 ]
    then
        echo "$(date) : Error inserting vrouter module"
        return 1
    fi

    if [ -f /sys/class/net/pkt1/queues/rx-0/rps_cpus ]; then
        pkt_setup pkt1
    fi
    if [ -f /sys/class/net/pkt2/queues/rx-0/rps_cpus ]; then 
        pkt_setup pkt2
    fi

    echo "$(date): Creating vhost interface: $DEVICE."
    # for bonding interfaces
    loops=0
    while [ ! -f /sys/class/net/$dev/address ]
    do
        sleep 1
        loops=$(($loops + 1))
        if [ $loops -ge 60 ]
        then
            echo "Unable to look at /sys/class/net/$dev/address"
            return 1
        fi
    done

    DEV_MAC=$(cat /sys/class/net/$dev/address)
    vif --create $DEVICE --mac $DEV_MAC
    if [ $? != 0 ]
    then
       echo "$(date): Error creating interface: $DEVICE"
    fi

    vif --add $DEVICE --mac $DEV_MAC --vrf 0 --mode x --type vhost
    if [ $? != 0 ]
    then
       echo "$(date): Error adding $DEVICE to vrouter"
    fi

    echo "$(date): Adding $dev to vrouter"
    DEV_MAC=$(cat /sys/class/net/$dev/address)
    vif --add $dev --mac $DEV_MAC --vrf 0 --mode x --type physical
    if [ $? != 0 ]
    then
        echo "$(date): Error adding $dev to vrouter"
    fi

    ifup $DEVICE
    return 0
}

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

lsmod |grep vrouter &>> $LOG
if [ $? != 0 ]
then
    insert_vrouter &>> $LOG
    echo "$(date): vrouter kernel module inserted." &>> $LOG
else
    echo "$(date): vrouter module already inserted." &>> $LOG
fi

 echo "$(date): Value $vgw_subnet_ip" &>> $LOG
if [ $vgw_subnet_ip != __VGW_SUBNET_IP__ ] 
then
    echo "$(date): Creating VGW Intreface as VGW Subnet is present" &>> $LOG
    create_virtual_gateway &>>$LOG
fi

