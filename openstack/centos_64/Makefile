LIST_SOURCES        := list
REPOBIN             := repo
CPLANE_GIT_ROOT     := $(shell $(REPOBIN) info contrail-controller|grep 'Mount path'|cut -f3 -d" ")
PKGING_GIT_ROOT     := $(CPLANE_GIT_ROOT)/../tools
PKGING_DISTDIR      := $(PKGING_GIT_ROOT)/packaging/common/rpm
CPLANE_SRC_VER      := $(shell cat $(CPLANE_GIT_ROOT)/src/base/version.info)
BUILD_BASE          := $(CPLANE_GIT_ROOT)/build/package-build
PKGBLDDIR           := $(BUILD_BASE)/BUILD
DISTRO_PACKAGING    := $(CPLANE_GIT_ROOT)/../distro/python-venv-packaging
OPENSTACK_PKGDIR    := $(CPLANE_GIT_ROOT)/../tools/packaging/openstack
DISTRO_BLDDIR       := $(CPLANE_GIT_ROOT)/../distro/openstack
DASH_PLUGIN_BLDDIR  := $(CPLANE_GIT_ROOT)/../contrail-horizon
DISTRO              := $(shell egrep -o "Fedora|CentOS|Ubuntu" /etc/issue)
PREP = prep
PPREP = pprep

G_TAG :=
ifdef GIT_VER
 G_TAG := --define "_gitVer $(GIT_VER)"
endif 
ifdef TAG
 G_TAG += --define "_buildTag $(CPLANE_SRC_VER).$(TAG)"
endif
ifdef FILE_LIST
 G_TAG += --define "_fileList $(FILE_LIST)"
endif
G_TAG += --define "_srcVer $(CPLANE_SRC_VER)"

ifndef CONTRAIL_SKU
  CONTRAIL_SKU := kilo
endif

$(PPREP):
	@echo some $(PPREP) work ...
	mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS,TOOLS}

$(PREP): $(PPREP)
	@echo some $(PREP) work ...
	@echo CPLANE_GIT_ROOT = $(CPLANE_GIT_ROOT)
	mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS,TOOLS}

neutronclient:package-python-neutronclient
python-neutronclient:package-python-neutronclient
package-python-neutronclient:
	@echo making rpm for package-python-neutronclient
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb neutronclient/${CONTRAIL_SKU}/python-neutronclient.spec $(G_TAG)

all: $(PREP)

clean:
	@echo clean
