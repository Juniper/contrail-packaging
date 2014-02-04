#!/usr/bin/env python
''' Generic Library for Packager scripts '''


import os
import re
import pdb
import sys
import copy
import shutil
import logging
import getpass
import tempfile
import platform
from lxml import etree
from xml.etree import ElementTree

from utils import Utils

log = logging.getLogger("pkg.%s" %__name__)

class BasePackager(Utils):
    ''' Base class for packager methods '''
    def __init__(self, **kwargs):
        self.base_pkg_files        = kwargs['base_package_file']
        self.depends_pkg_files     = kwargs['depends_package_file']
        self.cont_pkg_files        = kwargs['contrail_package_file']
        self.id                    = kwargs.get('build_id', 999)
        self.skew                  = kwargs.get('skew', 'grizzly')
        self.branch                = kwargs.get('branch', '1.03')
        store                      = kwargs['store_dir'].format(id=self.id)
        self.store                 = os.path.join(store, self.id)
        self.iso_prefix            = kwargs.get('iso_prefix', getpass.getuser())
        self.pkg_dir               = kwargs['package_dir']
        self.contrail_pkg_dir      = kwargs.get('contrail_package_dir', None)
        self.git_local_repo        = kwargs['git_local_repo'] 
        self.make_targets          = kwargs.get('make_targets', None)
        self.make_targets_file     = kwargs.get('make_targets_file', None)
        self.default_targets       = kwargs.get('default_targets', 
                                         ['thirdparty-all', 'openstack-all', 'contrail-all'])
        self.comps_xml_template    = kwargs.get('comps_xml_template', None)
        pkg_types                  = {'ubuntu': 'deb', 'centos': 'rpm', \
                                      'redhat': 'rpm', 'fedora': 'rpm'}
        self.platform              = platform.dist()[0].lower()
        self.pkg_type              = pkg_types[self.platform]
        self.pkg_repo              = os.path.join(self.store, 'pkg_repo')
        self.store_log_dir         = os.path.join(self.store, 'log')
        self.contrail_pkgs_store   = os.path.join(self.store, 'contrail_packages')
        self.pkgs_tgz              = os.path.join(self.contrail_pkgs_store,
                                                  'contrail_%ss.tgz' %self.pkg_type)
        self.packager_dir          = os.getcwd()
        self.contrail_pkgs_tgz     = os.path.join(self.packager_dir, \
                                                  'contrail_packages_%s.tgz' %self.id)
        self.base_pkgs             = {}
        self.depends_pkgs          = {}
        self.contrail_pkgs         = {}
        self.imgname               = ''
        self.targets               = []
        if self.platform == 'ubuntu': 
            self.default_targets = ['openstack-all', 'contrail-all']

    def setup_env(self):
        ''' setup basic environment necessary for packager like
            updating config data structures, creating dirs,
            copying package files..etc
        '''
        # get pkg info
        additems = {'found_at': {}}
        self.base_pkgs = self.parse_cfg_file(self.base_pkg_files)
        self.depends_pkgs = self.parse_cfg_file(self.depends_pkg_files)
        self.contrail_pkgs = self.parse_cfg_file(self.cont_pkg_files, additems)

        # create dirs
        self.create_dir(self.store)
        self.create_dir(self.pkg_repo)
        self.create_dir(self.contrail_pkgs_store)
        self.create_dir(self.store_log_dir)

        # Update make location with git local repo
        for target in self.contrail_pkgs.keys():
            self.contrail_pkgs[target]['makeloc'] = os.path.join(self.git_local_repo,
                                                     self.contrail_pkgs[target]['makeloc'])
            self.contrail_pkgs[target]['builtloc'] = os.path.join(self.git_local_repo,
                                                     self.contrail_pkgs[target]['builtloc'])

        # update os, depends package dir
        if self.pkg_dir:
            for each in self.base_pkgs.keys():
                self.base_pkgs[each]['location'] = self.pkg_dir
            for each in self.depends_pkgs.keys():
                self.depends_pkgs[each]['location'] = self.pkg_dir

        # update make target list
        if self.make_targets != None:
            self.targets += [self.make_targets] if type(self.make_targets) is str else \
                             self.make_targets
        if self.make_targets_file != None:
            self.targets += self.rtrv_lsv_file_info(self.make_targets_file)
       
        # Skip building all packages but not those supplied
        # in self.targets and contrail-install-packages
        # Update built loc and create support files
        if self.contrail_pkg_dir:
            # update make targets if contrail dir is supplied
            for target in self.contrail_pkgs.keys():
                if target in self.targets or \
                   target == 'contrail-install-packages':
                    continue
                self.contrail_pkgs[target]['builtloc'] = self.contrail_pkg_dir

            # pick up or create contrail_installer.tgz 
            if not ('contrail-setup' in self.targets or
                    'contrail-all' in self.targets):
                builddir = os.path.join(self.git_local_repo, 'controller', 'build')
                files = self.get_file_list(self.contrail_pkg_dir, 'contrail_installer.tgz')
                if len(files) != 0:
                    log.info('Copying %s/contrail_installer.tgz to %s' %(
                               self.contrail_pkg_dir, builddir))
                    shutil.copy('%s/contrail_installer.tgz' %self.contrail_pkg_dir,
                                builddir)
                else:
                    installer_script = os.path.join(self.git_local_repo, 'tools',
                                                     'provisioning', 'create_installer.py')
                    log.info('Creating contrail_installer.tgz...')
                    self.exec_cmd(installer_script, wd=builddir)
                    
        else:
            self.targets = self.default_targets
                    
        # OS PKGs and Depends PKGs
        self.check_package_md5(self.base_pkgs)
        self.check_package_md5(self.depends_pkgs)
        self.copy_pkg_files(self.depends_pkgs, self.pkg_repo)

    def make_pkgs(self):
        ''' make package with given TAG '''
        if len(self.targets) == 0:
            log.warn('make target list is empty...Nothing to make')
            return
        for each in self.targets:
            log.info('Making Target: %s' %each)
            cmd = 'make TAG=%s %s' %(self.id, each)
            self.exec_cmd(cmd, wd=self.contrail_pkgs[each]['makeloc'])

    def verify_built_pkgs_exists(self, targets=None, skips=None):
        ''' verify that contrail built packages are created and 
            and available in specific dirs
        '''
        missing = []
        targets = targets if targets else self.contrail_pkgs.keys()
        targets = list(set(targets) - set(skips)) if skips else targets
        for each in targets:
            pkgs = self.contrail_pkgs[each]['pkgs']
            pkgs = [pkgs] if type(pkgs) is str else pkgs
            for pkg in filter(None, pkgs):
                log.info('Verify Built Pkg (%s) is present in (%s)' %(
                          pkg, self.contrail_pkgs[each]['builtloc']))
                if self.contrail_pkgs[each]['found_at'].has_key(pkg):
                    #Already updated
                    continue
                pattern = self.contrail_pkgs[each]['pkg_pattern'].format(pkg=pkg)
                builtlocs = self.contrail_pkgs[each]['builtloc']
                if type(builtlocs) is str:
                    builtlocs = [builtlocs]
                flist = self.get_file_list(builtlocs, pattern)
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

    def create_log(self):
        filelist, pkglist = [], []
        filelist_file = os.path.join(self.store_log_dir, 'file_list.txt')
        pkglist_file = os.path.join(self.store_log_dir, '%s_list.txt' %self.pkg_type)
        for target in self.contrail_pkgs.keys():
            packages = self.contrail_pkgs[target]['pkgs']
            packages = [packages] if type(packages) is str else packages
            for pkg in filter(None, packages):
                pkglist.append(pkg)
                if self.contrail_pkgs[target]['found_at'][pkg] != '':
                    pkgfile = os.path.basename(self.contrail_pkgs[target]['found_at'][pkg])
                    filelist.append(pkgfile)
        with open(filelist_file, 'w') as fid:
            fid.write("%s\n" %"\n".join(sorted(filelist)))
            fid.flush()
        with open(pkglist_file, 'w') as fid:
            fid.write("%s\n" %"\n".join(sorted(pkglist)))
            fid.flush()
            
    def create_git_ids(self, manifest=None, filename=None):
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
            id = self.exec_cmd_out(cmd)[0].split('\t')[0]
            ids_dict[id] = url
        with open(filename, 'w') as file_id:
            #id_list = ['%s\t%s' %(item, key) for key, item in ids_dict.items()]
            id_list = ['{0:<60}    {1:<}'.format(item, key) for key, item in ids_dict.items()]
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
        pkgs = ['%s<packagereq type="mandatory">%s</packagereq>' % (' '*6, pkg)\
                for pkg in self.base_pkgs.keys()]
        template = self.comps_xml_template.format(__packagesinfo__='\n'.join(pkgs))
        with open(os.path.join(self.pkg_repo, 'comps.xml'), 'w') as fd:
            fd.write ('%s' %template)
            
    def create_ks(self):
        ''' create kick start file need for pungi '''
        ks_file = os.path.join (self.store, 'cf.ks')
        with open (ks_file, 'w') as fd:
            fd.write('repo --name=jnpr-ostk-%s --baseurl=file://%s\n' %(
                      self.iso_prefix, self.pkg_repo))
            fd.write('%packages --nobase\n')
            fd.write('@core\n')
            fd.write('%end\n')
        return ks_file

    def createrepo(self, dirname=os.getcwd(), extraargs=''):
        ''' execute create repo '''
        log.info('Executing createrepo...')
        self.exec_cmd('createrepo %s .' %extraargs, wd=dirname)   
                
    def create_contrail_pkg(self): 
        ''' make contrail-install-package after creating necessary
            tgz files
        '''
        # create contrail_packages_(id).tgz
        shutil.copy2('setup.sh', self.contrail_pkgs_store)
        shutil.copy2('README', self.contrail_pkgs_store)
        with open(os.path.join(self.contrail_pkgs_store, 'VERSION'), 'w') as fid:
            fid.writelines('BUILDID=%s\n' %self.id)
        self.create_tgz(self.contrail_pkgs_tgz, self.contrail_pkgs_store,
                        os.path.basename(self.contrail_pkgs_store))
        #make contrail-install-packages
        pkg = 'contrail-install-packages'
        pkginfo = self.contrail_pkgs[pkg]
        self.exec_cmd('make TAG=%s %s' %(self.id, pkg),
                       pkginfo['makeloc'])
