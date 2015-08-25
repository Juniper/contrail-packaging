#!/bin/bash
set -x
set -e

datetime_string=$(date +%Y_%m_%d__%H_%M_%S)
mkdir -p /var/log/contrail/install_logs/
log_file=/var/log/contrail/install_logs/provision_$datetime_string.log
exec &> >(tee -a "$log_file")

start_time=$(date +"%s")

SOURCES_LIST="sources_list"
TESTBED="testbed.py"
CONTRAIL_PKG=""
INSTALL_SM_LITE="install_sm_lite"
CLEANUP_PUPPET_AGENT=""
NO_LOCAL_REPO=1
LOCAL_REPO_DIR=/opt/contrail/contrail_local_repo
CLUSTER_ID=""

function usage()
{
    set +x
    echo "Usage"
    echo ""
    echo "$0"
    echo -e "\t-h --help"
    echo -e "\t-c|--contrail-package <pkg>"
    echo -e "\t-t|--testbed <testbed.py>"
    echo -e  "\t-ni|--no-install-sm-lite"
    echo -e "\t-cp|--cleanup-puppet-agent"
    echo -e "\t-nr|--no-local-repo"
    echo -e "\t-cid|--cluster-id <cluster-id>"
    echo ""
    set -x
}

if [ "$#" -eq 0 ]; then
   usage
   exit
fi

while [[ $# > 0 ]]
do
key="$1"

case $key in
    -c|--contrail-package)
    CONTRAIL_PKG="$2"
    shift # past argument
    ;;
    -t|--testbed)
    TESTBED="$2"
    shift # past argument
    ;;
    -nr|--no-local-repo)
    NO_LOCAL_REPO=0
    ;;
    -ni|--no-install-sm-lite)
    INSTALL_SM_LITE=""
    ;;
    -cp|--no-cleanup-puppet-agent)
    CLEANUP_PUPPET_AGENT="cleanup_puppet_agent"
    ;;
    -cid|--cluster-id)
    CLUSTER_ID="$2"
    shift # past argument
    ;;
    -h|--help)
    usage
    exit
    ;;
    *)
            # unknown option
    echo "ERROR: unknown parameter $key"
    usage
    exit 1
    ;;
esac
shift # past argument or value
done

if [ "$TESTBED" == "" ] || [ "$CONTRAIL_PKG" == "" ]; then
   exit
fi

function unmount_contrail_local_repo()
{
    echo "INFO: Removing Contrail Local Repo - $LOCAL_REPO_DIR"
    # Remove local repo dir
    if [ -d $LOCAL_REPO_DIR ]; then
        rm -rf $LOCAL_REPO_DIR
    fi

    # Remove preference file
    if [ -f /etc/apt/preferences.d/contrail_local_repo ]; then
        rm -f /etc/apt/preferences.d/contrail_local_repo
    fi

    set +e
    grep "^deb file:$LOCAL_REPO_DIR ./" /etc/apt/sources.list
    exit_status=$?
    set -e
    if [ $exit_status == 0 ]; then
        sed -i "s#deb file:$LOCAL_REPO_DIR ./##g" /etc/apt/sources.list
        apt-get update
    fi
}

function mount_contrail_local_repo()
{
    set -e
    # check if package is available
    if [ ! -f "$CONTRAIL_PKG" ]; then
        echo "ERROR: $CONTRAIL_PKG : No Such file..."
        exit 2
    fi

    # mount package and create local repo
    echo "INFO: Creating Local Repo -- $LOCAL_REPO_DIR"
    set +e
    grep "^deb file:$LOCAL_REPO_DIR ./" /etc/apt/sources.list
    exit_status=$?
    set -e

    if [ $exit_status != 0 ]; then
        mkdir -p $LOCAL_REPO_DIR
        dpkg -x $CONTRAIL_PKG $LOCAL_REPO_DIR
        (cd $LOCAL_REPO_DIR && tar xfz opt/contrail/contrail_packages/*.tgz)
        (cd $LOCAL_REPO_DIR && DEBIAN_FRONTEND=noninteractive dpkg -i binutils_*.deb dpkg-dev_*.deb libdpkg-perl_*.deb make_*.deb patch_*.deb)
        (cd $LOCAL_REPO_DIR && dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz)
        datetime_string=$(date +%Y_%m_%d__%H_%M_%S)
        cp /etc/apt/sources.list /etc/apt/sources.list.contrail.$datetime_string
        echo >> /etc/apt/sources.list
        sed -i "1 i\deb file:$LOCAL_REPO_DIR ./" /etc/apt/sources.list
        cp -v /opt/contrail/contrail_server_manager/contrail_local_preferences /etc/apt/preferences.d/contrail_local_repo
        apt-get update
    fi
}

function cleanup_puppet_agent()
{
   set +e
   apt-get -y --purge autoremove puppet puppet-common hiera
   set -e
}

if [ "$CLEANUP_PUPPET_AGENT" != "" ]; then
   echo "--> Remove puppet agent, if it is present"
   cleanup_puppet_agent
fi

# Install sever manager 
if [ "$INSTALL_SM_LITE" != "" ]; then
   # Create a local repo from contrail-install packages
   # so packages from this repo gets preferred
   if [ $NO_LOCAL_REPO != 0 ]; then
       echo "--> Provision contrail local repo"
       mount_contrail_local_repo
       LOCAL_REPO_MOUNTED=1
   fi

   echo "--> Install server manager lite"
   pushd /opt/contrail/contrail_server_manager
   ./setup.sh --all --smlite --nowebui --nosm-mon
   popd
fi 

echo "--> Convert testbed.py to server manager entities"
# Convert testbed.py to server manager object json files
optional_args=""
if [ ! -z "$CLUSTER_ID" ]; then
    optional_args="--cluster-id $CLUSTER_ID"
fi
/opt/contrail/server_manager/client/testbed_parser.py --testbed ${TESTBED} --contrail-packages ${CONTRAIL_PKG} $optional_args

echo "--> Pre provision checks to make sure setup is ready for contrail provisioning"
# Precheck the targets to make sure that, ready for contrail provisioning
SERVER_MGR_IP=$(grep listen_ip_addr /opt/contrail/server_manager/sm-config.ini | grep -Po "listen_ip_addr = \K.*")
/opt/contrail/server_manager/client/preconfig.py --server-json server.json --server-manager-ip ${SERVER_MGR_IP}

# Remove contrail local repo if any
if [[ $LOCAL_REPO_MOUNTED -eq 1 ]]; then
    unmount_contrail_local_repo
fi

echo "--> Adding server manager objects to server manager database"
# Create package, cluster, server objects
server-manager add image -f image.json 
server-manager add cluster -f cluster.json 
server-manager add server -f server.json 

echo "--> Provisioning the cluster"
# Provision the cluster
CONTRAIL_PKG_ID=$(python -c "import json; fid = open('image.json', 'r'); contents = fid.read(); cjson = json.loads(contents); print cjson['image'][0]['id']")
CLUSTER_ID=$(python -c "import json; fid = open('cluster.json', 'r'); data = json.load(fid); fid.close(); print data['cluster'][0]['id']")
server-manager provision -F --cluster_id $CLUSTER_ID ${CONTRAIL_PKG_ID}

end_time=$(date +"%s")
diff=$(($end_time-$start_time))
echo "--> Provisioning is issued, and took $(($diff / 60)) minutes and $(($diff % 60)) seconds."
echo "--> Check provisioning status using /opt/contrail/contrail_server_manager/provision_status.sh"
