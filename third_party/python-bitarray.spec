%define         _distrothirdpartydir distro/third_party

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
Name: python-bitarray
Summary: python bitarray %{?_gitVer}
Version: 0.8.0
Release: %{_relstr}%{?dist}
License: PSF
Group: Applications/System
URL: http://pypi.python.org/pypi/bitarray/
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description

%prep

# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
gitrepo=controller
grep $gitrepo .git/config &> /dev/null
if [ $? -ne 0 ]; then
    echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    exit -1
fi

%build

%install
install -d -m 755 %{buildroot}%{python_sitelib}
pushd %{_builddir}/..
pushd %{_distrothirdpartydir}/bitarray-0.8.1
%{__python} setup.py install --root=%{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitearch}/bitarray
%{python_sitearch}/bitarray-*.egg-info


%changelog
* Wed Dec 19 2012  <builder@build01> - bitarray-1
- Initial build.

