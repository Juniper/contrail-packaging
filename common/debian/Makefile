PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/common/debian=)
VENV_SPEC_DIR := $(SB_TOP)/distro/python-venv-packaging/DEBIAN

VENV = contrail-api-venv
PACKAGES = contrail-libs-deb contrail-vrouter-deb contrail-config-deb \
	contrail-control-deb

all: ${PACKAGES} ${VENV}
	echo "Build complete"

clean: $(PACKAGES:%-deb=%-clean) $(VENV:%=%-clean)
	echo "Clean"

%-deb:
	(cd $(@:-deb=); fakeroot debian/rules binary)

%-venv:
	(cd $(VENV_SPEC_DIR)/$@; fakeroot debian/rules binary)

%-venv-clean:
	(cd $(VENV_SPEC_DIR)/$(@:-clean=); fakeroot debian/rules clean)

%-clean:
	(cd $(@:-clean=); fakeroot debian/rules clean)


contrail-vrouter-deb: contrail-libs-deb
contrail-config-deb: contrail-api-venv