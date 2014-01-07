%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
Release:	    %{_relstr}%{?dist}
Summary: Contrail Openstack Storage %{?_gitVer}
Name: contrail-openstack-storage
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

%if 0%{?rhel}
Requires: epel-release
%endif
%if 0%{?fedora >= 17}
Requires: hdparm
Requires: ntp
%endif

Requires: snappy
Requires: leveldb
Requires: gdisk
Requires: python-argparse
Requires: gperftools-libs
Requires: ceph-deploy
Requires: pushy
Requires: ceph
Requires: ceph-devel
Requires: usbredir

%if 0%{?rhel}
Requires: qemu-kvm
Requires: qemu-guest-agent
Requires: qemu-guest-agent-win32
Requires: qemu-kvm-tools
%endif

%if 0%{?fedora >= 17}
Requires: ntp
%endif
# Now configure NTP

%if 0%{?fedora >= 17}
Requires: glib2-devel
Requires: make
Requires: autoconf
Requires: automake
Requires: libtool
Requires: zlib-devel
%endif

# make install QEMU

Requires: libvirt

Requires: python-cinder
Requires: openstack-cinder

%description
Contrail Package Requirements for Storage

%files

%changelog
* Fri Nov  8 2013 <mnishimoto@juniper.net>
* Initial build.

