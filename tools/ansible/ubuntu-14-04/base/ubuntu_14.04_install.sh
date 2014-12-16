#!/bin/sh
#
# Package needed for contrail build on ubuntu trusty (14.04)
# Definitely a work in progress.
# TODO:
#   - Move all linux-headers-${ver} to LINUX_HEADERS for easier tracking
#   - Change scp for /cs-shared to use mount and rsync

#
export DEBIAN_FRONTEND=noninteractive
apt-get update -y

LINUX_HDRS="linux-headers-3.13.0-34 linux-headers-3.13.0-34-generic"
LINUX_HDRS="$LINUX_HDRS linux-headers-3.13.0-24-generic"
LINUX_HDRS="$LINUX_HDRS linux-headers-3.13.0-35-generic"

apt-get install -y build-essential scons libboost-dev libcurl4-openssl-dev libgtest-dev google-mock libgoogle-perftools-dev libhiredis-dev liblog4cplus-dev libtbb-dev libxml2-dev libicu-dev libhttp-parser-dev git sshpass python-lxml unzip autoconf libtool flex bison libexpat-dev libgettextpo0 libprotobuf-dev libxml2-utils protobuf-compiler python-all libexpat-dev libgettextpo0 libprotobuf-dev libxml2-utils protobuf-compiler python-dev python-setuptools ruby-ronn ruby vim zsh debhelper firefox default-jdk libboost-all-dev python-sphinx python-sphinx module-assistant libxslt1-dev ant javahelper libcommons-codec-java libhttpcore-java liblog4j1.2-java $LINUX_HDRS

[ -d /usr/local/bin ] || mkdir -p /usr/local/bin

if [ ! -r /usr/local/bin/repo ]; then
    echo info: installing /usr/local/bin/repo
    curl https://storage.googleapis.com/git-repo-downloads/repo > /usr/local/bin/repo
    chmod 755 /usr/local/bin/repo
fi

if [ ! -r /usr/local/bin/python2.7 ]; then
    echo info: Creating /usr/local/bin/python2.7 symlink
    ln -s /usr/bin/python2.7 /usr/local/bin/python2.7
fi

# Need to use scp, and nullify the first-time unknown host issue
if [ ! -d /cs-shared/builder/cache ]; then
    echo info: Creating package cache: \"/cs-shared/builder/cache/ubuntu1404\"

    mkdir -p /cs-shared/builder/cache

    password=Juniper1
    server=root@contrail-ec-build14.juniper.net
    path=/volume/contrail/distro-packages/build/ubuntu1404
    # sshpass -p $password rsync -Ah --exclude=.git ${server}:${path} /cs-shared/builder/cache
    sshpass -p $password scp -pr -o StrictHostKeyChecking=no -q ${server}:${path} /cs-shared/builder/cache
fi

#Install libipfix from /cs-shared/builder/cache/ubuntu1404
dpkg -i /cs-shared/builder/cache/ubuntu1404/juno/libipfix_110209-1-0ubuntu0.14.04_amd64.deb
