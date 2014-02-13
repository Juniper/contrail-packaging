# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailetc /etc/contrail
%define         _servicedir  /usr/lib/systemd/system
%define         _supervisordir /etc/contrail/supervisord_vrouter_files
%define         _distropkgdir tools/packaging/common/control_files
%define         _controllersrcdir controller/src 

%if 0%{?_kernel_dir:1}
%define         _osVer	%(cat %{_kernel_dir}/include/linux/utsrelease.h | cut -d'"' -f2)
%else
%define         _osVer       %(uname -r)
%endif
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

%if 0%(grep -c Xen /etc/redhat-release)
%define		dist	.xen
%endif

%{echo: "Building release %{_relstr}\n"}

Name:		    contrail-vrouter
Version:	    %{_verstr}
Release:	    %{_relstr}%{?dist}
Summary:	    Contrail vRouter %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

Requires:	    sudo
Requires:	    patch
Requires:	    libcurl
Requires:	    contrail-libs
%if 0%(if [ "%{dist}" != ".xen" ]; then echo 1; fi)
Requires:           supervisor
Requires:           contrail-vrouter-venv
Requires:           xmltodict
%define _venv_root    /opt/contrail/vrouter-venv
%define _venvtr       --prefix=%{_venv_root}

%define _pyver        %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%define _pysitepkg    /lib/python%{_pyver}/site-packages

%endif

%description
Contrail Virtual Router package

BuildRequires:  systemd-units

%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}

# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=contrail-controller
grep $gitrepo .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "please run rpmbuild from ctrlplane git tree"
    exit -1
fi


%build

if [ %{?_kernel_dir} ]; then
    OPT_KERNEL="--kernel-dir=%{_kernel_dir}"
fi

scons -U --target=%{_target_cpu} ${OPT_KERNEL} src/vnsw/agent:vnswad
pushd %{_builddir}/..
scons -U --target=%{_target_cpu} ${OPT_KERNEL} vrouter
scons -U --target=%{_target_cpu} ${OPT_KERNEL} vrouter/utils
popd

%if 0%(if [ "%{dist}" != ".xen" ]; then echo 1; fi)
scons -U src/sandesh/common
pushd %{_builddir}/../tools/
scons -U sandesh/library/python:pysandesh
popd
scons -U src/discovery
scons -U --target=%{_target_cpu} ${OPT_KERNEL} src/vnsw/agent/uve
%endif

%install

# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_servicedir}
%if 0%(if [ "%{dist}" != ".xen" ]; then echo 1; fi)
install -d -m 755 %{buildroot}%{_supervisordir}
%endif
install -d -m 755 %{buildroot}/lib/modules/%{_osVer}/extra/net/vrouter

# install bin files
pushd %{_builddir}/..
install -p -m 755 build/debug/vrouter/utils/flow        %{buildroot}%{_bindir}/flow
install -p -m 755 build/debug/vrouter/utils/vif         %{buildroot}%{_bindir}/vif
install -p -m 755 build/debug/vrouter/utils/mirror      %{buildroot}%{_bindir}/mirror
install -p -m 755 build/debug/vrouter/utils/mpls        %{buildroot}%{_bindir}/mpls
install -p -m 755 build/debug/vrouter/utils/nh          %{buildroot}%{_bindir}/nh
install -p -m 755 build/debug/vrouter/utils/rt          %{buildroot}%{_bindir}/rt
install -p -m 755 build/debug/vrouter/utils/vrfstats    %{buildroot}%{_bindir}/vrfstats
install -p -m 755 build/debug/vrouter/utils/dropstats    %{buildroot}%{_bindir}/dropstats
install -p -m 755 build/debug/vrouter/utils/vxlan       %{buildroot}%{_bindir}/vxlan
install -p -m 755 build/debug/vnsw/agent/vnswad         %{buildroot}%{_bindir}/vnswad

# install etc files
if [ "%{?dist}" != ".xen" ]; then
install -p -m 644 %{_distropkgdir}/agent.conf               %{buildroot}%{_contrailetc}/rpm_agent.conf
install -p -m 644 %{_distropkgdir}/vrouter.conf             %{buildroot}%{_contrailetc}/vrouter.conf

install -p -m 755 %{_distropkgdir}/vnagent_ExecStartPre.sh  %{buildroot}%{_contrailetc}/vnagent_ExecStartPre.sh
install -p -m 755 %{_distropkgdir}/vnagent_ExecStartPost.sh %{buildroot}%{_contrailetc}/vnagent_ExecStartPost.sh
install -p -m 755 %{_distropkgdir}/vnagent_ExecStopPost.sh  %{buildroot}%{_contrailetc}/vnagent_ExecStopPost.sh
install -p -m 755 %{_distropkgdir}/vnagent_param_setup.sh   %{buildroot}%{_contrailetc}/vnagent_param_setup.sh
install -p -m 755 %{_distropkgdir}/contrail_reboot          %{buildroot}%{_contrailetc}/contrail_reboot
install -p -m 755 %{_distropkgdir}/supervisor-vrouter.service %{buildroot}%{_servicedir}/supervisor-vrouter.service
else
install -D -m 755 %{_distropkgdir}/contrail-vrouter	%{buildroot}/etc/init.d/contrail-vrouter
fi

%if 0%{?fedora} >= 17
install -D -m 755 %{_distropkgdir}/supervisor-vrouter.initd %{buildroot}/etc/init.d/supervisor-vrouter
install -p -m 755 %{_distropkgdir}/contrail-vrouter.initd.supervisord %{buildroot}/etc/init.d/contrail-vrouter
%endif

%if 0%{?rhel}
install -D -m 755 %{_distropkgdir}/supervisor-vrouter.initd %{buildroot}/etc/init.d/supervisor-vrouter
install -p -m 755 %{_distropkgdir}/contrail-vrouter.initd.supervisord %{buildroot}/etc/init.d/contrail-vrouter
%endif

# install others
install -p -m 755 vrouter/vrouter.ko   %{buildroot}/lib/modules/%{_osVer}/extra/net/vrouter/vrouter.ko

%if 0%(if [ "%{dist}" != ".xen" ]; then echo 1; fi)
# install .ini files for supervisord
install -p -m 755 %{_distropkgdir}/supervisord_vrouter.conf %{buildroot}%{_contrailetc}/supervisord_vrouter.conf
install -p -m 755 %{_distropkgdir}/contrail-vrouter.ini %{buildroot}%{_supervisordir}/contrail-vrouter.ini
install -p -m 755 %{_distropkgdir}/contrail-vrouter.rules %{buildroot}%{_supervisordir}/contrail-vrouter.rules
install -p -m 755 %{_distropkgdir}/supervisord_wrapper_scripts/contrail-vrouter.kill %{buildroot}%{_supervisordir}/contrail-vrouter.kill
%endif

# install pysandesh files
%if 0%(if [ "%{dist}" != ".xen" ]; then echo 1; fi)
%define _build_dist %{_builddir}/../build/debug
install -d -m 755 %{buildroot}%{_venv_root}
install -d -m 755 %{buildroot}%{_venv_root}/bin

install -p -m 755 %{_distropkgdir}/contrail-nodemgr.py %{buildroot}%{_venv_root}/bin/contrail-nodemgr
install -p -m 755 %{_controllersrcdir}/vnsw/agent/uve/mock_generator.py %{buildroot}%{_venv_root}/bin/mock_generator
install -p -m 755 %{_controllersrcdir}/vnsw/agent/uve/run_mock_generator %{buildroot}%{_venv_root}/bin/run_mock_generator

mkdir -p build/python_dist
pushd build/python_dist

tar zxf %{_build_dist}/vnsw/agent/uve/dist/vrouter-0.1dev.tar.gz
pushd vrouter-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
install -d -m 755 %{buildroot}/usr/share/doc/python-vrouter
if [ -d doc ]; then
   cp -R doc/* %{buildroot}/usr/share/doc/python-vrouter
fi
popd
tar zxf %{_build_dist}/sandesh/common/dist/sandesh-common-0.1dev.tar.gz
pushd sandesh-common-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd
tar zxf %{_build_dist}/tools/sandesh/library/python/dist/sandesh-0.1dev.tar.gz
pushd sandesh-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd
tar zxf %{_build_dist}/discovery/dist/discovery-0.1dev.tar.gz 
pushd discovery-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd
%endif

%post
%if 0%{?fedora} >= 17
/bin/systemctl daemon-reload
%endif

%if 0%{?fedora} >= 17 || 0%{?rhel}
# patch ifup-eth
#if [ $1 -eq 1 ]; then
# create the agent_param file
/etc/contrail/vnagent_param_setup.sh %{_osVer}
#fi
%endif

%preun
%if 0%{?fedora} >= 17
/bin/systemctl stop supervisor-vrouter.service
if [ $1 = 0 ] ; then
    /usr/sbin/rmmod vrouter
    /bin/systemctl --no-reload disable supervisor-vrouter.service
fi
%endif
exit 0

%postun
if [ $1 = 0 ] ; then
    /bin/systemctl daemon-reload || true
    cp /etc/sysconfig/network-scripts/ifup-eth.rpmsave /etc/sysconfig/network-scripts/ifup-eth
    phydev=`cat /etc/contrail/agent_param | grep dev | sed 's/dev=//g'`
    phydev_save_file=/etc/sysconfig/network-scripts/ifcfg-${phydev}.rpmsave
    phydev_file=/etc/sysconfig/network-scripts/ifcfg-${phydev}
    [ -f ${phydev_save_file} ] && mv ${phydev_save_file} ${phydev_file} || rm -f /etc/sysconfig/network-scripts/ifcfg-${phydev}
    rm -f /etc/sysconfig/network-scripts/ifcfg-vhost0
fi
exit 0

%files
%defattr(-, root, root)
%{_bindir}/flow
%{_bindir}/vif
%{_bindir}/mpls
%{_bindir}/mirror
%{_bindir}/nh
%{_bindir}/rt
%{_bindir}/vrfstats
%{_bindir}/vxlan
%{_bindir}/dropstats
%{_bindir}/vnswad

%if 0%(if [ "%{dist}" == ".xen" ]; then echo 1; fi)
%{_sysconfdir}/init.d/contrail-vrouter
%else
%{_venv_root}
%{_contrailetc}/rpm_agent.conf
%config(noreplace) %{_contrailetc}/vrouter.conf
%{_contrailetc}/vnagent_ExecStartPre.sh
%{_contrailetc}/vnagent_ExecStartPost.sh
%{_contrailetc}/vnagent_ExecStopPost.sh
%{_contrailetc}/vnagent_param_setup.sh
%{_contrailetc}/contrail_reboot
%{_servicedir}/supervisor-vrouter.service
%{_contrailetc}/supervisord_vrouter.conf
%{_supervisordir}/contrail-vrouter.ini
%{_supervisordir}/contrail-vrouter.rules
%{_supervisordir}/contrail-vrouter.kill
%{_venv_root}/bin/contrail-nodemgr
%{_venv_root}/bin/mock_generator
%{_venv_root}/bin/run_mock_generator
%endif
%if 0%{?rhel}
/etc/init.d/contrail-vrouter
/etc/init.d/supervisor-vrouter
%endif
%if 0%{?fedora} >= 17
/etc/init.d/contrail-vrouter
/etc/init.d/supervisor-vrouter
%endif

/lib/modules/%{_osVer}/extra/net/vrouter/vrouter.ko

%changelog

