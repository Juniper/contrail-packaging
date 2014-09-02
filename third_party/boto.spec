# view contents of rpm file: rpm -qlp <filename>.rpm

%define         _contrailopt /opt/contrail
%define         _relstr     2contrail 
%{echo: "Building release %{_relstr}\n"}
Name:           python-boto		
Version:	2.12.0
Release:	%{_relstr}%{?dist}
Summary:	boto %{?_gitVer}

Group:		Development/Languages
License:	MIT
#Source0:	boto_git_root

%description
Boto is a Python package that provides interfaces to Amazon Web Services.

%build
pushd %{_builddir}/../third_party/python-boto
%{__python} setup.py build
popd


%clean

%install
pushd %{_builddir}/../third_party/python-boto
%{__python} setup.py install --root=%{buildroot}
popd


%post

%files
%defattr(-,root,root)
%{python_sitelib}/boto
%{python_sitelib}/boto-2.12.0-py*.egg-info

%{_bindir}/asadmin
%{_bindir}/bundle_image
%{_bindir}/cfadmin
%{_bindir}/cq
%{_bindir}/cwutil
%{_bindir}/elbadmin
%{_bindir}/fetch_file
%{_bindir}/instance_events
%{_bindir}/kill_instance
%{_bindir}/launch_instance
%{_bindir}/list_instances
%{_bindir}/lss3
%{_bindir}/pyami_sendmail
%{_bindir}/route53
%{_bindir}/s3put
%{_bindir}/sdbadmin
%{_bindir}/taskadmin
%{_bindir}/dynamodb_dump
%{_bindir}/dynamodb_load
%{_bindir}/glacier
%{_bindir}/mturk



%changelog

