LIST_SOURCES        := list
REPOBIN             := repo
CPLANE_GIT_ROOT     := $(PWD:/tools/packaging/third_party=/controller)
PKGING_GIT_ROOT     := $(CPLANE_GIT_ROOT)/../tools
PKGING_DISTDIR      := $(PKGING_GIT_ROOT)/packaging/common/rpm
CPLANE_SRC_VER      := $(shell cat $(CPLANE_GIT_ROOT)/src/base/version.info)
BUILD_BASE          := $(CPLANE_GIT_ROOT)/build/package-build
PKGBLDDIR           := $(BUILD_BASE)/BUILD
DISTRO_PACKAGING    := $(CPLANE_GIT_ROOT)/../distro/python-venv-packaging
OPENSTACK_PKGDIR    := $(CPLANE_GIT_ROOT)/../tools/packaging/openstack
DISTRO_SRCDIR       := $(CPLANE_GIT_ROOT)/../distro/third_party
DISTRO_BLDDIR       := $(CPLANE_GIT_ROOT)/../distro/openstack
THIRDPARTY_DIR      := $(CPLANE_GIT_ROOT)/../third_party
THIRDPARTY_PKGDIR   := $(CPLANE_GIT_ROOT)/../tools/packaging/third_party
DISTRO              := $(shell egrep -o "Fedora|CentOS|Ubuntu|Red Hat" /etc/redhat-release)
DISTRO_VER          := $(shell egrep -o "[0-9.]+" /etc/redhat-release)
RPMBLDOPTS          := --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' -bb
PREP = prep
PPREP = pprep

G_TAG :=
TAG := $(shell date -u +%y%m%d%H%M)
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
  CONTRAIL_SKU := havana
endif

$(PPREP):
	@echo some $(PPREP) work ...
	mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS,TOOLS}

$(PREP): $(PPREP)
	@echo some $(PREP) work ...
	@echo CPLANE_GIT_ROOT = $(CPLANE_GIT_ROOT)
	mkdir -p $(BUILD_BASE)/{BUILD,RPMS,SOURCES,SPECS,SRPMS,TOOLS}

libvirt-client: libvirt
libvirt-devel: libvirt
libvirt-lock-sanlock: libvirt
libvirt-python: libvirt
libvirt-debuginfo: libvirt
libvirt: $(PPREP)
	@echo making rpm for libvirt
	@echo "Distro is $(DISTRO), DISTRO_VER is $(DISTRO_VER)"
	if [ "$(DISTRO)" == "Fedora" ]; then \
		[ -d $(BUILD_BASE)/SOURCES/libvirt ] || mkdir -p $(BUILD_BASE)/SOURCES/libvirt && \
		cd $(BUILD_BASE)/SOURCES/libvirt && cp -ar $(DISTRO_SRCDIR)/libvirt-0.9.12 . && \
		cd libvirt-0.9.12 && ./configure --localstatedir=/var && \
		$(MAKE) $(MFLAGS) dist && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(PKGBLDDIR)' -ta libvirt-0.9.12.tar.gz ; \
	elif [ "$(DISTRO)" == "CentOS" ] ; then \
            if [ "$(DISTRO_VER)" == "6.4" ] ; then \
		cp $(THIRDPARTY_DIR)/libvirt/libvirt-0.10.2-18.el6.src.rpm $(BUILD_BASE)/SOURCES/ && \
		cp $(THIRDPARTY_DIR)/libvirt/libvirt.centos.patch  $(BUILD_BASE)/SOURCES/ && \
		cd $(BUILD_BASE)/SOURCES && \
		rpm --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-i libvirt-0.10.2-18.el6.src.rpm && \
		cd $(BUILD_BASE)/SPECS && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-bp libvirt.spec && \
		cp $(THIRDPARTY_DIR)/libvirt/libvirt.centos.spec.patch  $(BUILD_BASE)/SPECS/ && \
		cp $(THIRDPARTY_DIR)/libvirt/libvirt.centos.spec.test-disable.patch $(BUILD_BASE)/SPECS/ && \
		patch -p0 -i $(THIRDPARTY_DIR)/libvirt/libvirt.centos.spec.patch && \
		patch -p0 -i $(THIRDPARTY_DIR)/libvirt/libvirt.centos.spec.test-disable.patch && \
		cd $(THIRDPARTY_DIR) && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-ba $(BUILD_BASE)/SPECS/libvirt.spec $(G_TAG); \
            elif [ "$(DISTRO_VER)" == "6.5" ] ; then \
                cp $(THIRDPARTY_DIR)/libvirt/libvirt-0.10.2-29.el6.src.rpm $(BUILD_BASE)/SOURCES/ && \
                cp $(THIRDPARTY_DIR)/libvirt/libvirt.centos65.patch  $(BUILD_BASE)/SOURCES/libvirt.centos.patch && \
                cd $(BUILD_BASE)/SOURCES && \
                rpm --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
                -i libvirt-0.10.2-29.el6.src.rpm && \
                cd $(BUILD_BASE)/SPECS && \
                rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
                -bp libvirt.spec && \
                cp $(THIRDPARTY_DIR)/libvirt/libvirt.centos65.spec.patch  $(BUILD_BASE)/SPECS/ && \
                patch -p0 -i $(THIRDPARTY_DIR)/libvirt/libvirt.centos65.spec.patch && \
                cd $(THIRDPARTY_DIR) && \
                rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
                -ba $(BUILD_BASE)/SPECS/libvirt.spec $(G_TAG); \
            fi ; \
	elif [ "$(DISTRO)" == "Red Hat" ] ; then \
            if [ "$(DISTRO_VER)" == "7.0" ] ; then \
		cp $(THIRDPARTY_DIR)/libvirt/libvirt-1.2.8-16.el7_1.1.src.rpm $(BUILD_BASE)/SOURCES/ && \
		cp $(THIRDPARTY_DIR)/libvirt/contrail_rhel70_libvirt_1.2.8.patch  $(BUILD_BASE)/SOURCES/ && \
		cd $(BUILD_BASE)/SOURCES && \
		rpm --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-i libvirt-1.2.8-16.el7_1.1.src.rpm && \
		cd $(BUILD_BASE)/SPECS && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-bp libvirt.spec && \
		cp $(THIRDPARTY_DIR)/libvirt/contrail_rhel70_libvirt_1.2.8.spec.patch  $(BUILD_BASE)/SPECS/ && \
		patch -p0 -i $(BUILD_BASE)/SPECS/contrail_rhel70_libvirt_1.2.8.spec.patch && \
		cd $(THIRDPARTY_DIR) && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-ba $(BUILD_BASE)/SPECS/libvirt.spec $(G_TAG); \
            fi ;\
        fi ; #line1

ixgbe-debuginfo: ixgbe
ixgbe: $(PPREP)
	@echo making rpm for ixgbe
	@echo "Distro is $(DISTRO)"
	if [ "$(DISTRO)" == "Fedora" ]; then \
		cd $(BUILD_BASE)/SOURCES && cp -ar $(DISTRO_SRCDIR)/ixgbe/* . && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-bb ixgbe.spec $(G_TAG); \
	fi

all: $(PREP) libvirt ixgbe

clean:
	@echo clean
