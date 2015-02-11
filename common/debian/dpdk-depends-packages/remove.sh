#!/bin/sh

repo_dir=/opt/contrail/contrail_install_repo_dpdk

# Escape repo_dir path for sed below
repo_dir_escaped=$(echo "$repo_dir" | sed -re 's:/:\\/:g')

# Remove repo line from /etc/apt/sources.list
date_str=$(date +%Y_%m_%d__%H_%M_%S)
sed -i".$date_str" -re "/^\s*deb\s+file:$repo_dir_escaped/ d" \
    /etc/apt/sources.list

# Rescan repositories
apt-get update

