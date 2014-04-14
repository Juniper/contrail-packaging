# view contents of rpm file: rpm -qlp <filename>.rpm


%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif

%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif

%define         _srcdir      /usr/src/vrouter-%{_relstr}

%{echo: "Building release %{_relstr}\n"}

Name:               contrail-vrouter-src-dkms
Version:            %{_verstr}
Release:            %{_relstr}%{?dist}
Summary:            Contrail vRouter source DKMS %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:           dkms

%description
Contrail Virtual Router Kernel Module Source DKMS package

BuildRequires:  systemd-units

%build
pushd %{_builddir}/..
scons -U --target=%{_target_cpu} vrouter/sandesh
popd

%prep

%install

#Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_srcdir}
install -d -m 755 %{buildroot}%{_srcdir}/dp-core
install -d -m 755 %{buildroot}%{_srcdir}/include
install -d -m 755 %{buildroot}%{_srcdir}/linux
install -d -m 755 %{buildroot}%{_srcdir}/sandesh
install -d -m 755 %{buildroot}%{_srcdir}/sandesh/gen-c
install -d -m 755 %{buildroot}%{_srcdir}/sandesh/library/
install -d -m 755 %{buildroot}%{_srcdir}/sandesh/library/c
install -d -m 755 %{buildroot}%{_srcdir}/sandesh/library/c/protocol
install -d -m 755 %{buildroot}%{_srcdir}/sandesh/library/c/transport

pushd %{_builddir}/..

echo "MAKE[0]=\"'make' -C . KERNELDIR=/lib/modules/\${kernelver}/build\"" >> %{buildroot}%{_srcdir}/dkms.conf
echo "CLEAN[0]=\"'make' -C . KERNELDIR=/lib/modules/\${kernelver}/build\"" >> %{buildroot}%{_srcdir}/dkms.conf
echo "DEST_MODULE_LOCATION[0]=\"/extra/net/vrouter\"" >> %{buildroot}%{_srcdir}/dkms.conf
echo "BUILT_MODULE_NAME[0]=\"vrouter\"" >> %{buildroot}%{_srcdir}/dkms.conf
echo "PACKAGE_NAME=vrouter" >> %{buildroot}%{_srcdir}/dkms.conf
echo "PACKAGE_VERSION=%{_relstr}" >> %{buildroot}%{_srcdir}/dkms.conf
echo "AUTOINSTALL=\"yes\"" >> %{buildroot}%{_srcdir}/dkms.conf

install -D -p -m 755 vrouter/dp-core/vnsw_ip4_mtrie.c %{buildroot}%{_srcdir}/dp-core/vnsw_ip4_mtrie.c
install -D -p -m 755 vrouter/dp-core/vr_bridge.c      %{buildroot}%{_srcdir}/dp-core/vr_bridge.c
install -D -p -m 755 vrouter/dp-core/vr_btable.c      %{buildroot}%{_srcdir}/dp-core/vr_btable.c
install -D -p -m 755 vrouter/dp-core/vr_datapath.c    %{buildroot}%{_srcdir}/dp-core/vr_datapath.c
install -D -p -m 755 vrouter/dp-core/vr_flow.c        %{buildroot}%{_srcdir}/dp-core/vr_flow.c
install -D -p -m 755 vrouter/dp-core/vr_fragment.c    %{buildroot}%{_srcdir}/dp-core/vr_fragment.c
install -D -p -m 755 vrouter/dp-core/vr_htable.c      %{buildroot}%{_srcdir}/dp-core/vr_htable.c
install -D -p -m 755 vrouter/dp-core/vr_index_table.c %{buildroot}%{_srcdir}/dp-core/vr_index_table.c
install -D -p -m 755 vrouter/dp-core/vr_interface.c   %{buildroot}%{_srcdir}/dp-core/vr_interface.c
install -D -p -m 755 vrouter/dp-core/vr_mcast.c       %{buildroot}%{_srcdir}/dp-core/vr_mcast.c
install -D -p -m 755 vrouter/dp-core/vr_message.c     %{buildroot}%{_srcdir}/dp-core/vr_message.c
install -D -p -m 755 vrouter/dp-core/vr_mirror.c      %{buildroot}%{_srcdir}/dp-core/vr_mirror.c
install -D -p -m 755 vrouter/dp-core/vr_mpls.c        %{buildroot}%{_srcdir}/dp-core/vr_mpls.c
install -D -p -m 755 vrouter/dp-core/vr_nexthop.c     %{buildroot}%{_srcdir}/dp-core/vr_nexthop.c
install -D -p -m 755 vrouter/dp-core/vrouter.c        %{buildroot}%{_srcdir}/dp-core/vrouter.c
install -D -p -m 755 vrouter/dp-core/vr_packet.c      %{buildroot}%{_srcdir}/dp-core/vr_packet.c
install -D -p -m 755 vrouter/dp-core/vr_proto_ip.c    %{buildroot}%{_srcdir}/dp-core/vr_proto_ip.c
install -D -p -m 755 vrouter/dp-core/vr_queue.c       %{buildroot}%{_srcdir}/dp-core/vr_queue.c
install -D -p -m 755 vrouter/dp-core/vr_response.c    %{buildroot}%{_srcdir}/dp-core/vr_response.c
install -D -p -m 755 vrouter/dp-core/vr_route.c       %{buildroot}%{_srcdir}/dp-core/vr_route.c
install -D -p -m 755 vrouter/dp-core/vr_sandesh.c     %{buildroot}%{_srcdir}/dp-core/vr_sandesh.c
install -D -p -m 755 vrouter/dp-core/vr_stats.c       %{buildroot}%{_srcdir}/dp-core/vr_stats.c
install -D -p -m 755 vrouter/dp-core/vr_vrf_assign.c  %{buildroot}%{_srcdir}/dp-core/vr_vrf_assign.c
install -D -p -m 755 vrouter/dp-core/vr_vxlan.c       %{buildroot}%{_srcdir}/dp-core/vr_vxlan.c

install -D -p -m 755 vrouter/include/nl_util.h        %{buildroot}%{_srcdir}/include/nl_util.h
install -D -p -m 755 vrouter/include/udp_util.h       %{buildroot}%{_srcdir}/include/udp_util.h
install -D -p -m 755 vrouter/include/ulinux.h         %{buildroot}%{_srcdir}/include/ulinux.h
install -D -p -m 755 vrouter/include/vhost.h          %{buildroot}%{_srcdir}/include/vhost.h
install -D -p -m 755 vrouter/include/vnsw_ip4_mtrie.h %{buildroot}%{_srcdir}/include/vnsw_ip4_mtrie.h
install -D -p -m 755 vrouter/include/vr_bridge.h      %{buildroot}%{_srcdir}/include/vr_bridge.h
install -D -p -m 755 vrouter/include/vr_btable.h      %{buildroot}%{_srcdir}/include/vr_btable.h
install -D -p -m 755 vrouter/include/vr_compat.h      %{buildroot}%{_srcdir}/include/vr_compat.h
install -D -p -m 755 vrouter/include/vr_defs.h        %{buildroot}%{_srcdir}/include/vr_defs.h
install -D -p -m 755 vrouter/include/vr_flow.h        %{buildroot}%{_srcdir}/include/vr_flow.h
install -D -p -m 755 vrouter/include/vr_fragment.h    %{buildroot}%{_srcdir}/include/vr_fragment.h
install -D -p -m 755 vrouter/include/vr_genetlink.h   %{buildroot}%{_srcdir}/include/vr_genetlink.h
install -D -p -m 755 vrouter/include/vr_hash.h        %{buildroot}%{_srcdir}/include/vr_hash.h
install -D -p -m 755 vrouter/include/vr_htable.h      %{buildroot}%{_srcdir}/include/vr_htable.h
install -D -p -m 755 vrouter/include/vr_index_table.h %{buildroot}%{_srcdir}/include/vr_index_table.h
install -D -p -m 755 vrouter/include/vr_interface.h   %{buildroot}%{_srcdir}/include/vr_interface.h
install -D -p -m 755 vrouter/include/vr_linux.h       %{buildroot}%{_srcdir}/include/vr_linux.h
install -D -p -m 755 vrouter/include/vr_mcast.h       %{buildroot}%{_srcdir}/include/vr_mcast.h
install -D -p -m 755 vrouter/include/vr_message.h     %{buildroot}%{_srcdir}/include/vr_message.h
install -D -p -m 755 vrouter/include/vr_mirror.h      %{buildroot}%{_srcdir}/include/vr_mirror.h
install -D -p -m 755 vrouter/include/vr_mpls.h        %{buildroot}%{_srcdir}/include/vr_mpls.h
install -D -p -m 755 vrouter/include/vr_nexthop.h     %{buildroot}%{_srcdir}/include/vr_nexthop.h
install -D -p -m 755 vrouter/include/vr_os.h          %{buildroot}%{_srcdir}/include/vr_os.h
install -D -p -m 755 vrouter/include/vrouter.h        %{buildroot}%{_srcdir}/include/vrouter.h
install -D -p -m 755 vrouter/include/vr_packet.h      %{buildroot}%{_srcdir}/include/vr_packet.h
install -D -p -m 755 vrouter/include/vr_proto.h       %{buildroot}%{_srcdir}/include/vr_proto.h
install -D -p -m 755 vrouter/include/vr_queue.h       %{buildroot}%{_srcdir}/include/vr_queue.h
install -D -p -m 755 vrouter/include/vr_response.h    %{buildroot}%{_srcdir}/include/vr_response.h
install -D -p -m 755 vrouter/include/vr_route.h       %{buildroot}%{_srcdir}/include/vr_route.h
install -D -p -m 755 vrouter/include/vr_sandesh.h     %{buildroot}%{_srcdir}/include/vr_sandesh.h
install -D -p -m 755 vrouter/include/vr_vxlan.h       %{buildroot}%{_srcdir}/include/vr_vxlan.h

install -D -p -m 755 vrouter/linux/vhost_dev.c        %{buildroot}%{_srcdir}/linux/vhost_dev.c
install -D -p -m 755 vrouter/linux/vr_genetlink.c     %{buildroot}%{_srcdir}/linux/vr_genetlink.c
install -D -p -m 755 vrouter/linux/vr_host_interface.c \
                                                      %{buildroot}%{_srcdir}/linux/vr_host_interface.c
install -D -p -m 755 vrouter/linux/vr_mem.c           %{buildroot}%{_srcdir}/linux/vr_mem.c
install -D -p -m 755 vrouter/linux/vrouter_mod.c      %{buildroot}%{_srcdir}/linux/vrouter_mod.c

install -D -p -m 755 build/debug/vrouter/sandesh/gen-c/vr_types.c \
                                                      %{buildroot}%{_srcdir}/sandesh/gen-c/vr_types.c
install -D -p -m 755 build/debug/vrouter/sandesh/gen-c/vr_types.h \
                                                      %{buildroot}%{_srcdir}/sandesh/gen-c/vr_types.h

install -D -p -m 755 tools/sandesh//library/c/sandesh.c \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/sandesh.c
install -D -p -m 755 tools/sandesh/library/c/sandesh.h \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/sandesh.h
install -D -p -m 755 tools/sandesh/library/c/thrift.h %{buildroot}%{_srcdir}/sandesh/library/c/thrift.h

install -D -p -m 755 tools/sandesh/library/c/protocol/thrift_binary_protocol.c \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/protocol/thrift_binary_protocol.c
install -D -p -m 755 tools/sandesh/library/c/protocol/thrift_binary_protocol.h \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/protocol/thrift_binary_protocol.h
install -D -p -m 755 tools/sandesh/library/c/protocol/thrift_protocol.c \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/protocol/thrift_protocol.c
install -D -p -m 755 tools/sandesh/library/c/protocol/thrift_protocol.h \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/protocol/thrift_protocol.h

install -D -p -m 755 tools/sandesh/library/c/transport/thrift_fake_transport.c \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/transport/thrift_fake_transport.c
install -D -p -m 755 tools/sandesh/library/c/transport/thrift_fake_transport.h \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/transport/thrift_fake_transport.h
install -D -p -m 755 tools/sandesh/library/c/transport/thrift_memory_buffer.c \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/transport/thrift_memory_buffer.c
install -D -p -m 755 tools/sandesh/library/c/transport/thrift_memory_buffer.h \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/transport/thrift_memory_buffer.h
install -D -p -m 755 tools/sandesh/library/c/transport/thrift_transport.c \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/transport/thrift_transport.c
install -D -p -m 755 tools/sandesh/library/c/transport/thrift_transport.h \
                                                      %{buildroot}%{_srcdir}/sandesh/library/c/transport/thrift_transport.h

install -D -p -m 755 vrouter/Makefile                 %{buildroot}%{_srcdir}/Makefile

popd


%post
cd /usr/src/vrouter-%{_relstr}
dkms add -m vrouter -v %{_relstr}

%preun
cd /usr/src/vrouter-%{_relstr}
dkms remove -m vrouter -v %{_relstr} --all
make clean
rm -rf /usr/src/vrouter-%{_relstr}

%files
%defattr(-,root,root,-)

%{_srcdir}/dp-core/vnsw_ip4_mtrie.c
%{_srcdir}/dp-core/vr_bridge.c
%{_srcdir}/dp-core/vr_btable.c
%{_srcdir}/dp-core/vr_datapath.c
%{_srcdir}/dp-core/vr_flow.c
%{_srcdir}/dp-core/vr_fragment.c
%{_srcdir}/dp-core/vr_htable.c
%{_srcdir}/dp-core/vr_index_table.c
%{_srcdir}/dp-core/vr_interface.c
%{_srcdir}/dp-core/vr_mcast.c
%{_srcdir}/dp-core/vr_message.c
%{_srcdir}/dp-core/vr_mirror.c
%{_srcdir}/dp-core/vr_mpls.c
%{_srcdir}/dp-core/vr_nexthop.c
%{_srcdir}/dp-core/vrouter.c
%{_srcdir}/dp-core/vr_packet.c
%{_srcdir}/dp-core/vr_proto_ip.c
%{_srcdir}/dp-core/vr_queue.c
%{_srcdir}/dp-core/vr_response.c
%{_srcdir}/dp-core/vr_route.c
%{_srcdir}/dp-core/vr_sandesh.c
%{_srcdir}/dp-core/vr_stats.c
%{_srcdir}/dp-core/vr_vrf_assign.c
%{_srcdir}/dp-core/vr_vxlan.c

%{_srcdir}/include/nl_util.h
%{_srcdir}/include/udp_util.h
%{_srcdir}/include/ulinux.h
%{_srcdir}/include/vhost.h
%{_srcdir}/include/vnsw_ip4_mtrie.h
%{_srcdir}/include/vr_bridge.h
%{_srcdir}/include/vr_btable.h
%{_srcdir}/include/vr_compat.h
%{_srcdir}/include/vr_defs.h
%{_srcdir}/include/vr_flow.h
%{_srcdir}/include/vr_fragment.h
%{_srcdir}/include/vr_genetlink.h
%{_srcdir}/include/vr_hash.h
%{_srcdir}/include/vr_htable.h
%{_srcdir}/include/vr_index_table.h
%{_srcdir}/include/vr_interface.h
%{_srcdir}/include/vr_linux.h
%{_srcdir}/include/vr_mcast.h
%{_srcdir}/include/vr_message.h
%{_srcdir}/include/vr_mirror.h
%{_srcdir}/include/vr_mpls.h
%{_srcdir}/include/vr_nexthop.h
%{_srcdir}/include/vr_os.h
%{_srcdir}/include/vrouter.h
%{_srcdir}/include/vr_packet.h
%{_srcdir}/include/vr_proto.h
%{_srcdir}/include/vr_queue.h
%{_srcdir}/include/vr_response.h
%{_srcdir}/include/vr_route.h
%{_srcdir}/include/vr_sandesh.h
%{_srcdir}/include/vr_vxlan.h

%{_srcdir}/linux/vhost_dev.c
%{_srcdir}/linux/vr_genetlink.c
%{_srcdir}/linux/vr_host_interface.c
%{_srcdir}/linux/vr_mem.c
%{_srcdir}/linux/vrouter_mod.c

%{_srcdir}/sandesh/gen-c/vr_types.c
%{_srcdir}/sandesh/gen-c/vr_types.h
%{_srcdir}/sandesh/library/c/sandesh.c
%{_srcdir}/sandesh/library/c/sandesh.h
%{_srcdir}/sandesh/library/c/thrift.h
%{_srcdir}/sandesh/library/c/protocol/thrift_binary_protocol.c
%{_srcdir}/sandesh/library/c/protocol/thrift_binary_protocol.h
%{_srcdir}/sandesh/library/c/protocol/thrift_protocol.c
%{_srcdir}/sandesh/library/c/protocol/thrift_protocol.h
%{_srcdir}/sandesh/library/c/transport/thrift_fake_transport.c
%{_srcdir}/sandesh/library/c/transport/thrift_fake_transport.h
%{_srcdir}/sandesh/library/c/transport/thrift_memory_buffer.c
%{_srcdir}/sandesh/library/c/transport/thrift_memory_buffer.h
%{_srcdir}/sandesh/library/c/transport/thrift_transport.c
%{_srcdir}/sandesh/library/c/transport/thrift_transport.h

%{_srcdir}/Makefile
%{_srcdir}/dkms.conf

%changelog

