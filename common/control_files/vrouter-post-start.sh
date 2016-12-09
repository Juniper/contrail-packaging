#!/bin/bash

source /etc/contrail/agent_param
ip link set dev $dev up

function create_qos_config() {

    echo "$(date): Adding qosmap configuration"
    qos_intf_array=(${qos_intf//,/ })
    i=0
    for ((i=0;i<${#qos_intf_array[@]};++i))
       do
       qosmap --set-queue ${qos_intf_array[i]} --dcbx ieee --bw $qos_bw --strict $qos_strictness --tc 0,1,2,3,4,5,6,7
       echo "qosmap --set-queue ${qos_intf_array[i]} --dcbx ieee --bw $qos_bw --strict $qos_strictness"
       if [ $? != 0 ]
           then
           echo "$(date): Error adding qos queue "
       fi

       done
}

if [ $qos_intf != __QOS_INTF_LIST__ ]
then
    echo "$(date): Executing qosmap set-queue command in ieee mode with --bw and --strict options." &>> $LOG
    create_qos_config &>> $LOG
fi
