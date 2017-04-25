#!/usr/bin/env python
"""
Script to insert extra TGZs from given SKUs to networking distribution tgz
"""

import argparse
import fnmatch
import logging as log
import os

import shutil
import subprocess
import sys
import tarfile
import tempfile

class toDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
         for value in values:
             if len(value.split('=')) != 2:
                 print "ERROR: Incorrect Argument format for Arg (%s)" % self.dest
                 print "ERROR: Expected argument format: <key>=<value>"
                 print "ERROR: Received argument (%s)" % value
                 raise RuntimeError('Incorrect Argument format (%s)' % value)
         setattr(namespace, self.dest,
                 dict([tuple(value.split('=')) for value in values]))

def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-dirs',
                        action=toDict,
                        nargs="+",
                        required=True,
                        help='Absolute path to directories where extra tgzs are stored')
    parser.add_argument('--build-id',
                        action='store',
                        required=True,
                        help='Build ID of the extra tgzs')
    parser.add_argument('--networking-tgz',
                        action='store',
                        required=True,
                        help='Absolute path of the networking TGZ')
    parser.add_argument('--extras-tgz',
                        action='store',
                        default='contrail-networking-openstack-extras',
                        help='Name of the TGZs which will hold extras packages')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Increase verbosity to debug')
    parser.add_argument('--package-names',
                        action='store',
                        nargs="+",
                        required=True,
                        help='Name of the tgzs to be picked up')
    parsed_info =  parser.parse_args(args)
    if len(args) == 0:
        parser.print_help()
        sys.exit(2)
    # Update logging verbosity
    if parsed_info.debug:
        log.basicConfig(level=log.DEBUG)
    else:
        log.basicConfig(level=log.INFO)
    return parsed_info


def get_as_list(elm):
    return [elm] if type(elm) is str and elm else elm

def get_file_list(dirs, pattern, recursion=True):
    ''' get a list of files that matches given pattern '''
    filelist = []
    dirs = get_as_list(dirs)
    for dirname in dirs:
        if recursion:
            for dirn, sdir, flist in os.walk(dirname):
                filelist += [os.path.abspath('%s/%s' %(dirn, fname)) \
                                for fname in fnmatch.filter(flist, pattern)]
        else:
            filelist += [os.path.abspath('%s/%s' %(dirname, fname)) \
                          for fname in fnmatch.filter(os.listdir(dirname), pattern)]
    return filter(None, filelist)

def get_md5(filename):
    if not os.access(filename, os.R_OK):
        raise RuntimeError('File (%s) is not readable or not present' % filename)
    md5, stderr = exec_cmd('md5sum %s | cut -d " " -f1' % filename)
    log.debug('MD5sum of (%s) is (%s)' % (filename, md5))
    return md5

def exec_cmd(cmd, wd=None):
    wd = wd or os.getcwd()
    log.debug('cd %s; %s' % (wd, cmd))
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=wd)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        log.error(stdout)
        log.error(stderr)
        raise RuntimeError('cd %s; Cmd: %s; **FAILED**' % (wd, cmd))
    return stdout.strip('\n'), stderr.strip('\n')

def extract_files(sources, dest):
    for src in sources:
        log.debug('Extract TGZ (%s) to (%s)' % (src, dest))
        if not tarfile.is_tarfile(src):
            raise RuntimeError('Unable to read TAR file (%s)' % src)
        tarfid = tarfile.open(src)
        tarfid.extractall(dest)
        tarfid.close()

def copy_tgz_files(src, dest):
    log.debug('Copy TGZ from (%s) to (%s)' % (src, dest))
    src_md5 = get_md5(src)
    shutil.copy2(src, dest)
    dest_file = os.path.join(dest, os.path.basename(src))
    dst_md5 = get_md5(dest_file)
    if src_md5 != dst_md5:
        raise RuntimeError('File copy from (%s) to (%s) failed' % (src, dest))
    return dest_file

def add_to_tar(tgz, sources):
    """
    Caution: Will rewrite given tgz file
    """
    tempdir = tempfile.mkdtemp()
    exec_cmd('tar -xzf %s -C %s' %(tgz, tempdir))
    sources = get_as_list(sources)
    for src in sources:
        log.debug('Copying (%s) to (%s) ...' % (src, tgz))
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(tempdir, os.path.basename(src)))
        else:
            shutil.copy2(src, os.path.join(tempdir, os.path.basename(src)))
    log.debug('Removing existing TGZ (%s)' % tgz)
    os.remove(tgz)
    exec_cmd('cd %s && tar -czf %s *' % (tempdir, tgz))
    log.debug('Recreated TGZ (%s) after adding (%s)' % (tgz, sources))
    shutil.rmtree(tempdir)

def main(cliargs):
    tempdir = tempfile.mkdtemp()
    log.debug('Created Temp Directory: %s' % tempdir)
    temp_networking_tgz = copy_tgz_files(cliargs.networking_tgz, tempdir)
    extras_tgz_path = os.path.join(tempdir, '%s_%s.tgz' % (cliargs.extras_tgz, cliargs.build_id))
    log.debug('Networking Extras TGZ: %s' % extras_tgz_path)
    exec_cmd('tar czf %s --files-from /dev/null' % extras_tgz_path)
    for dir_name, dir_path in cliargs.package_dirs.items():
        sku_dir = os.path.join(tempdir, dir_name)
        os.makedirs(sku_dir)
        log.debug('Create SKU Dir: %s' % sku_dir)
        package_files = []
        for package_name in cliargs.package_names:
            pattern = '%s_%s-%s.tgz' % (package_name, cliargs.build_id, dir_name)
            package_file = get_file_list(dir_path, pattern)
            if len(package_file) == 0:
                log.error('Searching TGZ file (%s) for given package (%s) '
                          'but is not found in (%s)' % (pattern, package_name, dir_path))
                log.error('Cleanup Temp dir (%s)' % tempdir)
                raise RuntimeError('Searching TGZ file (%s) for given package (%s) '
                                   'but is not found in (%s)' % (pattern, package_name, dir_path))
            package_files += package_file
        extract_files(package_files, sku_dir)
        add_to_tar(extras_tgz_path, sku_dir)
        shutil.rmtree(sku_dir)
    add_to_tar(temp_networking_tgz, extras_tgz_path)
    os.remove(extras_tgz_path)
    log.info('Updated TGZ is available at (%s)' % temp_networking_tgz)
    log.info('Remove (%s) after copying (%s)' % (tempdir, temp_networking_tgz))

if __name__ == '__main__':
    cliargs = parse_args(sys.argv[1:])
    main(cliargs)

