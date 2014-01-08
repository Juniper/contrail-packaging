PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/common/debian=)

PACKAGES = contrail-libs-deb \
	contrail-vrouter-deb \
	contrail-vrouter-init-deb \
	contrail-config-venv-deb \
	contrail-config-deb \
	contrail-config-extension-deb \
	contrail-control-deb \
	contrail-api-lib-deb \
	contrail-nova-vif-deb \
	ifmap-server-deb \
	supervisord-deb

all: ${PACKAGES}
	@echo "Build complete"

clean: $(PACKAGES:%-deb=%-clean)
	@echo "Clean"

ifmap-server-deb:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/ifmap-server)
	mkdir -p ${SB_TOP}/third_party
	cp -R ${SB_TOP}/third_party/ifmap-server ${BUILDDIR}
	cp -R ifmap-server/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

ifmap-server-clean:
	$(eval BUILDDIR=${SB_TOP}/build/third_party/ifmap-server)
	rm -rf ${BUILDDIR}

%-deb:
	(cd $(@:-deb=); fakeroot debian/rules binary)

%-clean:
	(cd $(@:-clean=); fakeroot debian/rules clean)


contrail-vrouter-deb: contrail-libs-deb
contrail-config-deb: contrail-config-venv-deb