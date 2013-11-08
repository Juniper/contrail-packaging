%define _ldconfdir /etc/ld.so.conf.d
%define         _distropkgdir tools/packaging/common/control_files

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%if 0%(grep -c Xen /etc/redhat-release)
%define dist .xen
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif

Release: %{_relstr}%{?dist}
Summary:  Libraries used by the Contrail Virtual Router %{?_gitVer}
Name:     contrail-libs
Version:	    %{_verstr}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

%if 0%(if [ %{dist} = ".xen" ]; then echo 1; fi)
Provides: libcurl
%endif

%description
Libraries used by the Contrail Virtual Router.

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
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi

%build
LIBS="build/lib/libtbb_debug.so.2 build/lib/libthrift.a build/lib/libboost_program_options.so build/lib/libboost_filesystem.so build/lib/libboost_system.so build/lib/liblog4cplus.so"
if [ $(grep -c XenServer /etc/redhat-release) -gt 0 ]; then
LIBS+=" build/lib/libcurl.a"
fi
pushd %{_builddir}/..
scons -U $LIBS
if [ $? -ne 0 ] ; then
    echo "build failed"
    exit -1
fi

%install
# Setup directory
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_libdir}/contrail
install -d -m 755 %{buildroot}%{_ldconfdir}

pushd %{_builddir}/..
# install libraries
install -p -m 755 build/lib/libtbb_debug.so.2                  %{buildroot}%{_libdir}/contrail/libtbb_debug.so.2
install -p -m 755 build/lib/libthrift-0.8.0.so                 %{buildroot}%{_libdir}/contrail/libthrift-0.8.0.so
install -p -m 755 build/lib/libthriftasio.so.0.0.0             %{buildroot}%{_libdir}/contrail/libthriftasio.so.0.0.0
install -p -m 755 build/lib/libboost_program_options.so.1.48.0 %{buildroot}%{_libdir}/contrail/libboost_program_options.so.1.48.0
install -p -m 755 build/lib/libboost_filesystem.so.1.48.0 %{buildroot}%{_libdir}/contrail/libboost_filesystem.so.1.48.0
install -p -m 755 build/lib/libboost_regex.so.1.48.0           %{buildroot}%{_libdir}/contrail/libboost_regex.so.1.48.0
install -p -m 755 build/lib/libboost_system.so.1.48.0          %{buildroot}%{_libdir}/contrail/libboost_system.so.1.48.0
install -p -m 755 build/lib/libboost_python.so.1.48.0          %{buildroot}%{_libdir}/contrail/libboost_python.so.1.48.0
install -p -m 755 build/lib/liblog4cplus-1.1.so.7.0.0          %{buildroot}%{_libdir}/contrail/liblog4cplus-1.1.so.7.0.0

#if [ $(grep -c XenServer /etc/redhat-release) -gt 0 ]; then
#install -p -m 755 build/lib/libcurl.so.4.2.0		%{buildroot}%{_libdir}/contrail/
#fi

%if %{_target_cpu} == "x86_64"
install -p -m 755 %{_distropkgdir}/contrail-64.conf             %{buildroot}%{_ldconfdir}/contrail-64.conf
%else
echo "%{_libdir}/contrail" > %{buildroot}%{_ldconfdir}/contrail.conf
%endif

ln -sf libtbb_debug.so.2 	  			  	%{buildroot}%{_libdir}/contrail/libtbb_debug.so
ln -sf libthriftasio.so.0.0.0 			  	%{buildroot}%{_libdir}/contrail/libthriftasio.so
ln -sf libboost_program_options.so.1.48.0	%{buildroot}%{_libdir}/contrail/libboost_program_options.so
ln -sf libboost_filesystem.so.1.48.0	%{buildroot}%{_libdir}/contrail/libboost_filesystem.so
ln -sf libboost_regex.so.1.48.0		   		%{buildroot}%{_libdir}/contrail/libboost_regex.so
ln -sf libboost_system.so.1.48.0          	%{buildroot}%{_libdir}/contrail/libboost_system.so
ln -sf libboost_python.so.1.48.0          	%{buildroot}%{_libdir}/contrail/libboost_python.so
ln -sf liblog4cplus-1.1.so.7.0.0    	  	%{buildroot}%{_libdir}/contrail/liblog4cplus-1.1.so.7
ln -sf liblog4cplus-1.1.so.7.0.0    	  	%{buildroot}%{_libdir}/contrail/liblog4cplus-1.1.so

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%{_libdir}/contrail
%if %{_target_cpu} == "x86_64"
%{_ldconfdir}/contrail-64.conf
%else
%{_ldconfdir}/contrail.conf
%endif

%changelog
* Fri Dec 21 2012 Dave Kunkel <dkunkel@contrailsystems.com>
- initial build
