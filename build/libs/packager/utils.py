#!/usr/bin/env python
''' Utilities for Packager scripts '''

import os
import sys
import logging
import subprocess
import select
import fcntl
import errno
import fnmatch
import rpm
import re
import operator
import shutil
import tarfile
from ConfigParser import SafeConfigParser

log = logging.getLogger("pkg.%s" %__name__)

class Utils(object):
    @staticmethod
    def get_uniq_id(prefix, retries=20):
     ''' Get an Unique ID based on prefix_id directory availability '''
     notfound = 0
     while retries > 0:
         id = random.randint(10, 1000)
         if not os.path.isdir(os.path.abspath('%s_%s' %(prefix, id))):
             notfound = 0
             break
         else:
             notfound = 1
             retries -= 1
         if notfound:
             raise IOError('Unable to find an unique name based on dir availability')
     return id

    @staticmethod
    def create_dir(dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        else:
            log.debug('Dir %s exists' %dirname)
        return dirname

    #def exec_cmd(self, cmd, wd=os.getcwd()):
    #    log.info('cd %s; cmd: \'%s\'' %(wd, cmd))
    #    with lcd(wd):
    #        local(cmd)

    def read_async(self, fd):
        '''read some data from a file descriptor, ignoring EAGAIN errors'''
        try:
            return fd.read()
        except IOError, e:
            if e.errno != errno.EAGAIN:
                raise e
            else:
                return ''

    def log_fds(self, fds):
        for fd in fds:
            out = self.read_async(fd)
            if out:
                sys.stdout.write(out)
                log.parent.handlers[1].stream.write(out)
                log.parent.handlers[1].stream.flush()

    def make_async(self, fd):
        '''add O_NONBLOCK flag to a file descriptor'''
        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

    def exec_cmd(self, cmd, wd=''):
        wd = wd or os.getcwd()
        wd = os.path.normpath(wd)
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
			raise RuntimeError('Cmd: %s; **FAILED**' %cmd)
            
    def mprocess(self, psize, cmd, inputs, precmd=None):
        pool = multiprocessing.Pool(processes=psize, initializer=precmd)
        result = pool.map(cmd, inputs) 
        pool.close()
        pool.join()
        return result

    @staticmethod
    def str_to_list(tstr, force=False):
        tstr = tstr.replace('\n', '')
        sstr = [sstr.strip() for sstr in tstr.split(',')]
        if force:
            return sstr
        else:
            return tstr if tstr.rfind(',') < 0 else sstr

    @staticmethod
    def rtrv_lsv_file_info(fname):
        rlist = []
        if fname and os.path.isfile(fname) and\
           os.lstat(fname).st_size != 0:
            with open(fname, 'r') as fid:
                rlist = fid.read().split('\n')
        return rlist

    def update_var(self, var):
        if len(var) == 0:
            return
        pat = re.compile(self.namemap['$WRAPPER$'])
        newvar = None

        if type(var) is str:
            newvar = pat.sub(lambda mat: self.namemap.get(mat.groups()[1], '-'), var)
        elif type(var) is tuple:
            newvar = []
            for each in var:
                newvar.append(pat.sub(lambda mat: self.namemap.get(mat.groups()[1], '-'), each))
            newvar = tuple(newvar)
        elif type(var) is list:
            newvar = []
            for each in var:
                newvar.append(pat.sub(lambda mat: self.namemap.get(mat.groups()[1], '-'), each))
        else:
			raise TypeError('Given Variable (%s) - %s type variables cant be updated' %(var, type(var)))
        return newvar

    @staticmethod
    def get_file_list(dirs, pattern, recursion=True):
        filelist = []
        for dirname in dirs:
            if recursion:
                for dir, sdir, flist in os.walk(dirname):
                    filelist += [os.path.abspath('%s/%s' %(dir, fname)) for fname in fnmatch.filter(flist, pattern)]  
            else:
                filelist += [os.path.abspath('%s/%s' %(dirname, fname)) for fname in fnmatch.filter(os.listdir(dirname), pattern)]
        return filelist

    def get_pkg_availability(self, pkgs, dirs, recursion=True):
        found = []
        missing = []
        for pkg in pkgs:
            pat = r'%s-[0-9]*.rpm' %pkg
            flist = self.get_file_list(dirs, pat, recursion)
            if len(flist) == 0:
                log.debug('No File found for given rpm (%s)' %pkg)
                missing += pkg
            else:
                flist = flist if len(flist) == 1 else self.get_latest_file(flist)
                log.debug('File (%s) found for given rpm (%s)' %(flist, pkg))
                found += (pkg, flist)
        return found, missing

    @staticmethod
    def get_latest_file(filelist):
        ctime = operator.attrgetter('st_ctime')
        filestats = map(lambda fname: (ctime(os.lstat(fname)), fname), filelist)
        return sorted(filestats)[-1][-1]

    @staticmethod
    def create_tgz(filename, srcdir, untar_as=''):
        log.info('Create tgz file (%s) from Dir (%s)' %(filename, srcdir))
        tar = tarfile.open(filename, 'w:gz')
        tar.add(srcdir, arcname=untar_as)
        tar.close()
        return os.path.abspath(filename)

    def parse_cfg_file(self, pkg_files, additems=None):
        rdict = {}
        pkg_parser = SafeConfigParser()
        pkg_parser.read(pkg_files)
        for sect in pkg_parser.sections():
            rdict[sect] = dict((iname, self.str_to_list(ival)) for iname, ival in pkg_parser.items(sect))
            if additems != None:
				for item in additems.keys():
					rdict[sect][item] = additems[item]
        return rdict

    def get_pkg_file_info(self, pkgfiles, *infolist):
        """Returns rpm information by querying given list of rpm"""
        ret_dict = {}
        ts = rpm.ts()
        ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
        infolist = infolist or ['RPMTAG_NAME']

        if type(pkgfiles) is str:
            pkgfiles = [pkgfiles]
        for each in pkgfiles:
            if not os.access(each, os.R_OK):
                self.log.warn('WARNING: %s is not readable' %each)
                continue
            fdno = os.open(each, os.O_RDONLY)
            hdr = ts.hdrFromFdno(fdno)
            os.close(fdno)
            ret_dict[hdr[rpm.RPMTAG_NAME]] = dict([(infoname, hdr[getattr(rpm, 'RPMTAG_%s' %infoname.upper())]) for infoname in infolist])
        return ret_dict

    def check_pkg_file_info(self, pkg, pkgfile, pkginfo, *verifylist):
        pkgfile_info = self.get_pkg_file_info(pkgfile, *verifylist)
        diff = filter(lambda verifies: pkginfo[verifies.lower()] != pkgfile_info[pkg][verifies], verifylist)
        if diff:
            log.warn('PKG File (%s):: Required (%s = %s) != Actual (%s = %s)' \
                     %(pkgfile, diff[0], pkginfo[diff[0].lower()], diff[0], pkgfile_info[pkg][diff[0]]))
            raise FileNotFoundError('PKG File (%s) do not match with given specs' %pkgfile)
        
    def filter_pkg_file(self, pkg, pkgfiles, pkginfo, *verifylist):
        pkgfiles_filtered = []
        for pkgfile in pkgfiles:
            pkgfile_info = self.get_pkg_file_info(pkgfile, *verifylist)
            diff = filter(lambda verifies: pkginfo[verifies.lower()] != pkgfile_info[pkg][verifies], verifylist)
            if diff:
                log.warn('PKG File (%s):: Required (%s = %s) != Actual (%s = %s)' \
                         %(pkgfile, diff[0], pkginfo[diff[0].lower()], diff[0], pkgfile_info[pkg][diff[0]]))
                log.warn('Skipping PKG File (%s)' %pkgfile)
            else:
                pkgfiles_filtered.append(pkgfile)
        return pkgfiles_filtered

    def verify_pkgs_exists(self, pkginfo):
        missing = []
        for pkg in pkginfo.keys():
            verifylist = pkginfo[pkg]['verifylist']
            pattern = pkginfo[pkg]['pattern'].format(pkg=pkg)
            locs = pkginfo[pkg]['location']
            if type(locs) is str:
				locs = [locs]		
            log.debug('Verify PKG (%s) is present in Directories (%s)' %(pkg, locs))
            pkgfiles = self.get_file_list(locs, pattern)
            if len(pkgfiles) == 0:
                log.error('Missing PKG (%s)' %pkg)
                missing.append(pkg)
            else:
                f_pkgfiles = self.filter_pkg_file(pkg, pkgfiles, pkginfo[pkg], *verifylist)
                if len(f_pkgfiles) == 0:
                    log.error('Missing PKG (%s)' %pkg)
                    missing.append(pkg)
                else:
                    pkgfile = self.get_latest_file(f_pkgfiles)
                    log.debug(pkgfile)
                    pkginfo[pkg]['found_at'] = pkgfile
        if len(missing) != 0:
            log.error('Required PKGs are missing: \n%s' %"\n".join(missing))
            raise IOError('One or More PKGs are not found')

    def import_file(self, cfile):
        cfile = os.path.abspath(os.path.expanduser(cfile))
        cfile_name = os.path.basename(cfile).strip('.py')
        cfile_dir  = os.path.dirname(cfile)
        sys.path.append(cfile_dir)
        try:
            cfgfile = __import__(cfile_name)
        except ImportError, err:
            raise ImportError('Unable to import "%s" file.\nERROR: %s' %(cfile_name, err))
        return cfgfile

    def update_cfg_vars(self, tdict):
        pat = re.compile(self.namemap['$WRAPPER$'])
        for each in tdict.keys():
           tdict[each] = dict(map(lambda k: k if not len(k[1]) != 0 else (k[0], self.update_var(k[1])), tdict[each].items()))

    def copy_pkg_files(self, pkginfo, destdir, error=True):
        for pkg in pkginfo.keys():
            if pkginfo[pkg]['found_at'] == '':
                if error:
                    raise IOError('No Info about package file for Package (%s) is not found' %pkg)
                else:
                    log.warn('No Info about package file for Package (%s) is not found' %pkg)
            pkgfile = pkginfo[pkg]['found_at']
            log.debug('Copying (%s) to Dir (%s)' %(pkgfile, destdir))
            shutil.copy(pkgfile, destdir)

    def copy_built_pkg_files(self, destdir, targets=None, skips=None, error=True):
        targets = targets if targets else self.cont_pkgs.keys()
        targets = list(set(targets) - set(skips)) if skips else targets		
        for each in targets:
            pkgs = self.cont_pkgs[each]['pkgs']
            pkgs = [pkgs] if type(pkgs) is str else pkgs
            for pkg in filter(None, pkgs):		
                if self.cont_pkgs[each]['found_at'][pkg] == '':
                    if error:
                        raise IOError('No Info about package file for Package (%s) is not found' %pkg)
                    else:
                        log.warn('No Info about package file for Package (%s) is not found' %pkg)
                pkgfile = self.cont_pkgs[each]['found_at'][pkg]
                log.debug('Copying (%s) to Dir (%s)' %(pkgfile, destdir))
                shutil.copy(pkgfile, destdir)
