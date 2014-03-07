PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/common/debian=)

ifdef CONTRAIL_SKU
else
  CONTRAIL_SKU := "havana"
endif

PACKAGES = contrail-libs-deb \
	contrail-analytics-venv-deb \
	contrail-analytics-deb \
	contrail-dns-deb \
	contrail-vrouter-deb \
	contrail-vrouter-init-deb \
	contrail-config-venv-deb \
	contrail-config-deb \
	contrail-config-extension-deb \
	contrail-control-deb \
	contrail-api-lib-deb \
	contrail-nova-vif-deb \
	contrail-nodejs-deb \
	contrail-webui-deb \
	contrail-nodemgr-deb \
	contrail-setup-deb \
	ifmap-server-deb \
	supervisord-deb \
	contrail-openstack-deb \
	contrail-openstack-analytics-deb \
	contrail-openstack-config-deb \
	contrail-openstack-config-grizzly-deb \
	contrail-openstack-control-deb \
	contrail-openstack-database-deb \
	contrail-openstack-vrouter-deb \
	contrail-openstack-webui-deb \
	contrail-fabric-utils-deb \
	euca2ools-deb \
	python-boto-deb \
	contrail-openstack-dashboard-deb

all: ${PACKAGES}
	@echo "Build complete"

clean: $(PACKAGES:%-deb=%-clean)
	@echo "Clean"

ifmap-server-deb:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/ifmap-server)
	mkdir -p ${SB_TOP}/third_party
	cp -R ${SB_TOP}/third_party/ifmap-server ${BUILDDIR}
	cp -R ifmap-server/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

ifmap-server-clean:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/ifmap-server)
	rm -rf ${BUILDDIR}

contrail-install-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/contrail-install-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-install-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules binary && mv ../contrail-install-packages_*_all.deb ../debian/)
	@echo "Wrote: ${BUILDDIR}/../debian/contrail-install-packages_*_all.deb"

contrail-install-packages-clean:
	$(eval BUILDDIR=${SB_TOP}/build/contrail-install-packages)
	rm -rf ${BUILDDIR}

contrail-fabric-utils-deb:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/contrail-fabric-utils)
	cp -R ${SB_TOP}/third_party/fabric-utils ${BUILDDIR}
	cp -R contrail-fabric-utils/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-fabric-utils-clean:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/contrail-fabric-utils)
	rm -rf ${BUILDDIR}

euca2ools-deb:
	$(eval BUILDDIR=${SB_TOP}/third_party/euca2ools)
	cp -R euca2ools/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

euca2ools-clean:
	$(eval BUILDDIR=${SB_TOP}/third_party/euca2ools)
	rm -rf ${BUILDDIR}/debian

python-boto-deb:
	$(eval BUILDDIR=${SB_TOP}/third_party/python-boto)
	cp -R python-boto/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

python-boto-clean:
	$(eval BUILDDIR=${SB_TOP}/third_party/python-boto)
	rm -rf ${BUILDDIR}/debian

contrail-openstack-dashboard-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-openstack-dashboard)
	mkdir -p ${BUILDDIR}
	cp -R ${SB_TOP}/contrail-horizon/* ${BUILDDIR}
	cp -R contrail-openstack-dashboard/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-openstack-dashboard-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-openstack-dashboard)
	rm -rf ${BUILDDIR}

%-deb:
	(cd $(@:-deb=); fakeroot debian/rules binary)

%-clean:
	(cd $(@:-clean=); fakeroot debian/rules clean)

contrail-openstack-config-deb: contrail-config-deb
	if [ '${CONTRAIL_SKU}' != 'grizzly' ]; then \
		(cd $(@:-deb=); fakeroot debian/rules binary); \
	fi

contrail-openstack-config-grizzly-deb: contrail-config-deb
	if [ '${CONTRAIL_SKU}' = 'grizzly' ]; then \
		(cd $(@:-deb=); fakeroot debian/rules binary); \
	fi

contrail-vrouter-deb: contrail-libs-deb
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-vrouter)
	mkdir -p ${BUILDDIR}
	$(eval BUILDKVER=3.8.0-29-generic)
	$(eval DISTRODIR=/lib/modules/${BUILDKVER}/build)
	(cd contrail-vrouter; fakeroot debian/rules binary OSVER=${BUILDKVER})
	$(eval KVER=$(shell uname -r))
	$(eval BUILDKVER=3.2.0-58-generic)
	$(eval DISTRODIR=/lib/modules/${BUILDKVER}/build)
	if [ -d ${DISTRODIR} ] && [ '${KVER}' != '${BUILDKVER}' ]; then \
                (cd contrail-vrouter; fakeroot debian/rules clean); \
		(cd contrail-vrouter; fakeroot debian/rules binary OSVER=${BUILDKVER}); \
        fi
	$(eval BUILDKVER=3.2.0-51-generic)
	$(eval DISTRODIR=/lib/modules/${BUILDKVER}/build)
	if [ -d ${DISTRODIR} ] && [ '${KVER}' != '${BUILDKVER}' ]; then \
                (cd contrail-vrouter; fakeroot debian/rules clean); \
		(cd contrail-vrouter; fakeroot debian/rules binary OSVER=${BUILDKVER}); \
        fi

contrail-config-deb: contrail-config-venv-deb
contrail-analytics-deb: contrail-analytics-venv-deb
contrail-webui-deb: contrail-nodejs-deb
contrail-dns-deb: contrail-libs-deb
contrail-nodemgr-deb: contrail-api-lib-deb
contrail-openstack-control-deb: contrail-control-deb
contrail-openstack-vrouter-deb: contrail-vrouter-deb
contrail-openstack-analytics-deb: contrail-analytics-deb
contrail-openstack-webui-deb: contrail-webui-deb
