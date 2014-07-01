#!/usr/bin/env python
'''
Copies list of packages specified in given package file from source directories
to desitnation directory
'''

__version__ = '1.0'

import os
import sys
import csv
import glob
import shutil
import os.path
import logging
import operator
import platform
import argparse
import subprocess


logging.basicConfig(format='%(asctime)-15s:: %(funcName)s:%(levelname)s:: '
                    '%(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


SCRIPTDIR = os.path.abspath(os.path.dirname(sys.argv[0]))


class Abspath(argparse.Action):
    def __call__(self, parser, namespace, values, options=None):
        if type(values) is list:
            setattr(namespace,
                    self.dest,
                    [os.path.abspath(os.path.expanduser(value))
                        for value in values])
        elif type(values) is str:
            setattr(namespace, self.dest,
                    os.path.abspath(os.path.expanduser(values)))
        else:
            print 'WARN: Not handled'


def get_abspath(dirname):
    return os.path.abspath(os.path.expanduser(dirname))


def check_dir_exists(dirnames):
    dirnames_local = dirnames if type(dirnames) is list else [dirnames]
    for dirname in dirnames_local:
        if not os.path.isdir(os.path.abspath(os.path.expanduser(dirname))):
            raise IOError('(%s): No Such directory exists' % dirname)
    return dirnames

def get_platform_info():
    '''Retrieve Platform Info and customize it'''
    platform_info = platform.linux_distribution()
    platform_info = map(str.lower, platform_info)
    platform_info = [pinfo.replace(' ', '') for pinfo in platform_info]
    return platform_info


def get_platform():
    return ''.join(get_platform_info()[0:2]).replace('.', '')


def get_as_list(items):
    return items if type(items) is list else [items]


def check_package_file(packagefile):
    if not os.path.isfile(packagefile):
        raise IOError('Package File (%s) do not exists' % packagefile)
    if os.stat(packagefile)[6] == 0:
        raise IOError('Package File (%s) is empty' % packagefile)


def copy_packages(files, destdir):
    if not os.path.isfile(destdir) and not os.path.isdir(destdir):
        log.info('Destination Dir (%s) do not exists. Creating!' % destdir)
        os.makedirs(destdir)

    files = get_as_list(files)
    for filename in files:
        #log.info('Copying (%s) to dir (%s)' % (filename, destdir))
        shutil.copy2(filename, destdir)


def get_latest_file(filelist):
    ''' get the latest file based on creation time from the
        given list of files
    '''
    if len(filelist) == 0:
        return ''
    filelist = get_as_list(filelist)
    ctime = operator.attrgetter('st_ctime')
    filestats = map(lambda fname: (ctime(os.lstat(fname)), fname), filelist)
    return sorted(filestats)[-1][-1]


def get_latest_package(pattern, sourcedirs):
    sourcedirs = [os.path.abspath(os.path.expanduser(dirname))
                  for dirname in get_as_list(sourcedirs)]
    packages = []
    for dirname in sourcedirs:
        packages += glob.glob(os.path.join(dirname, pattern))
    if len(packages) == 0:
        log.warn('Package Pattern (%s) is not found in any of dirs (%s)' % (
            pattern, sourcedirs))
        return
    elif len(packages) > 1:
        return get_latest_file(packages)
    else:
        return packages[0]


def get_packages_from_file(pattern, packagefile, sourcedirs, excludes=''):
    packages_locs = []
    missing_pkgs = []

    with open(packagefile, 'r') as fid:
        packages = fid.read().split('\n')
        packages = filter(None, packages)

    excludes = get_as_list(excludes)
    packages = list(set(packages) - set(excludes))
    for pkg in packages:
        pkg_pattern = pattern.format(pkg=pkg)
        pkg_loc = get_latest_package(pkg_pattern, sourcedirs)
        if not pkg_loc:
            log.error('Package (%s) is not found in Source dirs (%s)' % (
                      pkg, sourcedirs))
            missing_pkgs.append(pkg)
        else:
            packages_locs += [pkg_loc]

    if len(missing_pkgs) != 0:
        raise IOError('Unable to find below packages in given source dirs '
                      '(%s):\n%s' % (sourcedirs, "\n".join(missing_pkgs)))
    return packages_locs


def exec_cmd_out(cmd, wd=''):
    ''' execute given command after chdir to given directory
        and return output
    '''
    wd = wd or os.getcwd()
    wd = os.path.normpath(wd)
    if wd == os.getcwd():
        log.debug('cmd: %s' % cmd)
    else:
        log.debug('cd %s; cmd: %s' % (wd, cmd))
    proc = subprocess.Popen(cmd, shell=True, cwd=wd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        log.error(stdout)
        log.error(stderr)
        raise RuntimeError('cd %s; Cmd: %s; **FAILED**' % (wd, cmd))
    return stdout.strip('\n'), stderr.strip('\n')


def get_md5(package):
    return exec_cmd_out('md5sum %s' % package)[0].split()[0]


def check_package_md5(pkg_info):
    md5_failed_pkgs = []
    for package in pkg_info.keys():
        pkg_md5 = get_md5(pkg_info[package]['abspath'])
        if pkg_info[package]['md5'] != pkg_md5:
            log.error('MD5 sum of Package (%s = %s) != Actual MD5 (%s)' % (
                      pkg_info[package]['abspath'], pkg_info[package]['md5'],
                      pkg_md5))
            md5_failed_pkgs.append(package)
    if len(md5_failed_pkgs) != 0:
        raise RuntimeError('MD5 Validation for below packages '
                           'failed: \n%s' % ('\n'.join(md5_failed_pkgs)))
    return True


def get_thirdparty_packages_info_file(packagefile, sourcedirs):
    package_info = {}
    missing_pkgs = []
    with open(packagefile, 'rb') as fid:
        headers = fid.readline()
        headers = map(str.strip, headers.strip().split(','))
        if 'package' not in headers or 'md5' not in headers:
            raise RuntimeError('"package" or "md5" column in header is '
                               'missing in given package file '
                               '(%s)' % packagefile)
        reader = csv.DictReader(fid, fieldnames=headers)
        for pkg_info in reader:
            pkg_info = dict([(key.strip(), value.strip())
                             for key, value in pkg_info.items()])
            package_info.update({pkg_info['package']: pkg_info})
    for package in package_info.keys():
        pkg_loc = get_latest_package(package, sourcedirs)
        if not pkg_loc:
            log.error('Package (%s) is not found in Source dirs (%s)' % (
                      package, sourcedirs))
            missing_pkgs.append(package)
        else:
            package_info[package]['abspath'] = pkg_loc
    if len(missing_pkgs) != 0:
        raise IOError('Unable to find below packages in give source '
                      'dirs (%s): \n%s' % (sourcedirs,
                                           '\n'.join(missing_pkgs)))
    check_package_md5(package_info)
    return package_info
