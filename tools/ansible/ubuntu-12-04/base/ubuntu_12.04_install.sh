#!/bin/sh
#
# Package needed for contrail build on ubuntu precise (12.04)
# Definitely a work in progress.
# TODO:
#   - Move all linux-headers-${ver} to LINUX_HEADERS for easier tracking
#   - Remove =${ver} where possible
#   - Are explicit versions really required? Get rid of them
#   - Change scp for /cs-shared to use mount and rsync
#
export DEBIAN_FRONTEND=noninteractive
apt-get update -y

# Not (yet) used, move all linux-headers entries here.
LINUX_HDRS="linux-headers-3.13.0-34 linux-headers-3.13.0-34-generic"
LINUX_HDRS="$LINUX_HDRS linux-headers-3.13.0-24-generic"
LINUX_HDRS="$LINUX_HDRS linux-headers-3.13.0-35-generic"

apt-get install -y \
	git \
	xml-core=0.13 \
	python-lxml=2.3.2-1 \
	python-setuptools=0.6.24-1ubuntu1 \
	python-sphinx=1.1.3+dfsg-2ubuntu2.1 \
	python-pycurl=7.19.0-4ubuntu3 \
	automake=1:1.11.3-1ubuntu2 \
	bison=1:2.5.dfsg-2.1 \
	devscripts=2.11.6ubuntu1.6 \
	fakeroot=1.18.2-1 \
	libevent-dev=2.0.16-stable-1 \
	libxml2-dev \
	libxslt1-dev=1.1.26-8ubuntu1.3 \
	nfs-common \
	scons=2.1.0-1 \
	sysv-rc-conf=0.99-6 \
	xml-core=0.13 \
	scons=2.1.0-1 \
	gcc=4:4.6.3-1ubuntu5 \
	flex=2.5.35-10ubuntu3 \
	bison=1:2.5.dfsg-2.1 \
	make=3.81-8.1ubuntu1.1 \
	automake=1:1.11.3-1ubuntu2 \
	fakeroot=1.18.2-1 \
	dh-make=0.59ubuntu1 \
	fabric=1.3.2-5 \
	ant=1.8.2-4build1 \
	openjdk-6-jdk \
	alien=8.86 \
	python-eventlet=0.9.16-1ubuntu4.2 \
	python-paste=1.7.5.1-4ubuntu2 \
	pkg-config=0.26-1ubuntu1 \
	python-lxml=2.3.2-1 \
	python-pip=1.0-1build1 \
	python-setuptools=0.6.24-1ubuntu1 \
	python-sphinx=1.1.3+dfsg-2ubuntu2.1 \
	pkg-config=0.26-1ubuntu1 \
	python-pip=1.0-1build1 \
	python-virtualenv=1.7.1.2-1 \
	curl \
	debhelper=9.20120115ubuntu3 \
	cdbs=0.4.100ubuntu2 \
	libreadline-dev=6.2-8 \
	libavahi-client-dev=0.6.30-5ubuntu2.1 \
	open-iscsi-utils=2.0.871-0ubuntu9.12.04.2 \
	libdevmapper-dev=2:1.02.48-4ubuntu7.4 \
	libudev-dev \
	libpciaccess-dev=0.12.902-1ubuntu0.2 \
	policykit-1=0.104-1ubuntu1.1 \
	libcap-ng-dev=0.6.6-1ubuntu1 \
	libnl-3-dev=3.2.3-2ubuntu2 \
	libyajl-dev=1.0.12-2 \
	radvd=1:1.8.3-2 \
	python-software-properties=0.82.7.7 \
	libxml2-utils \
	libapparmor-dev \
	linux-headers-3.2.0-51=3.2.0-51.77 \
	linux-headers-3.2.0-58=3.2.0-58.88 \
	linux-headers-3.2.0-51-generic=3.2.0-51.77 \
	linux-headers-3.2.0-58-generic=3.2.0-58.88 \
	linux-headers-3.8.0-35=3.8.0-35.52~precise1 \
	linux-headers-3.8.0-35-generic=3.8.0-35.52~precise1 \
	linux-headers-3.8.0-31=3.8.0-31.46~precise1 \
	linux-headers-3.8.0-31-generic=3.8.0-31.46~precise1 \
	linux-headers-3.13.0-24=3.13.0-24.47~precise2 \
	linux-headers-3.13.0-24-generic=3.13.0-24.47~precise2 \
	linux-headers-3.13.0-34=3.13.0-34.60~precise1 \
	linux-headers-3.13.0-34-generic=3.13.0-34.60~precise1 \
	linux-headers-3.13.0-35-generic \
	dnsmasq-base=2.59-4ubuntu0.1 \
	libc6-dev \
	libcurl4-openssl-dev \
	build-essential=11.5ubuntu2.1 \
	libnuma-dev=2.0.8~rc3-1 \
	libpcap0.8-dev=1.1.1-10 \
	libpolkit-gobject-1-dev=0.104-1ubuntu1.1 \
	uuid-dev=2.20.1-1ubuntu3 \
	libparted0-dev \
	libgcrypt11-dev \
	libxen-dev \
	libsasl2-dev=2.1.25.dfsg1-3ubuntu0.1 \
	libbz2-dev=1.0.6-1 \
	g++=4:4.6.3-1ubuntu5 \
	libncurses5-dev=5.9-4 \
	libgnutls-dev \
	libtool=2.4.2-1ubuntu1 \
	libssl-dev \
	libcppunit-1.12-1=1.12.1-4 \
	libmount1=2.20.1-1ubuntu3 \
	python-all-dev=2.7.3-0ubuntu2.2 \
	python-dev=2.7.3-0ubuntu2.2 \
	sshpass=1.05-1 \
	linux-headers-3.11.0-22=3.11.0-22.38~precise1 \
	linux-headers-3.11.0-22-generic=3.11.0-22.38~precise1 \
	javahelper=0.40ubuntu1.1 \
	quilt=0.50-2 \
	liblog4j1.2-java=1.2.16-3ubuntu1 \
	libhttpcore-java=4.1.4-1 \
	libcommons-codec-java=1.5-1 \
	ruby-ronn=0.7.3-1 \
	module-assistant=0.11.4 \
	default-jdk=1:1.6-43ubuntu2 \
	libprotobuf7=2.4.1-1ubuntu2 \
	libprotoc7=2.4.1-1ubuntu2 \
	protobuf-compiler=2.4.1-1ubuntu2 \
	libprotobuf-lite7=2.4.1-1ubuntu2 \
	libprotobuf-dev=2.4.1-1ubuntu2 \
	linux-headers-3.11.0-22=3.11.0-22.38~precise1 \
	linux-headers-3.11.0-22-generic=3.11.0-22.38~precise1 \
	libcurl4-openssl-dev \
	libboost-dev=1.48.0.2 \
	google-mock=1.6.0-0ubuntu1 \
	libgoogle-perftools-dev=1.7-1ubuntu1 \
	libgtest-dev=1.6.0-1ubuntu4 \
	libhiredis-dev=0.10.1-2 \
	liblog4cplus-dev=1.0.4-1 \
	libtbb-dev=4.0+r233-1 \
	libicu-dev=4.8.1.1-3ubuntu0.1 \
	libxml2-dev \
	libcurl4-openssl-dev libxml2-utils \
	libxen-dev \
	lvm2=2.02.66-4ubuntu7.4 \
	libparted0-dev=2.3-8ubuntu5.2 \
	libapparmor-dev=2.7.102-0ubuntu3.10

#apt-get -y install libxml2-dev=2.7.8.dfsg-5.1ubuntu4.9 \
#apt-get -y install libxen-dev=4.1.5-0ubuntu0.12.04.2 \
#apt-get -y install lvm2=2.02.66-4ubuntu7.3 \
#apt-get -y install libparted0-dev=2.3-8ubuntu5.1 \
#apt-get -y install libapparmor-dev=2.7.102-0ubuntu3.9 \

[ -d /usr/local/bin ] || mkdir -p /usr/local/bin

if [ ! -r /usr/local/bin/repo ]; then
    echo info: installing /usr/local/bin/repo
    curl https://storage.googleapis.com/git-repo-downloads/repo > /usr/local/bin/repo
    chmod 755 /usr/local/bin/repo
fi

if [ ! -r /usr/local/bin/python2.7 ]; then
    echo info: Creating /usr/local/bin/python2.7 symlink
    ln -s /usr/bin/python2.7 /usr/local/bin/python2.7
fi

# Need to use scp, and nullify the first-time unknown host issue
if [ ! -d /cs-shared/builder/cache ]; then
    echo info: Creating package cache: \"/cs-shared/builder/cache/ubuntu1204\"

    mkdir -p /cs-shared/builder/cache

    password=Juniper1
    server=root@contrail-ec-build14.juniper.net
    path=/volume/contrail/distro-packages/build/ubuntu1204
    # sshpass -p $password rsync -Ah --exclude=.git ${server}:${path} /cs-shared/builder/cache
    sshpass -p $password scp -pr -o StrictHostKeyChecking=no -q ${server}:${path} /cs-shared/builder/cache
    (cd /cs-shared/builder/cache && ln -s ubuntu1204 ubuntu-12-04)
fi

#Install libipfix from /cs-shared/builder/cache/ubuntu1404
dpkg -i /cs-shared/builder/cache/ubuntu1204/juno/libipfix_110209-1-0ubuntu0.12.04_amd64.deb

