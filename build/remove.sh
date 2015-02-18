#!/bin/sh -x

dir_name=`dirname $0`
base_dir_name=`basename $dir_name`
if [ $dir_name = '.' ]; then
    base_dir_name=`echo $PWD | cut -d '/' -f4`
fi

line_num=`cat /etc/apt/sources.list | grep -n $base_dir_name | cut -d ':' -f1`
sed -i 's%deb file\:\/opt\/contrail\/'$base_dir_name' \.\/%%' /etc/apt/sources.list
sed -i ''$line_num'{/^$/d}' /etc/apt/sources.list

rm -f "/opt/contrail/.$base_dir_name"
echo "Removed /opt/contrail/.$base_dir_name"
# Rescan repositories
apt-get update
