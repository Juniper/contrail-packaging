
SRC_VER := $(shell cat ./controller/src/base/version.info)
BUILDNUM ?= $(shell date -u +%m%d%Y)
export BUILDTAG ?= $(SRC_VER)-$(BUILDNUM)

vijava-deb:
	(cd vijava && make all)

java-api-deb:
	(cd java-api && make all)

vrouter-java-api-deb:
	(cd vrouter-java-api && make all)

vcenter-plugin-deb:
	(cd vcenter-plugin && make all)

install-package-deb:
	$(eval BUILDDIR=./build/packages)
	mkdir -p ${BUILDDIR}
	cp -ar vcenter-plugin/packages/* ${BUILDDIR}
	(cd ${BUILDDIR}; debuild --preserve-envvar=BUILDTAG -i -us -uc -b)
	@echo "Wrote: build/contrail-vcenter-plugin_all.deb"

clean-install-package:
	$(eval BUILDDIR=./build/packages)
	rm -rf ${BUILDDIR}
	rm -rf ./build/contrail-install-vcenter-plugin*.*

clean: clean-install-package
	(cd vijava && make clean)
	(cd java-api && make clean)
	(cd vrouter-java-api make clean)
	(cd vcenter-plugin make clean)


all: vijava-deb java-api-deb vrouter-java-api-deb vcenter-plugin-deb install-package-deb
