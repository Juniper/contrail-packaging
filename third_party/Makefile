LIST_SOURCES        := list
REPOBIN             := repo
CPLANE_GIT_ROOT     := $(PWD:/tools/packaging/third_party=/controller)
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
DISTRO_SRCDIR       := $(CPLANE_GIT_ROOT)/../distro/third_party
DISTRO_BLDDIR       := $(CPLANE_GIT_ROOT)/../distro/openstack
THIRDPARTY_DIR      := $(CPLANE_GIT_ROOT)/../third_party
THIRDPARTY_PKGDIR   := $(CPLANE_GIT_ROOT)/../tools/packaging/third_party
RPM_PY              := --define "__python $(LOCAL_PY)"
DISTRO              := $(shell egrep -o "Fedora|CentOS|Ubuntu|Red Hat" /etc/issue)
DISTRO_VER          := $(shell egrep -o "[0-9.]+" /etc/issue)
RPMBLDOPTS          := --define '_topdir $(BUILD_BASE)' --define '_builddir $(CPLANE_GIT_ROOT)' -bb
PREP = prep
PPREP = pprep

G_TAG :=
TAG := $(shell date -u +%y%m%d%H%M)
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

contrail-fabric-utils: $(PPREP)
	@echo making rpm for contrail-fabric-utils
	rpmbuild $(RPMBLDOPTS) fabric-utils.spec $(G_TAG)
	cd $(THIRDPARTY_DIR) && tar -cvzf $(BUILD_BASE)/TOOLS/contrail-fabric-utils-$(TOOLS_VERSION).tgz fabric-utils

contrail-test:
	@echo making tgz for contrail-test
	cd $(THIRDPARTY_DIR) && tar -cvzf $(BUILD_BASE)/TOOLS/contrail-test-$(TOOLS_VERSION).tgz contrail-test

libvirt-client: libvirt
libvirt-devel: libvirt
libvirt-lock-sanlock: libvirt
libvirt-python: libvirt
libvirt-debuginfo: libvirt
libvirt:
	@echo making rpm for libvirt
	@echo "Distro is $(DISTRO), DISTRO_VER is $(DISTRO_VER)"
	if [ "$(DISTRO)" == "Fedora" ]; then \
		[ -d $(BUILD_BASE)/SOURCES/libvirt ] || mkdir -p $(BUILD_BASE)/SOURCES/libvirt && \
		cd $(BUILD_BASE)/SOURCES/libvirt && cp -ar $(DISTRO_SRCDIR)/libvirt-0.9.12 . && \
		cd libvirt-0.9.12 && ./configure --localstatedir=/var && \
		$(MAKE) $(MFLAGS) dist && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(PKGBLDDIR)' -ta libvirt-0.9.12.tar.gz ; \
	else if [ "$(DISTRO)" == "CentOS" ] ; then \
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
            else if [ "$(DISTRO_VER)" == "6.5" ] ; then \
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
        fi \
	fi \
	fi \
	fi

ixgbe-debuginfo: ixgbe
ixgbe: $(PPREP)
	@echo making rpm for ixgbe
	@echo "Distro is $(DISTRO)"
	if [ "$(DISTRO)" == "Fedora" ]; then \
		cd $(BUILD_BASE)/SOURCES && cp -ar $(DISTRO_SRCDIR)/ixgbe/* . && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-bb ixgbe.spec $(G_TAG); \
	fi

puppet: $(PREP)
	@echo making rpm for puppet
	rpmbuild $(RPMBLDOPTS) puppet.spec $(G_TAG)

all: $(PREP) contrail-fabric-utils contrail-test \
	libvirt puppet ixgbe

clean:
	@echo clean
