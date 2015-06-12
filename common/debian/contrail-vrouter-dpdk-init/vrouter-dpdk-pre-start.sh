#! /bin/bash

source /opt/contrail/bin/vrouter-functions.sh

set -x

vrouter_dpdk_if_bind &>> $LOG
