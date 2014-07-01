#!/usr/bin/env python
'''
Copies list of packages specified in given package file from source directories
to desitnation directory
'''

__version__ = '1.0'

import os
import sys
import logging
import argparse

import package_utils as utils

logging.basicConfig(format='%(asctime)-15s:: %(funcName)s:%(levelname)s:: '
                    '%(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


SCRIPTDIR = os.path.abspath(os.path.dirname(sys.argv[0]))


def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__,
                        help='Display version and exit')
    parser.add_argument('-i', '--build-id',
                        action='store',
                        default=None,
                        help='Specify Build ID')
    parser.add_argument('-s', '--source-dirs',
                        action=utils.Abspath,
                        required=True,
                        nargs='+',
                        type=utils.check_dir_exists,
                        help='Specify Directories where packages are present')
    parser.add_argument('-d', '--destination-dir',
                        action=utils.Abspath,
                        required=True,
                        help='Specify where to copy all packages')
    parser.add_argument('-p', '--package-file',
                        action=utils.Abspath,
                        required=True,
                        help='File that contains list of packages')
    parser.add_argument('-e', '--excludes',
                        action='store',
                        default=[],
                        nargs='+',
                        help='excluded package list')
    pargs = parser.parse_args(args)
    if len(args) == 0:
        parser.print_help()
        sys.exit(2)
    return dict(pargs._get_kwargs())


def copy_built_pkgs(build_id, package_file, source_dirs, destination_dir, excludes):
    utils.check_package_file(package_file)
    platform_ver = utils.get_platform_info()
    pkg_types = {'ubuntu': 'deb', 'centos': 'rpm',
                 'redhat': 'rpm', 'fedora': 'rpm'}
    extn = pkg_types[platform_ver[0]]
    if extn == 'rpm':
        pattern = '{pkg}-[0-9]*%s*.%s' % (build_id, extn) if build_id else \
                  '{pkg}-[0-9]*.%s' % extn
    elif extn == 'deb':
        pattern = '{pkg}_[0-9]*%s*.%s' % (build_id, extn) if build_id else \
                  '{pkg}_[0-9]*.%s' % extn
    else:
        raise RuntimeError('Unknow package extension. Cant decide package pattern')

    packages = utils.get_packages_from_file(pattern, package_file, source_dirs, excludes)
    if len(packages) == 0:
        raise Exception('No Packages to copy...from given source dirs (%s)' % source_dirs)
    utils.copy_packages(packages, destination_dir)
    
if __name__ == '__main__':
    cli_args = parse_args(sys.argv[1:])
    copy_built_pkgs(**cli_args)
