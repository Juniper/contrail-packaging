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
import traceback
from lxml import etree

#from utils import Utils
from libs.packager.utils import Utils

log = logging.getLogger("pkg")

class MakeError(Exception):
    pass

class BasePackager(Utils):
    ''' Base class for packager methods '''
    def __init__(self, **kwargs):
        self.debug                 = kwargs.get('debug', True) # echo unfiltered exec_cmd() output
        self.base_pkg_files        = self.expanduser(kwargs['base_package_file'])
        self.depends_pkg_files     = self.expanduser(kwargs['depends_package_file'])
        self.contrail_pkg_files    = self.expanduser(kwargs['contrail_package_file'])
        self.package_types         = kwargs.get('package_types', None)
        self.id                    = kwargs.get('build_id', 999)
        self.sku                   = kwargs.get('sku', 'mitaka')
        self.branch                = kwargs.get('branch', 9.9)
        self.copy_use_hard_link    = kwargs.get('copy_use_hard_link', False)
        self.store                 = self.expanduser(kwargs['store_dir'])
        self.abs_pkg_dirs          = self.expanduser(kwargs['absolute_package_dir'])
        self.cache_base_dir        = self.expanduser(kwargs['cache_base_dir'])
        self.contrail_pkg_dirs     = self.expanduser(kwargs.get('contrail_package_dir', None))
        self.git_local_repo        = self.expanduser(kwargs['git_local_repo'])
        self.make_targets          = kwargs.get('make_targets', None)
        self.fail_on_error         = kwargs.get('fail_on_error', False)
        self.make_targets_file     = self.expanduser(kwargs.get('make_targets_file', None))
        pkg_types                  = {'ubuntu': 'deb', 'centos': 'rpm', \
                                      'redhatenterpriselinuxserver': 'rpm', 'fedora': 'rpm',
                                      'centoslinux': 'rpm',
                                      'suselinuxenterpriseserver': 'rpm'}
        platform                   = self.get_platform_info(kwargs['os_version'])
        self.platform              = platform['default'][0]
        self.cache_subdir          = platform['formatted']
        self.pkg_type              = pkg_types[self.platform]
        self.store_log_dir         = os.path.join(self.store, 'package_info')
        self.artifacts_dir         = os.path.join(self.git_local_repo, 'build', 'artifacts')
        self.artifacts_extra_dir   = os.path.join(self.git_local_repo, 'build', 'artifacts_extra')
        self.sub_pkg_types         = []
        self.pkg_tgz_name          = ''
        self.default_targets       = []
        self.pkglist_file          = ''
        self.meta_pkg              = ''
        self.package_type          = ''
        self.packager_dir          = os.getcwd()
        self.base_pkgs             = {}
        self.depends_pkgs          = {}
        self.contrail_pkgs         = {}
        self.repo_dir              = ''
        self.exec_status           = 0

    def retrieve_pkgtypes_recursively(self, pkgtypes):
        '''Recursively retrieve dependent package type from given
           package types until the sub-package-type
        '''
        for pkgtype in pkgtypes:
            if (pkgtype in self.contrail_pkgs_dict.keys() and
                pkgtype in self.contrail_pkgs_dict[pkgtype].keys() and
                'sub_package_type' in self.contrail_pkgs_dict[pkgtype][pkgtype] and
                self.contrail_pkgs_dict[pkgtype][pkgtype]['sub_package_type']):
                sub_pkgs = copy.deepcopy(self.contrail_pkgs_dict[pkgtype][pkgtype]['sub_package_type'])
                #for sub_pkg in sub_pkgs:
                pkgtypes += self.retrieve_pkgtypes_recursively(self.get_as_list(sub_pkgs))
        return list(set(pkgtypes))

    def rearrange_types(self, pkgtypes):
        '''Rearrange a pkgtype if it has a sub_package_type
           defined so that sub_package_type builds first
        '''
        new_pkgtypes = copy.deepcopy(pkgtypes)
        for pkgtype in pkgtypes:
            # use dict where pkgtype is defined
            if pkgtype in self.contrail_pkgs_dict.keys():
               pkgs_dict = copy.deepcopy(self.contrail_pkgs_dict)
            elif pkgtype in self.depends_pkgs_dict.keys():
               pkgs_dict = copy.deepcopy(self.depends_pkgs_dict)
            else:
                log.error('Cant create an empty package for package '
                          'type (%s)' % pkgtype)
                log.error('Package type (%s) is found in contrail '
                         'package config but no packages are tagged '
                         'with that package type' % pkgtype)
                raise RuntimeError('No packages are tagged with '
                                   'Package type (%s); Empty package type '
                                   'is not allowed' % pkgtype)
            if not pkgtype in pkgs_dict[pkgtype].keys():
                log.warn('No Target for package type (%s) is present in'
                         ' contrail packages config file' % pkgtype)
                continue
            if 'sub_package_type' in pkgs_dict[pkgtype][pkgtype]:
                sub_package_types = pkgs_dict[pkgtype][pkgtype]['sub_package_type']
                sub_package_types = self.get_as_list(sub_package_types)
                for sub_type in filter(None, sub_package_types):
                    pkg_index = new_pkgtypes.index(pkgtype)
                    sub_index = new_pkgtypes.index(sub_type)
                    # move sub package type before current package type
                    if sub_index > pkg_index:
                        new_pkgtypes.remove(sub_type)
                        new_pkgtypes.insert(pkg_index, sub_type)
        return new_pkgtypes

    def ks_build(self):
        '''Execute Packager for each package type'''
        # get pkg info
        additems = {'found_at': {}, 'repo': ''}
        base_pkgs = self.parse_cfg_file(self.base_pkg_files)
        depends_pkgs = self.parse_cfg_file(self.depends_pkg_files)
        contrail_pkgs = self.parse_cfg_file(self.contrail_pkg_files, additems)
        base_pkgs_dict = self.get_dict_by_item(base_pkgs,
                                               'package_type')
        self.depends_pkgs_dict = self.get_dict_by_item(depends_pkgs,
                                                       'package_type')
        self.contrail_pkgs_dict = self.get_dict_by_item(contrail_pkgs,
                                                        'package_type')

        # build for given package_types. if not, find them from
        # config files
        if self.package_types:
            pkgtypes = self.retrieve_pkgtypes_recursively(copy.deepcopy(self.package_types))
        else:
            pkgtypes = list(set(sorted(self.contrail_pkgs_dict.keys() +
                                   self.depends_pkgs_dict.keys() +
                                   base_pkgs_dict.keys())))
            # make contrail-install-packages are done first
            if 'contrail-install-packages' in pkgtypes:
                pkgtypes.remove('contrail-install-packages')
                pkgtypes = ['contrail-install-packages'] + pkgtypes

        pkgtypes = self.rearrange_types(pkgtypes)
        # create packager stores
        self.create_dir(self.store)
        self.create_dir(self.store_log_dir)
        self.create_dir(self.artifacts_dir)
        self.create_dir(self.artifacts_extra_dir)

        for pkgtype in pkgtypes:
            self.package_type = pkgtype
            self.meta_pkg = pkgtype
            self.sub_pkg_types = []
            add_sku_tag = False
            log.info('Executing Build for Package Type (%s)' % pkgtype)
            try:
                self.base_pkgs, self.depends_pkgs = {}, {}
                self.contrail_pkgs = {}
                self.targets = []
                self.repo_dir = os.path.join(self.store, pkgtype)
                if self.package_type in self.contrail_pkgs_dict.keys():
                    self.contrail_pkgs = self.contrail_pkgs_dict[self.package_type]
                    if 'add_sku_tag' in self.contrail_pkgs[self.package_type] and \
                       self.contrail_pkgs[self.package_type]['add_sku_tag'].lower() == 'true':
                        add_sku_tag = True
                if add_sku_tag:
                    self.pkg_tgz_name = '%s_%s-%s-%s.tgz' % (self.package_type,
                                    self.branch, self.id, self.sku)
                else:
                    self.pkg_tgz_name = '%s_%s-%s.tgz' % (self.package_type,
                                    self.branch, self.id)

                self.pkglist_file = os.path.join(self.store_log_dir,
                                      '%s_%s_%s_list.txt' % (
                                      self.package_type, self.id, self.pkg_type))
                self.pkglist_thirdparty = os.path.join(self.store_log_dir,
                                          '%s_%s_%s_thirdparty.txt' % (
                                          self.package_type, self.id,
                                          self.pkg_type))
                self.default_targets = filter(lambda pkg: pkg.endswith('-default-target'),
                                          self.contrail_pkgs.keys())
                if base_pkgs_dict.has_key(pkgtype):
                    self.base_pkgs = base_pkgs_dict[pkgtype]
                if self.depends_pkgs_dict.has_key(pkgtype):
                    self.depends_pkgs = self.depends_pkgs_dict[pkgtype]
                if pkgtype in self.contrail_pkgs.keys():
                    if 'sub_package_type' in self.contrail_pkgs[pkgtype].keys():
                        self.sub_pkg_types = self.contrail_pkgs[pkgtype]['sub_package_type']
                        self.sub_pkg_types = self.get_as_list(self.sub_pkg_types)

                # Disabled temporarily
                # Verify/Copy package tgz for this pkgtype already exists
                # if contrail_pkg_dirs are given
                #if self.contrail_pkg_dirs:
                #    exists = self.check_pkgtype_exists(pkgtype)
                #    if exists:
                #        self.copy_pkgtype_tgz_to_store(pkgtype)
                #        log.debug('Skipping Building package tgz for package_type (%s)' % pkgtype)
                #        continue
                self.exec_steps()
                log.info('\n')
                log.info('Packager Store: %s' % self.store)
                log.info('Packager Completed Successfully for Type (%s)' % pkgtype)
                log.info('\n')
            except:
                self.exec_status = 255
                log.error(traceback.format_exc())
                log.error('Packager Failed for Type (%s)' % pkgtype)
                log.error('Skipping rest of the steps for Type (%s)' % pkgtype)
                if self.fail_on_error:
                    raise
        self.create_manifest_with_revision()

    def copy_pkgtype_tgz_to_store(self, package_type):
        '''Copy package tgz to store dir
        '''
        self.copyfiles(os.path.join(self.contrail_pkg_dirs, self.pkg_tgz_name), self.store, as_link=False)
        log.debug('Package TGZ (%s) for package_type (%s) is copied to (%s)' %(
            self.pkg_tgz_name, package_type, self.store))

    def check_pkgtype_exists(self, package_type):
        '''Check if given package_type already exists
           in contrail packages dirs
        '''
        exists = False
        if self.contrail_pkg_dirs:
            log.debug('Check if (%s) exists in (%s)' % (self.pkg_tgz_name, self.contrail_pkg_dirs))
            files = self.get_file_list(self.contrail_pkg_dirs, self.pkg_tgz_name, recursion=False)
            if len(files) == 0:
                log.warn('No Package TGZ for package_type (%s) is found at (%s)' % (package_type, self.contrail_pkg_dirs))
                log.info('Package TGZ for package_type (%s) needs to be built' % package_type)
            else:
                exists = True
        return exists

    def setup_env(self):
        ''' setup basic environment necessary for packager like
            updating config data structures, creating dirs,
            copying package files..etc
        '''

        # update repo dir with store dir prefix and get repo list
        self.update_repoinfo(self.base_pkgs, self.depends_pkgs,
                                           self.contrail_pkgs)

        # create packager local repo dir
        self.create_dir(self.repo_dir, recreate=True)

        # Update make location with git local repo
        for target in self.contrail_pkgs.keys():
            self.contrail_pkgs[target]['makeloc'] = os.path.join(self.git_local_repo,
                                                     self.contrail_pkgs[target]['makeloc'])
            self.contrail_pkgs[target]['builtloc'] = [os.path.join(self.git_local_repo, builtloc) for builtloc in
                                                         self.get_as_list(self.contrail_pkgs[target]['builtloc'])]

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
        # Update built loc with contrail_pkgs_dir if the target is empty
        # which basically means its a virtual target meant to pickup packages
        # than to build itself
        # Update built loc and create support files
        if self.contrail_pkg_dirs:
            # update build location if contrail dir is supplied
            for target in self.contrail_pkgs.keys():
                if ( target in self.targets or \
                   target == self.meta_pkg ) and \
                   self.contrail_pkgs[target]['target'] != '':
                    continue
                self.contrail_pkgs[target]['builtloc'] = self.contrail_pkg_dirs
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
            try:
                self.exec_cmd(cmd, wd=self.contrail_pkgs[target]['makeloc'])
            except:
                raise MakeError(sys.exc_info()[1])

    def verify_built_pkgs_exists(self, targets=None, skips=None,
                                 recursion=True):
        ''' verify that contrail built packages are created and
            and available in specific dirs
        '''
        missing = []
        targets = targets or self.contrail_pkgs.keys()
        skips = self.get_as_list(skips)
        targets = self.get_as_list(targets)
        if skips and targets:
            targets = list(set(targets) - set(skips))

        # Handle virtual targets
        # Virtual targets wont have targets but it may have
        # built packages to include in its tgz
        if not targets and len(self.contrail_pkgs) != 0 and \
           not self.contrail_pkgs[self.package_type]['target']:
            targets = self.contrail_pkgs.keys()

        for each in targets:
            if not self.contrail_pkgs.get(each, None):
                log.warn('Package (%s) is not defined in config...'
                          'Skipping verify (%s)' % (
                          each, each))
                return
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
        thirdparties = []
        for target in self.contrail_pkgs.keys():
            packages = self.contrail_pkgs[target]['pkgs']
            packages = [packages] if type(packages) is str else packages
            pkglist.extend(filter(None, packages))
        with open(self.pkglist_file, 'w') as fid:
            fid.write("%s\n" %"\n".join(sorted(pkglist)))
            fid.flush()
        for key, pkg_info in self.depends_pkgs.items():
            if pkg_info['file'].count('contrail') == 0:
                thirdparties.append('%s, %s' % (pkg_info['md5'], pkg_info['file']))
        with open(self.pkglist_thirdparty, 'w') as fid:
            fid.write('MD5, ThirdParty_Package\n')
            fid.write('\n'.join(thirdparties))
        log.info('Packages list file (%s) is created' % self.pkglist_file)
        log.info('Packages thirdparty list file (%s) '
                 'is created' % self.pkglist_thirdparty)

    def create_log(self):
        filelist = []
        filelist_file = os.path.join(self.store_log_dir,
                                     '%s_file_list.txt' % self.package_type)
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

    def create_manifest_with_revision(self, manifest=None, filename=None):
        '''Create a copy of manifest file with current GIT IDs as revision'''
        if os.environ.has_key('SKIP_CREATE_GIT_IDS'):
            return

        filename = filename or os.path.join(self.store, 'manifest_%s.xml' % self.id)
        manifest = manifest or os.path.join(self.git_local_repo, '.repo', 'manifest.xml')

        with open(manifest, 'r') as fid:
            manifest_str = fid.read()
        parser = etree.XMLParser()
        manifest_root = etree.fromstring(manifest_str, parser)
        for item in range(0, len(manifest_root)):
            if manifest_root[item].tag == 'project':
                tag_info = dict(manifest_root[item].items())
                repo_dir = os.path.join(self.git_local_repo, tag_info['path'])
                commit_id = self.get_git_latest_commit_id(repo_dir)
                manifest_root[item].attrib['revision'] = commit_id

        with open(filename, 'w') as fid:
            fid.write(etree.tostring(manifest_root, pretty_print=True))
            fid.flush()

        return filename

    def createrepo(self, extraargs=''):
        ''' execute create repo '''
        log.info('Executing createrepo in (%s)...' % self.repo_dir)
        packages_present = any([fname.endswith('.%s' % self.pkg_type)
                                for fname in os.listdir(self.repo_dir)])
        if packages_present:
            self.exec_cmd('createrepo %s .' % extraargs, wd=self.repo_dir)
        else:
            log.warn('No Packages of type (%s) found in (%s); '
                     'Skip creating Repo' % (self.pkg_type, self.repo_dir))

    def cleanup_store(self):
        log.info('Removing Packager repo dir (%s)' % self.repo_dir)
        shutil.rmtree(self.repo_dir)

    def add_sub_pkgs_tgz(self):
        '''Add sub package type TGZ to its parent repo dir'''
        missing = []
        if not self.sub_pkg_types:
            log.warn('No Sub Package type defined for this'
                     ' package type (%s)' % self.package_type)
            return

        pkginfo = self.contrail_pkgs.get(self.package_type, None)
        if not pkginfo:
            log.warn('Sub Package type cant be identified as'
                     ' a target for package type (%s) info is not specified'
                     ' in config file' % self.package_type)
            return
        if not os.access(self.repo_dir, os.W_OK):
            raise RuntimeError('Unable to copy sub package tgz'
                               ' to current package type repo'
                               ' dir (%s)' % self.repo_dir)
        for sub_type in self.sub_pkg_types:
            # find the tgz in self.store. if not available
            # probably sub_package_type is not executed before
            # current package type
            sub_pkg_tgz = "%s_%s-%s" % (sub_type, self.branch, self.id)
            if sub_type in self.contrail_pkgs_dict and \
                'add_sku_tag' in self.contrail_pkgs_dict[sub_type][sub_type] and \
                self.contrail_pkgs_dict[sub_type][sub_type]['add_sku_tag'].lower() == 'true':
                sub_pkg_tgz = "%s-%s.tgz" % (sub_pkg_tgz, self.sku)
            else:
                sub_pkg_tgz = "%s.tgz" % sub_pkg_tgz

            tgzfiles = self.get_file_list(self.store, sub_pkg_tgz, False)
            if len(tgzfiles) != 0:
                self.copyfiles(tgzfiles, self.repo_dir)
            else:
                log.warn('Missing Sub packages TGZ File (%s)' % sub_pkg_tgz)
                missing.append(sub_pkg_tgz)
        if len(missing) != 0:
            raise RuntimeError('Missing Sub Package TGZ files: \n%s' % "\n".join(missing))

    def create_contrail_pkg(self, *pkgs):
        ''' make meta packages
        '''
        #make final package that holds all other packages
        pkginfo = self.contrail_pkgs.get(self.meta_pkg, None)
        if not pkginfo:
            log.warn('Final package (%s) info is not specified'
                     ' in config file' % self.meta_pkg)
            log.warn('Skipping make %s' % self.meta_pkg)
            return
        if not pkginfo['target']:
            log.warn('Final package (%s) info has an empty'
                     ' target' % self.meta_pkg)
            return
        try:
            tgz_file = os.path.join(self.store, self.pkg_tgz_name)
            self.exec_cmd('make CONTRAIL_SKU=%s FILE_LIST=%s TAG=%s %s' %(
                           self.sku, tgz_file, self.id,
                           pkginfo['target']), pkginfo['makeloc'])
        except:
            raise MakeError(sys.exc_info()[1])

    def copy_to_artifacts(self):
        '''Copies rpm or deb files to artifacts directory'''
        if self.platform == 'ubuntu':
            builtdirs = [os.path.join(self.git_local_repo, 'build', 'debian'),
                         os.path.join(self.git_local_repo, 'build', 'packages'),
                         os.path.join(self.git_local_repo, 'build', 'openstack')]
            toolsdirs = [os.path.join(self.git_local_repo, 'build', 'tools')]
            pattern = '*.deb'
        else:
            basedir = os.path.join(self.git_local_repo, 'controller', 'build',
                                   'package-build')
            builtdirs = [os.path.join(basedir, 'RPMS', 'noarch'),\
                         os.path.join(basedir, 'RPMS', 'x86_64')]
            toolsdirs = [os.path.join(basedir, 'TOOLS')]
            pattern = '*.rpm'
        for dirname in builtdirs:
            if not os.path.isdir(dirname):
                log.warn('Dir (%s) do not exists. Skipping...' %dirname)
                continue
            pkgfiles = self.get_file_list(dirname, pattern, False)
            self.copyfiles(pkgfiles, self.artifacts_dir)

        # copy tools tgz to artifacts-extras
        for dirname in toolsdirs:
            if not os.path.isdir(dirname):
                log.warn('Dir (%s) do not exists. Skipping...' %dirname)
                continue
            pkgfiles = self.get_file_list(dirname, '*.tgz', False)
            self.copyfiles(pkgfiles, self.artifacts_extra_dir)

        # copy package tgz to artifacts dir
        tgz_files = self.get_file_list(self.store, '*.tgz', False)
        self.copyfiles(tgz_files, self.artifacts_dir)
