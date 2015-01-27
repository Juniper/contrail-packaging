#!/bin/sh

repo_dir=/opt/contrail/contrail_install_repo_dpdk

# Create a new repo
cd $repo_dir
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

# Escape repo_dir path for sed below
repo_dir_escaped=$(echo "$repo_dir" | sed -re 's:/:\\/:g')

# Insert new repo line at the top of /etc/apt/sources.list if not already
# present
sed_prg="
    0,/^\s*deb\s+/ {
        /^\s*deb\s+file:$repo_dir_escaped/ q
        /^\s*deb\s+/ i deb file:$repo_dir ./
    }
"
date_str=$(date +%Y_%m_%d__%H_%M_%S)
sed -i".$date_str" -re "$sed_prg" /etc/apt/sources.list

# Rescan repositories
apt-get update
