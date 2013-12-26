PWD := ${CURDIR}
SB_TOP := $(PWD:/tools/packaging/common/debian=)

PACKAGES  = contrail-libs-deb contrail-vrouter-deb

all: ${PACKAGES}
	echo "Build complete"

clean: $(foreach pkg, ${PACKAGES}, $(pkg:-deb=-clean))
	echo "Clean"

%-deb:
	(cd $(@:-deb=); fakeroot debian/rules binary)

%-clean:
	(cd $(@:-clean=); fakeroot debian/rules clean)


contrail-vrouter-deb: contrail-libs-deb