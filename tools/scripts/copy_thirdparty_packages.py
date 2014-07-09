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
    parser.add_argument('-s', '--source-dirs',
                        action=utils.Abspath,
                        required=True,
                        nargs='+',
                        help='Specify Directories where packages are present')
    parser.add_argument('-d', '--destination-dir',
                        action=utils.Abspath,
                        required=True,
                        help='Specify where to copy all packages')
    parser.add_argument('-p', '--package-file',
                        action=utils.Abspath,
                        required=True,
                        help='File that contains list of packages')
    parser.add_argument('-i', '--include-only',
                        action='store',
                        dest='includes',
                        default=[],
                        nargs='+',
                        help='Copy only specified packages')
    pargs = parser.parse_args(args)
    if len(args) == 0:
        parser.print_help()
        sys.exit(2)
    return dict(pargs._get_kwargs())


def copy_thirdparty_pkgs(package_file, source_dirs, destination_dir, includes):
    utils.check_package_file(package_file)
    packages_info = utils.get_thirdparty_packages_info_file(package_file,
                                                            source_dirs)
    # overriding for includes
    if includes:
        packages_info = dict((key, value) for key, value in 
                             packages_info.items() if key in includes)

    packages = [packages_info[pkg]['abspath'] for pkg in packages_info.keys()]
    if len(packages) == 0:
        raise Exception('No Packages to copy...from given source dirs '
                        '(%s)' % source_dirs)
    utils.copy_packages(packages, destination_dir)
    for pkg in packages_info.keys():
        packages_info[pkg]['abspath'] = os.path.join(
            destination_dir,
            packages_info[pkg]['package'])
    utils.check_package_md5(packages_info)

if __name__ == '__main__':
    cli_args = parse_args(sys.argv[1:])
    copy_thirdparty_pkgs(**cli_args)
