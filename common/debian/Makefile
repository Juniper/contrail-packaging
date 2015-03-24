PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/common/debian=)
SRC_VER := $(shell cat $(SB_TOP)/controller/src/base/version.info)
BUILDTIME := $(shell date -u +%y%m%d%H%M)

SERIES=$(shell lsb_release -c -s)

# Skip unit-tests for building packages
export BUILD_ONLY := TRUE

ifdef CONTRAIL_SKU
  export CONTRAIL_SKU
else
  export CONTRAIL_SKU := havana
endif

CONTRAIL_OPENSTACK_CONFIG := contrail-openstack-config-deb

ifeq ($(CONTRAIL_SKU),juno)
    CONTRAIL_OPENSTACK := contrail-openstack-juno-deb
    CONTRAIL_HEAT := contrail-heat-deb
    CEILOMETER_PLUGIN := ceilometer-plugin-contrail-deb
endif

ifeq ($(CONTRAIL_SKU),icehouse)
    CONTRAIL_OPENSTACK := contrail-openstack-icehouse-deb
    CONTRAIL_HEAT := contrail-heat-deb
    CEILOMETER_PLUGIN := ceilometer-plugin-contrail-deb
    ifeq ($(SERIES),precise)
        CONTRAIL_VRDPDK_INIT := contrail-vrouter-dpdk-init-deb
        CONTRAIL_VRDPDK_KMOD := contrail-dpdk-kernel-modules-dkms-deb
        CONTRAIL_VRDPDK_BIN  := contrail-vrouter-dpdk
    endif
endif

ifeq ($(CONTRAIL_SKU),havana)
    CONTRAIL_OPENSTACK := contrail-openstack-deb
endif

KVERS ?= $(shell uname -r)
ifndef CONTRAIL_VERSION
VERSION = 
ifdef TAG
VERSION = $(SRC_VER)-$(TAG)
else
VERSION = $(SRC_VER)-$(BUILDTIME)
endif
else
VERSION = $(CONTRAIL_VERSION)
endif


PACKAGES = \
        contrail \
        ifmap-server \
        ifmap-python-client \
        contrail-nova-vif-deb \
        contrail-nova-networkapi-deb \
        contrail-vrouter-init-deb \
        contrail-vrouter-common-deb \
        $(CONTRAIL_VRDPDK_BIN) \
        $(CONTRAIL_VRDPDK_INIT) \
	contrail-web-core-deb \
	contrail-web-controller-deb \
	contrail-web-server-manager-deb \
	contrail-nodemgr-deb \
	contrail-setup-deb \
	$(CONTRAIL_OPENSTACK) \
	contrail-openstack-ha-deb \
	contrail-openstack-analytics-deb \
	$(CONTRAIL_OPENSTACK_CONFIG) \
	contrail-openstack-control-deb \
	contrail-openstack-database-deb \
	contrail-openstack-vrouter-deb \
	contrail-openstack-webui-deb \
	contrail-fabric-utils-deb \
	contrail-test-deb \
	libvirt-deb \
	contrail-openstack-dashboard-deb \
	contrail-ostack-dashboard-deb \
	$(CONTRAIL_HEAT) \
	neutron-plugin-contrail-deb \
	$(CEILOMETER_PLUGIN) \
	contrail-vmware-utils-deb \
	contrail-f5-deb \
	$(CONTRAIL_VRDPDK_KMOD)

all: ${PACKAGES}
	@echo "Build complete"

server-manager-all: contrail-server-manager-deb \
                    contrail-server-manager-client-deb \
                    contrail-server-manager-monitoring-deb \
                    contrail-server-manager-installer-deb

clean: $(PACKAGES:%-deb=%-clean)
	@echo "Clean"

list:
	@echo $(patsubst %-deb,%,$(PACKAGES))

package-%: debian-%
	$(eval PACKAGE := $(patsubst package-%,%,$@))
	@echo "Building package $(PACKAGE)"
	(cd $(SB_TOP)/build/packages/$(PACKAGE); fakeroot debian/rules binary)

debian-%:
	$(eval PACKAGE := $(patsubst debian-%,%,$@))
	mkdir -p $(SB_TOP)/build/packages/$(PACKAGE)
	cp -R $(SB_TOP)/tools/packages/debian/$(PACKAGE)/debian $(SB_TOP)/build/packages/$(PACKAGE)
	chmod u+x $(SB_TOP)/build/packages/$(PACKAGE)/debian/rules
	rm -f $(SB_TOP)/build/packages/$(PACKAGE)/debian/ifmap-server.upstart

clean-%:
	$(eval PACKAGE := $(patsubst clean-%,%,$@))
	rm -rf $(SB_TOP)/build/packages/$(PACKAGE)

KERNEL_VERSIONS := 3.8.0-29-generic 3.2.0-58-generic 3.2.0-51-generic 3.11.0-22-generic \
                   3.13.0-24-generic 3.8.0-31-generic 3.13.0-34-generic 3.13.0-35-generic \
                   3.13.0-40-generic

AVAILABLE_KERNEL_VERSIONS := $(foreach kname, $(KERNEL_VERSIONS), $(shell [ -d /lib/modules/$(kname)/build ] && echo $(kname)))

package-contrail: debian-contrail
	$(eval PACKAGE := contrail)
	@echo "Building package $(PACKAGE)"
	sed -i 's/VERSION/$(VERSION)/g' $(SB_TOP)/build/packages/$(PACKAGE)/debian/changelog
	sed -i 's/SERIES/$(SERIES)/g' $(SB_TOP)/build/packages/$(PACKAGE)/debian/changelog
# TODO: add BUILDDEP_SERIES after https://review.opencontrail.org/#/c/2640/
	sed -i '/BUILDDEP_SERIES/d' $(SB_TOP)/build/packages/$(PACKAGE)/debian/control
	(cd $(SB_TOP)/build/packages/$(PACKAGE); dpkg-buildpackage -uc -us -b -rfakeroot)
	chmod u+x $(SB_TOP)/build/packages/contrail/debian/rules.modules
	$(foreach kver, $(AVAILABLE_KERNEL_VERSIONS), \
            (cd $(SB_TOP)/vrouter; git clean -f -d); \
            (cd $(SB_TOP)/build/packages/$(PACKAGE); \
            fakeroot debian/rules.modules KVERS=$(kver) clean; \
            fakeroot debian/rules.modules KVERS=$(kver) binary-modules); )

package-contrail-vrouter-dpdk:
	(cd ${SB_TOP}; make CONTRAIL_VERSION=$(VERSION) -f tools/packages/packages.make package-contrail-vrouter-dpdk)

contrail-vrouter-dpdk: package-contrail-vrouter-dpdk
	@echo "Package contrail-vrouter-dpdk done"

package-ifmap-server: clean-ifmap-server debian-ifmap-server
	$(eval PACKAGE := $(patsubst package-%,%,$@))
	@echo "Building package $(PACKAGE)"
	(cd $(SB_TOP)/build/packages/$(PACKAGE); fakeroot debian/rules \
                get-orig-source)
	(cd $(SB_TOP)/build/packages/$(PACKAGE); dpkg-buildpackage \
                -uc -us -b -rfakeroot)

contrail: package-contrail
	@echo "Package contrail done"

ifmap-server: package-ifmap-server
	@echo "Package ifmap-server done"

ifmap-python-client: package-ifmap-python-client
	@echo "Package ifmap-python client done"

contrail-install-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-install-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-install-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	@echo "Wrote: ${BUILDDIR}/../contrail-install-packages_$(VERSION)~$(CONTRAIL_SKU)_all.deb"

contrail-server-manager-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-server-manager/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-server-manager-client-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-client)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-server-manager-client/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-server-manager-monitoring-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-monitoring)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-server-manager-monitoring/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-server-manager-installer-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-installer)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-server-manager-installer/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-install-packages-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-install-packages)
	rm -rf ${BUILDDIR}

contrail-server-manager-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager)
	rm -rf ${BUILDDIR}

contrail-server-manager-client-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-client)
	rm -rf ${BUILDDIR}

contrail-server-manager-installer-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-installer)
	rm -rf ${BUILDDIR}

contrail-server-manager-monitoring-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-monitoring)
	rm -rf ${BUILDDIR}

contrail-fabric-utils-deb:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/contrail-fabric-utils)
	cp -R ${SB_TOP}/third_party/fabric-utils ${BUILDDIR}
	cp -R contrail-fabric-utils/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	(mkdir -p $(SB_TOP)/build/tools/; cd ${SB_TOP}/third_party/; tar -cvzf $(SB_TOP)/build/tools/contrail-fabric-utils-$(VERSION)~$(CONTRAIL_SKU).tgz fabric-utils)
	@echo "Wrote: $(SB_TOP)/build/tools/contrail-fabric-utils-$(VERSION)~$(CONTRAIL_SKU).tgz"

contrail-fabric-utils-clean:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/contrail-fabric-utils)
	$(eval TGZ_FILE=$(SB_TOP)/build/tools/contrail-fabric-utils-$(VERSION)~$(CONTRAIL_SKU).tgz)
	rm -rf ${BUILDDIR}
	rm -rf ${TGZ_FILE}

contrail-test-deb:
	(mkdir -p $(SB_TOP)/build/tools/; cd ${SB_TOP}/third_party/; tar -cvzf $(SB_TOP)/build/tools/contrail-test-$(VERSION)~$(CONTRAIL_SKU).tgz contrail-test)
	@echo "Wrote: $(SB_TOP)/build/tools/contrail-test-$(VERSION)~$(CONTRAIL_SKU).tgz"

contrail-test-clean:
	$(eval TGZ_FILE=$(SB_TOP)/build/tools/contrail-test-$(VERSION)~$(CONTRAIL_SKU).tgz)
	rm -rf ${TGZ_FILE}

contrail-openstack-icehouse-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/tmp)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -R contrail-openstack/debian ${BUILDDIR}
	(cd ${BUILDDIR}; [ -f debian/control.icehouse.in ] && python \
	$(SB_TOP)/tools/packaging/tools/scripts/add_dependency_version.py \
	  --version $(VERSION) --file debian/control.icehouse.in ) || echo no control.icehouse.in
	cp ${BUILDDIR}/debian/control.icehouse ${BUILDDIR}/debian/control
	cp ${BUILDDIR}/debian/rules.icehouse ${BUILDDIR}/debian/rules
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-openstack-icehouse-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/tmp)
	rm -rf ${BUILDDIR}

contrail-openstack-juno-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/tmp)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -R contrail-openstack/debian ${BUILDDIR}
	(cd ${BUILDDIR}; [ -f debian/control.juno.in ] && python \
	$(SB_TOP)/tools/packaging/tools/scripts/add_dependency_version.py \
	  --version $(VERSION) --file debian/control.juno.in ) || echo no control.juno.in
	cp ${BUILDDIR}/debian/control.juno ${BUILDDIR}/debian/control
	cp ${BUILDDIR}/debian/rules.juno ${BUILDDIR}/debian/rules
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-openstack-juno-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/tmp)
	rm -rf ${BUILDDIR}

contrail-openstack-dashboard-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-openstack-dashboard) \
	mkdir -p ${BUILDDIR}/debian;
	cp -R ${SB_TOP}/contrail-horizon/* ${BUILDDIR};
	(cp -R contrail-openstack-dashboard/debian/${CONTRAIL_SKU}/* ${BUILDDIR}/debian);
	(cd ${BUILDDIR}; fakeroot debian/rules binary);

contrail-openstack-dashboard-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-openstack-dashboard)
	rm -rf ${BUILDDIR}

contrail-ostack-dashboard-deb:
	if [ '${CONTRAIL_SKU}' = 'havana' ]; then \
		$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-ostack-dashboard) \
		mkdir -p ${BUILDDIR}/debian; \
		cp -R ${SB_TOP}/distro/openstack/horizon/* ${BUILDDIR}; \
		cp -prf ${SB_TOP}/distro/openstack/horizon/.git ${BUILDDIR}; \
		(cp -R contrail-ostack-dashboard/debian/havana/* ${BUILDDIR}/debian); \
		(cd ${BUILDDIR}; fakeroot debian/rules binary); \
	fi
contrail-ostack-dashboard-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-ostack-dashboard)
	rm -rf ${BUILDDIR}

libvirt-deb:
	$(eval LIBDIR=${SB_TOP}/third_party/libvirt)
	$(eval BUILDDIR=${SB_TOP}/build/debian)
	if test -d ${LIBDIR}; then \
		rm -rf ${LIBDIR}/libvirt-0.9.8; \
		(cd ${LIBDIR}; dpkg-source -x libvirt_0.9.8-2ubuntu17.17.dsc); \
		(cd ${LIBDIR}; patch -p0 -i libvirt.ubuntu.patch); \
		(cd ${LIBDIR}; patch -p0 -i libvirt.ubuntu.test-disable.patch); \
		(cd ${LIBDIR}; patch -p0 -i libvirt.ubuntu.gnulib_test_disable.patch); \
		(cd ${LIBDIR}; patch -p0 -i libvirt_0.9.8_17.17.ubuntu.version.patch); \
		(cd ${LIBDIR}/libvirt-0.9.8; dpkg-buildpackage -b -uc); \
		(cd ${LIBDIR}; mv libvirt0_0.9.8-2ubuntu17.17_amd64.deb ${BUILDDIR}); \
		(cd ${LIBDIR}; mv libvirt-bin_0.9.8-2ubuntu17.17_amd64.deb ${BUILDDIR}); \
		(cd ${LIBDIR}; mv python-libvirt_0.9.8-2ubuntu17.17_amd64.deb ${BUILDDIR}); \
		(cd ${LIBDIR}; rm *.deb); \
	fi
libvirt-clean:
	$(eval LIBDIR=${SB_TOP}/third_party/libvirt)
	rm -rf ${LIBDIR}/libvirt-0.9.8

contrail-web-core-deb:
	cd $(SB_TOP)/contrail-webui-third-party && python fetch_packages.py
	(cd $(@:-deb=); fakeroot debian/rules clean)
	(cd $(@:-deb=); fakeroot debian/rules binary)

%-deb:
	(cd $(@:-deb=); [ -f debian/control.in ] && python \
         $(SB_TOP)/tools/packaging/tools/scripts/add_dependency_version.py \
           --version $(VERSION) --file debian/control.in ) || echo no control.in
	(cd $(@:-deb=); fakeroot debian/rules clean)
	(cd $(@:-deb=); fakeroot debian/rules binary)

%-clean:
	(cd $(@:-clean=); fakeroot debian/rules clean)
	(cd $(@:-clean=); [ -f debian/control.in ] && rm -f debian/control) || \
                || echo no control.in

neutron-plugin-contrail-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/neutron-plugin-contrail) \
	mkdir -p ${BUILDDIR}; \
	cp -R ${SB_TOP}/openstack/neutron_plugin/* ${BUILDDIR}; \
	cp -R ${SB_TOP}/tools/packages/debian/neutron-plugin-contrail/debian ${BUILDDIR}/debian; \
	sed -i 's/VERSION/$(VERSION)/g' ${BUILDDIR}/debian/changelog; \
	(cd ${BUILDDIR}; fakeroot debian/rules clean); \
	(cd ${BUILDDIR}; fakeroot debian/rules binary);

neutron-plugin-contrail-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/neutron-plugin-contrail) \
	rm -rf ${BUILDDIR};

ceilometer-plugin-contrail-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/ceilometer-plugin-contrail) \
	mkdir -p ${BUILDDIR}; \
	cp -R ${SB_TOP}/openstack/ceilometer_plugin/* ${BUILDDIR}; \
	cp -R ${SB_TOP}/tools/packages/debian/ceilometer-plugin-contrail/debian ${BUILDDIR}/debian; \
	sed -i 's/VERSION/$(VERSION)/g' ${BUILDDIR}/debian/changelog; \
	(cd ${BUILDDIR}; fakeroot debian/rules clean); \
	(cd ${BUILDDIR}; fakeroot debian/rules binary);

ceilometer-plugin-contrail-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/ceilometer-plugin-contrail) \
	rm -rf ${BUILDDIR};

contrail-heat-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-heat) \
	mkdir -p ${BUILDDIR}; \
	cp -R ${SB_TOP}/openstack/contrail-heat/* ${BUILDDIR}; \
	cp -R ${SB_TOP}/tools/packages/debian/contrail-heat/debian ${BUILDDIR}/debian; \
	sed -i 's/VERSION/$(VERSION)/g' ${BUILDDIR}/debian/changelog; \
	(cd ${BUILDDIR}; fakeroot debian/rules clean); \
	(cd ${BUILDDIR}; fakeroot debian/rules binary);

contrail-heat-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-heat) \
	rm -rf ${BUILDDIR};

contrail-vrouter-deb: contrail-libs-deb
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-vrouter)
	mkdir -p ${BUILDDIR}
	$(eval BUILDKVER=3.8.0-29-generic)
	$(eval DISTRODIR=/lib/modules/${BUILDKVER}/build)
	(cd contrail-vrouter; fakeroot debian/rules clean); \
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
	$(eval BUILDKVER=3.8.0-31-generic)
	$(eval DISTRODIR=/lib/modules/${BUILDKVER}/build)
	if [ -d ${DISTRODIR} ] && [ '${KVER}' != '${BUILDKVER}' ]; then \
		(cd contrail-vrouter; fakeroot debian/rules clean); \
		(cd contrail-vrouter; fakeroot debian/rules binary OSVER=${BUILDKVER}); \
	fi
	$(eval BUILDKVER=3.13.0-24-generic)
	$(eval DISTRODIR=/lib/modules/${BUILDKVER}/build)
	if [ -d ${DISTRODIR} ] && [ '${KVER}' != '${BUILDKVER}' ]; then \
		(cd contrail-vrouter; fakeroot debian/rules clean); \
		(cd contrail-vrouter; fakeroot debian/rules binary OSVER=${BUILDKVER}); \
	fi
	$(eval BUILDKVER=3.11.0-22-generic)
	$(eval DISTRODIR=/lib/modules/${BUILDKVER}/build)
	if [ -d ${DISTRODIR} ] && [ '${KVER}' != '${BUILDKVER}' ]; then \
		(cd contrail-vrouter; fakeroot debian/rules clean); \
		(cd contrail-vrouter; fakeroot debian/rules binary OSVER=${BUILDKVER}); \
	fi
	$(eval BUILDKVER=3.13.0-34-generic)
	$(eval DISTRODIR=/lib/modules/${BUILDKVER}/build)
	if [ -d ${DISTRODIR} ] && [ '${KVER}' != '${BUILDKVER}' ]; then \
		(cd contrail-vrouter; fakeroot debian/rules clean); \
		(cd contrail-vrouter; fakeroot debian/rules binary OSVER=${BUILDKVER}); \
	fi

dpdk-depends-packages-deb:
	(cd $(@:-deb=); fakeroot debian/rules clean)
	(cd $(@:-deb=); fakeroot debian/rules binary)

contrail-dpdk-kernel-modules-dkms-deb:
	(cd $(@:-deb=); sed -re "1 s/VERSION/$(VERSION)/" \
	    debian/changelog.in > debian/changelog)
	(cd $(@:-deb=); fakeroot debian/rules clean)
	(cd $(@:-deb=); fakeroot debian/rules binary)

contrail-dpdk-kernel-modules-dkms-clean:
	(cd $(@:-clean=); fakeroot debian/rules clean)
	(cd $(@:-clean=); rm -rf debian/changelog)

