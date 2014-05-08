LIST_SOURCES        := list
REPOBIN             := repo
CPLANE_GIT_ROOT     := $(shell $(REPOBIN) info contrail-controller|grep 'Mount path'|cut -f3 -d" ")
PKGING_GIT_ROOT     := $(CPLANE_GIT_ROOT)/../tools
PKGING_DISTDIR      := $(PKGING_GIT_ROOT)/packaging/common/rpm
CPLANE_SRC_VER      := $(shell cat $(CPLANE_GIT_ROOT)/src/base/version.info)
BUILD_BASE          := $(CPLANE_GIT_ROOT)/build/package-build
BUILD_SRC           := $(BUILD_BASE)/SOURCES
PKGBLDDIR           := $(BUILD_BASE)/BUILD
LOCAL_PY_PTH        := $(BUILD_BASE)/BUILD/python2.7
LOCAL_PY            := $(LOCAL_PY_PTH)/bin/python
LOCAL_PY_BLD        := $(BUILD_BASE)/BUILDROOT/Python-2.7.5
LOCAL_PY_DEF        := --define "_python_path $(LOCAL_PY_PTH)"
DISTRO_PACKAGING    := $(CPLANE_GIT_ROOT)/../distro/python-venv-packaging
RPM_PY              := --define "__python $(LOCAL_PY)"
DISTRO              := $(shell egrep -o "Fedora|CentOS|Ubuntu" /etc/issue)
RPMBLDOPTS          := --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' -bb
PREP = prep
PPREP = pprep

# Skip unit-tests for building packages
BUILD_ONLY := TRUE

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

ifdef CONTRAIL_SKU
else
  CONTRAIL_SKU := "grizzly"
endif
G_TAG += --define "_skuTag $(CONTRAIL_SKU)"


$(PPREP):
	@echo some $(PPREP) work ...
	mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS,TOOLS}

$(PREP): $(PPREP)
	@echo some $(PREP) work ...
	@echo CPLANE_GIT_ROOT = $(CPLANE_GIT_ROOT)
	mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS,TOOLS}

localpy: $(LOCAL_PY)
$(LOCAL_PY): $(PPREP)
	@echo Compiling python
	if [ ! -d $(PKGBLDDIR)/packaging ]; then mkdir $(PKGBLDDIR)/packaging && \
		cd $(PKGBLDDIR)/packaging && cp -ar $(DISTRO_PACKAGING)/archives .; \
	fi 
	if [ ! -f $(LOCAL_PY) ]; then mkdir  -p $$( dirname $(LOCAL_PY_BLD) ) && \
		tar xjvf $(DISTRO_PACKAGING)/archives/Python-2.7.5.tar.bz2 \
		-C $$( dirname $(LOCAL_PY_BLD) ) && cd $(LOCAL_PY_BLD) && \
		./configure --prefix=$(LOCAL_PY_PTH) && make install &&  \
		$(LOCAL_PY) $(PKGBLDDIR)/packaging/archives/ez_setup.py; \
	fi

contrail-analytics: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-analytics
	rpmbuild $(RPMBLDOPTS) contrail-analytics.spec $(G_TAG) $(RPM_PY)

contrail-api-extension: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-api-extension
	rpmbuild $(RPMBLDOPTS) contrail-api-extension.spec $(G_TAG) $(RPM_PY)

contrail-api-lib: $(PREP)
	@echo making rpm for contrail-api-lib
	rpmbuild $(RPMBLDOPTS) contrail-api-lib.spec $(G_TAG)

contrail-config: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-config
	rpmbuild $(RPMBLDOPTS) contrail-config.spec  $(G_TAG) $(RPM_PY)

contrail-control: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-control
	rpmbuild $(RPMBLDOPTS) contrail-control.spec $(G_TAG) $(RPM_PY)

contrail-dns: $(PREP)
	@echo making rpm for contrail-dns
	rpmbuild $(RPMBLDOPTS) contrail-dns.spec  $(G_TAG)

contrail-interface-name: $(PREP)
	@echo making rpm for contrail-interface-name
	rpmbuild $(RPMBLDOPTS) contrail-interface-name.spec  $(G_TAG)

contrail-libs: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-libs
	rpmbuild $(RPMBLDOPTS) contrail-libs.spec $(G_TAG) $(RPM_PY)

contrail-vrouter: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-vrouter
	rpmbuild $(RPMBLDOPTS) contrail-vrouter.spec  $(G_TAG) $(RPM_PY)

contrail-nova-vif: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-nova-vif
	rpmbuild $(RPMBLDOPTS) contrail-nova-vif.spec $(G_TAG)

contrail-setup: $(PREP)
	@echo making rpm for contrail-setup
	rpmbuild $(RPMBLDOPTS) contrail-setup.spec $(G_TAG)

contrail-setup-with-guest: $(PREP)
	@echo making rpm for contrail-setup-with-guest
	rpmbuild $(RPMBLDOPTS) contrail-setup-with-guest.spec $(G_TAG)

# venv packages
contrail-analytics-venv: $(LOCAL_PY)
	rpmbuild $(RPMBLDOPTS) contrail-analytics-venv.spec $(G_TAG) $(RPM_PY) $(LOCAL_PY_DEF)

contrail-api-venv: $(LOCAL_PY)
	rpmbuild $(RPMBLDOPTS)  contrail-api-venv.spec $(G_TAG) $(RPM_PY) $(LOCAL_PY_DEF)

contrail-control-venv: $(LOCAL_PY)
	rpmbuild $(RPMBLDOPTS) contrail-control-venv.spec $(G_TAG) $(RPM_PY) $(LOCAL_PY_DEF)

contrail-database-venv: $(LOCAL_PY)
	rpmbuild $(RPMBLDOPTS) contrail-database-venv.spec $(G_TAG) $(RPM_PY) $(LOCAL_PY_DEF)

contrail-vrouter-venv: $(LOCAL_PY)
	rpmbuild $(RPMBLDOPTS) contrail-vrouter-venv.spec $(G_TAG) $(RPM_PY) $(LOCAL_PY_DEF)

venv-packages: packaging
packaging: contrail-api-venv contrail-analytics-venv contrail-vrouter-venv contrail-control-venv \
	contrail-database-venv

# Contrail Cloudstack stuff
contrail-cloudstack-utils: $(PREP)
	@echo making rpm for contrail-cloudstack-utils
	rpmbuild $(RPMBLDOPTS) contrail-cloudstack-utils.spec $(G_TAG)

# Contrail Openstack stuff
contrail-openstack: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack
	rpmbuild $(RPMBLDOPTS) contrail-openstack.spec $(G_TAG) $(RPM_PY)

contrail-openstack-analytics: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-analytics
	rpmbuild $(RPMBLDOPTS) contrail-openstack-analytics.spec $(G_TAG) $(RPM_PY)

ifeq ($(CONTRAIL_SKU), grizzly)
contrail-openstack-config: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-config
	rpmbuild $(RPMBLDOPTS) contrail-openstack-config.spec $(G_TAG) $(RPM_PY)
else
contrail-openstack-config: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-config
	rpmbuild $(RPMBLDOPTS) contrail-openstack-havana-config.spec $(G_TAG) $(RPM_PY)
endif

contrail-openstack-control: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-control
	rpmbuild $(RPMBLDOPTS) contrail-openstack-control.spec $(G_TAG) $(RPM_PY)

contrail-openstack-database: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-database
	rpmbuild $(RPMBLDOPTS) contrail-openstack-database.spec $(G_TAG) $(RPM_PY)

contrail-openstack-vrouter: $(PREP)
	@echo making rpm for contrail-openstack-vrouter
	rpmbuild $(RPMBLDOPTS) contrail-openstack-vrouter.spec  $(G_TAG)

contrail-openstack-webui: $(PREP)
	@echo making rpm for contrail-openstack-webui
	rpmbuild $(RPMBLDOPTS) contrail-openstack-webui.spec $(G_TAG)

contrail-openstack-storage: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-storage
	if [ "$(DISTRO)" == "CentOS" ]; then \
		rpmbuild $(RPMBLDOPTS) contrail-openstack-storage.spec $(G_TAG) $(RPM_PY); \
	fi

contrail-openstack-all: contrail-openstack contrail-openstack-analytics contrail-openstack-config \
	contrail-openstack-control contrail-openstack-database contrail-openstack-vrouter \
	contrail-openstack-webui contrail-openstack-storage

contrail-webui:
	@echo making rpm for contrail-webui
	cd $(CPLANE_GIT_ROOT)/../contrail-web-core && make package
	cp contrail-webui.spec $(BUILD_BASE)/SPECS/
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
	cp ../control_files/supervisord_wrapper_scripts/contrail-webui.kill $(BUILD_SRC)/
	cp ../control_files/supervisord_wrapper_scripts/contrail-webui-middleware.kill $(BUILD_SRC)/
	cp ../control_files/redis-webui.conf $(BUILD_SRC)/
	cp ../control_files/redis-webui.ini $(BUILD_SRC)/
	cp ../control_files/redis-webui.initd.supervisord $(BUILD_SRC)/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-webui.spec $(G_TAG)

contrail-nodejs:
	cp contrail-nodejs.spec $(BUILD_BASE)/SPECS/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-nodejs.spec $(G_TAG)

contrail-install-packages: $(PREP)
	@echo making rpm for contrail-install-packages
	rpmbuild $(RPMBLDOPTS) contrail-install-packages.spec  $(G_TAG)

contrail-database: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-database
	cp contrail-database.spec $(BUILD_BASE)/SPECS/
	cp ../control_files/contrail-database.initd $(BUILD_SRC)/
	cp ../control_files/supervisord_contrail_database.conf $(BUILD_SRC)/
	cp ../control_files/supervisord_contrail_database.initd $(BUILD_SRC)/
	rpmbuild $(RPMBLDOPTS) $(BUILD_BASE)/SPECS/contrail-database.spec $(G_TAG) $(RPM_PY)

all: $(PREP) contrail-analytics contrail-api-extension contrail-api-lib contrail-config \
	contrail-control contrail-dns contrail-interface-name contrail-libs contrail-vrouter \
	contrail-setup contrail-openstack-all contrail-webui contrail-nodejs venv-packages \
	contrail-database contrail-nova-vif

clean:
	@echo clean

