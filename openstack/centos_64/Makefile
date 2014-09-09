LIST_SOURCES        := list
REPOBIN             := repo
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
OPENSTACK_PKGDIR    := $(CPLANE_GIT_ROOT)/../tools/packaging/openstack
DISTRO_BLDDIR       := $(CPLANE_GIT_ROOT)/../distro/openstack
DASH_PLUGIN_BLDDIR  := $(CPLANE_GIT_ROOT)/../contrail-horizon
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

ifndef CONTRAIL_SKU
  CONTRAIL_SKU := havana
endif

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

# Openstack packages
ifeq ($(CONTRAIL_SKU), havana)
nova: package-nova
openstack-nova-cert: package-nova
openstack-nova-objectstore: package-nova
openstack-nova-scheduler: package-nova
openstack-nova-api: package-nova
python-nova: package-nova
openstack-nova-compute: package-nova
openstack-nova-console: package-nova
openstack-nova-common: package-nova
openstack-nova-doc: package-nova
package-nova: $(PREP)
	@echo making havana rpm for package-nova
	echo $(OPENSTACK_PKGDIR)
	cd $(OPENSTACK_PKGDIR)/centos_64/nova/havana && \
	cp `grep '^Source[0-9]\+:' openstack-nova.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/
	cd $(OPENSTACK_PKGDIR)/centos_64/nova/havana && \
	cp `grep '^Patch[0-9]\+:' openstack-nova.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb nova/havana/openstack-nova.spec $(G_TAG)

neutron: package-neutron
python-neutron: package-neutron
openstack-neutron-contrail: package-neutron
openstack-neutron-contrail: package-neutron
package-neutron: $(PREP)
	@echo making rpm for package-neutron for havana
	echo $(OPENSTACK_PKGDIR)
	cd $(OPENSTACK_PKGDIR)/centos_64/neutron/havana && \
	cp `grep '^Source[0-9]\+:' openstack-neutron.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb neutron/havana/openstack-neutron.spec $(G_TAG)

horizon: package-horizon
openstack-dashboard: package-horizon
package-horizon: $(PREP)
	@echo making rpm for package-horizon
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb horizon/havana/openstack-horizon.spec $(G_TAG)

contrail-openstack-dashboard: $(PREP)
	@echo making rpm for package-horizon
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DASH_PLUGIN_BLDDIR)' \
	-bb horizon-plugin/havana/openstack-horizon-plugin.spec $(G_TAG)

all: $(PREP) package-nova package-neutron horizon contrail-openstack-dashboard
else
all: $(PREP)
endif

clean:
	@echo clean
