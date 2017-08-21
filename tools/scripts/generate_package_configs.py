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
import subprocess
from ConfigParser import SafeConfigParser

def get_header_file():
    header_file = os.path.join(os.getcwd(), 'header_file')
    return header_file if os.access(header_file, os.R_OK) else None

def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--package-dirs',
                        nargs='+',
                        default=os.getcwd(),
                        help='Absolute directory path from where packages'\
                             ' have to be picked up')
    parser.add_argument('-t', '--package-type',
                        action='store',
                        default=get_system_pkg_type(),
                        help='Specify package type is rpm or deb')
    parser.add_argument('-f', '--header-file',
                        action='store',
                        default=get_header_file(),
                        help='File containing header info')
    return parser.parse_args(args)
    
def get_system_pkg_type():
    pkg_type_def = {'centos': 'rpm', 'redhat': 'rpm', \
                    'fedora': 'rpm', 'ubuntu': 'deb'}
    return pkg_type_def[platform.dist()[0].lower()]

def get_pkg_name(dirname, pkgfile):
    pkgname_with_version = None
    if pkgfile.endswith('.deb'):
        cmd = 'dpkg-deb --showformat=\'${Package}_${Version}\' -W %s' % pkgfile
        name_cmd = 'dpkg-deb --showformat=\'${Package}\' -W %s' % pkgfile
    elif pkgfile.endswith('.rpm'):
        cmd = 'rpm -qp --queryformat "%%{NAME}-%%{VERSION}-%%{RELEASE}" %s' % pkgfile
        name_cmd = 'rpm -qp --queryformat "%%{NAME}" %s' % pkgfile
    else:
        raise RuntimeError('Package (%s) is not an rpm or deb' % pkgfile)
    cmd_out = os.popen(cmd)
    pkgname_with_version = cmd_out.read().strip()

    name_cmd_out = os.popen(name_cmd)
    pkgname = name_cmd_out.read().strip()
    
    if not pkgname_with_version or not pkgname:
        raise RuntimeError('Retrived Package Name (%s);'\
                           ' Cant retrieve Package Name for file (%s) '
                           'correctly' %(pkgname_with_version, pkgfile))
    return pkgname_with_version, pkgname
    
def get_file_list(pkg_type, dirname):
    files = []
    findcmd = 'find %s -name "*.%s"' % (dirname, pkg_type)
    op = subprocess.Popen(findcmd, shell=True, stdout=subprocess.PIPE)
    stdout, stderr = op.communicate()
    files = stdout.split('\n')[:-1]
    #files = fnmatch.filter(os.listdir(dirname), '*.%s' % pkg_type)
    if len(files) == 0:
        raise RuntimeError('No %s files in current directory?' % pkg_type)
    pkg_type_file = fnmatch.filter(os.listdir(dirname), 'package_type')
    if pkg_type_file:
        files += pkg_type_file
    return files

def get_pkg_data(dirname, files):
    pkg_data = []
    pkg_types = []
    if 'package_type' in files:
        with open('%s/package_type' % dirname, 'r') as fid:
            pkg_types =  fid.read().strip().split('\n')
        files.remove('package_type')
    for fpath in files:
        #cmd = os.popen('cd %s && md5sum %s' % (dirname, fpath))
        cmd = os.popen('md5sum %s' % fpath)
        md5 = cmd.read().strip('\n').split()[0]
        pkg_name_info = get_pkg_name(dirname, fpath)
        fname = os.path.basename(fpath)
        pkg_data_item = {'file' : re.sub(r'%', '%%', fname), 'md5': md5, 'header': pkg_name_info[0], 'pkgname': pkg_name_info[1]}
        if pkg_types:
            pkg_data_item['package_type'] = ", ".join(pkg_types)
        pkg_data_item['source'] = "repo:%s" % dirname
        pkg_data_item['dirname'] = dirname.split(os.path.sep)[0]
        pkg_data.append((fname, pkg_data_item))
    return pkg_data

# Generation
def generate_cfg(pkg_data, filename, header_file):
    # add first package's package type in header
    fname, pkg_info = pkg_data[0]
    if header_file:
        with open(header_file, 'r') as fid:
            header_info = fid.read()
    with open(filename, 'w') as fid:
        fid.write(header_info)
        if pkg_info.get('package_type', None):
            fid.write('package_type   = %s\n' % pkg_info['package_type'])
        fid.write('\n')
        for fname, pkg_info in pkg_data:
            fid.write('[%s]\n' % pkg_info['header'])
            fid.write('file           = %s\n' % pkg_info['file'])
            fid.write('md5            = %s\n' % pkg_info['md5'])
            fid.write('source         = %s\n' % pkg_info['source'])
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
    print 'INFO: Total Number of package files: %s' % len(files)
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

# check no duplicates
def check_pkg_data(pkg_data):
    actual_pkg_names = []
    duplicates = []
    decor_lines = '-' * 77
    for key, items in pkg_data:
        actual_pkg_names.append(items['pkgname'])
    for each in actual_pkg_names:
        if actual_pkg_names.count(each) > 1:
            duplicates.append(each)
    if len(duplicates) != 0:
        print "Probable duplicates"
        print '\n%s\n%s\n%s' %(decor_lines, '\n'.join(duplicates),
                               decor_lines)
        raise RuntimeError('Probable duplicates. Please correct and rerun')
    

def main(args):
    cliargs = parse_args(args)
    print 'Executing: %s' %" ".join(sys.argv)
    filename = 'new_config_file.cfg'
    all_pkg_data = []
    for dirname in cliargs.package_dirs:
        files = get_file_list(cliargs.package_type, dirname)
        all_pkg_data += get_pkg_data(dirname, files)
    all_pkg_data = sorted(all_pkg_data, key=lambda x: x[0])
    check_pkg_data(all_pkg_data)
    generate_cfg(all_pkg_data, filename, cliargs.header_file)
    validate_cfg(dict(all_pkg_data).keys(), filename)

if __name__ == '__main__':
    main(sys.argv[1:])
