import os
import re
import sys
import time
import glob
import shutil
import platform
import tempfile
import argparse
import commands
import datetime
import ConfigParser
import logging

from fabric.api import local,env
from fabric.operations import get, put, run
from fabric.context_managers import lcd, settings, cd

printlog = logging.getLogger('nightly')
form = '%(asctime)-15s::%(lineno)s::%(funcName)s::  %(message)s'
sh = logging.StreamHandler(sys.stdout)
fh = logging.FileHandler('nightly.log')
formatter = logging.Formatter(form)
sh.setFormatter(formatter)
fh.setFormatter(formatter)
printlog.addHandler(sh)
printlog.addHandler(fh)
printlog.setLevel(logging.INFO)

class CommonUtil (object):
    def getstatusoutput(self, cmd):
        """Return (status, output) of executing cmd in a shell."""
        pipe = os.popen('{ ' + cmd + '; } 2>&1', 'r')
        text = ''
        while True:
            line = pipe.readline()
            if line == '':
                break
            text += line
            printlog.info(line)
        sts = pipe.close()
        if sts is None: sts = 0
        if text[-1:] == '\n': text = text[:-1]
        return sts, text

    def run_shell (self, cmd):
        printlog.info('+ ' + cmd)
        s, o = self.getstatusoutput (cmd)
        if s: raise RuntimeError, '+ %s[%d]\n%s' % (cmd, s, o)
        printlog.info('+ %s Done [%d]\n' % (cmd, s))
        return o

    def rpm_get_name (self, fl):
        o = self.run_shell (
                "rpm --nosignature -qp --queryformat '%%{NAME}' %s" % fl)
        return o

    def rpm_name_check (self, pkg, fl):
        o = self.rpm_get_name (fl)
        return o == pkg

    def rpm_list_by_pattern (self, name, wildcard):
        for f in filter (lambda x: self.rpm_name_check (name, x),
                glob.glob (wildcard)):
            yield f


class Repo (CommonUtil):
    def __init__ (self, name, git, pkg_list, dont_build=False, branch=None):
        self.name       = name
        self.pkgs       = [] + pkg_list
        self.git        = git
        self.gid        = None
        self.dont_build = dont_build
        self._latest    = {}
        self._extra_tag = ''
        if branch:
            self._bqlfy = '-b %s' % branch
        else:
            self._bqlfy = '-t HEAD'

    def set_et (self, s):
        self._extra_tag = 'FILE_LIST=%s' % s

    def get_gid (self):
        if self.gid is None:
            s, o = commands.getstatusoutput (
                    'git ls-remote %s %s' % (
                        self.git, self._bqlfy))
            self.gid = o.split()[0]
        return self.gid

    def by_name (self, n):
        if n == self.name:
            return self
        return None

    def by_pkg (self, n):
        if n in self.pkgs:
            return self
        return None

    def has_pkg (self, p):
        return p in self.pkgs

    def first_pkg (self):
        return self.pkgs[0]

    def build (self, tag, target, repo=None):
        if self.dont_build:
            printlog.info('skipping build for %s (dont build is set)' % self.name)
            return []
        s, o = 0, 'ss'
        o = self.run_shell ('make GIT_VER=%s TAG=%s %s %s' % (
                self.get_gid (), tag, self._extra_tag, self.name))
        #cp the files over
        blist = []
        for pk in self.pkgs:
	    for arch in ('x86_64', 'noarch'):
		for f in self.rpm_list_by_pattern (pk, os.path.join (
		    os.path.expanduser('~'), 'rpmbuild', 'RPMS', arch,
			  "%s*-%s.*.rpm" % (pk, tag))):
		    printlog.info('rpm = %s' % f)
		    blist.append ((pk, f))
        for pk, f in blist:
            tf = os.path.join (target, os.path.basename (f))
            if os.path.isfile (tf):
                os.remove (tf)
            shutil.copy2 (f, tf)
            self._latest[pk] = tf
            printlog.info('+ cp %s %s' % (f, tf))
            if repo:
                for fx in self.rpm_list_by_pattern (pk, os.path.join (
                            repo, "%s*.rpm" % pk)):
                    os.remove (fx)
		printlog.info('copying rpm = %s' % tf)
                shutil.copy2 (tf, repo)
        return map (lambda x: os.path.basename (x[1]), blist)

        
class NightlyBuilder (CommonUtil):
    package_list = [
        Repo ('nova', "ssh://git@bitbucket.org/contrail_admin/nova",
            ["openstack-nova-cert", "openstack-nova-objectstore",
             "openstack-nova-scheduler", "openstack-nova-api", "python-nova",
             "openstack-nova-compute", "openstack-nova-console",
             "openstack-nova-common", "openstack-nova-doc", "openstack-nova",
             "openstack-nova-cells", "openstack-nova-conductor"]),
        Repo ("quantum",
            "ssh://git@bitbucket.org/contrail_admin/quantum",
            ["python-quantum", "openstack-quantum",
             "openstack-quantum-contrail"]),
        Repo ("cinder", "ssh://git@bitbucket.org/contrail_admin/cinder",
            ["openstack-cinder-doc", "openstack-cinder", "python-cinder"]),
        Repo ("glance", "ssh://git@bitbucket.org/contrail_admin/glance",
            ["openstack-glance", "python-glance", "openstack-glance-doc"]),
        Repo ("keystone", "ssh://git@bitbucket.org/contrail_admin/keystone",
            ["openstack-keystone", "python-keystone"]),
        Repo ("packaging", "ssh://git@bitbucket.org/contrail_admin/packaging",
            ["contrail-api-venv", "contrail-analytics-venv", "contrail-control-venv", "contrail-vrouter-venv", "contrail-database-venv"]),
        Repo ("horizon", "ssh://git@bitbucket.org/contrail_admin/horizon",
            ["openstack-dashboard", "django-horizon"]),
        Repo ("cassandra", "ssh://git@bitbucket.org/contrail_admin/cassandra",
            ["contrail-database"]),
        Repo ("zookeeper", "ssh://git@bitbucket.org/contrail_admin/zookeeper",
            ["zookeeper", "zookeeper-lib", "zkpython"],True),
        Repo ("django-openstack-auth",
            "ssh://git@bitbucket.org/contrail_admin/django-openstack-auth",
            ["python-django-openstack-auth"]),
        Repo ("ifmap-server",
            "ssh://git@bitbucket.org/contrail_admin/ifmap-server",
            ["irond"]),
        Repo ('package-python-novaclient',
            "ssh://git@bitbucket.org/contrail_admin/python-novaclient",
            ["python-novaclient", "python-novaclient-doc"]),
        Repo ("python-glanceclient",
            "ssh://git@bitbucket.org/contrail_admin/python-glanceclient",
            ["python-glanceclient"]),
        Repo ("python-quantumclient",
            "ssh://git@bitbucket.org/contrail_admin/python-quantumclient",
            ["python-quantumclient"]),
        Repo ("python-swiftclient",
            "ssh://git@bitbucket.org/contrail_admin/python-swiftclient",
            ["python-swiftclient"]),
        Repo ("python-cinderclient",
            "ssh://git@bitbucket.org/contrail_admin/python-cinderclient",
            ["python-cinderclient"]),
        Repo ("python-keystoneclient",
            "ssh://git@bitbucket.org/contrail_admin/python-keystoneclient",
            ["python-keystoneclient", "python-keystoneclient-doc"]),
        Repo ("puppet",
            "ssh://git@bitbucket.org/contrail_admin/puppet.git",
            ["puppet", "puppet-server"]),
        Repo ("webob",
            "ssh://git@bitbucket.org/contrail_admin/webob.git",
            ["python-webob"]),
        Repo ("contrail-fabric-utils",
            "ssh://git@bitbucket.org/contrail_admin/fabric-utils.git",
            ["contrail-fabric-utils"]),
        Repo ("ixgbe",
            "ssh://git@bitbucket.org/contrail_admin/ixgbe.git",
            ["ixgbe"]),
        Repo ("euca2ools",
            "ssh://git@bitbucket.org/contrail_admin/euca2ools.git",
            ["euca2ools"]),
        Repo ("python-boto",
            "ssh://git@bitbucket.org/contrail_admin/boto.git",
            ["python-boto"],
            branch='2.12.0'),
    ]
    if 'fedora' in platform.dist()[0]:
        package_list.append(
            Repo ("libvirt",
                "ssh://git@bitbucket.org/contrail_admin/libvirt.git",
                ["libvirt", 'libvirt-client', 'libvirt-python',
                 'libvirt-debuginfo', 'libvirt-daemon',
                 'libvirt-daemon-config-nwfilter', 'libvirt-daemon-config-network']))
        package_list.append(
            Repo ("ctrlplane",
                "ssh://git@bitbucket.org/contrail_admin/ctrlplane",
                ['contrail-config', 'contrail-control', 'contrail-dns', 'contrail-libs',
                'python-bitarray', 'xmltodict', 'redis-py', 'hiredis-py', 'contrail-webui',
                'contrail-nodejs', 'contrail-vrouter', 'contrail-interface-name', 'contrail-analytics',
                'contrail-setup', 'python-pycassa',
                'python-thrift', 'supervisor', 'contrail-openstack-analytics', 'contrail-openstack-config',
                'contrail-openstack', 'contrail-openstack-control', 'contrail-openstack-vrouter',
                'contrail-openstack-webui', 'contrail-api-lib', 'contrail-api-extension', 'contrail-openstack-database']))
    else:
        package_list.append(
            Repo ("libvirt",
                 "ssh://git@bitbucket.org/contrail_admin/libvirt.git",
                ["libvirt", 'libvirt-client', 'libvirt-python',
                 'libvirt-debuginfo']))
        package_list.append(
            Repo ("ctrlplane",
                "ssh://git@bitbucket.org/contrail_admin/ctrlplane",
                ['contrail-config', 'contrail-control', 'contrail-dns', 'contrail-libs',
                'python-bitarray', 'xmltodict', 'redis-py', 'hiredis-py', 'contrail-webui',
                'contrail-nodejs', 'contrail-vrouter', 'contrail-interface-name', 'contrail-analytics',
                'contrail-setup', 'python-pycassa',
                'python-thrift', 'supervisor', 'contrail-openstack-analytics', 'contrail-openstack-config',
                'contrail-openstack', 'contrail-openstack-control', 'contrail-openstack-vrouter',
                'contrail-openstack-storage',
                'contrail-openstack-webui', 'contrail-api-lib', 'contrail-api-extension', 'contrail-openstack-database']))

    def __init__ (self, args = ''):
        if not isinstance(args, str):
            raise TypeError, 'Expecting cli string, got %s of type %' % (
                str(args), str(type (args)))
        self.build_targets = set ()
        self.new_rpms = set ()
        self.__fpat = None
        self.__fpat_n = None
        self.__fpat_a = None
        self.nightly_build_repo = None
        self.copy_b_files= False        
        self._latest = {}
        self.datestr = datetime.datetime.utcnow().strftime("%y%m%d%H%M")
        self.parse_args (args)
        self.cache_rpms = packages.cache_rpms ()
        self.build_rpms = self._build_rpms ()
        self.mk_iso_init ()
        self.init_env ()
        self.sanity ()

    def _dist_filter (self, rpm):
    	dist = platform.dist()[0]
    	if  dist == 'centos' or dist == 'redhat':
    	    if rpm in ('ixgbe', ):
    	    	return False
    	return rpm not in self.cache_rpms

    def _build_rpms (self):
        s = []
        for p in self.package_list:
            s += filter (self._dist_filter, p.pkgs)
        return s

    def repos (self):
        for i in self.package_list:
            yield i

    def find_repo_by_pkg (self, name):
        for r in self.repos ():
            if r.by_pkg (name):
                return r

    def find_repo_by_name (self, name):
        for r in self.repos ():
            if r.by_name (name):
                return r
        
    def fix_git_repo (self):
        ans = 'wrong'
        while ans.strip ()[0].lower () not in "caps":
            ans = raw_input (
             'Do you like to (c)ontinue, (p)ull, (s)tash-n-pull, (a)bort?')
        a = ans.strip ()[0].lower ()
        if a == 'a':
            printlog.info('Terminate on user request')
            sys.exit (1)
        elif a == 'p':
            printlog.info('+ git pull')
            s, o = commands.getstatusoutput ('git pull')
            printlog.info('..exited with %d\n%s' % (s, o))
            if s != 0:
                sys.exit (2)
        elif a == 's':
            printlog.info('+ git stash')
            s, o = commands.getstatusoutput ('git stash')
            printlog.info('..exited with %d\n%s' % (s, o))
            if s != 0:
                sys.exit (2)
            printlog.info('+ git pull')
            s, o = commands.getstatusoutput ('git pull')
            printlog.info('..exited with %d\n%s' % (s, o))
            if s != 0:
                sys.exit (2)

        
    def init_env (self):
        #import pdb; pdb.set_trace ()
        if self.args.nightly:
            self.nightly_build_repo = os.path.join ('/cs-shared/builder', self.args.nightly)
            if os.path.isdir (self.nightly_build_repo):
                return
            else:
                raise IOError, '%s build is not found at %' % (
                        self.args.nightly, self.nightly_build_repo)
        self._cwd = os.getcwd ()
        os.chdir (os.path.realpath (os.path.dirname (sys.argv[0])))
        s, o = commands.getstatusoutput ('git ls-remote origin -t HEAD')
        local_git_head = o.split()[0]
        remote_git_head = self.find_repo_by_name ('ctrlplane').get_gid ()
        #if local_git_head != remote_git_head:
        #    printlog.info('Local ctrlplane repo is not at Master head')
        #    if self.args.force:
        #        printlog.info('Ignoring for "force" option')
        #    else:
        #        self.fix_git_repo ()

        printlog.info('%s, %s, %s, %s' %(self.args, self.targets, local_git_head, remote_git_head))
        printlog.info('%s, %s' %(self.args.force, self.args.target_dir))

        if self.args.master and not os.path.samefile (self.args.master,
                self.args.target_dir):
            if not os.path.isdir (self.args.target_dir):
                self.run_shell ('mkdir -p %s' % self.args.target_dir)
            self.run_shell ('for f in %s/*/*.rpm; do  ln -sf $f %s; done' % (
                                      self.args.master, self.args.target_dir))
        self.build_target_list ()
	
    def mk_iso_init (self):
        if self.args._id:
            base = '%s/%d' % (self.args.store, self.args._id)
            self.run_shell  ('rm -rf %s' % (base))
            self.run_shell  ('mkdir -p %s/{prepo,repo,log}' % (base))
            self.run_shell  ('rm  -f %s/repo/*.rpm' % (base))
            self.store_dir = base
            self.repo_dir = os.path.join (self.store_dir, 'repo')
            self.prepo_dir = os.path.join (self.store_dir, 'prepo')
            self.git_ids_file = '%s/%s_%s.txt' %(self.store_dir,'git_build',
                    self.args._id)
            with open ('%s/log/rpm_list.txt' % base, 'w') as f:
                for pkg in filter (lambda x: not x.endswith ('debuginfo'),
                                sorted (self.build_rpms)):
                    f.write ('%s\n' % (pkg))
                f.flush ()
                self.find_repo_by_name ('ctrlplane').set_et (
                    '%s/log/rpm_list.txt' % base)

            

    def build_target_list (self):
        if self.targets:
            if self.args.all or self.args._id:
                printlog.info('command line --all overrides specific targets')
            else:
                for t in self.targets:
                    r = self.find_repo_by_pkg (t)
                    if r is None:
                        printlog.info('No package found for %s' % t)
                    else:
                        printlog.info('%s package found for %s' % (r.name, t))
                        self.build_targets.add (r)
                if not self.build_targets:
                    printlog.info('Nothing to build, consider -a to build all')
                    sys.exit (3)
        elif self.args.all or self.args._id:
            self.build_targets |= set (self.package_list)

        bl = list (self.build_targets)
        fl = []
        for r in bl:
            if self.args.force:
                fl.append (r)
                if r.dont_build:
                    # refactor, need this to find latest
                    self.need_rebuild (r)
            elif self.need_rebuild (r):
                fl.append (r)
        self.build_targets = set (fl)
    
    def need_rebuild (self, r):
        #import pdb; pdb.set_trace ()
        #if r.has_pkg ('contrail-vrouter'):
        #    import pdb; pdb.set_trace ()
        mark = False
        for pn in r.pkgs:
            sfl = []
                
            for arch in ('x86_64', 'noarch'):
                flist = self.rpm_list_by_pattern (pn, os.path.join (
                    self.args.target_dir, "%s*.%s.rpm" % (pn, arch)))
                sfl += sorted (flist, key=lambda x: self._sort_key (
                                    pn, arch, x))
            if sfl:
                #printlog.info(sfl, sfl[-1])
                if r.dont_build:
                    printlog.info('DEBUG: sfl: %s-- %s' %(sfl, self.repo_dir))
                    shutil.copy (sfl[-1], self.repo_dir)
                    r._latest[pn] = sfl[-1]
                else:
                    if self.args.skipbuild:
                        shutil.copy (sfl[-1], self.repo_dir)
                        r._latest[pn] = sfl[-1]
                    else:
                        o = self.run_shell (
                            "rpm --nosignature -qp --queryformat '%%{SUMMARY}' %s" % sfl[-1])
                        ol = re.split (r'\s+', o)[-1]
                        gid = r.get_gid ()
                        printlog.info(r.name, pn, arch, ol, gid)
                        if ol:
                            if ol != gid:
                                #if len (sfl) > 20:
                                #    for df in sfl[:-21]:
                                #        os.remove (df)
                                mark = True
                            elif self.args._id:
                                shutil.copy (sfl[-1], self.repo_dir)
                                r._latest[pn] = sfl[-1]
                        else:
                            mark = True
            else:
                mark = True
        #end for
        # Store the latest git id for each repo
        if self.args._id:
            line = '%s %s' %(r.git, r.get_gid()) 
            ## self.run_shell('grep -q \'%s\' %s || echo \"%s\" >> %s' %(
                           ## line, self.git_ids_file, line, self.git_ids_file))
        return mark

    def _sort_key (self, name, arch, fn):
        m = self._fpat (name, arch).match (fn)
        if m:
            return int (m.groups() [0])
        return 0

    def _fpat (self, name, arch):
        if name != self.__fpat_n or arch != self.__fpat_a:
            self.__fpat = None
        if self.__fpat is None:
            self.__fpat = re.compile (r'.*%s.*(\d{6}).%s.rpm' % (name, arch))
        return self.__fpat

    def sanity (self):
        if self.nightly_build_repo:
            return
        if not os.access(self.args.target_dir, os.W_OK):
            raise IOError, '%s is not writable' % self.args.target_dir
        self.run_shell (
                'mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}')
            
    def do_rpm_build (self):
        if self.nightly_build_repo:
            return
        if self.args.skipbuild:
            return
        self.build_them ()
        if self.args._id:
            self.write_new_pkg_list ()
        # Copy build artifacts to SV only if jenkins triggered the build
        if self.args.from_jenkins:
            self.copy_b_files=True
#            self.copy_build_files()
            
    def build (self):
        self.do_rpm_build ()
        self.mk_iso ()
        if not self.nightly_build_repo:
            self.mk_link_repo ()
            #self.update_repo (self.args.target_dir)
        if self.copy_b_files:
            self.copy_build_files()
        return
      
    def mk_link_repo (self):
        for pkg, fl in self._latest.items ():
            tf = os.path.join (self.prepo_dir, os.path.basename(fl))
            if os.path.isfile (tf):
                os.remove (tf)
            os.symlink (fl, tf)
            #printlog.info('+ %s %s->%s' % (pkg, tf, fl))
      
    def copy_build_files (self):
        blr_server='stack@10.204.216.49'
        svl_server='10.84.5.101'
        
        self.run_shell('mkdir -p %s/ctrlplane' %(self.store_dir))
        # remove .o and .a files 
        self.run_shell('find %s -name *.o | xargs rm -f ' %(self.args.workspace))
        self.run_shell('find %s -name *.a | xargs rm -f ' %(self.args.workspace))
        self.run_shell('cd %s ; tar cf %s/ctrlplane_files.tar .' %(self.args.workspace,self.args.workspace))
        self.run_shell('cp %s/ctrlplane_files.tar %s' %(self.args.workspace,self.store_dir))
        self.run_shell('rm -f %s/ctrlplane_files.tar' %(self.args.workspace))
        with settings(host_string=blr_server, warn_only=True):
	    run('mkdir -p %s/ctrlplane; tar xf %s/ctrlplane_files.tar -C %s/ctrlplane' %(self.store_dir,self.store_dir,self.store_dir))
	    run('rm -f %s/ctrlplane_files.tar' %(self.store_dir))

        # Save space, no need to save contrail_installer.tgz for now
        self.run_shell('rm -f %s/ctrlplane/contrail_installer.tgz' %(self.store_dir))    
        dest_dir= self.args.store
        self.run_shell('ln -s %s %s/%s' %(self.store_dir, dest_dir, self.datestr))
        
        for host in [ svl_server ] : 
            with settings(warn_only=True):
                local('sync')
            with settings(host_string= 'builder@%s' %(host) , warn_only=True):
                run( 'sudo ln -s %s %s/%s' %(self.store_dir, dest_dir, self.datestr))

    def get_nightly_rpms (self):
        for f in glob.glob (os.path.join (self.nightly_build_repo,
                'prepo', '*.rpm')):
            n = self.rpm_get_name (f)
            self._latest[n] = os.path.normpath (f)
            shutil.copy2 (self._latest[n], self.repo_dir)
            

    def make_contrail_pkg(self):
        contrail_pkg_dir = '%s/../contrail_packages' % self.repo_dir
        #Create repo
        self.run_shell('cd %s; createrepo .' % self.repo_dir)

        #Create the contrail rpms tgz
        self.run_shell('mkdir %s' % contrail_pkg_dir)
        self.run_shell('cd %s; tar -cvzf %s/contrail_rpms.tgz .' %  
                       (self.repo_dir, contrail_pkg_dir))

        #Copy all required files to the repo_dir/contrail_packages.
        self.run_shell('cp README %s' % contrail_pkg_dir)
        self.run_shell('cp setup.sh %s' % contrail_pkg_dir)
        self.run_shell('cp -R helpers %s' % contrail_pkg_dir)
        self.run_shell('echo "BUILDID=%s" > %s/VERSION' % (self.args._id, contrail_pkg_dir))

        #Create a contrail packages tgz with the rpms tgz and required file.
        pwd = os.getcwd()
        self.run_shell('cd %s/..; tar -cvzf %s/contrail_packages_%s.tgz contrail_packages' %  
                       (self.repo_dir, pwd, self.args._id))
        self.run_shell('cd ../common/rpm; make TAG=%s contrail-install-packages' % self.args._id)
        pkg_name = glob.glob('%s/noarch/contrail-install-packages*%s*.rpm' %
                             (self.args.master, self.args._id))[0]
        shutil.copy('%s' % pkg_name, self.repo_dir)
        shutil.copy('%s' % pkg_name, '%s' % self.store_dir)

        #Remove the tgz after building the rpm
        #self.run_shell('rm -rf %s/contrail_packages' % self.repo_dir)

    def mk_iso (self):
        if self.args._id:
            if self.nightly_build_repo:
                self.get_nightly_rpms ()
            else:
                self.get_other_rpms ()
                self.get_built_rpms ()
            self.replace_rpms ()
            self.make_contrail_pkg()
            self.mk_conf_xml ()
            self.mk_ks ()
            self.update_repo ('-g comps.xml %s' % self.repo_dir)
            self.run_pungi ()
            self.copy_tools()

    def copy_tools(self):
        tools = glob.glob('%s/../TOOLS/contrail*.tgz' % self.args.master)
        for tool in tools:
        shutil.copy(tool, '%s' % self.store_dir)

    def write_new_pkg_list (self):
        self.rpm_list_file=os.path.join (self.store_dir, 'log','file-list-%s' % self.datestr)
        with open (self.rpm_list_file, 'w') as f:
            for fl in self.new_rpms:
                f.write ('%s\n' % fl)
                printlog.info('+ new', fl)
       
    def replace_rpms (self):
        pass

    def run_pungi (self):
        self.run_shell('sync')
        time.sleep(20)
        temp_dir= tempfile.mkdtemp()
        self.run_shell ('''cd %s; sudo pungi --name=%s --config=cf.ks          \
            --nosource --destdir=%s/destdir --cachedir=%s/cachedir   \
            --force --ver=%s''' % (self.store_dir, 
                self.args.btag, temp_dir, temp_dir, self.args._id))
        self.run_shell ('''sudo find %s \( -name *x86_64.iso -o -name *x86_64-DVD.iso \) | xargs -n1 -i cp {} %s/''' %( temp_dir, self.store_dir))
        self.run_shell('sudo rm -rf %s' %(temp_dir) )

    def mk_ks (self):
        tmplate_top = '''repo --name=jnpr-ostk-%s --baseurl=file://%s
%%packages --nobase
''' % (self.args.btag, self.repo_dir)
        tmplate_end = '''
%end
'''
        with open (os.path.join (self.store_dir, 'cf.ks'), 'w') as fd:
            fd.write (tmplate_top)
            fd.write('@core')
            fd.write (tmplate_end)
       
    def mk_conf_xml (self):
        tmplate_top = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE comps PUBLIC "-//Red Hat, Inc.//DTD Comps info//EN" "comps.dtd">
<comps>

  <group>
   <id>core</id>
   <default>false</default>
   <uservisible>true</uservisible>
   <display_order>1024</display_order>
   <name>core</name>
   <description>Contrail Distro </description>
    <packagelist>
'''
        tmplate_end = '''
      <packagereq type="mandatory">contrail-install-packages</packagereq>
    </packagelist>
  </group>
</comps>
'''
        with open (os.path.join (self.repo_dir, 'comps.xml'), 'w') as fd:
            fd.write (tmplate_top)
            for pkg in BASE_PKGS.keys():
                fd.write (
                    '     <packagereq type="mandatory">%s</packagereq>\n' % (pkg))
            fd.write (tmplate_end)

    def update_repo (self, path):
        o = self.run_shell ('createrepo %s' % path)
            
    def build_them (self):
        rlist = list (self.build_targets)
        printlog.info('ready to build %s' % ', '.join (map (lambda x: x.name, rlist)))
        if self.args._id:
	    dt = self.args._id
        else:
	    dt = self.datestr
        for p in rlist:
            p.pkgs = filter (lambda y: y in self.build_rpms, p.pkgs)
            if self.args._id:
                [self.new_rpms.add (x) for x in p.build (
                        dt, self.args.target_dir, self.repo_dir)]


    def parse_args (self, args):
        ''' cli args in a flat string '''
        conf_parser = argparse.ArgumentParser(add_help = False)
        
        conf_parser.add_argument("-c", "--conf_file",
                                 help="Specify config file", metavar="FILE")
        args, remaining_argv = conf_parser.parse_known_args(args.split())

        defaults = {
            'target_dir' :      os.path.expanduser ('~/rpmbuild/my-repo'),
            'master' :          '/cs-shared/builder/RPMS',
            'cache' :           '/cs-shared/builder/cache',
            'all' :             False,
            '_id' :             None,
            'store' :           '/cs-shared/builder',
            'btag' :             os.environ['USER'],
            'workspace' : 	'/home/stack/jenkins/workspace/DailyBuild',
            'from_jenkins' :    False
        }

        if args.conf_file:
            config = ConfigParser.SafeConfigParser()
            config.read([args.conf_file])
            defaults.update(dict(config.items("DEFAULTS")))

        # Override with CLI options
        # Don't surpress add_help here so it will handle -h
        parser = argparse.ArgumentParser(
            # Inherit options from config_parser
            parents=[conf_parser],
            # printlog.info(script description with -h/--help)
            description=__doc__,
            # Don't mess with format of description
            formatter_class=argparse.RawDescriptionHelpFormatter,
            )
        parser.set_defaults(**defaults)

        parser.add_argument('-t', "--target_dir", dest="target_dir",
               help = "target rpm repo")
        parser.add_argument('-a', "--all", action="store_true",
               dest="all", help = "build everything")
        parser.add_argument('-f', "--force", action="store_true",
               dest="force", help = "ignore check for git-id")
        #group = parser.add_mutually_exclusive_group ()
        parser.add_argument('-i', "--id", type=int, 
               dest="_id", help = "build id")
        parser.add_argument('-s', "--store", 
               dest="store", help = "build store id")
        parser.add_argument('-C', "--cache", 
               dest="cache", help = "build store cache")
        parser.add_argument('-m', "--master", 
               dest="master", help = "master to symlink to")
        parser.add_argument('-k', "--skipbuild", action="store_true",
                default=False, dest="skipbuild", help = "skip build")
        parser.add_argument('-b', "--build_tag", 
               dest="btag", help = "build tag for iso")
        parser.add_argument('-w', "--workspace", 
               dest="workspace", help= "Location of ctrlplane source code")
        parser.add_argument('-j', "--fromjenkins", action='store_true',
               dest="from_jenkins", help= "Flag to identify if jenkins triggered the build")
        parser.add_argument('-B', "--build_id", 
               dest="nightly", help= "Bypass to pick by nightly id /cs-shared/builder assumed")
        
        self.args, self.targets = parser.parse_known_args(remaining_argv)

    def verify_cache (self, linkpath):
        #import pdb; pdb.set_trace ()
        err, cnt = '', 0
        dist = packages.find_distro ()
        for pkg in self.cache_rpms:
            try:
                filename = os.path.join(self.args.cache,
                                        packages.packages[pkg][dist]['filename'])
            except KeyError:
                filename = os.path.join(self.args.cache,
                                        BASE_PKGS[pkg]['filename'])
            if os.path.isfile (filename):
                shutil.copy (filename, linkpath)
                printlog.info('copying %s ...' % filename)
                self._latest[pkg] = filename
            else:
                err += 'pkg %s is missing in %s\n' % (
                    packages.packages[pkg][dist]['filename'], self.args.cache)
                printlog.info('ERROR  %s ...' % filename)
                cnt += 1

        if cnt:
            raise IOError, 'Error on %d packages:\n%s' % (cnt, err)

    def verify_build (self):
        self.verify_rpms (self.repo_dir, self.build_rpms)
        for pkg in self.build_rpms:
            self._latest[pkg] = os.path.normpath (os.path.join (
                        self.args.target_dir, os.path.basename (
                            self._latest[pkg])))

    def get_built_rpms (self):
        return self.verify_build ()

    def get_other_rpms (self):
        self.verify_cache (self.repo_dir)

    def verify_rpms (self, path, rpmlist, linkpath=None):
        err, cnt = '', 0
        for pkg in rpmlist:
            flist = [x for x in self.rpm_list_by_pattern (pkg, os.path.join (
                        path, "%s*.rpm" % pkg))]
            if len (flist) != 1:
                err += 'pkg %s with %s at [%s]\n' % (pkg, str(flist), path)
                printlog.info('ERROR  pkg = %s , flist = %s, path = %s' % (pkg, flist, path))
                cnt += 1
            else:
                if linkpath:
                    shutil.copy (flist[0], linkpath)
                self._latest[pkg] = flist[0]
        if cnt:
            raise IOError, 'Error on %d packages:\n%s' % (cnt, err)

if __name__ == '__main__':
    DISTRO = platform.dist()[0]
    if 'centos' in DISTRO:
        import packages
        from centos.base import packages as base_pkgs
    elif 'fedora' in DISTRO:
        import packages
        from fedora.base import packages as base_pkgs
    elif 'redhat' in DISTRO:
        import redhat.dependent as packages
        from redhat.base import packages as base_pkgs
    rel = packages.find_distro()
    BASE_PKGS = base_pkgs[rel]


    nb = NightlyBuilder (' '.join (sys.argv[1:]))
    nb.build ()
