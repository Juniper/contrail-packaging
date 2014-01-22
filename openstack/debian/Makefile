PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/openstack/debian=)

PACKAGES = openstack-neutron-deb

all: ${PACKAGES}
	@echo "Build complete"

clean: $(PACKAGES:%-deb=%-clean)
	@echo "Clean"

%-deb:
	$(eval PKGNAME:=$(@:openstack-%-deb=%))
	$(eval BUILDDIR=${SB_TOP}/build/openstack/${PKGNAME})
	mkdir -p ${SB_TOP}/build/openstack
	cp -R ${SB_TOP}/distro/openstack/${PKGNAME} ${BUILDDIR}
	cp -R $(@:-deb=)/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

%-clean:
	$(eval PKGNAME:=$(@:openstack-%-clean=%))
	$(eval BUILDDIR=${SB_TOP}/build/openstack/${PKGNAME})
	rm -rf ${BUILDDIR}

