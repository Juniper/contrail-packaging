# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}


Name:		    euca2ools
Version:	    1.0
Release:	    %{_relstr}
Summary:	    Euca2ools %{?_gitVer}

Group:		    Applications/System
License:	    BSD
Source0:        ec2_git_root

%description
Euca2ools for Amazon APIs

BuildRequires:  systemd-units

%prep


%build
#pushd $(cat %{SOURCE0})
#%{__python} setup.py sdist
pushd %{_builddir}/../third_party/euca2ools
%{__python} setup.py install --root=%{buildroot}
popd

%clean


#pushd $(cat %{SOURCE0})

%post

%files
%defattr(-, root, root)
/usr/bin/euare-accountaliascreate
/usr/bin/euare-accountaliasdelete
/usr/bin/euare-accountaliaslist
/usr/bin/euare-accountcreate
/usr/bin/euare-accountdel
/usr/bin/euare-accountdelpolicy
/usr/bin/euare-accountgetpolicy
/usr/bin/euare-accountgetsummary
/usr/bin/euare-accountlist
/usr/bin/euare-accountlistpolicies
/usr/bin/euare-accountuploadpolicy
/usr/bin/euare-getldapsyncstatus
/usr/bin/euare-groupaddpolicy
/usr/bin/euare-groupadduser
/usr/bin/euare-groupcreate
/usr/bin/euare-groupdel
/usr/bin/euare-groupdelpolicy
/usr/bin/euare-groupgetpolicy
/usr/bin/euare-grouplistbypath
/usr/bin/euare-grouplistpolicies
/usr/bin/euare-grouplistusers
/usr/bin/euare-groupmod
/usr/bin/euare-groupremoveuser
/usr/bin/euare-groupuploadpolicy
/usr/bin/euare-servercertdel
/usr/bin/euare-servercertgetattributes
/usr/bin/euare-servercertlistbypath
/usr/bin/euare-servercertmod
/usr/bin/euare-servercertupload
/usr/bin/euare-useraddcert
/usr/bin/euare-useraddkey
/usr/bin/euare-useraddloginprofile
/usr/bin/euare-useraddpolicy
/usr/bin/euare-usercreate
/usr/bin/euare-usercreatecert
/usr/bin/euare-userdeactivatemfadevice
/usr/bin/euare-userdel
/usr/bin/euare-userdelcert
/usr/bin/euare-userdelkey
/usr/bin/euare-userdelloginprofile
/usr/bin/euare-userdelpolicy
/usr/bin/euare-userenablemfadevice
/usr/bin/euare-usergetattributes
/usr/bin/euare-usergetinfo
/usr/bin/euare-usergetloginprofile
/usr/bin/euare-usergetpolicy
/usr/bin/euare-userlistbypath
/usr/bin/euare-userlistcerts
/usr/bin/euare-userlistgroups
/usr/bin/euare-userlistkeys
/usr/bin/euare-userlistmfadevices
/usr/bin/euare-userlistpolicies
/usr/bin/euare-usermod
/usr/bin/euare-usermodcert
/usr/bin/euare-usermodkey
/usr/bin/euare-usermodloginprofile
/usr/bin/euare-userresyncmfadevice
/usr/bin/euare-userupdateinfo
/usr/bin/euare-useruploadpolicy
/usr/bin/euca-add-group
/usr/bin/euca-add-keypair
/usr/bin/euca-allocate-address
/usr/bin/euca-associate-address
/usr/bin/euca-associate-dhcp-options
/usr/bin/euca-attach-volume
/usr/bin/euca-authorize
/usr/bin/euca-bundle-image
/usr/bin/euca-bundle-instance
/usr/bin/euca-bundle-upload
/usr/bin/euca-bundle-vol
/usr/bin/euca-cancel-bundle-task
/usr/bin/euca-check-bucket
/usr/bin/euca-confirm-product-instance
/usr/bin/euca-create-dhcp-options
/usr/bin/euca-create-group
/usr/bin/euca-create-image
/usr/bin/euca-create-keypair
/usr/bin/euca-create-snapshot
/usr/bin/euca-create-subnet
/usr/bin/euca-create-tags
/usr/bin/euca-create-volume
/usr/bin/euca-create-vpc
/usr/bin/euca-delete-bundle
/usr/bin/euca-delete-dhcp-options
/usr/bin/euca-delete-group
/usr/bin/euca-delete-keypair
/usr/bin/euca-delete-snapshot
/usr/bin/euca-delete-subnet
/usr/bin/euca-delete-tags
/usr/bin/euca-delete-volume
/usr/bin/euca-delete-vpc
/usr/bin/euca-deregister
/usr/bin/euca-describe-addresses
/usr/bin/euca-describe-availability-zones
/usr/bin/euca-describe-bundle-tasks
/usr/bin/euca-describe-dhcp-options
/usr/bin/euca-describe-group
/usr/bin/euca-describe-groups
/usr/bin/euca-describe-image-attribute
/usr/bin/euca-describe-images
/usr/bin/euca-describe-instances
/usr/bin/euca-describe-keypairs
/usr/bin/euca-describe-regions
/usr/bin/euca-describe-snapshots
/usr/bin/euca-describe-subnets
/usr/bin/euca-describe-tags
/usr/bin/euca-describe-volumes
/usr/bin/euca-describe-vpcs
/usr/bin/euca-detach-volume
/usr/bin/euca-disassociate-address
/usr/bin/euca-download-bundle
/usr/bin/euca-get-console-output
/usr/bin/euca-get-password
/usr/bin/euca-get-password-data
/usr/bin/euca-import-keypair
/usr/bin/euca-modify-image-attribute
/usr/bin/euca-monitor-instances
/usr/bin/euca-reboot-instances
/usr/bin/euca-register
/usr/bin/euca-release-address
/usr/bin/euca-reset-image-attribute
/usr/bin/euca-revoke
/usr/bin/euca-run-instances
/usr/bin/euca-start-instances
/usr/bin/euca-stop-instances
/usr/bin/euca-terminate-instances
/usr/bin/euca-unbundle
/usr/bin/euca-unmonitor-instances
/usr/bin/euca-upload-bundle
/usr/bin/euca-version
/usr/bin/euca-create-network-acl
/usr/bin/euca-create-network-acl-entry
/usr/bin/euca-delete-network-acl
/usr/bin/euca-delete-network-acl-entry
/usr/bin/euca-replace-network-acl-entry
/usr/bin/euca-replace-network-acl-association
/usr/bin/euca-describe-network-acls
/usr/bin/euca-create-security-group
/usr/bin/euca-delete-security-group
/usr/bin/euca-authorize-security-group-egress
/usr/bin/euca-authorize-security-group-ingress
/usr/bin/euca-revoke-security-group-egress
/usr/bin/euca-revoke-security-group-ingress
/usr/bin/euca-describe-security-groups
/usr/bin/euca-create-route-table
/usr/bin/euca-create-route
/usr/bin/euca-delete-route
/usr/bin/euca-replace-route
/usr/bin/euca-delete-route-table
/usr/bin/euca-associate-route-table
/usr/bin/euca-disassociate-route-table
/usr/bin/euca-replace-route-table-association
/usr/bin/euca-describe-route-tables
/usr/bin/eustore-describe-images
/usr/bin/eustore-install-image
## TODO - this needs to be fixed
##/usr/bin/euca-attach-internet-gateway
##/usr/bin/euca-create-internet-gateway
##/usr/bin/euca-delete-internet-gateway
##/usr/bin/euca-describe-internet-gateways
##/usr/bin/euca-detach-internet-gateway
%{python_sitelib}/euca2ools-0.0.0-py*.egg-info
%{python_sitelib}/euca2ools/

%changelog

