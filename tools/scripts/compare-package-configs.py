#!/usr/bin/env python
"""
To compare package configs used by packager.py
"""

import os
import sys
import fnmatch
import argparse
import operator

from ConfigParser import SafeConfigParser
from distutils.version import LooseVersion

try:
    import apt_pkg
    apt_pkg.init_system()
except:
    import rpm

def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-type',
                        action='store',
                        default=None,
                        help='filter based on package type')
    parser.add_argument('--left-location',
                        action='store',
                        required=True,
                        help='Location of packages')
    parser.add_argument('--right-location',
                        action='store',
                        required=True,
                        help='Location of packages')
    parser.add_argument('--left-configs',
                        action='store',
                        nargs='+',
                        help='Left Config files, Usually Existing config files')
    parser.add_argument('--right-configs',
                        action='store',
                        nargs='+',
                        help='Right config files, Usually new config under test')
    parsed_info =  parser.parse_args(args)
    if len(args) == 0:
        parser.print_help()
        sys.exit(2)

    return parsed_info

def exec_cmd_out(cmd):
    cmd_out = os.popen(cmd)
    return cmd_out.read().strip().split()

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

def get_md5(files):
    md5dict = {}
    if files is None or len(files) == 0:
        return
    files = get_as_list(files)
    for filename in files:
        if not os.path.isfile(filename):
            print 'ERROR: File (%s) is not present' % filename
            continue
        md5out = exec_cmd_out('md5sum %s' %filename)
        if len(md5out) == 0:
            continue
        md5dict[filename] = md5out[0]
    return md5dict

def check_package_md5(pkginfo, location='location'):
    failed_packages = []
    for pkg in pkginfo.keys():
        pkg_loc = pkginfo[pkg][location]

        # Location is empty. Cant check md5sum
        if pkg_loc is '':
            msg = 'Given Location (%s) of the Package (%s) is empty' % (location, pkg)
            failed_packages.append(msg)
            print 'ERROR: %s' % msg
            continue

        # No package file found
        pkgfiles = get_file_list(pkg_loc, pkginfo[pkg]['file'], True)
        if len(pkgfiles) == 0:
            msg = 'Package file for package (%s) is not present in (%s)' %(
                   pkg, pkg_loc)
            failed_packages.append(msg)
            print 'ERROR: %s' % msg
            continue

        # No MD5 can be retrived
        md5_info = get_md5(pkgfiles)
        if len(md5_info) == 0:
            msg = 'MD5 checksum is empty for file (%s).\n' % pkgfiles +\
                  'Expected (%s) != Actual (%s)' % (pkginfo[pkg]['md5'], None)
            failed_packages.append(msg)
            print 'ERROR: %s' % msg
            continue

        # Atleast one of the files matches with expected MD5
        for filename in md5_info.keys():
            if pkginfo[pkg]['md5'] == md5_info[filename]:
                pkginfo[pkg]['found_at'] = filename
            else:
                print 'WARN: MD5 checksum mismatch for Package (%s) ' % filename

        # No match for expected MD5sum
        if not pkginfo[pkg]['found_at']:
            for filename in md5_info.keys():
                msg = 'MD5 Checksum validation for Package (%s) failed.\n' % filename +\
                      'Expected (%s) != Actual (%s)' % (
                      pkginfo[pkg]['md5'], md5_info[filename])
                failed_packages.append(msg)
                print 'ERROR: %s' % msg

    if len(failed_packages) != 0:
        raise RuntimeError('MD5 Checksum validation failed for below packages... '
                           'Review Errors; \n%s' % "\n".join(failed_packages))

def get_as_list(elm):
    return [elm] if type(elm) is str else elm

def get_dict_by_item(tdict, titem):
    matrix = {}
    try:
        cfg_itemgetter = operator.itemgetter(titem)
    except:
        return
    for key, items in tdict.items():
        matrix_keys = cfg_itemgetter(items)
        matrix_keys = get_as_list(matrix_keys)
        for matrix_key in matrix_keys:
            if not matrix.has_key(matrix_key):
                matrix[matrix_key] = {}
            matrix[matrix_key].update({key: items})

def str_to_list(tstr, force=False):
    ''' convert string separated with comma into a list '''
    tstr = tstr.replace('\n', '')
    sstr = [sstr.strip() for sstr in tstr.split(',')]
    if force:
        return sstr
    else:
        return tstr if tstr.rfind(',') < 0 else sstr

def parse_cfg_file(cfg_files, additems=None):
    ''' parse the given config files and return a dictionary
        with sections as keys and its items as dictionary items
    '''
    parsed_dict = {}
    sections = []
    cfg_files = get_as_list(cfg_files)
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
            parsed_dict[sect] = dict((iname, str_to_list(ival)) \
                                   for iname, ival in parser.items(sect))
            if additems != None:
                for item in additems.keys():
                    parsed_dict[sect][item] = copy.deepcopy(additems[item])
        sections.extend(parser.sections())
        del parser
    return parsed_dict

def get_cfg_info(pkg_type, location, *cfg_files):
    cfg_dict = parse_cfg_file(cfg_files)
    for key in cfg_dict.keys():
        if not cfg_dict[key]['location']:
            cfg_dict[key]['location'] = location
        else:
            print "WARNING: %s: Location (%s) is not empty" % (key, cfg_dict[key]['location'])
    if pkg_type:
        cfg_dict = {key: value for (key, value) in cfg_dict.items() if pkg_type in value['package_type']}
        #cfg_dict = get_dict_by_item(cfg_dict, pkg_type)
    return cfg_dict

def create_pkg_info(pkg_dict):
    pkg_list = []
    check_package_md5(pkg_dict)
    for key, value in pkg_dict.items():
        pkg_loc = pkg_dict[key]['found_at']
        if not os.access(pkg_loc, os.R_OK):
            raise RuntimeError('Package file (%s) not present' % pkg_loc)
        if pkg_loc.endswith('.deb'):
            cmd = 'dpkg-deb --showformat=\'${Package} ${Version}\' -W %s' % pkg_loc
            cmd_out = os.popen(cmd)
            cmd_out = cmd_out.read().strip().split()
            pkg_name, pkg_version = cmd_out
        else:
            cmd = 'rpm -qp --qf \"%%{N} %%{epochnum} %%{V} %%{R}\" %s' % pkg_loc
            cmd_out = os.popen(cmd)
            cmd_out = cmd_out.read().strip().split()
            pkg_name = cmd_out[0]
            pkg_version = cmd_out[1:]
        value.update([('version', pkg_version)])
        pkg_list.append((pkg_name, value))
    return pkg_list

def compare_pkg_info(info_list1, info_list2):
    info_dict1 = dict(info_list1)
    info_dict2 = dict(info_list2)

    missing_pkgs, md5_mismatch, upgraded, downgraded = [], [], [], []
    
    for key, value in info_dict1.items():
        if not key in info_dict2.keys():
            print 'WARNING: Package (%s) is missing in other dict' % key
            missing_pkgs.append(key)
            continue
        if  value['file'].endswith('.deb'):
            # Ubuntu
            vc = apt_pkg.version_compare(value['version'], info_dict2[key]['version'])     
        elif value['file'].endswith('.rpm'):
            # Centos
            vc = rpm.labelCompare(tuple(value['version']), tuple(info_dict2[key]['version']))

        if vc > 0:
            print 'Package (%s): Got Downgraded' % key
            downgraded.append('%s: Original Version (%s) > Current Version (%s)' % (key, value['version'], info_dict2[key]['version']))
        elif vc < 0:
            print 'Package (%s): Got Upgraded' % key
            upgraded.append('%s: Original Version (%s) < Current Version (%s)' % (key, value['version'], info_dict2[key]['version']))
        else:
            if value['md5'] == info_dict2[key]['md5']:
                print 'Package (%s): Is Untouched' % key
            else:
                print 'Package (%s): Is of Same version but MD5 is different' % key
                md5_mismatch.append('%s: Original MD5 (%s) != Current MD5 (%s)' % (key, value['md5'], info_dict2[key]['md5']))

    print "\n\nMD5 mismatch: \n%s" % "\n".join(md5_mismatch)
    print "\n\nUpgraded Packages: \n%s" % "\n".join(upgraded)
    print "\n\nDowngraded Packages: \n%s" % "\n".join(downgraded)
    print "\n\nMissing Packages: \n%s" % "\n".join(missing_pkgs)

def generate_new_pkg_cfgs(pkg_info, fname):
    with open(fname, 'w') as fid:
        for pkgname, value in pkg_info:
            fid.write('[%s]\n' % pkgname)
            fid.write('file     = %s\n' % value['file'])
            fid.write('version  = %s\n' % value['version'])
            fid.write('md5      = %s\n' % value['md5'])
            fid.write('location = %s\n' % value['location'])
            fid.write('\n')
            fid.flush()
 
def main(args):
    cliargs = parse_args(args)
    print 'Executing: %s' % " ".join(sys.argv)
    left_cfg_info = get_cfg_info(cliargs.package_type, cliargs.left_location, *cliargs.left_configs)
    right_cfg_info = get_cfg_info(cliargs.package_type, cliargs.right_location, *cliargs.right_configs)
    left_pkg_info = create_pkg_info(left_cfg_info)
    right_pkg_info = create_pkg_info(right_cfg_info)
    try:
        compare_pkg_info(left_pkg_info, right_pkg_info)
    except Exception, err:
        raise
    finally:
        generate_new_pkg_cfgs(left_pkg_info, 'left_pkgs.cfg')
        generate_new_pkg_cfgs(right_pkg_info, 'right_pkgs.cfg')

if __name__ == '__main__':
    main(sys.argv[1:])
