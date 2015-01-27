#!/bin/sh

repo_dir=/opt/contrail/contrail_install_repo_dpdk

# Create a new repo
cd $repo_dir
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

# Insert new repo line at the top of /etc/apt/sources.list if not already
# present
cd /etc/apt
grep -E "^\s*deb\s+file:$repo_dir\s+\./" sources.list
if [ $? != 0 ]; then
    date_str=$(date +%Y_%m_%d__%H_%M_%S)
    mv sources.list sources.list.$date_str
    echo "deb file:$repo_dir ./" > sources.list
    cat sources.list.$date_str >> sources.list
fi

# Rescan repositories
apt-get update
