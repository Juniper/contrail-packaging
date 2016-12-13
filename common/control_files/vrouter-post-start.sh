#!/bin/bash

source /etc/contrail/agent_param
ip link set dev $dev up

function create_qos_config() {

    bond_dir="/sys/class/net/${dev}/bonding"
    QOS_INTF_LIST=""
    if [ -d ${bond_dir} ]; then
        QOS_INTF_LIST=`cat ${bond_dir}/slaves | tr ' ' '\n' | sort | tr '\n' ' '`
        QOS_INTF_LIST="${QOS_INTF_LIST% }"
    else
        QOS_INTF_LIST="${dev}"
    fi

    echo "$(date): Running qosmap.py script\n"
    python /usr/share/contrail-utils/qosmap.py --interface_list $QOS_INTF_LIST --qos_scheduling
}

if [ $qos_enabled != false ]
then
    echo "$(date): Executing qosmap set-queue command in ieee mode with --bw and --strict options." &>> $LOG
    create_qos_config &>> $LOG
fi
