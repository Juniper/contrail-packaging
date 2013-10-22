LIST_SOURCES        := list
REPOBIN             := /cs-shared/tools/bin/repo
CPLANE_GIT_ROOT     := $(shell $(REPOBIN) info contrail-controller|grep 'Mount path'|cut -f3 -d" ")
PKGING_GIT_ROOT     := $(CPLANE_GIT_ROOT)/../tools
PKGING_DISTDIR      := $(PKGING_GIT_ROOT)/packaging/common/rpm
CPLANE_SRC_VER      := $(shell cat $(CPLANE_GIT_ROOT)/src/base/version.info)
BUILD_BASE          := $(CPLANE_GIT_ROOT)/build/package-build
PKGBLDDIR           := $(BUILD_BASE)/BUILD
LOCAL_PY_PTH        := $(BUILD_BASE)/BUILD/python2.7
LOCAL_PY            := $(LOCAL_PY_PTH)/bin/python
LOCAL_PY_BLD        := $(BUILD_BASE)/BUILDROOT/Python-2.7.5
DISTRO_PACKAGING    := $(CPLANE_GIT_ROOT)/../distro/python-venv-packaging
RPM_PY              := --define "__python $(LOCAL_PY)"
DISTRO              := $(shell egrep -o "Fedora|CentOS|Ubuntu" /etc/issue)
PREP = prep
PPREP = pprep

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


$(PPREP):
	@echo some $(PPREP) work ...
	[ -d $(BUILD_BASE)/SOURCES ] || mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

$(PREP): $(PPREP)
	@echo some $(PREP) work ...
	@echo CPLANE_GIT_ROOT = $(CPLANE_GIT_ROOT)
	[ -d $(BUILD_BASE)/SOURCES ] || mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

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
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-analytics.spec $(G_TAG) $(RPM_PY)

contrail-api-extension: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-api-extension
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-api-extension.spec $(G_TAG) $(RPM_PY)

contrail-api-lib: $(PREP)
	@echo making rpm for contrail-api-lib
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-api-lib.spec $(G_TAG)

contrail-config: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-config
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-config.spec  $(G_TAG) $(RPM_PY)

contrail-control: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-control
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-control.spec $(G_TAG) $(RPM_PY)

contrail-dns: $(PREP)
	@echo making rpm for contrail-dns
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-dns.spec  $(G_TAG)

contrail-interface-name: $(PREP)
	@echo making rpm for contrail-interface-name
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-interface-name.spec  $(G_TAG)

contrail-libs: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-libs
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-libs.spec $(G_TAG) $(RPM_PY)

contrail-vrouter: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-vrouter
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-vrouter.spec  $(G_TAG) $(RPM_PY)

contrail-setup: $(PREP)
	@echo making rpm for contrail-setup
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-setup.spec $(G_TAG)

contrail-setup-with-guest: $(PREP)
	@echo making rpm for contrail-setup-with-guest
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' \
	--define '_builddir $(CPLANE_GIT_ROOT)' contrail-setup-with-guest.spec $(G_TAG)




	## rpmbuild --define '_topdir $(BUILD_BASE)' --define "_builddir $(BUILD_BASE)" \


contrail-analytics-venv: $(LOCAL_PY)
	rpmbuild --define '_topdir $(BUILD_BASE)' --define "_builddir $(CPLANE_GIT_ROOT)" \
	-bb contrail-analytics-venv.spec $(G_TAG) $(RPM_PY) --define "_python_path $(LOCAL_PY_PTH)"

contrail-api-venv: $(LOCAL_PY)
	rpmbuild --define '_topdir $(BUILD_BASE)' --define "_builddir $(CPLANE_GIT_ROOT)" \
	-bb contrail-api-venv.spec $(G_TAG) $(RPM_PY) --define "_python_path $(LOCAL_PY_PTH)"

contrail-control-venv: $(LOCAL_PY)
	rpmbuild --define '_topdir $(BUILD_BASE)' --define "_builddir $(CPLANE_GIT_ROOT)" \
	-bb contrail-control-venv.spec $(G_TAG) $(RPM_PY) --define "_python_path $(LOCAL_PY_PTH)"

contrail-database-venv: $(LOCAL_PY)
	rpmbuild --define '_topdir $(BUILD_BASE)' --define "_builddir $(CPLANE_GIT_ROOT)" \
	-bb contrail-database-venv.spec $(G_TAG) $(RPM_PY) --define "_python_path $(LOCAL_PY_PTH)"

contrail-vrouter-venv: $(LOCAL_PY)
	rpmbuild --define '_topdir $(BUILD_BASE)' --define "_builddir $(CPLANE_GIT_ROOT)" \
	-bb contrail-vrouter-venv.spec $(G_TAG) $(RPM_PY) --define "_python_path $(LOCAL_PY_PTH)"

venv-packages: packaging
packaging: contrail-api-venv contrail-analytics-venv contrail-vrouter-venv contrail-control-venv \
	contrail-database-venv


# Contrail Openstack stuff
contrail-openstack-analytics: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-analytics
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' contrail-openstack-analytics.spec $(G_TAG) $(RPM_PY)

contrail-openstack-config: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-config
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' contrail-openstack-config.spec $(G_TAG) $(RPM_PY)

contrail-openstack-control: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-control
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' contrail-openstack-control.spec $(G_TAG) $(RPM_PY)

contrail-openstack-database: $(PREP) $(LOCAL_PY)
	@echo making rpm for contrail-openstack-database
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' contrail-openstack-database.spec $(G_TAG) $(RPM_PY)

contrail-openstack-vrouter: $(PREP)
	@echo making rpm for contrail-openstack-vrouter
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' contrail-openstack-vrouter.spec  $(G_TAG)

contrail-openstack-webui: $(PREP)
	@echo making rpm for contrail-openstack-webui
	rpmbuild -bb --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' contrail-openstack-webui.spec $(G_TAG)

# NOT working - need to fix for the other repo
contrail-webui:
	@echo making rpm for contrail-webui
	cd $(CPLANE_GIT_ROOT)/../contrail-web-core && make package
	cp contrail-webui.spec $(BUILD_BASE)/SPECS/
	cp ../control_files/contrailWebServer.sh $(BUILD_BASE)/SOURCES/
	cp ../control_files/contrailWebMiddleware.sh $(BUILD_BASE)/SOURCES/
	cp ../control_files/contrail-webui-middleware.service $(BUILD_BASE)/SOURCES/
	cp ../control_files/contrail-webui.service $(BUILD_BASE)/SOURCES/
	cp ../control_files/supervisord_webui.conf $(BUILD_BASE)/SOURCES/
	cp ../control_files/supervisor-webui.initd $(BUILD_BASE)/SOURCES/
	cp ../control_files/supervisor-webui.service $(BUILD_BASE)/SOURCES/
	cp ../control_files/contrail-webui.initd.supervisord $(BUILD_BASE)/SOURCES/
	cp ../control_files/contrail-webui-middleware.initd.supervisord $(BUILD_BASE)/SOURCES/
	cp ../control_files/contrail-webui.ini $(BUILD_BASE)/SOURCES/
	cp ../control_files/contrail-webui-middleware.ini $(BUILD_BASE)/SOURCES/
	cp ../control_files/supervisord_wrapper_scripts/contrail-webui.kill $(BUILD_BASE)/SOURCES/
	cp ../control_files/supervisord_wrapper_scripts/contrail-webui-middleware.kill $(BUILD_BASE)/SOURCES/
	cp ../control_files/redis-webui.conf $(BUILD_BASE)/SOURCES/
	cp ../control_files/redis-webui.ini $(BUILD_BASE)/SOURCES/
	cp ../control_files/redis-webui.initd.supervisord $(BUILD_BASE)/SOURCES/
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' \
	-bb $(BUILD_BASE)/SPECS/contrail-webui.spec $(G_TAG)

# NOT working - need to fix for the other repo for webui
contrail-nodejs:
	cp contrail-nodejs.spec $(BUILD_BASE)/SPECS/
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' \
	-bb $(BUILD_BASE)/SPECS/contrail-nodejs.spec $(G_TAG)

contrail-install-packages: $(PREP)
	@echo making rpm for contrail-install-packages
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' \
	-bb contrail-install-packages.spec  $(G_TAG)


all: $(PREP) contrail-analytics contrail-api-extension contrail-api-lib contrail-config \
	contrail-control contrail-dns contrail-interface-name contrail-libs contrail-vrouter \
	contrail-setup contrail-setup-with-guest  contrail-openstack-analytics \
	contrail-openstack-config contrail-openstack-control contrail-openstack-database \
	contrail-openstack-vrouter contrail-openstack-webui contrail-webui contrail-nodejs \
	venv-packages


clean:
	@echo clean

