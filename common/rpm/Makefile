LIST_SOURCES        := list
PWD                 := ${CURDIR}
CPLANE_GIT_ROOT     := $(PWD:/tools/packaging/common/rpm=/controller)
PKGING_GIT_ROOT     := $(CPLANE_GIT_ROOT)/../tools
PKGING_DISTDIR      := $(PKGING_GIT_ROOT)/packaging/common/rpm
CPLANE_SRC_VER      := $(shell cat $(CPLANE_GIT_ROOT)/src/base/version.info)
BUILD_BASE          := $(CPLANE_GIT_ROOT)/build/package-build
BUILD_SRC           := $(BUILD_BASE)/SOURCES
PKGBLDDIR           := $(BUILD_BASE)/BUILD
DISTRO_PACKAGING    := $(CPLANE_GIT_ROOT)/../distro/python-venv-packaging
THIRDPARTY_DIR      := $(CPLANE_GIT_ROOT)/../third_party
DISTRO              := $(shell egrep -ho "Fedora|CentOS|Red Hat|SUSE" /etc/*-release | sort -u | head -n 1)
RPMBLDOPTS          := --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' -bb
SB_TOP              := $(CPLANE_GIT_ROOT)/..
SB_TOPDIR	    := --define '_sbtop $(SB_TOP)'
PREP = prep
PPREP = pprep

# Skip unit-tests for building packages
export BUILD_ONLY := TRUE

G_TAG :=
ifdef GIT_VER
 G_TAG := --define "_gitVer $(GIT_VER)"
endif 
ifdef TAG
 G_TAG += --define "_buildTag $(TAG)"
endif
ifdef FILE_LIST
 G_TAG += --define "_fileList $(FILE_LIST)"
endif
G_TAG += --define "_srcVer $(CPLANE_SRC_VER)"

ifdef  TAG
 TOOLS_VERSION := $(CPLANE_SRC_VER)-$(TAG)
else
 TOOLS_VERSION := $(CPLANE_SRC_VER)
endif

ifdef CONTRAIL_SKU
else
  CONTRAIL_SKU := "liberty"
endif
G_TAG += --define "_skuTag $(CONTRAIL_SKU)"

# If contrail-test repo is present, then it will be packaged (as tgz)
ifeq ($(wildcard $(SB_TOP)/third_party/contrail-test),)
    CONTRAIL_TEST :=
else
    CONTRAIL_TEST := contrail-test
endif

$(PPREP):
	@echo some $(PPREP) work ...
	mkdir -p $(SB_TOP)/build
	mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS,TOOLS}

$(PREP): $(PPREP)
	@echo some $(PREP) work ...
	@echo CPLANE_GIT_ROOT = $(CPLANE_GIT_ROOT)
	mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS,TOOLS}

contrail: $(PREP)
	@echo making rpm for contrail
	rpmbuild $(RPMBLDOPTS) $(SB_TOP)/tools/packages/rpm/contrail/contrail.spec $(G_TAG) $(SB_TOPDIR)

contrail-api-extension: $(PREP)
	@echo making rpm for contrail-api-extension
	rpmbuild $(RPMBLDOPTS) contrail-api-extension.spec $(G_TAG)

contrail-nova-networkapi: $(PREP)
	@echo making rpm for contrail-nova-networkapi
	rpmbuild $(RPMBLDOPTS) contrail-nova-networkapi.spec $(G_TAG)

contrail-api-lib: $(PREP)
	@echo making rpm for contrail-api-lib
	rpmbuild $(RPMBLDOPTS) contrail-api-lib.spec $(G_TAG)

contrail-nodemgr: $(PREP)
	@echo making rpm for contrail-nodemgr
	rpmbuild $(RPMBLDOPTS) contrail-nodemgr.spec  $(G_TAG)

contrail-interface-name: $(PREP)
	@echo making rpm for contrail-interface-name
	rpmbuild $(RPMBLDOPTS) contrail-interface-name.spec  $(G_TAG)

contrail-libs: $(PREP)
	@echo making rpm for contrail-libs
	rpmbuild $(RPMBLDOPTS) contrail-libs.spec $(G_TAG)

contrail-nova-vif: $(PREP)
	@echo making rpm for contrail-nova-vif
	rpmbuild $(RPMBLDOPTS) contrail-nova-vif.spec $(G_TAG)

neutron-plugin-contrail: $(PREP)
	@echo making rpm for neutron-plugin-plugin
	rpmbuild $(RPMBLDOPTS) neutron-plugin-contrail.spec $(G_TAG)

ceilometer-plugin-contrail: $(PREP)
	@echo making rpm for ceilometer-plugin-contrail
	rpmbuild $(RPMBLDOPTS) ceilometer-plugin-contrail.spec $(G_TAG)

contrail-heat: $(PREP)
	@echo making rpm for contrail-heat
	rpmbuild $(RPMBLDOPTS) contrail-heat.spec $(G_TAG)

contrail-setup: $(PREP)
	@echo making rpm for contrail-setup
	rpmbuild $(RPMBLDOPTS) contrail-setup.spec $(G_TAG)

# Contrail Cloudstack stuff
contrail-cloudstack-utils: $(PREP)
	@echo making rpm for contrail-cloudstack-utils
	rpmbuild $(RPMBLDOPTS) contrail-cloudstack-utils.spec $(G_TAG)

# Contrail Openstack stuff
contrail-openstack: $(PREP)
	@echo making rpm for contrail-openstack $(CONTRAIL_SKU)
	if [ "$(CONTRAIL_SKU)" == "juno" ]; then \
	    rpmbuild $(RPMBLDOPTS) contrail-openstack-juno.spec $(G_TAG) ;\
	else \
	    rpmbuild $(RPMBLDOPTS) contrail-openstack-liberty.spec $(G_TAG) ;\
	fi

contrail-openstack-ha: $(PREP)
	@echo making rpm for contrail-openstack-ha
	rpmbuild $(RPMBLDOPTS) contrail-openstack-ha.spec $(G_TAG)

contrail-openstack-analytics: $(PREP)
	@echo making rpm for contrail-openstack-analytics
	rpmbuild $(RPMBLDOPTS) contrail-openstack-analytics.spec $(G_TAG)

contrail-openstack-config: $(PREP)
	@echo making rpm for contrail-openstack-config
	if [ "$(CONTRAIL_SKU)" == "juno" ]; then \
	    rpmbuild $(RPMBLDOPTS) contrail-openstack-icehouse-config.spec $(G_TAG) ;\
	else \
	    rpmbuild $(RPMBLDOPTS) contrail-openstack-config-common.spec $(G_TAG) ;\
	fi

contrail-openstack-control: $(PREP)
	@echo making rpm for contrail-openstack-control
	rpmbuild $(RPMBLDOPTS) contrail-openstack-control.spec $(G_TAG)

contrail-openstack-database: $(PREP)
	@echo making rpm for contrail-openstack-database
	rpmbuild $(RPMBLDOPTS) contrail-openstack-database.spec $(G_TAG)

contrail-openstack-vrouter: $(PREP)
	@echo making rpm for contrail-openstack-vrouter
	rpmbuild $(RPMBLDOPTS) contrail-openstack-vrouter.spec  $(G_TAG)

contrail-openstack-webui: $(PREP)
	@echo making rpm for contrail-openstack-webui
	rpmbuild $(RPMBLDOPTS) contrail-openstack-webui.spec $(G_TAG)

contrail-openstack-storage: $(PREP)
	@echo making rpm for contrail-openstack-storage
	if [ "$(DISTRO)" == "CentOS" ]; then \
		rpmbuild $(RPMBLDOPTS) contrail-openstack-storage.spec $(G_TAG); \
	fi

contrail-openstack-all: contrail-openstack contrail-openstack-analytics contrail-openstack-config \
	contrail-openstack-control contrail-openstack-database contrail-openstack-vrouter \
	contrail-openstack-webui contrail-openstack-storage contrail-openstack-ha

contrail-web-core:
	@echo making rpm for contrail-web-core
	cd $(CPLANE_GIT_ROOT)/../contrail-webui-third-party && python fetch_packages.py
	cd $(CPLANE_GIT_ROOT)/../contrail-web-core && make package REPO=$(CPLANE_GIT_ROOT)/../contrail-web-core
	cp contrail-web-core.spec $(BUILD_BASE)/SPECS/
	cp ../control_files/contrailWebServer.sh $(BUILD_SRC)/
	cp ../control_files/contrailWebMiddleware.sh $(BUILD_SRC)/
	cp ../control_files/contrail-webui-middleware.service $(BUILD_SRC)/
	cp ../control_files/contrail-webui.service $(BUILD_SRC)/
	cp ../control_files/supervisord_webui.conf $(BUILD_SRC)/
	cp ../control_files/supervisor-webui.initd $(BUILD_SRC)/
	cp ../control_files/supervisor-webui.service $(BUILD_SRC)/
	cp ../control_files/contrail-webui.initd.supervisord $(BUILD_SRC)/
	cp ../control_files/contrail-webui-middleware.initd.supervisord $(BUILD_SRC)/
	cp ../control_files/contrail-webui.ini $(BUILD_SRC)/
	cp ../control_files/contrail-webui-middleware.ini $(BUILD_SRC)/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-web-core.spec $(G_TAG)

contrail-web-controller:
	@echo making rpm for contrail-web-controller
	cd $(CPLANE_GIT_ROOT)/../contrail-web-core && make package REPO=$(CPLANE_GIT_ROOT)/../contrail-web-controller,webController
	cp contrail-web-controller.spec $(BUILD_BASE)/SPECS/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-web-controller.spec $(G_TAG)

contrail-web-server-manager: $(PREP)
	@echo making rpm for contrail-web-server-manager
	cd $(CPLANE_GIT_ROOT)/../contrail-web-core && make package REPO=$(CPLANE_GIT_ROOT)/../contrail-web-server-manager,serverManager
	cp contrail-web-server-manager.spec $(BUILD_BASE)/SPECS/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-web-server-manager.spec $(G_TAG)

contrail-install-packages: $(PREP)
	@echo making rpm for contrail-install-packages
	rpmbuild $(RPMBLDOPTS) contrail-install-packages.spec  $(G_TAG)

contrail-installer-packages: $(PREP)
	@echo making rpm for contrail-installer-packages
	rpmbuild $(RPMBLDOPTS) contrail-installer-packages.spec  $(G_TAG)

contrail-packages: $(PREP)
	@echo making rpm for contrail-packages
	rpmbuild $(RPMBLDOPTS) contrail-packages.spec  $(G_TAG)

contrail-thirdparty-packages: $(PREP)
	@echo making rpm for contrail-thirdparty-packages
	rpmbuild $(RPMBLDOPTS) contrail-thirdparty-packages.spec  $(G_TAG)

contrail-dependent-packages: $(PREP)
	@echo making rpm for contrail-dependent-packages
	rpmbuild $(RPMBLDOPTS) contrail-dependent-packages.spec  $(G_TAG)

contrail-openstack-packages: $(PREP)
	@echo making rpm for contrail-openstack-packages
	rpmbuild $(RPMBLDOPTS) contrail-openstack-packages.spec  $(G_TAG)

contrail-database: $(PREP)
	@echo making rpm for contrail-database
	cp contrail-database.spec $(BUILD_BASE)/SPECS/
	cp ../control_files/contrail-database.initd $(BUILD_SRC)/
	cp ../control_files/kafka.initd $(BUILD_SRC)/
	cp ../control_files/supervisord_database.conf $(BUILD_SRC)/
	cp ../control_files/supervisord_contrail_database.initd $(BUILD_SRC)/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-database.spec $(G_TAG)

contrail-database-common: $(PREP)
	@echo making rpm for contrail-database-common
	rpmbuild $(RPMBLDOPTS) contrail-database-common.spec $(G_TAG)

contrail-server-manager: $(PREP)
	@echo making rpm for contrail-server-manager
	cp contrail-server-manager.spec $(BUILD_BASE)/SPECS/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-server-manager.spec $(G_TAG)

contrail-server-manager-installer: $(PREP)
	@echo making rpm for contrail-server-manager-installer
	cp contrail-server-manager-installer.spec $(BUILD_BASE)/SPECS/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-server-manager-installer.spec $(G_TAG)

contrail-server-manager-client: $(PREP)
	@echo making rom for contrail-server-manager-client
	cp contrail-server-manager-client.spec $(BUILD_BASE)/SPECS/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-server-manager-client.spec $(G_TAG)

contrail-vrouter-init: $(PREP)
	@echo making rpm for contrail-vrouter-init
	rpmbuild $(RPMBLDOPTS) contrail-vrouter-init.spec $(G_TAG)

contrail-vrouter-common: $(PREP)
	@echo making rpm for contrail-vrouter-common
	rpmbuild $(RPMBLDOPTS) contrail-vrouter-common.spec $(G_TAG)

contrail-fabric-utils: $(PPREP)
	@echo making rpm for contrail-fabric-utils
	rpmbuild $(RPMBLDOPTS) fabric-utils.spec $(G_TAG)
	cd $(THIRDPARTY_DIR) && tar -cvzf $(BUILD_BASE)/TOOLS/contrail-fabric-utils-$(TOOLS_VERSION).tgz fabric-utils

contrail-test:
	@echo making tgz for contrail-test
	cd $(THIRDPARTY_DIR) && tar -cvzf $(BUILD_BASE)/TOOLS/contrail-test-$(TOOLS_VERSION).tgz contrail-test

contrail-puppet: $(PREP)
	@echo making rpm for contrail-puppet
	rpmbuild $(RPMBLDOPTS) $(SB_TOP)/tools/contrail-server-manager/build/rpm/contrail-puppet.spec  $(G_TAG)

contrail-puppet-tgz:
	( [ -f $(SB_TOP)/build/artifacts_extra/contrail-puppet_$(TOOLS_VERSION)~$(CONTRAIL_SKU).tar.gz ] && \
	  rm -f $(SB_TOP)/build/artifacts_extra/contrail-puppet_$(TOOLS_VERSION)~$(CONTRAIL_SKU).tar.gz ) ; \
	( rm -rf $(SB_TOP)/build/contrail-puppet-tgz-builddir/ ) ; \
	( mkdir -p $(SB_TOP)/build/artifacts_extra/) ;\
	( mkdir -p $(SB_TOP)/build/contrail-puppet-tgz-builddir/ ); \
	( [ -d $(SB_TOP)/tools/puppet/ ] && [ -d $(SB_TOP)/tools/puppet-third-party/ ] && \
	    cp -a $(SB_TOP)/tools/puppet/ $(SB_TOP)/build/contrail-puppet-tgz-builddir/ && \
	    cp -rp $(SB_TOP)/tools/puppet-third-party/* $(SB_TOP)/build/contrail-puppet-tgz-builddir/puppet/contrail/environment/modules/ && \
	    cd $(SB_TOP)/build/contrail-puppet-tgz-builddir/puppet/ && \
	    tar -czf $(SB_TOP)/build/artifacts_extra/contrail-puppet_$(TOOLS_VERSION)~$(CONTRAIL_SKU).tar.gz * ) || echo -e \
	    "\n\nWARNING: $(SB_TOP)/tools/puppet/ or $(SB_TOP)/tools/puppet-third-party is not found; Skipping contrail-puppet\n\n"

contrail-sm-ansible:
	( [ -f $(SB_TOP)/build/artifacts_extra/contrail-sm-ansible_$(TOOLS_VERSION).tar.gz ] && \
	  rm -f $(SB_TOP)/build/artifacts_extra/contrail-sm-ansible_$(TOOLS_VERSION).tar.gz ) ;\
	(mkdir -p $(SB_TOP)/build/artifacts_extra/) ;\
	( [ -d $(SB_TOP)/tools/sm-ansible/ ] && \
	    cd $(SB_TOP)/tools/sm-ansible/ && \
	    tar -czf $(SB_TOP)/build/artifacts_extra/contrail-sm-ansible_$(TOOLS_VERSION).tar.gz * ) || \
	    echo "WARNING: $(SB_TOP)/tools/sm-ansible/ not found; Skipping contrail-sm-ansible"

NEUTRON_PLUGIN = neutron-plugin-contrail
CONTRAIL_HEAT = contrail-heat
CEILOMETER_PLUGIN = ceilometer-plugin-contrail

all: $(PREP) contrail \
       contrail-interface-name \
       contrail-nodemgr contrail-setup contrail-openstack-all \
       contrail-web-core contrail-web-controller contrail-database \
	   contrail-database-common \
       ${NEUTRON_PLUGIN} ${CONTRAIL_HEAT} ${CEILOMETER_PLUGIN} \
       contrail-vrouter-init contrail-vrouter-common contrail-nova-networkapi \
       contrail-fabric-utils ${CONTRAIL_TEST} contrail-puppet contrail-sm-ansible \
       contrail-puppet-tgz

server-manager-all: contrail-server-manager contrail-server-manager-client \
    contrail-web-server-manager

clean:
	@echo clean

