#
# This is 2.1.1 circa folsom rc2
#
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}


Name:       python-quantumclient
Epoch:      1
Version:    2.1.1
Release:    %{_relstr}
Summary:    Python API and CLI for OpenStack Quantum %{?_gitVer}

Group:      Development/Languages
License:    ASL 2.0
URL:        https://github.com/openstack/python-quantumclient
BuildArch:  noarch


Requires:   python-cliff >= 1.0
Requires:   python-httplib2
Requires:   python-prettytable >= 0.6
Requires:   python-setuptools
Requires:   python-simplejson
Requires:   contrail-api-venv

BuildRequires: python2-devel
BuildRequires: python-setuptools

%description
Client library and command line utility for interacting with Openstack
Quantum's API.

%prep
#%setup -q
## if [ -d python-quantumclient ]; then
   ## (cd python-quantumclient; git stash; git pull)
## else
   ## git clone git@bitbucket.org:contrail_admin/python-quantumclient.git
## fi


# Change cliff version requirement (https://bugs.launchpad.net/python-quantumclient/+bug/1049989)
pushd %{_builddir}/..
pushd third_party/python-quantumclient
#sed -i 's/cliff>=1.2.1/cliff>=1.0/' tools/pip-requires
sed -i 's/cliff>=1.4/cliff>=1.0/' requirements.txt
sed -i 's/pbr.*//' requirements.txt
sed -i 's/d2to1.*//' requirements.txt

%build
pushd %{_builddir}/..
pushd third_party/python-quantumclient

%{__python} setup.py build

%install
pushd %{_builddir}/..
pushd third_party/python-quantumclient
%{__python} setup.py install -O1 --skip-build --root %{buildroot} %{?_venvtr}
%{__python} setup.py sdist
install -p -D -m 644 dist/python-quantumclient-7dca989.tar.gz %{buildroot}/opt/contrail/api-venv/archive/python-quantumclient-7dca989.tar.gz
#awk '{if (NR!=1) {print}}' %{buildroot}%{_venv_root}/bin/quantum > quantum.n
#mv quantum.n %{buildroot}%{_venv_root}/bin/quantum

popd

# Remove unused files
rm -rf %{buildroot}%{python_sitelib}/quantumclient/tests

%files
## %doc python-quantumclient/LICENSE
## %doc python-quantumclient/README.rst
%{_bindir}/quantum
%{python_sitelib}/quantumclient
%{python_sitelib}/*.egg-info
/opt/contrail/api-venv/archive/python-quantumclient-7dca989.tar.gz


%changelog
* Mon Sep 24 2012 Robert Kukura <rkukura@redhat.com> - 1:2.1.1-0
- Update to 2.1.1

* Fri Sep 14 2012 Robert Kukura <rkukura@redhat.com> - 1:2.0.23-0
- Update to 2.0.23

* Wed Sep 12 2012 Robert Kukura <rkukura@redhat.com> - 1:2.0.22-0
- Update to 2.0.22
- Change cliff version dependency to >= 1.0
- Change prettytable version dependency to >= 0.6

* Tue Sep 11 2012 Robert Kukura <rkukura@redhat.com> - 1:2.0.21-0
- Update to 2.0.21
- Strip dependency on cliff version >= 1.2.1

* Fri Aug 24 2012 Alan Pevec <apevec@redhat.com> 1:2.0-2
- Remove PyXML dep (#851687) and unused prettytable dep

* Wed Aug 22 2012 Alan Pevec <apevec@redhat.com> 1:2.0-1
- Add dependency on python-setuptools (#850847)
- Update to 2.0

* Tue Aug  7 2012 Robert Kukura <rkukura@redhat.com> - 1:0.1.1-1
- Update to 0.1.1, new epoch

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2012.2-0.3.f1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 18 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.2.f1
- Add conflict with python-quantum 2012.1 since site-packages/quantum is no longer provided.

* Mon Jun 18 2012 Robert Kukura <rkukura@redhat.com> - 2012.2-0.1.f1
- Update to folsom milestone 1

* Mon Apr  9 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-1
- Update to essex final release

* Thu Apr  5 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.5.rc2
- Update to essex rc2 milestone
- Exclude tests

* Wed Mar 21 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.4.rc1
- Update to official essex rc1 milestone
- Include LICENSE file

* Mon Mar 19 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.3.e4
- Update to essex RC1

* Thu Mar  1 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.2.e4
- Update to essex milestone 4

* Thu Jan 26 2012 Cole Robinson <crobinso@redhat.com> - 2012.1-0.1.e3
- Initial package
