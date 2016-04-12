#!/bin/bash -x

to_build=${@:-'contrail-test contrail-test-ci'}
TEST_ARTIFACT=${TEST_ARTIFACT:-$(readlink -f build/artifacts_extra/contrail-test2-*~$1.tgz)}
TEST_CI_ARTIFACT=${TEST_CI_ARTIFACT:-$(readlink -f build/artifacts_extra/contrail-test-ci-*~$1.tgz)}
FABRIC_UTILS_ARTIFACT=${FABRIC_UTILS_ARTIFACT:-$(readlink -f build/artifacts_extra/contrail-fabric-utils-*~$1.tgz)}
CONTRAIL_PACKAGE_DEB=${CONTRAIL_PACKAGE_DEB:-$(readlink -f build/artifacts/contrail-install-packages*~$1_all.deb)}
DOCKER_IMAGE_EXPORT_PATH=${DOCKER_IMAGE_EXPORT_PATH:-$(readlink -f build/artifacts/)}
IPADDRESS=${IPADDRESS:-$(ip a show docker0 | awk '/inet / {split ($2,a,"/"); print a[1]}')}

tmp=$(mktemp -d)
tar zxv -C $tmp -f $TEST_CI_ARTIFACT contrail-test-ci/install.sh
for build in $to_build; do
    #Build docker
    bash $tmp/contrail-test-ci/install.sh docker-build --test-artifact $TEST_ARTIFACT \
	--ci-artifact $TEST_CI_ARTIFACT --fab-artifact $FABRIC_UTILS_ARTIFACT \
	-u ssh://${IPADDRESS}/${CONTRAIL_PACKAGE_DEB} --export $DOCKER_IMAGE_EXPORT_PATH $build
    [ $? = 0 ] && touch ci_docker_build_successful 
done
rm -fr $tmp
