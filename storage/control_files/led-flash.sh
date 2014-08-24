#!/bin/bash

TMP_FILE=/tmp/temp.txt
LOG_FILE=/tmp/led-flash.log
TMP_EXECUTE_DIR=/tmp

# usage
function usage()
{
  echo "usage: $0 [flash-enable|flash-disable] osd-name[osd.<number>]"
  return 1
}
  # usage

# function which flashes led on a drive, given osd number
function flash_led() {
  local total_controllers=$1
  local serial=$2
  local operation=$3
  if [ "$total_controllers" == "0" ]; then
    echo "No LSI controller or error in information from sas2ircu command"
    exit 1
  fi
  for (( i=0; i<$total_controllers; i++))
  do
    enclosure=`sas2ircu $i DISPLAY | grep "Enclosure#" | cut -d ":" -f 2`
    bay=`sas2ircu $i DISPLAY | grep -B7 "$serial" | grep Slot | \
        cut -d ":" -f 2 | tr -d ' '`
    local re='[a-zA-Z]'
    if [[ "$bay" =~ $re ]]; then
      echo "Error getting bay"
      exit 2
    fi
    if [ "$operation" == "flash-enable" ]; then
      sas2ircu $i LOCATE $enclosure:$bay ON > "$LOG_FILE" 2>&1
      echo "LED on $osd turned ON"
    elif [ "$operation" == "flash-disable" ]; then
      sas2ircu $i LOCATE $enclosure:$bay OFF > "$LOG_FILE" 2>&1
      echo "LED on $osd turned OFF"
    else
      usage
      return
    fi
  done
}
  # flash_led

# function which checks if SAS2008 or SAS2308
# LSI controller is present on the machine.
# led functionality only works with the above
# two controllers
function check_lsi()
{
  local output=`lspci | grep LSI`
  local is_lsi=`echo $output | grep SAS2008`
  if [ -z "$is_lsi" ]; then
    is_lsi=`echo $output | grep SAS2308`
    if [ -z "$is_lsi" ]; then
      echo >&2 "No correct LSI controller present."
      returnval=2
    fi
  fi
  echo $returnval
}
  # check_lsi

if [ $# -ne 2 ]; then
    usage
    exit 1
fi

RET=$(check_lsi)
echo $RET
if [ "$RET" == "2" ]; then
   exit 2
fi

HOST=`hostname`
OPERATION=$1
if [[ "$OPERATION" != "flash-enable" && "$OPERATION" != "flash-disable" ]]
then
  usage
  exit 1
fi

OSD=$2
if [[ "$OSD" != *.* && "$OSD" != "osd" && -n ${OSD//[0-9]} ]]; then
  usage
  exit 1
fi

command -v smartctl > /dev/null
if [ $? != '0' ]; then
  echo "Install smartmontools to support smartctl"
  exit 1
fi

command -v sas2ircu > /dev/null
if [ $? != '0' ]; then
  echo "Install sas2ircu utility"
  exit 1
fi

if [ -n "$HOST" ]; then
  # ceph.conf is needed in the current directory to
  # run ceph-deploy command
  cd $TMP_EXECUTE_DIR
  rm -rf ceph.conf
  ln -s /etc/ceph/ceph.conf ceph.conf
  # Get osd to disk mapping
  `ceph-deploy disk list "$HOST" > "$TMP_FILE" 2>&1`
  if [ $? == 0 ]; then
    cd -
    ARR1=`cat $TMP_FILE | grep $OSD`
    # Split ARR1 into an array 'ARR' by using space as delimiter
    IFS=' ' read -a ARR <<< "$ARR1"
    LEN_ARR=${#ARR[*]}
    if [ -n "$LEN_ARR" ]; then
      # disk corressponding to osd
      DISK="${ARR[2]}"
      DISK=${DISK%?}
      DISK=`basename $DISK`
      if echo "$DISK" | grep -q "sd"; then
        res=`smartctl -i /dev/"$DISK" | grep Serial`
        if [ $? == 0 ]; then
          SERIAL=`echo $res | cut -d ":" -f 2 | tr -d ' '`
          if [ $? != 0 ]; then
            exit 1
          fi
        else
          exit 1
        fi
        # sas2ircu command shows first 8 characters of serial number
        SERIAL=${SERIAL:0:8}
        # Index will give sequnetial numbers of controllers
        # Last value of Index will give total number
        # Output of last two lines of command:
        # root@cmbu-ceph-4:~# sas2ircu LIST  | tail -n 2 | tr -s ' '
        # 0 SAS2308_1 1000h 86h 00h:04h:00h:00h 15d9h 0691h
        # SAS2IRCU: Utility Completed Successfully.
        res=`sas2ircu LIST | tail -n 2`
        if [ $? != 0 ]; then
          exit 1
        fi
        res=`echo $res | tr -s ' '`
        if [ $? != 0 ]; then
          exit 1
        fi
        TOTAL_CONTROLLERS=`echo $res | cut -d " " -f 2 | head -n 1`
        if [ $? != 0 ]; then
          exit 1
        fi
        TOTAL_CONTROLLERS=$((TOTAL_CONTROLLERS+1))
        flash_led $TOTAL_CONTROLLERS $SERIAL $OPERATION
      else
        echo "Error getting disk name"
      fi
    else
      echo "Array length is 0"
    fi
  else
    echo "Error executing ceph-deploy command"
  fi
else
  echo "Error getting hostname"
fi
