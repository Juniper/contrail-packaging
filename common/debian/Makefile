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

# If contrail-test repo is present, then it will be packaged (as tgz)
# Maybe be over-ridden based on CONTRAIL_SKU
ifeq ($(wildcard $(SB_TOP)/third_party/contrail-test),)
    CONTRAIL_TEST :=
else
    CONTRAIL_TEST := contrail-test-deb
endif

# Ditto for contrail-test-ci repo
ifeq ($(wildcard ${SB_TOP}/tools/contrail-test-ci),)
    CONTRAIL_TEST_CI :=
else
    CONTRAIL_TEST_CI := contrail-test-ci-deb
endif

CEILOMETER_PLUGIN := ceilometer-plugin-contrail-deb

ifeq ($(CONTRAIL_SKU), vcenter)
    # We do not build contrail-test-ci tarball for vcenter
    CONTRAIL_TEST_CI :=
    CEILOMETER_PLUGIN :=
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
	ukai-deb \
	ifmap-server \
        ifmap-python-client \
        contrail-nova-vif-deb \
        contrail-nova-networkapi-deb \
	contrail-vrouter-init-deb \
	contrail-vrouter-common-deb \
	contrail-vrouter-dpdk \
	contrail-vrouter-dpdk-init \
	contrail-web-core-deb \
	contrail-web-controller-deb \
	contrail-web-server-manager-deb \
	contrail-setup-deb \
	contrail-openstack-deb \
	contrail-openstack-ha-deb \
	contrail-openstack-analytics-deb \
	contrail-openstack-config-deb \
	contrail-openstack-control-deb \
	contrail-database-common-deb \
	contrail-openstack-database-deb \
	contrail-openstack-vrouter-deb \
	contrail-openstack-webui-deb \
	contrail-fabric-utils-deb \
	$(CONTRAIL_TEST_CI) \
	$(CONTRAIL_TEST) \
	libvirt-deb \
	contrail-openstack-dashboard-deb \
	contrail-ostack-dashboard-deb \
	contrail-heat-deb \
	neutron-plugin-contrail-deb \
	$(CEILOMETER_PLUGIN) \
	contrail-f5-deb \
	contrail-vmware-utils-deb \
	contrail-puppet-deb \
	$(CONTRAIL_VCENTER_PLUGIN)

all: ${PACKAGES}
	@echo "Build complete"

PACKAGES_VMWARE = \
        contrail \
	ukai-deb \
        ifmap-server \
        ifmap-python-client \
        contrail-vrouter-init-deb \
        contrail-vrouter-common-deb \
        $(CONTRAIL_VRDPDK_BIN) \
        $(CONTRAIL_VRDPDK_INIT) \
        contrail-web-core-deb \
        contrail-web-controller-deb \
        contrail-web-server-manager-deb \
        contrail-setup-deb \
        contrail-openstack-ha-deb \
        contrail-openstack-analytics-deb \
        contrail-openstack-control-deb \
	contrail-database-common-deb \
        contrail-openstack-database-deb \
        contrail-openstack-webui-deb \
        contrail-fabric-utils-deb \
        $(CONTRAIL_TEST_CI) \
        $(CONTRAIL_TEST) \
        libvirt-deb \
	contrail-f5-deb \
        contrail-vmware-config-deb \
        contrail-vmware-utils-deb \
        contrail-vmware-vrouter-deb \
	contrail-install-vcenter-plugin

all_vmware: ${PACKAGES_VMWARE}
	@echo "Build complete"

# Building vcenter-plugin 
contrail-install-vcenter-plugin:
	(cd vcenter-plugin && make all && \
    cd build && cp contrail-install-vcenter-plugin*.deb $(SB_TOP)/build/debian)
#end vcenter-plugin build

server-manager-all: contrail-server-manager-deb \
                    contrail-server-manager-lite-deb \
                    contrail-server-manager-client-deb \
                    contrail-server-manager-cliff-client-deb \
                    contrail-server-manager-installer-deb \
                    contrail-server-manager-client-tgz

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
	cp -R $(SB_TOP)/tools/packages/utils $(SB_TOP)/build/packages/$(PACKAGE)/debian/
	chmod u+x $(SB_TOP)/build/packages/$(PACKAGE)/debian/rules
	rm -f $(SB_TOP)/build/packages/$(PACKAGE)/debian/ifmap-server.upstart

clean-%:
	$(eval PACKAGE := $(patsubst clean-%,%,$@))
	rm -rf $(SB_TOP)/build/packages/$(PACKAGE)

KERNEL_VERSIONS := 3.8.0-29-generic 3.2.0-58-generic 3.2.0-51-generic 3.11.0-22-generic \
                   3.13.0-24-generic 3.8.0-31-generic 3.13.0-34-generic 3.13.0-35-generic \
                   3.13.0-40-generic 3.13.0-83-generic 3.13.0-85-generic 4.4.0-34-generic \
                   4.4.0-38-generic

AVAILABLE_KERNEL_VERSIONS := $(foreach kname, $(KERNEL_VERSIONS), $(shell [ -d /lib/modules/$(kname)/build ] && echo $(kname)))

package-contrail: debian-contrail
	$(eval PACKAGE := contrail)
	@echo "Building package $(PACKAGE)"
	sed -i 's/VERSION/$(VERSION)/g' $(SB_TOP)/build/packages/$(PACKAGE)/debian/changelog
	sed -i 's/SERIES/$(SERIES)/g' $(SB_TOP)/build/packages/$(PACKAGE)/debian/changelog
	sed -i '/BUILDDEP_SERIES/d' $(SB_TOP)/build/packages/$(PACKAGE)/debian/control
	# Append series specific depends
	(cd $(SB_TOP)/build/packages/$(PACKAGE)/debian; sed -i '/SUPERVISORDEP_SERIES/r supervisordep.$(SERIES)' control)
	sed -i '/SUPERVISORDEP_SERIES/d' $(SB_TOP)/build/packages/$(PACKAGE)/debian/control
	# Append series specific install files
	$(eval CONTRAIL_INSTALL_SERIES := $(shell find $(SB_TOP)/build/packages/$(PACKAGE)/debian/ -name '*.install.$(SERIES)'))
	$(foreach series_fname, $(CONTRAIL_INSTALL_SERIES), \
			(cd $(SB_TOP)/build/packages/$(PACKAGE)/debian;\
			sed -i '/INSTALL_SERIES/r $(series_fname)' $(patsubst %.$(SERIES),%,$(series_fname))); )
	$(eval CONTRAIL_INSTALL := $(shell find $(SB_TOP)/build/packages/$(PACKAGE)/debian/ -name '*.install'))
	$(foreach install_fname, $(CONTRAIL_INSTALL), \
			(cd $(SB_TOP)/build/packages/$(PACKAGE)/debian;\
			sed -i '/INSTALL_SERIES/d' $(install_fname)); )
	# Append series specific dirs
	$(eval CONTRAIL_DIRS_SERIES := $(shell find $(SB_TOP)/build/packages/$(PACKAGE)/debian/ -name '*.dirs.$(SERIES)'))
	$(foreach series_dirname, $(CONTRAIL_DIRS_SERIES), \
			(cd $(SB_TOP)/build/packages/$(PACKAGE)/debian;\
			sed -i '/DIRS_SERIES/r $(series_dirname)' $(patsubst %.$(SERIES),%,$(series_dirname))); )
	$(eval CONTRAIL_DIRS := $(shell find $(SB_TOP)/build/packages/$(PACKAGE)/debian/ -name '*.dirs'))
	$(foreach dir_fname, $(CONTRAIL_DIRS), \
			(cd $(SB_TOP)/build/packages/$(PACKAGE)/debian;\
			sed -i '/DIRS_SERIES/d' $(dir_fname)); )
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

contrail-installer-packages: contrail-installer-packages-deb
contrail-installer-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-installer-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-installer-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	@echo "Wrote: ${BUILDDIR}/../contrail-installer-packages_$(VERSION)~$(CONTRAIL_SKU)_all.deb"

contrail-install-packages: contrail-install-packages-deb
contrail-install-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-install-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-install-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	@echo "Wrote: ${BUILDDIR}/../contrail-install-packages_$(VERSION)~$(CONTRAIL_SKU)_all.deb"

contrail-packages: contrail-packages-deb
contrail-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	@echo "Wrote: ${BUILDDIR}/../contrail-packages_$(VERSION)~$(CONTRAIL_SKU)_all.deb"

contrail-dependent-packages: contrail-dependent-packages-deb
contrail-dependent-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-dependent-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-dependent-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	@echo "Wrote: ${BUILDDIR}/../contrail-dependent-packages_$(VERSION)~$(CONTRAIL_SKU)_all.deb"

contrail-openstack-packages: contrail-openstack-packages-deb
contrail-openstack-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-openstack-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-openstack-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	@echo "Wrote: ${BUILDDIR}/../contrail-openstack-packages_$(VERSION)~$(CONTRAIL_SKU)_all.deb"

contrail-thirdparty-packages: contrail-thirdparty-packages-deb
contrail-thirdparty-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-thirdparty-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-thirdparty-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	@echo "Wrote: ${BUILDDIR}/../contrail-thirdparty-packages_$(VERSION)~$(CONTRAIL_SKU)_all.deb"

contrail-server-manager-client-tgz:
	(mkdir -p $(SB_TOP)/build/tools/; cd ${SB_TOP}/tools/contrail-server-manager/src/client/ && tar -czf $(SB_TOP)/build/tools/contrail-server-manager-client-$(VERSION)~$(CONTRAIL_SKU).tgz *)
        @echo "Wrote: $(SB_TOP)/build/tools/contrail-server-manager-client-$(VERSION)~$(CONTRAIL_SKU).tgz"

contrail-server-manager-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-server-manager/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-server-manager-lite-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-lite)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-server-manager-lite/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-server-manager-client-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-client)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-server-manager-client/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

contrail-server-manager-cliff-client-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-server-manager-cliff-client)
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	@echo "$(VERSION)" > $(SB_TOP)/tools/contrail-server-manager/src/smgr_cliff_client/contrail_version.txt
	@echo "$(CONTRAIL_SKU)" > $(SB_TOP)/tools/contrail-server-manager/src/smgr_cliff_client/contrail_sku.txt
	cp -ar ${SB_TOP}/tools/packaging/common/debian/contrail-server-manager-cliff-client/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	(mkdir -p $(SB_TOP)/build/tools/; cp $(SB_TOP)/tools/contrail-server-manager/src/smgr_cliff_client/dist/servermanagercli-$(VERSION)-$(CONTRAIL_SKU).tar.gz $(SB_TOP)/build/tools/contrail-server-manager-cliff-client-$(VERSION)~$(CONTRAIL_SKU).tgz)

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

contrail-fabric-utils-deb:
	$(eval PACKAGE := contrail-fabric-utils)
	$(eval BUILDDIR=${SB_TOP}/build/third_party/$(PACKAGE))
	cp -R ${SB_TOP}/third_party/fabric-utils ${BUILDDIR}
	cp -R $(PACKAGE)/debian ${BUILDDIR}/debian
	$(eval DEFAULT_CONTROL_IN := control.in)
	@echo "Default control file: $(DEFAULT_CONTROL_IN)"
	@echo "Looking for control file: control.$(SERIES).in"
	$(eval SERIES_CONTROL_IN := $(shell [ -f $(PACKAGE)/debian/control.$(SERIES).in ] && echo 'control.$(SERIES).in'  || echo $(DEFAULT_CONTROL_IN)))
	@echo "Looking for control file: control.$(SERIES).$(CONTRAIL_SKU).in"
	$(eval CONTROL_IN := $(shell [ -f $(PACKAGE)/debian/control.$(SERIES).$(CONTRAIL_SKU).in ] && echo 'control.$(SERIES).$(CONTRAIL_SKU).in' || echo $(SERIES_CONTROL_IN)))
	@echo "Using control file: $(CONTROL_IN)"
	cp ${BUILDDIR}/debian/${CONTROL_IN} ${BUILDDIR}/debian/control
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	(mkdir -p $(SB_TOP)/build/tools/; cd ${SB_TOP}/third_party/; tar -cvzf $(SB_TOP)/build/tools/contrail-fabric-utils-$(VERSION)~$(CONTRAIL_SKU).tgz fabric-utils)
	@echo "Wrote: $(SB_TOP)/build/tools/contrail-fabric-utils-$(VERSION)~$(CONTRAIL_SKU).tgz"

contrail-fabric-utils-clean:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/contrail-fabric-utils)
	$(eval TGZ_FILE=$(SB_TOP)/build/tools/contrail-fabric-utils-$(VERSION)~$(CONTRAIL_SKU).tgz)
	rm -rf ${BUILDDIR}
	rm -rf ${TGZ_FILE}

contrail-test-ci-deb:
	@mkdir -p $(SB_TOP)/build/tools
	(cd ${SB_TOP}/tools && tar -cvzf $(SB_TOP)/build/artifacts_extra/contrail-test-ci-$(VERSION)~$(CONTRAIL_SKU).tgz contrail-test-ci)
	@echo "Wrote: $(SB_TOP)/build/artifacts_extra/contrail-test-ci-$(VERSION)~$(CONTRAIL_SKU).tgz"

contrail-test-deb:
	@mkdir -p $(SB_TOP)/build/tools
	(cd ${SB_TOP}/third_party && tar -cvzf $(SB_TOP)/build/tools/contrail-test-$(VERSION)~$(CONTRAIL_SKU).tgz contrail-test)
	@echo "Wrote: $(SB_TOP)/build/tools/contrail-test-$(VERSION)~$(CONTRAIL_SKU).tgz"

contrail-test-clean:
	$(eval TGZ_FILE=$(SB_TOP)/build/tools/contrail-test-$(VERSION)~$(CONTRAIL_SKU).tgz)
	rm -rf ${TGZ_FILE}

contrail-test-ci-clean:
	$(eval TGZ_FILE=$(SB_TOP)/build/artifacts_extra/contrail-test-ci-$(VERSION)~$(CONTRAIL_SKU).tgz)
	rm -rf ${TGZ_FILE}

contrail-openstack-dashboard-deb:
	if [ -d ${SB_TOP}/contrail-horizon ]; then \
		$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-openstack-dashboard) \
		mkdir -p ${BUILDDIR}/debian; \
		cp -R ${SB_TOP}/contrail-horizon/* ${BUILDDIR}; \
		(cp -R contrail-openstack-dashboard/debian/${CONTRAIL_SKU}/* ${BUILDDIR}/debian); \
		(cd ${BUILDDIR}; fakeroot debian/rules binary); \
	fi

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
	$(eval PACKAGE := $(@:-deb=))
	$(eval BUILDDIR=${SB_TOP}/build/debian/packaging/$(PACKAGE))
	rm -rf ${BUILDDIR}
	mkdir -p ${BUILDDIR}/debian
	cp -R $(PACKAGE)/debian ${BUILDDIR}
	$(eval DEFAULT_CONTROL := control)
	@echo "Default control file: $(DEFAULT_CONTROL)"
	@echo "Looking for control file: control.in"
	$(eval DEFAULT_CONTROL_IN := $(shell [ -f $(PACKAGE)/debian/control.in ] && echo 'control.in'  || echo $(DEFAULT_CONTROL)))
	@echo "Looking for control file: control.$(SERIES).in"
	$(eval SERIES_CONTROL_IN := $(shell [ -f $(PACKAGE)/debian/control.$(SERIES).in ] && echo 'control.$(SERIES).in'  || echo $(DEFAULT_CONTROL_IN)))
	@echo "Looking for control file: control.$(SERIES).$(CONTRAIL_SKU).in"
	$(eval CONTROL_IN := $(shell [ -f $(PACKAGE)/debian/control.$(SERIES).$(CONTRAIL_SKU).in ] && echo 'control.$(SERIES).$(CONTRAIL_SKU).in' || echo $(SERIES_CONTROL_IN)))
	@echo "Using control file: $(CONTROL_IN)"
	(cd ${BUILDDIR}; python $(SB_TOP)/tools/packaging/tools/scripts/add_dependency_version.py \
		--version $(VERSION) --file debian/$(CONTROL_IN) --outfile debian/control)
	$(eval DEFAULT_RULES := rules)
	@echo "Default rules file: $(DEFAULT_RULES)"
	@echo "Looking for rules file: rules.$(SERIES)"
	$(eval SERIES_RULES := $(shell [ -f $(PACKAGE)/debian/rules.$(SERIES) ] && echo 'rules.$(SERIES)' || echo $(DEFAULT_RULES)))
	@echo "Looking for rules file: rules.$(SERIES).$(CONTRAIL_SKU)"
	$(eval RULES := $(shell [ -f $(PACKAGE)/debian/rules.$(SERIES).$(CONTRAIL_SKU) ] && echo 'rules.$(SERIES).$(CONTRAIL_SKU)' || echo $(SERIES_RULES)))
	@echo "Using rules file: $(RULES)"
	cp $(PACKAGE)/debian/$(RULES) ${BUILDDIR}/debian/rules
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

%-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/packaging/$(@:-clean=))
	rm -rf ${BUILDDIR}

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
	if [ -d ${SB_TOP}/openstack/ceilometer_plugin ]; then \
		$(eval BUILDDIR=${SB_TOP}/build/debian/ceilometer-plugin-contrail) \
		mkdir -p ${BUILDDIR}; \
		cp -R ${SB_TOP}/openstack/ceilometer_plugin/* ${BUILDDIR}; \
		cp -R ${SB_TOP}/tools/packages/debian/ceilometer-plugin-contrail/debian ${BUILDDIR}/debian; \
		sed -i 's/VERSION/$(VERSION)/g' ${BUILDDIR}/debian/changelog; \
		(cd ${BUILDDIR}; fakeroot debian/rules clean); \
		(cd ${BUILDDIR}; fakeroot debian/rules binary); \
	fi

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

ukai-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/ukai) \
	mkdir -p ${BUILDDIR}; \
	cp -R ${SB_TOP}/ukai/* ${BUILDDIR}; \
	cd ${BUILDDIR}; \
	make deb

ukai-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/ukai) \
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

contrail-puppet-deb:
	mkdir -p $(SB_TOP)/build/debian/$(@:-deb=)
	cp -R $(SB_TOP)/tools/contrail-server-manager/build/debian/contrail-puppet/debian $(SB_TOP)/build/debian/$(@:-deb=)/
	chmod u+x $(SB_TOP)/build/debian/$(@:-deb=)/debian/rules
	(cd $(SB_TOP)/build/debian/$(@:-deb=); fakeroot debian/rules clean)
	(cd $(SB_TOP)/build/debian/$(@:-deb=); fakeroot debian/rules binary)

contrail-puppet-clean:
	(cd $(SB_TOP)/build/debian/$(@:-clean=); fakeroot debian/rules clean)
	(rm -rf $(SB_TOP)/build/debian/$(@:-clean=))
