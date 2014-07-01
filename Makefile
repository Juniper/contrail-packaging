# Master Makefile to build packages based on platform or feature. Make targets in this Makefile will
# trigger make commands in different directories. 
#
# Macros
# TAG               BUILD TAG. e.g. 1234
# CONTRAIL_SKU      SKU NAME. e.g. grizzly/havana
# PACKAGE_FILE      File containing list of packages to be packaged
#                   e.g. ubuntu1204-havana-contrail - contains list of contrail maked packages to be packaged
#                   e.g. ubuntu1204-havana-thirdparty - contains list of thirdparty packages downloaded
#                                                       from internet along with md5 sum to be packaged
# OS_VERSION        Linux dist version info. eg. ubuntu1204, ubuntu-12-04
# PACKAGE_DIRS      Location where packages are available
#

DISTRO := $(shell python -c "import platform;print platform.linux_distribution()[0].replace(' ', '').lower()")
SB_TOP := $(PWD:/tools/packaging=)

ifdef OS_VERSION
export OS_VER = $(shell echo $(OS_VERSION) | sed 's,[-|.],,g')
else
export OS_VER = $(shell PYTHONPATH=$(PYTHONPATH):$(SB_TOP)/tools/packaging/build/ python -c "import package_utils; print package_utils.get_platform()")
endif

ifndef TAG
export TAG := $(shell python -c "from random import randint; print randint(99, 9999)")
$(info Using TAG = $(TAG))
endif

ifndef CONTRAIL_SKU
export CONTRAIL_SKU := $(shell grep -oP '<label name="sku" value="\K\w+' $(SB_TOP)/.repo/manifest.xml)
$(info Using CONTRAIL_SKU = $(CONTRAIL_SKU))
endif

ifndef PACKAGE_FILE
PACKAGE_FILE := $(SB_TOP)/tools/packaging/package_configs/$(OS_VER)-$(CONTRAIL_SKU)-contrail
$(info Using PACKAGE_FILE = $(PACKAGE_FILE))
endif

detect-os: $(DISTRO)


######################## INDIVIDUAL MAKE TARGETS OF CENTOS PLATFORM ###############################

centos-contrail-thirdparty:
	@echo -e "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "CENTOS: making third party rpms" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/third_party; make all || (echo "CENTOS: make thirdpaty packages FAILED"; exit 1)

centos-openstack:
	@echo -e "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "CENTOS: openstack rpms" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/openstack/centos_64; make all || (echo "CENTOS: make openstack packages FAILED"; exit 1)

centos-contrail:
	@echo -e "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "CENTOS: contrail rpms" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/common/rpm; make FILE_LIST=$(PACKAGE_FILE) all || (echo "CENTOS: make contrail packages FAILED"; exit 1)

centos-install-packages:
	@echo -e "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "CENTOS: make contrail-install-packages" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/common/rpm; make contrail-install-packages || (echo "CENTOS: make contrail-install-packages FAILED"; exit 1)

centos-thirdparty-packages:
	@echo -e "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "CENTOS: make contrail-thirdparty-packages" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/common/rpm; make contrail-thirdparty-packages || (echo "CENTOS: make contrail-install-packages FAILED"; exit 1)

######################## INDIVIDUAL MAKE TARGETS OF UBUNTU PLATFORM ###############################

ubuntu-openstack:
	@echo "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "UBUNTU: making openstack deb" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/openstack/debian; make all || (echo "UBUNTU: make openstack FAILED"; exit 1)

ubuntu-contrail:
	@echo "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "UBUNTU: making contrail-thirdparty and contrail deb" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/common/debian; make FILE_LIST=$(PACKAGE_FILE) all || (echo "UBUNTU: make contrail or thirdparty FAILED"; exit 1)

ubuntu-install-packages:
	@echo "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "UBUNTU: make contrail-install-packages" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/common/debian; make contrail-install-packages-deb || (echo "UBUNTU: make contrail-install-packages FAILED"; exit 1)

ubuntu-thirdparty-packages:
	@echo "\n\n *** Executing Make Procedures of $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	@echo "UBUNTU: make contrail-thirdparty-packages" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd $(SB_TOP)/tools/packaging/common/debian; make contrail-thirdparty-packages-deb || (echo "UBUNTU: make contrail-install-packages FAILED"; exit 1)

ubuntu-storage-packages:
	@echo "\n\n *** Executing Make Procedures for $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd storage/debian; make all || (echo "UBUNTU: make ubuntu-storage packages FAILED"; exit 1)

ubuntu-storage-install-packages:
	@echo "\n\n *** Executing Make Procedures for $@ *** \n\n" | gawk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $$0 }'
	cd storage/debian; make contrail-storage-packages-deb || (echo "UBUNTU: make ubuntu-storage-install-packages FAILED"; exit 1)

ubuntu-storage:
ifeq ($(CONTRAIL_SKU), havana)
	make ubuntu-storage-packages ubuntu-storage-install-packages
else
	@echo "UBUNTU-STORAGE: Grizzly is not supported yet"
endif


######################## INDIVIDUAL MAKE TARGETS OF FEDORA PLATFORM ###############################

fedora:
	@echo -e "\n\n *** Executing Make Procedures of $@ *** \n\n"
	@echo "FEDORA: making third party rpms"
	cd third_party; make all;
	@echo "FEDORA: making openstack rpms"
	cd openstack/centos_64; make all;
	@echo "FEDORA: making contrail rpms"
	cd common/rpm; make all;
	@echo "FEDORA: ALL MAKEs SUCCEEDED"

######################## INDIVIDUAL MAKE TARGETS OF REDHAT PLATFORM ###############################

redhatenterpriselinuxserver: redhat
redhat:
	@echo -e "\n\n *** Executing Make Procedures of $@ *** \n\n"
	@echo "REDHAT: making third party rpms"
	cd third_party; make all;
	@echo "REDHAT: making openstack rpms"
	cd openstack/centos_64; make all;
	@echo "REDHAT: making contrail rpms"
	cd common/rpm; make all;
	@echo "REDHAT: ALL MAKEs SUCCEEDED"

####################### COPY TO ARTIFACTS #######################################
post-exec:
	$(eval ARTIFACTS_DIR=$(SB_TOP)/build/artifacts/)
	@mkdir -p $(ARTIFACTS_DIR)
	@echo "Copying built packages to artifacts dir"
	@$(SB_TOP)/tools/packaging/build/copy_packages_to_artifacts.py --source-dirs $(ALL_PKGS_DIRS) \
								      --destination-dir $(ARTIFACTS_DIR)
	exit $(MAKE_STATUS)


######################## MAKE TARGETS OF PLATFORMS ###############################

ubuntu:
	make ubuntu-openstack ubuntu-contrail ubuntu-install-packages ubuntu-thirdparty-packages ubuntu-storage ; \
	make post-exec ALL_PKGS_DIRS="$(SB_TOP)/build/debian $(SB_TOP)/build/openstack $(SB_TOP)/build/packages/" MAKE_STATUS=$$?

centos:
	make centos-contrail-thirdparty centos-openstack centos-contrail centos-install-packages centos-thirdparty-packages ; \
	make post-exec ALL_PKGS_DIRS="$(SB_TOP)/controller/build/package-build/RPMS/noarch $(SB_TOP)/controller/build/package-build/RPMS/x86_64" MAKE_STATUS=$$?
