#!/usr/bin/env python
''' Generic Library for Packager scripts '''

import sys
import os
import logging
import getpass
import copy
import shutil
import tempfile
import pdb
import re

from utils import Utils

log = logging.getLogger("pkg.%s" %__name__)

class TestExecution(Utils):
	def __init__(self, **kwargs):
		self.fab_env      = kwargs['fabric_repo']
		self.fab_cmds     = kwargs['fabric_exec_cmds']
		self.setup_cmds   = kwargs['fabric_setup_cmds']
		
	def fabric_exec_cmds(self):
		for cmd in self.fab_cmds:
			log.info('Executing Fabric Command: %s' %cmd)
			self.exec_cmd('fab %s' %cmd, wd=self.fab_env)

	def setup_nodes(self):
		#reimage
		for cmd in self.setup_cmds:
			self.exec_cmd(cmd, self.fab_env)
	
	def run(self):
		self.setup_nodes()
		self.exec_cmd('fab print_status', self.fab_env)
		self.fabric_exec_cmds()
		
		
class GitRepo(Utils):
    def __init__(self, repo_dir, url, cwd_repo):
        self.repo_dir  = repo_dir
        self.url       = url
        self.cwd_repo  = cwd_repo

    def create_git_config(self, gitconfig):
        gitdir = os.path.join(self.cwd_repo, '.git')
        gitconfig_file = os.path.join(gitdir, 'config')
        e_repo = os.path.join(os.path.expanduser('~'), '.repo')
        if os.path.isdir(e_repo):
            log.debug('Git repo is already initialized at {edir},\
                       Moving {edir} as {edir}_moved'.format(edir=e_repo))

        if not os.path.isdir(gitdir):
            log.debug('Git config dir {dirn} do not exists.\
                       Creating Dir {dirn} ...'.format(dirn=gitdir))
            os.mkdir(gitdir)

        if not os.path.isfile(gitconfig_file):
            log.debug('Git config fie {gfile} do not exists.\
                       Creating Dir {gfile} ...'.format(gfile=gitconfig_file))
            with open(gitconfig_file, 'w') as fid:
                fid.write(gitconfig)

    def init_repo(self, template=None):
        usr = getpass.getuser()
        usrhome = os.path.expanduser('~')
        gitconfig_file = os.path.join(usrhome, '.git', 'config')
        if not os.path.isdir(self.repo_dir):
            os.makedirs(self.repo_dir)

        if template != None:
	    self.create_git_config(template)

	    self.exec_cmd('echo $(pwd)', wd=self.repo_dir)
        self.exec_cmd('git config user.name %s' %usr)
        self.exec_cmd('git config --global user.email %s@juniper.net' %usr)
        self.exec_cmd('repo init -u %s' %self.url, wd=self.repo_dir)

    def repo_sync(self):
        log.info('Syncing Repo...')
        self.exec_cmd('repo sync -j 8', wd=self.repo_dir)

    def fetch_packages(self, loclist):
        for loc in loclist:
            loc = os.path.join(self.repo_dir, loc)
            log.info('Fetch Packages in (%s)' %loc)
            self.exec_cmd('python fetch_packages.py', wd=loc)


class BasePackager(Utils):
    def __init__(self, **kwargs):
        self.id                    = kwargs['id']
        self.skip_build            = kwargs['skip_build']
        self.store                 = kwargs['store'].format(id=self.id)
        self.build_name            = kwargs['build_name']
        self.pkg_dirs              = kwargs['pkg_dirs']
        self.cont_pkg_dirs         = kwargs['cont_pkg_dirs']
        self.jenkins               = kwargs['jenkins']
        self.base_pkg_files        = kwargs['base_pkg_files']
        self.deps_pkg_files        = kwargs['deps_pkg_files']
        self.cont_pkg_files        = kwargs['cont_pkg_files']
        self.cfg_file              = kwargs['cfg_file']
        self.exec_list             = kwargs['exec']
        self.git_fetch_pkgdirs     = kwargs['git_fetch_pkgdirs']
        self.git_lrepo             = kwargs['git_local_repo'].format(id=self.id)
        self.install_grepo         = kwargs['install_local_repo']
        self.no_sync_repo          = kwargs['no_sync_repo']
        self.git_url               = kwargs['git_url']
        self.level                 = kwargs['log_level']
        self.fabenv                = kwargs['fab_env']
        self.fab_cmds              = kwargs['exec']
        self.no_parallel_make      = kwargs['no_parallel_make']
        self.targets               = kwargs['make_targets'] + \
                                     self.rtrv_lsv_file_info(kwargs['make_targets_file'])      
        self.config                = self.import_file(self.cfg_file)
        self.gitconfig             = self.config.gitconfig
        self.namemap               = self.config.NAMEMAP
        self.pkg_type              = self.config.pkg_type
        self.comps_xml_template    = self.config.comps_xml_template
        self.pkg_repo              = os.path.join(self.store, 'pkg_repo')
        self.cont_pkgs_dir         = os.path.join(self.store, 'contrail_packages')
        self.pkgs_tgz              = os.path.join(self.cont_pkgs_dir, 'contrail_%ss.tgz' %self.pkg_type)
        self.git_build_dir         = os.path.join(self.git_lrepo, 'tools', 'packaging', 'build')
        self.cont_pkgs_tgz         = os.path.join(self.git_build_dir, 'contrail_packages_%s.tgz' %self.id)
        self.base_pkgs             = {}
        self.deps_pkgs             = {}
        self.cont_pkgs             = {}
        self._curr_info            = {}
        self.imgname               = ''
    
    def update_namemap(self):
        if self.namemap is None:
            return
        pat = re.compile(r'-RUNTIME-')
        if pat.match(self.namemap['GIT_LOCAL_REPO']):
            self.namemap['GIT_LOCAL_REPO'] = self.git_lrepo
    
    def create_git_repo(self):
        lrepo = GitRepo(self.git_lrepo, self.git_url, self.git_lrepo)
        if self.install_grepo:
            log.debug('Install Git Local Repo in %s' %self.git_lrepo)
            lrepo.init_repo(self.gitconfig)
        else:
            log.debug('Skipping Install Git Local Repo')
        if not self.no_sync_repo:
            lrepo.repo_sync()
        lrepo.fetch_packages(self.git_fetch_pkgdirs)


    def setup_env(self):
        # get pkg info
        self.update_namemap()
        additems = {'found_at': dict()}
        self.base_pkgs = self.parse_cfg_file(self.base_pkg_files)
        self.deps_pkgs = self.parse_cfg_file(self.deps_pkg_files)
        self.cont_pkgs = self.parse_cfg_file(self.cont_pkg_files, additems)
        self.update_cfg_vars(self.cont_pkgs)

        # create dirs
        if self.install_grepo:
			self.create_dir(self.git_lrepo)
        self.create_dir(self.store)
        self.create_dir(self.pkg_repo)
        self.create_dir(self.cont_pkgs_dir)

        # update dir list
        if self.pkg_dirs:
            for each in self.base_pkgs.keys():
                self.base_pkgs[each][location] = self.pkg_dirs
            for each in self.debs_pkgs.keys():
                self.base_pkgs[each][location] = self.pkg_dirs

        # update contrail dir list
        if self.cont_pkg_dirs:
            for target in self.cont_pkgs.keys():
                self.cont_pkgs[target]['buildloc'] = self.cont_pkg_dirs
                    
        # OS PKGs and Depends PKGs
        self.verify_pkgs_exists(self.base_pkgs)
        self.verify_pkgs_exists(self.deps_pkgs)
        self.copy_pkg_files(self.deps_pkgs, self.pkg_repo)

    def make_pkgs(self):
        for each in self.targets:
            log.info('Making Target: %s' %each)
            cmd = 'make TAG=%s %s' %(self.id, each)
            if not self.no_parallel_make:
                parallel = self.cont_pkgs[each]['poolsize']
                cmd += ' -j %s' %int(parallel)
            self.exec_cmd(cmd, wd=self.cont_pkgs[each]['makeloc'])

    def test_run(self):
        test = TestExecution(fabric_repo=self.fabenv,\
                             fabric_exec_cmds=self.fab_cmds,\
                             fabric_setup_cmds=['fab bringup_test_node:%s' %self.imgname])
        test.run()

    def verify_built_pkgs_exists(self, targets=None, skips=None):
        missing = []
        targets = targets if targets else self.cont_pkgs.keys()
        targets = list(set(targets) - set(skips)) if skips else targets
        for each in targets:
            pkgs = self.cont_pkgs[each]['pkgs']
            pkgs = [pkgs] if type(pkgs) is str else pkgs
            for pkg in filter(None, pkgs):
                log.info('Verify Built Pkg (%s) is present in (%s)' %(
                          pkg, self.cont_pkgs[each]['buildloc']))
                if self.cont_pkgs[each]['found_at'].has_key(pkg):
                    continue
                pattern = self.cont_pkgs[each]['pkg_pattern'].format(pkg=pkg)
                buildlocs = self.cont_pkgs[each]['buildloc']
                if type(buildlocs) is str:
                    buildlocs = [buildloc]
                flist = self.get_file_list(buildlocs, pattern)
                if len(flist) != 0:
                    pkgfile = self.get_latest_file(flist)
                    log.debug(pkgfile)
                    self.cont_pkgs[each]['found_at'][pkg] = pkgfile
                else:
                    missing.append(pkg)
                    log.error('Built Package file for Package (%s) is not found @ %s' %(
                               pkg, self.cont_pkgs[each]['buildloc'])) 
        if len(missing) != 0:
            log.error('Package file for One or More built package are not found')
            raise IOError('Missing Packages: \n%s' %"\n".join(missing)) 

    def run_pungi(self, ks_file):
        self.exec_cmd('sync')
        tempdir = tempfile.mkdtemp()
        self.exec_cmd('sudo pungi \
                            --name=%s \
                            --config=%s \
                            --destdir=%s/destdir \
                            --cachedir=%s/cachedir \
                            --ver=%s \
                            --force \
                            --nosource' %(self.build_name, ks_file, 
                                          tempdir, tempdir, self.id),
                        wd=self.store)
        isofiles = self.get_file_list([tempdir], '%s-%s*-DVD.iso' %(
                                      self.build_name, self.id))
        isofile = self.get_latest_file(isofiles)
        self.imgname = isofile
        shutil.copy2(isofile, self.store)
        self.exec_cmd('sudo rm -rf %s' %tempdir)
        log.info('ISO (%s) has been built Successfully!'%isofile)
        log.info('ISO (%s) is copied to %s' %(isofile, self.store))

    def create_comps_xml (self):
        pkgs = ['%s<packagereq type="mandatory">%s</packagereq>' % (' '*6, pkg)\
                for pkg in self.base_pkgs.keys()]
        template = self.comps_xml_template.format(pkgsinfo='\n'.join(pkgs))
        with open(os.path.join(self.pkg_repo, 'comps.xml'), 'w') as fd:
            fd.write ('%s' %template)
            
    def create_ks(self):
        ks_file = os.path.join (self.store, 'cf.ks')
        with open (ks_file, 'w') as fd:
            fd.write('repo --name=jnpr-ostk-%s --baseurl=file://%s\n' %(
                      self.build_name, self.pkg_repo))
            fd.write('%packages --nobase\n')
            fd.write('@core\n')
            fd.write('%end\n')
        return ks_file

    def createrepo(self, dirname=os.getcwd(), extraargs=''):
        log.info('Executing createrepo...')
        self.exec_cmd('createrepo %s .' %extraargs, wd=dirname)   
        		
    def create_contrail_pkg(self): 
        # create contrail_packages_(id).tgz
        shutil.copy2('setup.sh', self.cont_pkgs_dir)
        shutil.copy2('README', self.cont_pkgs_dir)
        with open(os.path.join(self.cont_pkgs_dir, 'VERSION'), 'w') as fid:
			fid.writelines('BUILDID=%s\n' %self.id)
        self.create_tgz(self.cont_pkgs_tgz, self.cont_pkgs_dir)
		#make contrail-install-packages
        pkg = 'contrail-install-packages'
        pkginfo = self.cont_pkgs[pkg]
        self.exec_cmd('make TAG=%s %s' %(self.id, pkg),
                       pkginfo['makeloc'])
