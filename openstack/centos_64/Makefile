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
  CONTRAIL_SKU := grizzly
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
auth: django-openstack-auth
python-django-openstack-auth: django-openstack-auth
django-openstack-auth: $(PREP)
	@echo making rpm for django-openstack-auth
	cd $(OPENSTACK_PKGDIR)/centos_64/django-openstack-auth && \
	cp `grep '^Source[0-9]\+:' django-openstack-auth.spec|cut -d: -f2` $(BUILD_BASE)/SOURCES/ 
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb django-openstack-auth/django-openstack-auth.spec $(G_TAG)

ifeq ($(CONTRAIL_SKU), grizzly)
cinder: package-cinder
openstack-cinder-doc: package-cinder
python-cinder: package-cinder
package-cinder: $(PREP)
	@echo making rpm for package-cinder
	cd $(OPENSTACK_PKGDIR)/centos_64/cinder && \
	cp `grep '^Source[0-9]\+:' openstack-cinder.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/ 
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb cinder/openstack-cinder.spec $(G_TAG)

glance: package-glance
python-glance: package-glance
openstack-glance-doc: package-glance
package-glance: $(PREP)
	@echo making rpm for package-glance
	cd $(OPENSTACK_PKGDIR)/centos_64/glance && \
	cp `grep '^Source[0-9]\+:' package-glance.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/ 
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb glance/package-glance.spec $(G_TAG)

horizon: package-horizon
openstack-dashboard: package-horizon
package-horizon: $(PREP)
	@echo making rpm for package-horizon
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb horizon/openstack-horizon.spec $(G_TAG)

keystone: package-keystone
python-keystone: package-keystone
package-keystone: $(PREP)
	@echo making rpm for package-keystone
	cd $(OPENSTACK_PKGDIR)/centos_64/keystone && \
	cp `grep '^Source[0-9]\+:' package-keystone.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/ 
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb keystone/package-keystone.spec $(G_TAG)

contrail-openstack-dashboard: $(PREP)
	@echo making rpm for package-horizon
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DASH_PLUGIN_BLDDIR)' \
	-bb horizon-plugin/openstack-horizon-plugin.spec $(G_TAG)

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
	@echo making rpm for package-nova
	cd $(OPENSTACK_PKGDIR)/centos_64/nova && \
	cp `grep '^Source[0-9]\+:' openstack-nova.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/ 
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb nova/openstack-nova.spec $(G_TAG)

quantum: package-quantum
python-quantum: package-quantum
openstack-quantum-contrail: package-quantum
openstack-quantum-contrail: package-quantum
package-quantum: $(PREP)
	@echo making rpm for package-quantum
	cd $(OPENSTACK_PKGDIR)/centos_64/quantum && \
	cp `grep '^Source[0-9]\+:' openstack-quantum.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/ 
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb quantum/openstack-quantum.spec $(G_TAG)


all: $(PREP) auth cinder glance horizon keystone nova quantum contrail-openstack-dashboard
else
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
	cd $(OPENSTACK_PKGDIR)/centos_64/nova && \
	cp `grep '^Source[0-9]\+:' openstack-havana-nova.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb nova/openstack-havana-nova.spec $(G_TAG)

neutron: package-neutron
python-neutron: package-neutron
openstack-neutron-contrail: package-neutron
openstack-neutron-contrail: package-neutron
package-neutron: $(PREP)
	@echo making rpm for package-neutron for havana
	echo $(OPENSTACK_PKGDIR)
	cd $(OPENSTACK_PKGDIR)/centos_64/neutron && \
	cp `grep '^Source[0-9]\+:' openstack-neutron.spec | cut -d: -f2` $(BUILD_BASE)/SOURCES/
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb neutron/openstack-neutron.spec $(G_TAG)

horizon: package-horizon
openstack-dashboard: package-horizon
package-horizon: $(PREP)
	@echo making rpm for package-horizon
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DISTRO_BLDDIR)' \
	-bb horizon/openstack-horizon-havana.spec $(G_TAG)

contrail-openstack-dashboard: $(PREP)
	@echo making rpm for package-horizon
	rpmbuild --define '_topdir $(BUILD_BASE)' --define '_builddir $(DASH_PLUGIN_BLDDIR)' \
	-bb horizon-plugin/openstack-horizon-plugin-havana.spec $(G_TAG)

all: $(PREP) package-nova package-neutron horizon contrail-openstack-dashboard
endif

clean:
	@echo clean
