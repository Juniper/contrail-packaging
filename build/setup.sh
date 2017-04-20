#!/bin/bash

repopath=/etc/yum.repos.d/
if [ -d /etc/zypp/repos.d ]; then
    repopath=/etc/zypp/repos.d/
fi

# create contrail installer repo
cat << __EOT__ > $repopath/contrail-install.repo
[contrail_install_repo]
name=contrail_install_repo
baseurl=file:///opt/contrail/contrail_install_repo/
enabled=1
priority=1
gpgcheck=0
__EOT__

# backup old directories in case of upgrade
if [ -d /opt/contrail/contrail_install_repo ]; then
    mkdir -p /opt/contrail/contrail_install_repo_backup
    mv /opt/contrail/contrail_install_repo/* /opt/contrail/contrail_install_repo_backup/
fi

# copy files over
mkdir -p /opt/contrail/contrail_install_repo
mkdir -p /opt/contrail/bin

cd /opt/contrail/contrail_install_repo; tar xvzf /opt/contrail/contrail_packages/contrail_rpms.tgz

# create shell scripts and put to bin
cp /opt/contrail/contrail_packages/helpers/* /opt/contrail/bin/

# Remove existing python-crypto-2.0.1 rpm.
yum -y --disablerepo=* remove python-crypto-2.0.1

# Priority Override for obsolete packages
priorities_conf="/etc/yum/pluginconf.d/priorities.conf"
[ -f $priorities_conf ] && \
grep -qi "\[main\]" $priorities_conf && \
! grep -q "check_obsoletes\s*=\s*1" $priorities_conf && \
sed -i 's/\[main\]$/&\ncheck_obsoletes = 1/' $priorities_conf && \
echo "PASS: Added Priority Override for Obsolete packages" || ( \
grep -q "check_obsoletes\s*=\s*1" $priorities_conf && \
echo "PASS: Priority Override for Obsolete packages already exists. Nothing to do" ) || ( \
[ ! -f $priorities_conf ] && echo "WARNING: $priorities_conf not found" ) || ( \
echo "WARNING: Couldnt add priority Override for Obsolete packages. Check..." && \
cat $priorities_conf )

#Install basic packages 
yum -y install contrail-fabric-utils contrail-setup
