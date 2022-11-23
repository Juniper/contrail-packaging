#!/bin/bash -x

sku=$1
shift
to_build=${@:-'contrail-test-ci contrail-test'}
VERSION=$(cat controller/src/base/version.info)
TEST_ARTIFACT=${TEST_ARTIFACT:-$(readlink -f build/artifacts_extra/contrail-test-${VERSION}-*~$sku.tgz)}
TEST_CI_ARTIFACT=${TEST_CI_ARTIFACT:-$(readlink -f build/artifacts_extra/contrail-test-ci-*~$sku.tgz)}
FABRIC_UTILS_ARTIFACT=${FABRIC_UTILS_ARTIFACT:-$(readlink -f build/artifacts_extra/contrail-fabric-utils-*~$sku.tgz)}
CONTRAIL_PACKAGE_DEB=${CONTRAIL_PACKAGE_DEB:-$(readlink -f build/artifacts/contrail-install-packages*~${sku}_all.deb)}
DOCKER_IMAGE_EXPORT_PATH=${DOCKER_IMAGE_EXPORT_PATH:-$(readlink -f build/artifacts/)}
#IPADDRESS=${IPADDRESS:-$(ip a show docker0 | awk '/inet / {split ($2,a,"/"); print a[1]}')}
IPADDRESS="172.17.0.1"
export SSHPASS=c0ntrail123

clean_up() {
    for j in `docker images| tr -s ' ' | cut -d ' ' -f3 | grep -v IMAGE`
    do
        docker rmi -f $j
    done

    for i in `docker ps -a | tr -s ' ' | cut -d ' ' -f1 | grep -v CONTAINER`
    do
        docker rm -f $i
    done
}

tmp=$(mktemp -d)
tar zxv -C $tmp -f $TEST_CI_ARTIFACT contrail-test-ci/install.sh

for container in $to_build; do
    echo "Building container for $container..."
    tag=$(echo $container | sed -e 's/-/_/g')
    bash -x $tmp/contrail-test-ci/install.sh docker-build --test-artifact $TEST_ARTIFACT \
        --ci-artifact $TEST_CI_ARTIFACT --fab-artifact $FABRIC_UTILS_ARTIFACT \
        -u ssh://${IPADDRESS}/${CONTRAIL_PACKAGE_DEB} --export $DOCKER_IMAGE_EXPORT_PATH $container
    rc=$?
    if [[ $rc = 0 ]]; then
        touch ci_docker_build_${tag}_successful
    else
        echo "ERROR: Docker build for $container failed"
        break
    fi
done

clean_up
rm -rf $tmp
[[ $rc = 0 ]] && echo "Docker build completed!"
set +e
source /usr/local/jenkins/slave_scripts/ci-infra/ci-utils.sh
DOCKER_IMAGE=$(ls build/artifacts/docker-image-contrail-test-*.gz 2>/dev/null)
if [[ $? = 0 ]]; then
    retry sshpass -p c0ntrail123 rsync -acz --no-owner --no-group $DOCKER_IMAGE ci-admin@bfs.englab.juniper.ne:$CI_IMAGE_DIR
fi
