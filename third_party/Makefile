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
DISTRO_SRCDIR       := $(CPLANE_GIT_ROOT)/../distro/third_party
DISTRO_BLDDIR       := $(CPLANE_GIT_ROOT)/../distro/openstack
THIRDPARTY_DIR      := $(CPLANE_GIT_ROOT)/../third_party
THIRDPARTY_PKGDIR   := $(CPLANE_GIT_ROOT)/../tools/packaging/third_party
RPM_PY              := --define "__python $(LOCAL_PY)"
DISTRO              := $(shell egrep -o "Fedora|CentOS|Ubuntu" /etc/issue)
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

# openstack python client packages
cinderclient: package-python-cinderclient
python-cinderclient: package-python-cinderclient
package-python-cinderclient:
	@echo making rpm for package-python-cinderclient
	rpmbuild $(RPMBLDOPTS) python-cinderclient.spec $(G_TAG)

glanceclient: package-python-glanceclient
python-glanceclient: package-python-glanceclient
package-python-glanceclient:
	@echo making rpm for package-python-glanceclient
	rpmbuild $(RPMBLDOPTS) python-glanceclient.spec $(G_TAG)

keystoneclient: package-python-keystoneclient
python-keystoneclient: package-python-keystoneclient
package-python-keystoneclient:
	@echo making rpm for package-python-keystoneclient
	rpmbuild $(RPMBLDOPTS) python-keystoneclient.spec $(G_TAG)

novaclient: package-python-novaclient
python-novaclient: package-python-novaclient
package-python-novaclient:
	@echo making rpm for package-python-novaclient
	rpmbuild $(RPMBLDOPTS) python-novaclient.spec $(G_TAG)

quantumclient:package-python-quantumclient
python-quantumclient:package-python-quantumclient
package-python-quantumclient:
	@echo making rpm for package-python-quantumclient
	rpmbuild $(RPMBLDOPTS) python-quantumclient.spec $(G_TAG)

swiftclient: package-python-swiftclient
python-swiftclient: package-python-swiftclient
package-python-swiftclient:
	@echo making rpm for package-python-swiftclient
	rpmbuild $(RPMBLDOPTS) python-swiftclient.spec $(G_TAG)

all-openstack-client: $(PREP) cinderclient glanceclient keystoneclient novaclient quantumclient \
	swiftclient



# Other 3rd party packages
contrail-fabric-utils:
	@echo making rpm for contrail-fabric-utils
	rpmbuild $(RPMBLDOPTS) fabric-utils.spec $(G_TAG)
	cd $(THIRDPARTY_DIR) && tar -cvzf $(BUILD_BASE)/TOOLS/contrail-fabric-utils-$(TOOLS_VERSION).tgz fabric-utils

contrail-test:
	@echo making tgz for contrail-test
	cd $(THIRDPARTY_DIR) && tar -cvzf $(BUILD_BASE)/TOOLS/contrail-test-$(TOOLS_VERSION).tgz contrail-test

euca2ools:
	@echo making rpm for euca2ools
	rpmbuild $(RPMBLDOPTS) euca2ools.spec $(G_TAG)

hiredis-py: $(PREP) $(LOCAL_PY)
	@echo making rpm for hiredis-py
	rpmbuild $(RPMBLDOPTS) hiredis-py.spec $(G_TAG) $(RPM_PY)

ifmap-server:
	@echo making rpm for ifmap-server
	rpmbuild $(RPMBLDOPTS) irond.spec $(G_TAG)

python-boto:
	@echo making rpm for python-boto
	rpmbuild $(RPMBLDOPTS) boto.spec $(G_TAG)


libvirt-client: libvirt
libvirt-devel: libvirt
libvirt-lock-sanlock: libvirt
libvirt-python: libvirt
libvirt-debuginfo: libvirt
libvirt:
	@echo making rpm for libvirt
	@echo "Distro is $(DISTRO)"
	if [ "$(DISTRO)" == "Fedora" ]; then \
		[ -d $(BUILD_BASE)/SOURCES/libvirt ] || mkdir -p $(BUILD_BASE)/SOURCES/libvirt && \
		cd $(BUILD_BASE)/SOURCES/libvirt && cp -ar $(DISTRO_SRCDIR)/libvirt-0.9.12 . && \
		cd libvirt-0.9.12 && ./configure --localstatedir=/var && \
		$(MAKE) $(MFLAGS) dist && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(PKGBLDDIR)' -ta libvirt-0.9.12.tar.gz ; \
	else cp $(THIRDPARTY_DIR)/libvirt/libvirt-0.10.2-18.el6.src.rpm $(BUILD_BASE)/SOURCES/ && \
		cp $(THIRDPARTY_DIR)/libvirt/libvirt.centos.patch  $(BUILD_BASE)/SOURCES/ && \
		cd $(BUILD_BASE)/SOURCES && \
		rpm --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-i libvirt-0.10.2-18.el6.src.rpm && \
		cd $(BUILD_BASE)/SPECS && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-bp libvirt.spec && \
		cp $(THIRDPARTY_DIR)/libvirt/libvirt.centos.spec.patch  $(BUILD_BASE)/SPECS/ && \
		patch -p0 -i $(THIRDPARTY_DIR)/libvirt/libvirt.centos.spec.patch && \
		cd $(THIRDPARTY_DIR) && \
		rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(BUILD_BASE)' \
		-ba $(BUILD_BASE)/SPECS/libvirt.spec $(G_TAG); \
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

python-bitarray: $(PREP) $(LOCAL_PY)
	@echo making rpm for python-bitarray
	rpmbuild $(RPMBLDOPTS) python-bitarray.spec $(G_TAG) $(RPM_PY)

python-geventhttpclient: $(PREP) $(LOCAL_PY)
	@echo making rpm for python-geventhttpclient
	rpmbuild $(RPMBLDOPTS) python-geventhttpclient.spec $(G_TAG) $(RPM_PY)

python-pycassa: $(PREP) $(LOCAL_PY)
	@echo making rpm for python-pycassa
	rpmbuild $(RPMBLDOPTS) python-pycassa.spec $(G_TAG) $(RPM_PY)

python-thrift: $(PREP)
	@echo making rpm for python-thrift
	rpmbuild $(RPMBLDOPTS) python-thrift.spec $(G_TAG)

redis-py: $(PREP) $(LOCAL_PY)
	@echo making rpm for redis-py
	rpmbuild $(RPMBLDOPTS) redis-py.spec $(G_TAG) $(RPM_PY)

supervisor: $(PREP) $(LOCAL_PY)
	@echo making rpm for supervisor
	rpmbuild $(RPMBLDOPTS) supervisor.spec $(G_TAG) $(RPM_PY)

webob:
	@echo making rpm for webob
	cp $(THIRDPARTY_DIR)/webob/WebOb-1.2.3.tar.gz $(BUILD_BASE)/SOURCES/ && \
	rpmbuild $(RPMBLDOPTS) python-webob.spec $(G_TAG)

xmltodict: $(PREP)
	@echo making rpm for xmltodict
	rpmbuild $(RPMBLDOPTS) xmltodict.spec $(G_TAG)

zookeeper: $(PREP)
	@echo making rpm for zookeeper
	sed -i 's#<property name="version" value="3.4.3"#<property name="version" value="3.4.3.$(CPLANE_SRC_VER).$(TAG)"#g' $(DISTRO_SRCDIR)/zookeeper/build.xml
	cd $(DISTRO_SRCDIR)/zookeeper  && \
	ant rpm
	cp $(DISTRO_SRCDIR)/zookeeper/build/*[0-9].rpm $(BUILD_BASE)/RPMS/x86_64/
	cp $(DISTRO_SRCDIR)/zookeeper/build/contrib/zkpython/*[0-9].rpm $(BUILD_BASE)/RPMS/x86_64/


all: $(PREP) all-openstack-client contrail-fabric-utils contrail-test euca2ools hiredis-py \
	ifmap-server python-boto libvirt puppet python-bitarray python-geventhttpclient \
	libvirt puppet python-bitarray python-geventhttpclient python-pycassa python-thrift \
	redis-py supervisor webob xmltodict zookeeper ixgbe

clean:
	@echo clean
