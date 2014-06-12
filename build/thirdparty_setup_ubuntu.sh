#!/bin/sh

# copy files over
echo "Create Repo dir and Untar all thirdparty packages"
mkdir -p /opt/contrail/contrail_thirdparty_repo
cd /opt/contrail/contrail_thirdparty_repo; tar xvzf /opt/contrail/contrail_packages/contrail_thirdparty_debs.tgz

echo "Create Repo and Update sources.list"
cd /etc/apt/
# create repo with only local packages
datetime_string=`date +%Y_%m_%d__%H_%M_%S`
cp sources.list sources.list.$datetime_string
echo "deb file:/opt/contrail/contrail_thirdparty_repo ./" > local_repo

#modify /etc/apt/soruces.list/ to add local repo on the top
grep "deb file:/opt/contrail/contrail_thirdparty_repo ./" sources.list

if [ $? != 0 ]; then
    cat local_repo sources.list > new_sources.list
    mv new_sources.list sources.list
fi

# Allow unauthenticated pacakges to get installed.
# Do not over-write apt.conf. Instead just append what is necessary
# retaining other useful configurations such as http::proxy info.
apt_auth="APT::Get::AllowUnauthenticated \"true\";"
grep --quiet "$apt_auth" apt.conf
if [ "$?" != "0" ]; then
    echo "$apt_auth" >> apt.conf
fi

#scan pkgs in local repo and create Packages.gz
cd /opt/contrail/contrail_thirdparty_repo
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
apt-get update

exit 0
