PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/openstack/debian=)

ifdef CONTRAIL_SKU
else
  CONTRAIL_SKU := "kilo"
endif

PACKAGES = openstack-neutron-deb \
	openstack-nova-deb \
	openstack-python-neutronclient-deb \
	openstack-nova-docker-deb

all: ${PACKAGES}
	@echo "Build complete"

clean: $(PACKAGES:%-deb=%-clean)
	@echo "Clean"

%-deb:
	$(eval PKGNAME:=$(@:openstack-%-deb=%))
	$(eval BUILDDIR=${SB_TOP}/build/openstack/${PKGNAME})
	$(eval DISTRODIR=${SB_TOP}/distro/openstack/${PKGNAME})
	if test -d ${DISTRODIR}; then \
		mkdir -p ${SB_TOP}/build/openstack; \
		cp -R ${SB_TOP}/distro/openstack/${PKGNAME} ${BUILDDIR}; \
		cp -R $(@:-deb=)/${CONTRAIL_SKU}/debian ${BUILDDIR}/debian; \
		(cd ${BUILDDIR}; fakeroot debian/rules binary) \
	fi
%-clean:
	$(eval PKGNAME:=$(@:openstack-%-clean=%))
	$(eval BUILDDIR=${SB_TOP}/build/openstack/${PKGNAME})
	rm -rf ${BUILDDIR}
