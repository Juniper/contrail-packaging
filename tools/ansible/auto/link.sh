#!/bin/sh

# No longer want to create links.
# Copying the files over so folks can work disconnected.

# cd /usr/local/bin
# ln -s /volume/ssd-tools/bin/config-ansible .
# ln -s /volume/ssd-tools/bin/contrail-archive .
# ln -s /volume/ssd-tools/bin/contrail-build .
# ln -s /volume/ssd-tools/bin/contrail-manipulate-manifest .
# ln -s /volume/ssd-tools/bin/create-base-manifest .
# ln -s /volume/ssd-tools/bin/create-config .
# ln -s /volume/ssd-tools/bin/fix-manifest.py .
# ln -s /volume/ssd-tools/bin/merge-manifest .

mkdir -p /cs-shared/builder
cd /cs-shared/builder
ln -s /volume/junosv-storage01/contrail/distro-packages/build/ cache 

mkdir -p /ecbuilds
cd /ecbuilds
tar xzf /tmp/gitcommits.tgz

