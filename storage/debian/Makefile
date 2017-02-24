PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/storage/debian=)
SRC_VER := $(shell cat $(SB_TOP)/controller/src/base/version.info)
BUILDTIME := $(shell date -u +%y%m%d%H%M)

ifdef CONTRAIL_SKU
  export CONTRAIL_SKU
else
  export CONTRAIL_SKU := kilo
endif

VERSION = 
ifdef TAG
VERSION = $(SRC_VER)-$(TAG)
else
VERSION = $(SRC_VER)-$(BUILDTIME)
endif

PACKAGES =	contrail-storage-deb	\
            contrail-web-storage-deb \


all: ${PACKAGES}
	@echo "Build complete"

clean: $(PACKAGES:%-deb=%-clean)
	@echo "Clean"


contrail-storage-packages-deb:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-storage-packages)
	mkdir -p ${BUILDDIR}
	cp -ar ${SB_TOP}/tools/packaging/storage/debian/contrail-storage-packages/debian ${BUILDDIR}
	(cd ${BUILDDIR}; fakeroot debian/rules clean)
	(cd ${BUILDDIR}; fakeroot debian/rules binary)
	@echo "Wrote: ${BUILDDIR}/contrail-storage-packages_$(VERSION)~$(CONTRAIL_SKU)_all.deb"

contrail-storage-packages-clean:
	$(eval BUILDDIR=${SB_TOP}/build/debian/contrail-storage-packages)
	rm -rf ${BUILDDIR}

%-deb:
	(cd $(@:-deb=); fakeroot debian/rules clean)
	(cd $(@:-deb=); fakeroot debian/rules binary)

%-clean:
	(cd $(@:-clean=); fakeroot debian/rules clean)

