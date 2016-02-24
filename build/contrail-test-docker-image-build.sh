#!/bin/bash

to_build=${@:-'contrail-test contrail-test-ci'}
TEST_ARTIFACT=${TEST_ARTIFACT:-$(readlink -f sb/build/artifacts_extra/docker-contrail-test-*~kilo.tgz)}
TEST_CI_ARTIFACT=${TEST_CI_ARTIFACT:-$(readlink -f sb/build/artifacts_extra/docker-contrail-test-ci-*~kilo.tgz)}
FABRIC_UTILS_ARTIFACT=${FABRIC_UTILS_ARTIFACT:-$(readlink -f sb/build/artifacts_extra/contrail-fabric-utils-*~kilo.tgz)}
CONTRAIL_PACKAGE_DEB_JUNO=${CONTRAIL_PACKAGE_DEB_JUNO:-$(readlink -f sb/build/artifacts/contrail-install-packages*~juno_all.deb)}
CONTRAIL_PACKAGE_DEB_KILO=${CONTRAIL_PACKAGE_DEB_KILO:-$(readlink -f sb/build/artifacts/contrail-install-packages*~kilo_all.deb)}
DOCKER_IMAGE_EXPORT_PATH=${DOCKER_IMAGE_EXPORT_PATH:-$(readlink -f sb/build/artifacts/)}
IPADDRESS=${IPADDRESS:-$(ip a show docker0 | awk '/inet / {split ($2,a,"/"); print a[1]}')}

tmp=$(mktemp -d)
tar zxv -C $tmp -f $TEST_CI_ARTIFACT contrail-test-ci/install.sh
for build in $to_build; do
    #Build for kilo
    bash $tmp/contrail-test-ci/install.sh docker-build --test-artifact $TEST_ARTIFACT \
	--ci-artifact $TEST_CI_ARTIFACT --fab-artifact $FABRIC_UTILS_ARTIFACT \
	-u ssh://${IPADDRESS}/${CONTRAIL_PACKAGE_DEB_KILO} --export $DOCKER_IMAGE_EXPORT_PATH $build
    #Build for juno
    bash $tmp/contrail-test-ci/install.sh docker-build --test-artifact $TEST_ARTIFACT \
	--ci-artifact $TEST_CI_ARTIFACT --fab-artifact $FABRIC_UTILS_ARTIFACT \
	-u ssh://${IPADDRESS}/${CONTRAIL_PACKAGE_DEB_JUNO} --export $DOCKER_IMAGE_EXPORT_PATH $build
done
rm -fr $tmp

