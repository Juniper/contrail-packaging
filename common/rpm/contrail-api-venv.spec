%if 0%{?_buildTag:1}
%define     _relstr      %{_buildTag}
%else
%define     _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo:     "Building venv contrail api release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
Release:    %{_relstr}%{?dist}
Summary:    Contrail API virtual env %{?_gitVer}
Name:       contrail-api-venv
Version:	    %{_verstr}
License:    Commercial
Group:      Applications/System
URL:        http://www.contrailsystems.com/
Autoreq:0

%if 0%{?_python_path:1}
%define     _lpy  %(%{__python} -c 'import os; print os.path.expanduser ("%{_python_path}")')
%define     _vpy  --python=%{_lpy}/bin/python
%endif
%define     _pyprefix %(%{__python} -c 'import sys; print sys.prefix')
%define     _pyver    %( %{__python} -c "import sys; print '%s.%s' % sys.version_info[0:2]" )
%description
Creates virtual env for contrail api role

%prep
#%setup -q
# start from git root.. run this
#       git rev-parse --show-toplevel > %{SOURCE0}

# make sure we are in ctrlplane repo
# gitrepo=$(basename $(git remote show origin | grep "Fetch URL" | cut -d: -f3 ))
# if [ x$gitrepo != xctrlplane.git ]; then
%define _pth %{buildroot}

## gitrepo=packaging
## grep $gitrepo .git/config &> /dev/null
## if [ $? -ne 0 ]; then
    ## echo "Please use rpmbuild --define \"_builddir <git_sandbox>\""
    ## exit -1
## fi

%build

tar xzvf %{_builddir}/BUILD/packaging/archives/virtualenv-1.9.1.tar.gz 
#patch -p0 < %{_builddir}/archives/venv-always-cp.diff
pushd virtualenv-1.9.1 
mkdir -p reqs/cfgm
cat > reqs/reqs.txt <<END
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/greenlet-0.4.1.zip
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/gevent-0.13.8.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/eventlet-0.9.17.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/lxml-2.3.3.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/geventhttpclient-1.0a.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/netaddr-0.7.5.zip
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/extras-0.0.3.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/requests-1.1.0.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/wsgiref-0.1.2.zip
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/zope.interface-3.8.0.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/netifaces-0.8.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/pycrypto-2.6.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/paramiko-1.11.0.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/Fabric-1.7.0.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/bitarray-0.8.0.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/thrift-0.8.0.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/psutil-1.0.1.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/iso8601-0.1.4.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/prettytable-0.7.2.zip
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/simplejson-3.3.0.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/argparse-1.2.1.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/oslo.config-1.1.1.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/d2to1-0.2.11.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/pyparsing-1.5.7.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/cmd2-0.6.5.1.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/cliff-1.4.4.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/httplib2-0.8.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/repoze.lru-0.6.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/Paste-1.7.5.1.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/PasteDeploy-1.5.0.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/SQLAlchemy-0.8.2.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/Routes-1.13.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/qpid-python-0.20.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/stevedore-0.11.tar.gz
%{_builddir}/virtualenv-1.9.1/reqs/cfgm/pbr-0.5.21.tar.gz
END

for f in greenlet-0.4.1.zip lxml-2.3.3.tar.gz netaddr-0.7.5.zip           \
        requests-1.1.0.tar.gz virtualenv-1.9.1.tar.gz gevent-0.13.8.tar.gz   \
        geventhttpclient-1.0a.tar.gz extras-0.0.3.tar.gz wsgiref-0.1.2.zip   \
        zope.interface-3.8.0.tar.gz netifaces-0.8.tar.gz pycrypto-2.6.tar.gz \
        paramiko-1.11.0.tar.gz Fabric-1.7.0.tar.gz bitarray-0.8.0.tar.gz     \
        thrift-0.8.0.tar.gz psutil-1.0.1.tar.gz iso8601-0.1.4.tar.gz         \
        prettytable-0.7.2.zip simplejson-3.3.0.tar.gz argparse-1.2.1.tar.gz  \
        oslo.config-1.1.1.tar.gz d2to1-0.2.11.tar.gz pyparsing-1.5.7.tar.gz  \
        cmd2-0.6.5.1.tar.gz cliff-1.4.4.tar.gz httplib2-0.8.tar.gz           \
        eventlet-0.9.17.tar.gz repoze.lru-0.6.tar.gz Paste-1.7.5.1.tar.gz    \
        PasteDeploy-1.5.0.tar.gz SQLAlchemy-0.8.2.tar.gz Routes-1.13.tar.gz  \
        qpid-python-0.20.tar.gz stevedore-0.11.tar.gz pbr-0.5.21.tar.gz; do
    cp %{_builddir}/BUILD/packaging/archives/$f reqs/cfgm
done

%install
install -d -m 755 %{buildroot}/opt/contrail/
%define _target %{buildroot}/opt/contrail/api-venv

# start venv
pushd %{_builddir}/virtualenv-1.9.1
%{__python} virtualenv.py %{?_vpy} --extra-search-dir=$(pwd)/reqs --extra-search-dir=$(pwd)/virtualenv_support --never-download --system-site-packages %{_target}
popd


pushd %{_target}

source bin/activate
pip install --index-url='' --requirement %{_builddir}/virtualenv-1.9.1/reqs/reqs.txt
#PYTHONPATH=%{_target}/lib/python2.7/site-packages:$PYTHONPATH pip install --index-url='' --install-option="--install-lib=%{_target}/lib/python2.7/site-packages" --requirement %{_builddir}/virtualenv-1.9.1/reqs/reqs.txt

deactivate

#VIRTUAL_ENV=/opt/contrail/cfgm-venv/virtualenv-1.9.1/cfgm-venv %{__python} virtualenv.py --relocatable ENV

_npth=$(echo %{_pth} | sed 's/\//\\\//g')
for f in $(find . -type f -exec grep -nH "%{_pth}" {} \; | grep -v 'Binary file' | cut -d: -f1); do
    sed "s/${_npth}//g" $f > ${f}.b
    mv ${f}.b $f
    echo "changed $f .... Done!"
done
popd

rm -rf %{_builddir}/virtualenv-1.9.1

ls -als %{_target}/bin/
rm -f %{_target}/lib64 %{_target}/bin/python2 %{_target}/bin/python%{_pyver}

for f in $(find %{_target} -type l -print ); do
    x=$(pwd)
    cd $(dirname $f)
    f=$(basename $f)
    p=$(readlink $f)
    rm -f $f
    cp -ar $p $f
    cd $x
done
%if 0%{?_python_path:1}
cp -fr %{_lpy}/lib/python%{_pyver}/* %{_target}/lib/python%{_pyver}
%endif
find %{_target} -name '*.py[oc]' | xargs rm -f
rm -rf %{_target}/lib/python2.7/lib2to3/tests %{_target}/lib/python2.7/test


%files
%defattr(-,root,root,-)
/opt/contrail/api-venv

%post
pushd /opt/contrail/api-venv/
rm -rf lib64
ln -sf lib lib64
cd bin
ln -sf python python2
ln -sf python python%{_pyver}
chmod +x *

%changelog
* Thu Jul 11 2013 Ted Ghose <ted@build01> - venv
- Initial build.

