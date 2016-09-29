# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail
%define         _provdir      %{_builddir}/../tools/provisioning

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_fileList:1}
%define         _flist      %{_fileList}
%else
%define         _flist      None
%endif
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
%if 0%{?_skuTag:1}
%define         _sku     %{_skuTag}
%else
%define         _sku      None
%endif


Name:		    contrail-install-packages
Version:	    %{_verstr}
Release:	    %{_relstr}~%{_sku}%{?dist}
Summary:	    Contrail Installer %{?_gitVer}
BuildArch:          noarch

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc



%description
Contrail Installer Packages - Container of Contrail RPMs

%install

# Setup directories
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_contrailopt}
install -d -m 755 %{buildroot}%{_contrailopt}/puppet
install -d -m 755 %{buildroot}%{_contrailopt}/contrail_packages

# install files
pushd %{_builddir}/..
install -p -m 755 tools/packaging/build/setup.sh %{buildroot}%{_contrailopt}/contrail_packages/setup.sh.new

# %{_builddir}%/../build/puppet is a temp dir for puppet-third-party and puppet
install -d -m 755 %{_builddir}%/../build/puppet
cp -rp %{_builddir}%/../tools/puppet %{_builddir}%/../build/
# Install puppet manifests
if [ -d %{_builddir}%/../tools/puppet-third-party ]; then echo "New Modules"; cp -rp %{_builddir}%/../tools/puppet-third-party/* %{_builddir}%/../build/puppet/contrail/environment/modules/ ; fi


# Install puppet manifests
tar -cvzf %{_builddir}/../build/contrail-puppet-manifest.tgz -C %{_builddir}/../build/puppet .

install -p -m 755 %{_builddir}/../build/contrail-puppet-manifest.tgz %{buildroot}%{_contrailopt}/puppet/contrail-puppet-manifest.tgz

if [ -f %{_flist} ]; then echo "Using TGZ FILE = %{_flist}"; install -p -m 644 %{_flist} %{buildroot}%{_contrailopt}/contrail_packages/contrail_rpms.tgz; else echo "ERROR: TGZ file containing all rpms is not supplied or not present"; echo "Supply Argument: FILE_LIST=<TGZ FILE>"; exit 1; fi

%post
# To solve the upgrade issue, in 1.10, setup.sh was packaged in contrail-setup and contrail-install-packages
# So when upgrading contrail-install-packages, it will fail, we will need to use rpm -iU --force to upgrade
# To avoid this and use yum localinstall this post section is added
# Should remove this post section in the next release, No harm in keeping it
if [ -f %{_contrailopt}/contrail_packages/setup.sh.new ]; then
    mv %{_contrailopt}/contrail_packages/setup.sh.new %{_contrailopt}/contrail_packages/setup.sh
fi

%files
%defattr(-, root, root)
%{_contrailopt}/contrail_packages/setup.sh.new
%{_contrailopt}/contrail_packages/contrail_rpms.tgz
%{_contrailopt}/puppet/contrail-puppet-manifest.tgz

%changelog
* Mon Jan 25 2016 - npchandran@juniper.net
- Removing pip related steps in contrail cloud packages

