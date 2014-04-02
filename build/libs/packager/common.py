#!/usr/bin/env python
''' Generic Library for Packager scripts '''


import os
import re
import sys
import copy
import shutil
import logging
import getpass
import tempfile
import operator
import platform
from lxml import etree
from xml.etree import ElementTree

from utils import Utils

log = logging.getLogger("pkg.%s" %__name__)
PLATFORM = Utils.get_platform_info()

class BasePackager(Utils):
    ''' Base class for packager methods '''
    def __init__(self, **kwargs):
        self.base_pkg_files        = self.expanduser(kwargs['base_package_file'])
        self.depends_pkg_files     = self.expanduser(kwargs['depends_package_file'])
        self.contrail_pkg_files    = self.expanduser(kwargs['contrail_package_file'])
        self.id                    = kwargs.get('build_id', 999)
        self.sku                   = kwargs.get('sku', 'grizzly')
        self.branch                = kwargs.get('branch', None)
        store                      = self.expanduser(kwargs['store_dir'])
        self.store                 = os.path.join(store, str(self.id))
        self.iso_prefix            = kwargs.get('iso_prefix', getpass.getuser())
        self.abs_pkg_dirs          = self.expanduser(kwargs['absolute_package_dir'])
        self.cache_base_dir        = self.expanduser(kwargs['cache_base_dir'])
        self.contrail_pkg_dirs     = self.expanduser(kwargs.get('contrail_package_dir', None))
        self.git_local_repo        = self.expanduser(kwargs['git_local_repo']) 
        self.make_targets          = kwargs.get('make_targets', None)
        self.make_targets_file     = self.expanduser(kwargs.get('make_targets_file', None))
        self.comps_xml_template    = kwargs.get('comps_xml_template', None)
        pkg_types                  = {'ubuntu': 'deb', 'centos': 'rpm', \
                                      'redhat': 'rpm', 'fedora': 'rpm'}
        self.platform              = platform.dist()[0].lower()
        self.platform              = PLATFORM[0]
        self.cache_subdir          = "".join(PLATFORM[:2]).lower().replace('.', '')
        self.pkg_type              = pkg_types[self.platform]
        self.store_log_dir         = os.path.join(self.store, 'log')
        self.artifacts_dir         = os.path.join(self.git_local_repo, 'build', 'artifacts')
        self.artifacts_extra_dir   = os.path.join(self.git_local_repo, 'build', 'artifacts_extra')
        self.default_targets       = []
        self.pkglist_file          = ''
        self.meta_pkg              = ''
        self.packager_dir          = os.getcwd()
        self.base_pkgs             = {}
        self.depends_pkgs          = {}
        self.contrail_pkgs         = {}
        self.imgname               = ''
        self.repo_dirs             = []
        self.exec_status           = 0

    def ks_build(self):
        '''Execute Packager for each package type'''
        # get pkg info
        additems = {'found_at': {}, 'repo': ''}
        base_pkgs = self.parse_cfg_file(self.base_pkg_files)
        depends_pkgs = self.parse_cfg_file(self.depends_pkg_files)
        contrail_pkgs = self.parse_cfg_file(self.contrail_pkg_files, additems)
        base_pkgs_dict = self.get_dict_by_item(base_pkgs, 'package_type')
        depends_pkgs_dict = self.get_dict_by_item(depends_pkgs, 'package_type')
        contrail_pkgs_dict = self.get_dict_by_item(contrail_pkgs, 'package_type')
        # make contrail-install-packages are done first
        pkgtypes = sorted(contrail_pkgs_dict.keys())
        if 'contrail-install-packages' in pkgtypes:
            pkgtypes.remove('contrail-install-packages')
            pkgtypes = ['contrail-install-packages'] + pkgtypes

        for pkgtype in pkgtypes:
            try:
                self.base_pkgs, self.depends_pkgs = {}, {}
                self.targets = []
                self.contrail_pkgs = contrail_pkgs_dict[pkgtype]
                self.meta_pkg = pkgtype
                self.pkglist_file = os.path.join(self.store, 'log', 
                                             '%s_%s_list.txt' % (
                                             self.meta_pkg, self.pkg_type))
                self.default_targets = filter(lambda pkg: pkg.endswith('-default-target'),
                                          self.contrail_pkgs.keys()) 
                if base_pkgs_dict.has_key(pkgtype):
                    self.base_pkgs = base_pkgs_dict[pkgtype]
                if depends_pkgs_dict.has_key(pkgtype):
                    self.depends_pkgs = depends_pkgs_dict[pkgtype]
                self.exec_steps()
                log.info('\n')
                log.info('Packager Store: %s' % self.store)
                log.info('Packager Completed Successfully for Type (%s)' % pkgtype)
                log.info('\n')
           except:
                self.exec_status = 255
                log.error('Packager Failed for Type (%s)' % pkgtype)
                log.error('Skipping rest of the steps for Type (%s)' % pkgtype)
          
    def setup_env(self):
        ''' setup basic environment necessary for packager like
            updating config data structures, creating dirs,
            copying package files..etc
        '''
        
        # update branch and build tag and tgz name
        # Temporarily override user input for branch
        self.branch = self.exec_cmd_out('cat %s/controller/src/base/version.info' 
                                             %self.git_local_repo)[0]
        
        # update repo dir with store dir prefix and get repo list
        self.update_repoinfo(self.base_pkgs, self.depends_pkgs,
                                           self.contrail_pkgs)
        self.repo_dirs = self.get_repodirs(self.base_pkgs, self.depends_pkgs, 
                                           self.contrail_pkgs)

        # create dirs
        self.create_dir(self.store)
        self.create_dir(self.store_log_dir)
        self.create_dir(self.artifacts_dir)
        self.create_dir(self.artifacts_extra_dir)
        for repo_dir in self.repo_dirs:
            self.create_dir(repo_dir)

        # Update make location with git local repo
        for target in self.contrail_pkgs.keys():
            self.contrail_pkgs[target]['makeloc'] = os.path.join(self.git_local_repo,
                                                     self.contrail_pkgs[target]['makeloc'])
            self.contrail_pkgs[target]['builtloc'] = os.path.join(self.git_local_repo,
                                                     self.contrail_pkgs[target]['builtloc'])

        # update location of os and dependent package location
        cache_dir = []
        if type(self.cache_base_dir) is str:
            self.cache_base_dir = [self.cache_base_dir]
        for dirname in self.cache_base_dir:
            cache_dir.append(self.expanduser(os.path.join(dirname,
                               self.cache_subdir, self.sku)))
        for each in self.base_pkgs.keys():
            if self.base_pkgs[each]['location'] == '':
                self.base_pkgs[each]['location'] = cache_dir
        for each in self.depends_pkgs.keys():
            if self.depends_pkgs[each]['location'] == '':
                self.depends_pkgs[each]['location'] = cache_dir

        # override location of os and dependent packages if absolute path given
        if self.abs_pkg_dirs:
            for each in self.base_pkgs.keys():
                self.base_pkgs[each]['location'] = self.abs_pkg_dirs
            for each in self.depends_pkgs.keys():
                self.depends_pkgs[each]['location'] = self.abs_pkg_dirs

        # update make target list
        if self.make_targets != None and len(self.make_targets) != 0:
            for pkg in self.get_as_list(self.make_targets):
                if pkg not in self.contrail_pkgs.keys():
                    log.warn('Skipping Target (%s). Not defined in (%s)' % (
                             pkg, self.contrail_pkg_files))
                    continue
                self.targets += [pkg]
        if self.make_targets_file != None:
            targets_frm_file = self.rtrv_lsv_file_info(self.make_targets_file)
            for pkg in self.get_as_list(targets_frm_file):
                if pkg not in self.contrail_pkgs.keys():
                    log.warn('Skipping Target (%s). Not defined in (%s)' % (
                             pkg, self.contrail_pkg_files))
                    continue
                self.targets += [pkg]
       
        # Skip building all packages but not those supplied
        # in self.targets and self.meta_pkg
        # Update built loc and create support files
        if self.contrail_pkg_dirs:
            # update build location if contrail dir is supplied
            for target in self.contrail_pkgs.keys():
                if target in self.targets or \
                   target in self.meta_pkg:
                    continue
                self.contrail_pkgs[target]['builtloc'] = self.contrail_pkg_dirs

            # pick up or create contrail_installer.tgz 
            if not ('contrail-setup' in [tgt.strip('-deb') for tgt in self.targets] or
                    'contrail-all' in self.targets):
                if self.platform == 'ubuntu':
                    builddir = os.path.join(self.git_local_repo, 'build', 'debian')
                else:
                    builddir = os.path.join(self.git_local_repo, 'controller', 'build')
                self.create_dir(builddir)
                files = self.get_file_list(self.contrail_pkg_dirs, 'contrail_installer.tgz')
                installer_tgz = self.get_latest_file(files)
                if installer_tgz != '':
                    log.info('Copying %s to %s' %(installer_tgz, builddir))
                    shutil.copy(installer_tgz, builddir)
                else:
                    installer_script = os.path.join(self.git_local_repo, 'tools',
                                                     'provisioning', 'create_installer.py')
                    log.info('Creating contrail_installer.tgz...')
                    self.exec_cmd(installer_script, wd=builddir)
                    
        else:
            self.targets = self.targets or self.default_targets
                    
        # OS PKGs and Depends PKGs
        self.check_package_md5(self.base_pkgs)
        self.check_package_md5(self.depends_pkgs)
        self.copy_pkg_files(self.depends_pkgs)
        self.copy_pkg_files(self.base_pkgs)
        self.check_package_md5(self.base_pkgs, 'repo')
        self.check_package_md5(self.depends_pkgs, 'repo')

    def make_pkgs(self):
        ''' make package with given TAG '''
        if len(self.targets) == 0:
            log.warn('make target list is empty...Nothing to make')
            return
        for target in self.targets:
            log.info('Making Target: %s' %target)
            if not self.contrail_pkgs.has_key(target):
                raise RuntimeError('Target (%s) is not defined in %s' %(
                                    target, self.contrail_pkg_files))
            cmd = 'make CONTRAIL_SKU=%s TAG=%s FILE_LIST=%s %s' %(self.sku, 
                       self.id, self.pkglist_file,
                       self.contrail_pkgs[target]['target'])
            self.exec_cmd(cmd, wd=self.contrail_pkgs[target]['makeloc'])

    def verify_built_pkgs_exists(self, targets=None, skips=None,
                                 recursion=True):
        ''' verify that contrail built packages are created and 
            and available in specific dirs
        '''
        missing = []
        targets = targets if targets else self.contrail_pkgs.keys()
        targets = list(set(targets) - set(self.get_as_list(skips))) if skips \
                            else self.get_as_list(targets)
        for each in targets:
            pkgs = self.contrail_pkgs[each]['pkgs']
            pkgs = self.get_as_list(pkgs)
            for pkg in filter(None, pkgs):
                log.info('Verify Built Pkg (%s) is present in (%s)' %(
                          pkg, self.contrail_pkgs[each]['builtloc']))
                if self.contrail_pkgs[each]['found_at'].has_key(pkg):
                    #Already updated
                    continue
                pattern = self.contrail_pkgs[each]['pkg_pattern'].format(pkg=pkg)
                builtlocs = self.contrail_pkgs[each]['builtloc']
                builtlocs = self.get_as_list(builtlocs)
                flist = self.get_file_list(builtlocs, pattern,
                                           recursion=recursion)
                if len(flist) != 0:
                    pkgfile = self.get_latest_file(flist)
                    log.debug(pkgfile)
                    self.contrail_pkgs[each]['found_at'][pkg] = pkgfile
                else:
                    missing.append(pkg)
                    log.error('Built Package file for Package (%s) is not found @ %s' %(
                               pkg, self.contrail_pkgs[each]['builtloc'])) 
        if len(missing) != 0:
            log.error('Package file for One or More built package are not found')
            raise IOError('Missing Packages: \n%s' %"\n".join(missing)) 

    def create_pkg_list_file(self):
        pkglist = []
        for target in self.contrail_pkgs.keys():
            packages = self.contrail_pkgs[target]['pkgs']
            packages = [packages] if type(packages) is str else packages
            pkglist.extend(filter(None, packages))
        with open(self.pkglist_file, 'w') as fid:
            fid.write("%s\n" %"\n".join(sorted(pkglist)))
            fid.flush()
        log.info('Packages list file (%s) is created' %self.pkglist_file)

    def create_log(self):
        filelist = []
        filelist_file = os.path.join(self.store_log_dir, 
                                     '%s_file_list.txt' %self.meta_pkg)
        for target in self.contrail_pkgs.keys():
            packages = self.contrail_pkgs[target]['pkgs']
            packages = [packages] if type(packages) is str else packages
            for pkg in filter(None, packages):
                if self.contrail_pkgs[target]['found_at'][pkg] != '':
                    pkgfile = os.path.basename(self.contrail_pkgs[target]['found_at'][pkg])
                    filelist.append(pkgfile)
        with open(filelist_file, 'w') as fid:
            fid.write("%s\n" %"\n".join(sorted(filelist)))
            fid.flush()

    def create_git_ids(self, manifest=None, filename=None, retries=5):
        filename = filename or os.path.join(self.store, 'git_build_%s.txt' %self.id)
        manifest = manifest or os.path.join(self.git_local_repo, '.repo', 'manifest.xml')
        ids_dict = {}
        tree = ElementTree.parse(manifest)
        for project in tree.findall('project'):
            element_dict = dict(project.items())
            parsed_element = self.parse_git_cfg_file(os.path.join(self.git_local_repo, 
                                                                element_dict['path'], 
                                                               '.git', 'config'))
            url = parsed_element[r'remote "%s"' %element_dict['remote']]['url']
            cmd = 'git ls-remote %s %s' %(url, element_dict.get('revision', 'HEAD'))
            for retry in range(retries):
                gitid = ''
                try:
                    gitid_info = self.exec_cmd_out(cmd)
                except:
                    log.warn('Retrieve GIT ID for URL (%s) Failed'\
                             ' Retrying...' % cmd)
                else:
                    gitid = gitid_info[0].split('\t')[0]
                    ids_dict[gitid] = url
                    break
                finally:
                    if retry == retries - 1 and gitid == '':
                        log.error('Unable to retrieve Git ID for URL (%s)' % url)
                        log.error('Skipping...')
                        
        with open(filename, 'w') as file_id:
            #id_list = ['%s\t%s' %(item, key) for key, item in ids_dict.items()]
            id_list = ['{0:<60}    {1:<}'.format(item, key) \
                           for key, item in ids_dict.items()]
            file_id.write('%s\n' %"\n".join(id_list))
            file_id.flush()
        return filename
        
    def run_pungi(self, ks_file):
        ''' execute pungi tool and copy built iso file to store directory '''
        self.exec_cmd('sync')
        tempdir = tempfile.mkdtemp()
        self.exec_cmd('sudo pungi \
                            --name=%s \
                            --config=%s \
                            --destdir=%s/destdir \
                            --cachedir=%s/cachedir \
                            --ver=%s \
                            --force \
                            --nosource' %(self.iso_prefix, ks_file, 
                                          tempdir, tempdir, self.id),
                        wd=self.store)
        isofiles = self.get_file_list([tempdir], '%s-%s*-DVD.iso' %(
                                      self.iso_prefix, self.id))
        isofile = self.get_latest_file(isofiles)
        shutil.copy2(isofile, self.store)
        self.imgname = os.path.join(self.store, os.path.basename(isofile))
        self.exec_cmd('sudo rm -rf %s' %tempdir)
        log.info('ISO (%s) has been built Successfully!'%isofile)
        log.info('ISO (%s) is copied to (%s)' %(isofile, self.imgname))

    def create_comps_xml (self):
        ''' create comps xml need for repo creation '''
        repo_dir = os.path.join(self.store, self.meta_pkg)
        pkgs = ['%s<packagereq type="mandatory">%s</packagereq>' % (' '*6, pkg)\
                for pkg in self.base_pkgs.keys()]
        template = self.comps_xml_template.format(__packagesinfo__='\n'.join(pkgs))
        with open(os.path.join(repo_dir, 'comps.xml'), 'w') as fd:
            fd.write ('%s' %template)
            
    def create_ks(self):
        ''' create kick start file need for pungi '''
        ks_file = os.path.join (self.store, 'cf.ks')
        repo_dir = os.path.join(self.store, self.meta_pkg)
        with open (ks_file, 'w') as fd:
            fd.write('repo --name=jnpr-ostk-%s --baseurl=file://%s\n' %(
                      self.iso_prefix, repo_dir))
            fd.write('%packages --nobase\n')
            fd.write('@core\n')
            fd.write('%end\n')
        return ks_file

    def createrepo(self, extraargs=''):
        ''' execute create repo '''
        for repo_dir in self.repo_dirs:
            log.info('Executing createrepo in (%s)...' %repo_dir)
            self.exec_cmd('createrepo %s .' %extraargs, wd=repo_dir)   
                
    def create_contrail_pkg(self, *pkgs): 
        ''' make meta packages
        '''
        #make contrail-install-packages
        pkginfo = self.contrail_pkgs[self.meta_pkg]
        tgz_name = os.path.join(self.store,
                                '%s_%s-%s~%s.tgz' %(self.meta_pkg,
                                self.branch, self.id, self.sku))
        self.exec_cmd('make CONTRAIL_SKU=%s FILE_LIST=%s TAG=%s %s' %(
                       self.sku, tgz_name, self.id,
                       pkginfo['target']), pkginfo['makeloc'])
        log.debug('Removing TGZ File (%s) after Make' % tgz_name)
        os.unlink(tgz_name)
