PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/openstack/debian=)

PACKAGES = openstack-neutron-deb

%-deb:
	$(eval PKGNAME:=$(@:openstack-%-deb=%))
	$(eval BUILDDIR=${SB_TOP}/build/openstack/${PKGNAME})
	cp -R ${SB_TOP}/distro/openstack/${PKGNAME} ${BUILDDIR}
	cp -R $(@:-deb=)/debian ${BUILDDIR}/debian
	(cd ${BUILDDIR}; fakeroot debian/rules binary)

%-clean:
	$(eval PKGNAME:=$(@:openstack-%-clean=%))
	$(eval BUILDDIR=${SB_TOP}/build/openstack/${PKGNAME})
	rm -rf ${BUILDDIR}

