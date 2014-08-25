mkdir -p /opt/contrail/contrail_storage_repo
cd /opt/contrail/contrail_storage_repo; tar xvzf /opt/contrail/contrail_packages/contrail_storage_debs.tgz

sleep 1
# create shell scripts and put to bin
mkdir -p /opt/contrail/bin

cd /etc/apt/
# create repo with only local packages
datetime_string=`date +%Y_%m_%d__%H_%M_%S`
cp sources.list sources.list.$datetime_string
echo "deb file:/opt/contrail/contrail_storage_repo ./" > local_storage_repo

#modify /etc/apt/soruces.list/ to add local repo on the top
grep "deb file:/opt/contrail/contrail_storage_repo ./" sources.list
if [ $? != 0 ]; then
     sed '1 a\deb file:/opt/contrail/contrail_storage_repo ./' sources.list > /tmp/sources.temp.list
     mv /tmp/sources.temp.list sources.list
fi

#Allow unauthenticated pacakges to get installed
#scan pkgs in local repo and create Packages.gz
cd /opt/contrail/contrail_storage_repo
dpkg-scanpackages . /dev/null |  gzip -9c > Packages.gz
apt-get update


