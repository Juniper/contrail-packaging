PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/openstack/debian=)

ifdef CONTRAIL_SKU
else
  CONTRAIL_SKU := "havana"
endif

PACKAGES = openstack-quantum-deb \
	openstack-neutron-deb \
	openstack-nova-deb \
	openstack-python-neutronclient-deb \
	openstack-python-quantumclient-deb

all: ${PACKAGES}
	@echo "Build complete"

clean: $(PACKAGES:%-deb=%-clean)
	@echo "Clean"

ifneq ($(CONTRAIL_SKU), icehouse)
openstack-nova-deb:
	$(eval BUILDDIR=${SB_TOP}/build/openstack/nova)
	$(eval DISTRODIR=${SB_TOP}/distro/openstack/nova)
	if test -d ${DISTRODIR}; then \
		mkdir -p ${SB_TOP}/build/openstack; \
		cp -R ${SB_TOP}/distro/openstack/nova ${BUILDDIR}; \
		cp -R openstack-nova/debian ${BUILDDIR}/debian; \
		(if [ '${CONTRAIL_SKU}' != 'grizzly' ]; then \
			(cp openstack-nova/debian/changelog.havana ${BUILDDIR}/debian/changelog); \
		fi); \
		(cd ${BUILDDIR}; fakeroot debian/rules binary); \
	fi

openstack-nova-clean:
	$(eval BUILDDIR=${SB_TOP}/build/openstack/nova)
	rm -rf ${BUILDDIR}

%-deb:
	$(eval PKGNAME:=$(@:openstack-%-deb=%))
	$(eval BUILDDIR=${SB_TOP}/build/openstack/${PKGNAME})
	$(eval DISTRODIR=${SB_TOP}/distro/openstack/${PKGNAME})
	if test -d ${DISTRODIR}; then \
		mkdir -p ${SB_TOP}/build/openstack; \
		cp -R ${SB_TOP}/distro/openstack/${PKGNAME} ${BUILDDIR}; \
		cp -R $(@:-deb=)/debian ${BUILDDIR}/debian; \
		(cd ${BUILDDIR}; fakeroot debian/rules binary) \
	fi

endif
%-clean:
	$(eval PKGNAME:=$(@:openstack-%-clean=%))
	$(eval BUILDDIR=${SB_TOP}/build/openstack/${PKGNAME})
	rm -rf ${BUILDDIR}
