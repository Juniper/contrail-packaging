#!/usr/bin/env python
''' Generate config file entires in a temp file which
    can be added to depends config files.
    CAUTION: Some entries could be missed or updated wrongly
             Please review the output file thoroughly
'''

import re
import os
import sys
import fnmatch
import platform
import argparse
from ConfigParser import SafeConfigParser

def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--package-dir',
                        action='store',
                        default=os.getcwd(),
                        help='Absolute directory path from where packages'\
                             ' have to be picked up')
    parser.add_argument('-t', '--package-type',
                        action='store',
                        default=get_system_pkg_type(),
                        help='Specify package type is rpm or deb')
    return parser.parse_args(args)
    
def get_system_pkg_type():
    pkg_type_def = {'centos': 'rpm', 'redhat': 'rpm', \
                    'fedora': 'rpm', 'ubuntu': 'deb'}
    return pkg_type_def[platform.dist()[0].lower()]

def get_pkg_name(pkgfile):
    pkgname = None
    if pkgfile.endswith('.deb'):
        cmd = 'dpkg-deb --showformat=\'${Package}_${Version}\' -W %s' % pkgfile
    elif pkgfile.endswith('.rpm'):
        cmd = 'rpm -qp --queryformat "%%{NAME}-%%{VERSION}-%%{RELEASE}" %s' % pkgfile
    else:
        raise RuntimeError('Package (%s) is not an rpm or deb' % pkgfile)
    cmd_out = os.popen(cmd)
    pkgname = cmd_out.read().strip()
    
    if not pkgname:
        raise RuntimeError('Retrived Package Name (%s);'\
                           ' Cant retrieve Package Name for file (%s) '
                           'correctly' %(pkgname, pkgfile))
    return pkgname
    
def get_file_list(pkg_type, dirname):
    files = fnmatch.filter(os.listdir(dirname), '*.%s' % pkg_type)
    if len(files) == 0:
        raise RuntimeError('No %s files in current directory?' % pkg_type)
    return files

# Generation
def generate_cfg(files, filename):
    pkg_data = [(fname, get_pkg_name(fname)) for fname in files]
    pkg_data = sorted(pkg_data, key=lambda x: x[1])
    with open(filename, 'w') as fid:
        for each, pkgname in pkg_data:
            cmd = os.popen('md5sum %s' %each)
            md5 = cmd.read().strip('\n').split()[0]
            fid.write('[%s]\n' %pkgname)
            fid.write('file  = %s\n' %re.sub(r'%', '%%', each))
            fid.write('md5   = %s\n' %md5)
            fid.write('\n')
            fid.flush()
#end: generate_cfg

def validate_cfg(files, cfg):
    pfiles = []
    parser = SafeConfigParser()
    parser.read(cfg)
    for each in parser.sections():
        pfiles += [dict(parser.items(each))['file']]
    decor_lines = '-' * 77
    print 'INFO: Total Number of package files: %s' %len(files)
    print 'INFO: Total Number of package files in (%s): %s' %(cfg, len(pfiles))
    err_pkgs = set(files) - set(pfiles)

    # Reporting
    if err_pkgs != set([]):
        print 'ERROR: Couldnt generate cfg file entries for below files'
        print '\n%s\n%s\n%s' %(decor_lines, '\n'.join(list(err_pkgs)),
                               decor_lines)
        raise RuntimeError('File Generated (%s), but some mismatches,' 
                           ' please go through the file carefully' %cfg)
    else:
        print 'File Generated: %s' %cfg
#end: validate_cfg

def main(args):
    cliargs = parse_args(args)
    print 'Executing: %s' %" ".join(sys.argv)
    filename = 'new_config_file.cfg'
    files = get_file_list(cliargs.package_type, cliargs.package_dir)
    generate_cfg(files, filename)
    validate_cfg(files, filename)

if __name__ == '__main__':
    main(sys.argv[1:])
