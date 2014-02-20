#!/bin/sh

cd /usr/local/bin
ln -s /volume/ssd-tools/bin/config-ansible .
ln -s /volume/ssd-tools/bin/contrail-archive .
ln -s /volume/ssd-tools/bin/contrail-build .
ln -s /volume/ssd-tools/bin/create-base-manifest .
ln -s /volume/ssd-tools/bin/create-config .
ln -s /volume/ssd-tools/bin/fix-manifest.py .
ln -s /volume/ssd-tools/bin/merge-manifest .

mkdir -p /cs-shared/builder
cd /cs-shared/builder
ln -s /volume/junosv-storage01/contrail/build cache 

mkdir -p /ecbuilds
cd /ecbuilds
tar xzf /tmp/gitcommits.tgz

