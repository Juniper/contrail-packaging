#!/bin/bash

if [ -z $1 ]; then
    echo "ERROR: Supply package name"
    echo "Usage: centos-mirror-package-search <package-name>"
    exit 2
fi

pkgs=$(find -L /home/npchandran/mount_dont_del/mirrors/.centos-mirrors/ -name "${1}*.rpm")
echo "SNAPSHOT-ID | MD5SUM | PACKAGE LOCATION"
for pkg in $pkgs; do
    path=${pkg#/home/npchandran/mount_dont_del/mirrors/.centos-mirrors/}
    md5sum_pkg=$(md5sum $pkg | cut -d " " -f1)
    snapshot=$(echo $path | grep -o "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]")
    if [ ! -z $snapshot ]; then
        echo "$snapshot |  $md5sum_pkg | $path "
        echo
    fi
done
