#!/usr/bin/env python
''' Utilities for Packager scripts '''

import os
import re
import sys
import copy
import glob
import fcntl
import errno
import Queue
import select
import shutil
import tarfile
import logging
import fnmatch
import operator
import platform
import tempfile
import itertools
import subprocess

from ConfigParser import SafeConfigParser

log = logging.getLogger("pkg")

class Utils(object):
    ''' Utilities for packager '''

    def expanduser(self, dirnames=None):
        '''Expand user ~ in directory names'''
        if dirnames is None:
            return None
        dirnames = self.get_as_list(dirnames)
        absdirs = [os.path.abspath(os.path.expanduser(dirname)) \
                  for dirname in dirnames]
        return absdirs[0] if len(absdirs) == 1 else absdirs

    @staticmethod
    def get_platform_info(os_version=None):
        '''Retrieve Platform Info and customize it'''
        platform_dict = {}
        if not os_version:
            platform_dict['default'] = map(str.lower, platform.linux_distribution())
            platform_dict['default'] = [pinfo.replace(' ', '') for pinfo in platform_dict['default']]
        else:
            version = ''.join(re.findall('\d+', os_version))
            os_type = ''.join(re.findall('[^\d|^.|^\s]*', str(os_version).lower()))
            platform_dict['default'] = [os_type, version]
        platform_dict['formatted'] = ''.join(platform_dict['default'][:2]).replace('.', '')
        return platform_dict

    @staticmethod
    def create_dir(dirname, recreate=False):
        dirname = os.path.expanduser(dirname)
        if not os.path.exists(dirname):
            log.debug('Creating directory: %s' %dirname)
            os.makedirs(dirname)
        else:
            log.debug('Dir %s exists' %dirname)
            if recreate:
                log.debug('Remove and Recreate existing (%s)' % dirname)
                shutil.rmtree(dirname)
                os.makedirs(dirname)
        return dirname


    def copyfiles(self, files, dirs):
        files = self.get_as_list(files)
        dirs  = self.get_as_list(dirs)
        copyiter = itertools.product(files, dirs)
        for item in copyiter:
            shutil.copy2(*item)
            
    def read_async(self, fd):
        '''read data from a file descriptor, ignoring EAGAIN errors'''
        try:
            return fd.read()
        except IOError, e:
            if e.errno != errno.EAGAIN:
                raise e
            else:
                return ''

    def log_fds(self, fds):
        ''' print logs to stdout, stream and file handlers '''
        for fd in fds:
            out = self.read_async(fd)
            if out:
                sys.stdout.write(out)
                log.handlers[1].stream.write(out)
                log.handlers[1].stream.flush()


    def make_async(self, fd):
        '''add O_NONBLOCK flag to a file descriptor'''
        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

    def exec_cmd_out(self, cmd, wd=''):
        ''' execute given command after chdir to given directory 
            and return output
        '''
        wd = wd or os.getcwd()
        wd = os.path.normpath(wd)
        if wd == os.getcwd():
            log.debug('cmd: %s' % cmd)
        else:
            log.debug('cd %s; cmd: %s' %(wd, cmd))
        proc = subprocess.Popen(cmd, shell=True, cwd=wd, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)  
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            log.error(stdout)
            log.error(stderr)
            raise RuntimeError('cd %s; Cmd: %s; **FAILED**' % (wd, cmd))
        return stdout.strip('\n'), stderr.strip('\n')
  
    def exec_cmd(self, cmd, wd=''):
        ''' DEBUG execute given command after chdir to given directory '''
        wd = wd or os.getcwd()
        wd = os.path.normpath(wd)
        if wd == os.getcwd():
            log.debug('cmd: %s' % cmd)
        else:
            log.debug('cd %s; cmd: %s' %(wd, cmd))
        proc = subprocess.Popen(cmd, shell=True, cwd=wd, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        self.make_async(proc.stdout)
        self.make_async(proc.stderr)
        while True:
            rlist, wlist, xlist = select.select([proc.stdout, proc.stderr], [], [])
            self.log_fds(rlist)
            if proc.poll() is not None:
                self.log_fds([proc.stdout, proc.stderr])
                break
        proc.communicate()
        if proc.returncode != 0:
            log.error('Cmd: %s; **FAILED**' %cmd)
            raise RuntimeError('cd %s; Cmd: %s; **FAILED**' % (wd, cmd))
        
    @staticmethod
    def get_as_list(elm):
        return [elm] if type(elm) is str else elm

    @staticmethod
    def str_to_list(tstr, force=False):
        ''' convert string separated with comma into a list '''
        tstr = tstr.replace('\n', '')
        sstr = [sstr.strip() for sstr in tstr.split(',')]
        if force:
            return sstr
        else:
            return tstr if tstr.rfind(',') < 0 else sstr

    @staticmethod
    def rtrv_lsv_file_info(fname):
        ''' read given file and create a line with every line as list element '''
        file_info_list = []
        if fname and os.path.isfile(fname) and\
           os.lstat(fname).st_size != 0:
            with open(fname, 'r') as fid:
                file_info_list = fid.read().split('\n')
        return filter(None, file_info_list)

    def get_md5(self, files):
        md5dict = {}
        if files is None or len(files) == 0:
            return
        files = self.get_as_list(files)
        for filename in files:
            if not os.path.isfile(filename):
                log.error('File (%s) is not present' %filename)
                continue
            md5out = self.exec_cmd_out('md5sum %s' %filename)
            if len(md5out) == 0:
                continue
            md5dict[filename] = md5out[0].split()[0]
        return md5dict

    def check_package_md5(self, pkginfo, location='location'):
        failed_packages = []
        for pkg in pkginfo.keys():
            pkg_loc = pkginfo[pkg][location]

            # Location is empty. Cant check md5sum
            if pkg_loc is '':
                msg = 'Given Location (%s) of the Package (%s) is empty' % (location, pkg)
                failed_packages.append(msg)
                log.error(msg)
                continue

            # No package file found
            pkgfiles = self.get_file_list(pkg_loc, pkginfo[pkg]['file'], True)
            if len(pkgfiles) == 0:
                msg = 'Package file for package (%s) is not present in (%s)' %(
                       pkg, pkg_loc)
                failed_packages.append(msg)
                log.error(msg)
                continue

            # No MD5 can be retrived
            md5_info = self.get_md5(pkgfiles)
            if len(md5_info) == 0:
                msg = 'MD5 checksum is empty for file (%s).\n' % pkgfiles +\
                      'Expected (%s) != Actual (%s)' % (pkginfo[pkg]['md5'], None)
                failed_packages.append(msg)
                log.error(msg)
                continue

            # Atleast one of the files matches with expected MD5
            for filename in md5_info.keys():
                if pkginfo[pkg]['md5'] == md5_info[filename]:
                    pkginfo[pkg]['found_at'] = filename
                else:
                    log.warn('MD5 checksum mismatch for Package (%s) ' % filename)

            # No match for expected MD5sum
            if not pkginfo[pkg]['found_at']:
                for filename in md5_info.keys():
                    msg = 'MD5 Checksum validation for Package (%s) failed.\n' % filename +\
                          'Expected (%s) != Actual (%s)' % (
                          pkginfo[pkg]['md5'], md5_info[filename])
                    failed_packages.append(msg)
                    log.error(msg)

        if len(failed_packages) != 0:
            raise RuntimeError('MD5 Checksum validation failed for below packages... '
                               'Review Errors; \n%s' % "\n".join(failed_packages))
            
    def get_file_list(self, dirs, pattern, recursion=True):
        ''' get a list of files that matches given pattern '''
        filelist = []
        dirs = self.get_as_list(dirs)
        for dirname in dirs:
            if recursion:
                for dirn, sdir, flist in os.walk(dirname):
                    filelist += [os.path.abspath('%s/%s' %(dirn, fname)) \
                                    for fname in fnmatch.filter(flist, pattern)]  
            else:
                filelist += [os.path.abspath('%s/%s' %(dirname, fname)) \
                              for fname in fnmatch.filter(os.listdir(dirname), pattern)]
        return filter(None, filelist)

    def get_files_by_pattern(self, patterns, strict=False):
        ''' get a list of files that matches given pattern '''
        filelist = []
        patterns = self.get_as_list(patterns)
        for pattern in patterns:
            filelist.extend(glob.glob(pattern))
        filelist = filter(None, filelist)
        if strict:
            if len(patterns) != 0 and len(filelist) == 0:
                raise RuntimeError('No Matching files for given pattern (%s)' % patterns)
        return filelist

    def get_latest_file(self, filelist):
        ''' get the latest file based on creation time from the 
            given list of files
        '''
        if len(filelist) == 0:
            return ''
        filelist = self.get_as_list(filelist)
        ctime = operator.attrgetter('st_ctime')
        filestats = map(lambda fname: (ctime(os.lstat(fname)), fname), filelist)
        if len(filestats) == 0:
            raise RuntimeError('File list is empty; file list (%s) for given filelist (%s)' %(
                                filestats, filelist))
        return sorted(filestats)[-1][-1]

    @staticmethod
    def create_tgz(filename, srcdir, untar_as=''):
        ''' create a compressed tar file from the given directory
        '''
        log.info('Create tgz file (%s) from Dir (%s) and to untar as (\'%s\')' %(
                 filename, srcdir, untar_as))
        tar = tarfile.open(filename, 'w:gz')
        tar.add(srcdir, arcname=untar_as)
        tar.close()
        return os.path.abspath(filename)

    def create_pkgs_tgz(self, dirname=None):
        '''Create tgz from each repo directory'''
        dirname = dirname or self.repo_dir
        tgz_prefix = os.path.basename(dirname)
        tgz_name = os.path.join(self.store, 
                                '%s_%s-%s~%s.tgz' % (tgz_prefix,
                                self.branch, self.id, self.sku))
        log.info('Create (%s) file' % tgz_name)
        self.create_tgz(tgz_name, dirname)

    def get_git_latest_commit_id(self, dirname):
        '''execute git log in the given repo dir and return commit id'''
        commit_id = self.exec_cmd_out('git log --format="%H" -1', wd=dirname)
        if not commit_id:
            return ''
        log.debug('Commit ID: %s' % commit_id[0])
        return commit_id[0]
        
    def parse_cfg_file(self, cfg_files, additems=None):
        ''' parse the given config files and return a dictionary
            with sections as keys and its items as dictionary items
        '''
        parsed_dict = {}
        sections = []
        cfg_files = self.get_as_list(cfg_files)
        for cfg_file in cfg_files:
            parser = SafeConfigParser()
            parsed_files = parser.read(cfg_file)
            if cfg_file not in parsed_files:
                raise RuntimeError('Unable to parse (%s), '
                                   'No such file or invalid format' %cfg_file)
            common_sections = list(set(parser.sections()) & \
                                   set(sections))
            if len(common_sections) != 0:
                raise RuntimeError('Duplication Section Error while parsing '
                           '(%s): %s' %(cfg_file, "\n".join(common_sections)))
            for sect in parser.sections():
                parsed_dict[sect] = dict((iname, self.str_to_list(ival)) \
                                       for iname, ival in parser.items(sect))
                if additems != None:
                    for item in additems.keys():
                        parsed_dict[sect][item] = copy.deepcopy(additems[item])
            sections.extend(parser.sections())
            del parser
        return parsed_dict

    def import_file(self, cfile):
        ''' import a module based on its absolute path '''
        cfile = os.path.abspath(os.path.expanduser(cfile))
        cfile_name = os.path.basename(cfile).strip('.py')
        cfile_dir  = os.path.dirname(cfile)
        sys.path.append(cfile_dir)
        try:
            cfgfile = __import__(cfile_name)
        except ImportError, err:
            raise ImportError('Unable to import "%s" file.\nERROR: %s' %(cfile_name, err))
        return cfgfile

    def get_repodirs(self, *pkgcfgs):
        '''Get list of repo dirs defined for each package'''
        repo_dirs = []
        for pkgcfg in pkgcfgs:
            repos = [pkgcfg[pkg]['repo'] for pkg in pkgcfg.keys()]
            repo_dirs.extend(repos)
        repo_dirs = list(set(repo_dirs))
        log.debug('Repo dirs from config files:')
        for dirname in repo_dirs:
            log.debug(dirname)
        return filter(None, repo_dirs)

    def update_repoinfo(self, *pkgcfgs):
        '''Update repo of each package with repo dir value'''
        for pkgcfg in pkgcfgs:
            for pkg in pkgcfg.keys():
                pkgcfg[pkg]['repo'] = self.repo_dir

    def get_dict_by_item(self, tdict, titem):
        matrix = {}
        cfg_itemgetter = operator.itemgetter(titem)
        for key, items in tdict.items():
            matrix_keys = cfg_itemgetter(items)
            matrix_keys = self.get_as_list(matrix_keys)
            for matrix_key in matrix_keys:
                if not matrix.has_key(matrix_key):
                    matrix[matrix_key] = {}
                matrix[matrix_key].update({key: items})
        return matrix

    def copy_pkg_files(self, pkginfo, error=True):
        ''' copy the packages present in location specified in package data structure
            to given destination directories
        '''
        for pkg in pkginfo.keys():
            if pkginfo[pkg]['found_at'] == '':
                if error:
                    raise IOError('Info about package file for '
                                  'Package (%s) is not found' %pkg)
                else:
                    log.warn('Skipping Copy package file (%s)' % pkg)
                    log.warn('Info about package file for '
                             'Package (%s) is not found' %pkg)
                    continue
            pkgfile = pkginfo[pkg]['found_at']
            destdirs = pkginfo[pkg]['repo']
            self.copyfiles(pkgfile, destdirs)

    def copy_built_pkg_files(self, targets=None, destdirs=None, 
                             extra_dirs=None, skips=None, error=True):
        ''' copy the contrail packages present in location specified in 
            package data structure to given destination directories
        '''
        targets = targets or self.contrail_pkgs.keys()
        targets = list(set(targets) - set(self.get_as_list(skips))) if skips \
                            else self.get_as_list(targets)
        if destdirs is not None:
            destdirs = self.get_as_list(destdirs)
        if extra_dirs is not None:
            extra_dirs = self.get_as_list(extra_dirs)

        for each in targets:
            pkgs = self.contrail_pkgs[each]['pkgs']
            pkgs = self.get_as_list(pkgs)
            for pkg in filter(None, pkgs):      
                if self.contrail_pkgs[each]['found_at'][pkg] == '':
                    if error:
                        raise IOError('Info about package file for '
                                      'Package (%s) is not found' %pkg)
                    else:
                        log.warn('Skipping Copy package file (%s)' % pkg)
                        log.warn('Info about package file for '
                                 'Package (%s) is not found' %pkg)
                        continue
                pkgfile = self.contrail_pkgs[each]['found_at'][pkg]
                repo_dirs = destdirs or \
                            self.get_as_list(self.contrail_pkgs[each]['repo'])
                if extra_dirs is not None:
                    repo_dirs.extend(extra_dirs)
                self.copyfiles(pkgfile, repo_dirs)

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

