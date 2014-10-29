#!/usr/bin/env python
''' Python Packager Script to Make Packages and Create an ISO '''
VERSION = '1.0'

import os
import argparse
import sys
import textwrap
import logging
import time
import platform
import random
import pprint
import datetime
import logging.config

from logger import logger
logging.setLoggerClass(logger.PackagerLogger)
from libs.packager.utils import Utils

#get script dir
SCRIPTDIR = os.path.abspath(os.path.dirname(sys.argv[0]))

# Import packager based on distribution
sys.path.append(os.path.abspath(os.path.join(SCRIPTDIR, 'libs', 'packager')))

log = logging.getLogger("pkg")

class PackagerArgParser(Utils):
    ''' Argument parser for Packager '''
    def __init__(self, desc, version, args):
        self.unparsed_args = args
        self.parser        = None
        self.cliargs       = {}
        self.version       = version
        desc               = textwrap.fill(textwrap.dedent(desc).strip(), width=79)
        self.desc          = 'Description:\n%s\n%s\n\n' %(desc, '-' * 79)
        self.define_args()
        self.set_cli_defaults()

    @staticmethod
    def is_file_exists(filenames):
        filenames_local = [filenames] if type(filenames) is str else filenames
        for filename in filenames_local:
            filename = os.path.abspath(os.path.expanduser(filename))
            if not os.path.isfile(filename):
                raise RuntimeError('file (%s) does not exists' %filename)
        return filenames

    @staticmethod
    def is_dir_exists(dirnames):
        dirnames_local = [dirnames] if type(dirnames) is str else dirnames
        for dirname in dirnames_local:
            dirname = os.path.abspath(os.path.expanduser(dirname))
            if not os.path.isdir(dirname):
                raise RuntimeError('Directory (%s) does not exists' %dirname)
        return dirnames

    def set_cli_defaults(self):
        timestamp = time.strftime('%m%d%y%H%M%S')
        logname = 'packager_{id}_%s.log' %timestamp
        pkg_file_dir = os.path.join(SCRIPTDIR, 'package_configs')
        base_pkg_file = 'base*_packages.cfg'
        deps_pkg_file = 'depends*_packages.cfg'
        cont_pkg_file = 'contrail*_packages.cfg'
        git_local_repo = SCRIPTDIR.replace('tools/packaging/build', '')
        if git_local_repo == '':
            raise RuntimeError('Cant find Git local Repo directory (sandbox)...')
        cache_base_dir = os.path.join(os.path.sep, 'cs-shared', 'builder', 'cache')
        sku_cmd = os.popen("grep -oP '<label name=\"sku\" value=\"\K\w+' %s" % os.path.join(
                           git_local_repo, '.repo', 'manifest.xml'))
        skuname = sku_cmd.read().strip()

        self.defaults = {
            'build_id'              : random.randint(1000, 9999), 
            'sku'                   : skuname,
            'branch'                : None, 
            'store_dir'             : os.path.join(git_local_repo, 'build'),
            'absolute_package_dir'  : None,
            'contrail_package_dir'  : None,
            'base_package_file'     : [os.path.join(pkg_file_dir, '{dist_dir}', '{skuname}', base_pkg_file)],
            'depends_package_file'  : [os.path.join(pkg_file_dir, '{dist_dir}', '{skuname}', deps_pkg_file)],
            'contrail_package_file' : [os.path.join(pkg_file_dir, '{dist_dir}', '{skuname}', cont_pkg_file)],
            'make_targets'          : [],
            'make_targets_file'     : None,
            'loglevel'              : 'DEBUG',
            'logfile'               : os.path.join('{storedir}', 'logs', logname),
            'log_config'            : os.path.join(SCRIPTDIR, 'logger', 'logging.cfg'),
            'git_local_repo'        : git_local_repo,
            'cache_base_dir'        : [cache_base_dir],
            'fail_on_error'         : False,
            'post_job'              : None,
        }
  
    def get_config_file_args(self):
        cfg_file_defaults = self.parse_cfg_file(self.cfg_file)
        return cfg_file_defaults['config']

    @staticmethod
    def banner(infodict):
        banner = []
        print
        banner.append('-' * 78)
        if len(infodict) != 0:
            elmwidth = max(map(len, infodict.keys()))
            for elm, value in infodict.items():
                banner.append("* {0:<{elmwidth}}  : {1: <} ".format(elm, value, 
                                                            elmwidth=elmwidth))
        else:
            banner.append('No Info')
        banner.append('-' * 78)
        log.info('\n%s' %'\n'.join(banner))
        log.info('')   
        log.info('')   

    def parse(self):
        ''' parse cli arguments from packager '''
        parser = argparse.ArgumentParser(add_help=False,
                                         parents=[self.parser])
        cfg_file_defaults = self.parse_cfg_file(self.cfg_file)
        parser.set_defaults(**self.defaults)
        parser.set_defaults(**cfg_file_defaults['config'])
        ns_cliargs = parser.parse_args(self.unparsed_args)

        # Create log file
        ns_cliargs.logfile = self.defaults['logfile'].format(storedir=ns_cliargs.store_dir,
                                                             id=ns_cliargs.build_id)
        if not os.path.isdir(os.path.dirname(ns_cliargs.logfile)):
            os.makedirs(os.path.dirname(ns_cliargs.logfile))
        logging.config.fileConfig(self.defaults['log_config'],
                                  defaults={'loglevel': self.defaults['loglevel'], 
                                            'logfile': ns_cliargs.logfile})

        # set default branch
        if ns_cliargs.branch is None:
            output = os.popen('cat %s/controller/src/base/version.info'
                                             % ns_cliargs.git_local_repo)
            ns_cliargs.branch = output.read().strip()

        # update sku in package files
        ns_cliargs.base_package_file = [base_file.format(skuname=ns_cliargs.sku,
                                       dist_dir=ns_cliargs.os_version) for \
                                           base_file in Utils.get_as_list(ns_cliargs.base_package_file)]
        ns_cliargs.base_package_file = self.get_files_by_pattern(ns_cliargs.base_package_file, False)

        ns_cliargs.depends_package_file = [deps_file.format(skuname=ns_cliargs.sku,
                                          dist_dir=ns_cliargs.os_version) for \
                                              deps_file in Utils.get_as_list(ns_cliargs.depends_package_file)]
        ns_cliargs.depends_package_file = self.get_files_by_pattern(ns_cliargs.depends_package_file, True)

        ns_cliargs.contrail_package_file = [cont_file.format(skuname=ns_cliargs.sku,
                                               dist_dir=ns_cliargs.os_version) for \
                                               cont_file in Utils.get_as_list(ns_cliargs.contrail_package_file)]
        ns_cliargs.contrail_package_file = self.get_files_by_pattern(ns_cliargs.contrail_package_file, True)

        # validate file and dir exists
        self.is_dir_exists(ns_cliargs.cache_base_dir)
        if ns_cliargs.absolute_package_dir is not None:
            self.is_dir_exists(ns_cliargs.absolute_package_dir)
        if ns_cliargs.contrail_package_dir is not None:
            self.is_dir_exists(ns_cliargs.contrail_package_dir)
        self.is_file_exists(ns_cliargs.base_package_file)
        self.is_file_exists(ns_cliargs.depends_package_file)
        self.is_file_exists(ns_cliargs.contrail_package_file)

        # convert namespace as a dict
        self.cliargs = dict(ns_cliargs._get_kwargs())
        if self.cliargs['populate_defaults']:
            log.info('Arguments from config file')
            log.info(self.cliargs['config'])
            self.banner(self.get_config_file_args())
            log.info('Populated Arguments: ')
            new_args = dict([('--%s' % key.replace('_', '-'), value) for key, value in self.cliargs.items()])
            new_args['--build-id'] = '%s (random number)' % new_args['--build-id']
            new_args['--logfile'] = '%s (based on build-id and timestamp)' % new_args['--logfile']
            self.banner(new_args)
            sys.exit(0)

    def define_args(self):
        ''' Define arguments for packager script '''
        cparser = argparse.ArgumentParser(add_help=False)
        cparser.add_argument('--config', '-c',
                             action='store',
                             default=os.path.join(SCRIPTDIR, 'config.cfg'),
                             help='Config File for the Packager')
        file_ns, rargs = cparser.parse_known_args(self.unparsed_args)
        self.cfg_file = file_ns.config

        os_parser = argparse.ArgumentParser(add_help=False)
        platform_info = Utils.get_platform_info()
        os_parser.add_argument('--os-version', '-O',
                             action='store',
                             default=platform_info['formatted'],
                             help='Specify OS Type and Version. \
                                   eg: centos64, ubuntu1204, redhatlinuxenterprise70')
        file_ns, rargs = os_parser.parse_known_args(self.unparsed_args)

        aparser = argparse.ArgumentParser(parents=[cparser, os_parser],
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                          description=self.desc)
        aparser.add_argument('--version', '-v',
                             action='version',
                             version=self.version,
                             help='Print version and exit')
        aparser.add_argument('--build-id', '-i',
                             action='store',
                             default='Random number from 1000-9999',
                             help='Build ID of the new packages')
        aparser.add_argument('--sku',
                             action='store',
                             default='Derived from manifest sku',
                             help='Specify Openstack release')
        aparser.add_argument('--branch',
                             action='store',
                             default='from sandbox/controller/src/base/version.info',
                             help='Specify GIT branch name')
        aparser.add_argument('--store-dir', '-s',
                             action='store',
                             default='sandbox/build/',
                             help='Directory Location to which new packages be saved')
        aparser.add_argument('--cache-base-dir', '-C',
                             action='store',
                             default='/cs-shared/builder/cache',
                             nargs='+',
                             help='Base directory location where OS and third\
                                   party packages are available.\
                                   packager will check files in \
                                   base_cache_dir/distribution/sku/. eg\
                                   /cs-shared/builder/cache/centos64/grizzly/')
        aparser.add_argument('--absolute-package-dir', '-a',
                             action='store',
                             default=None,
                             nargs='+',
                             help='Absolute Directory Location where OS and third\
                                   party packages are available')
        aparser.add_argument('--contrail-package-dir', '-P',
                             action='store',
                             default=None,
                             nargs='+',
                             help='Directory Location where pre-maked Contrail packages\
                                   are available')
        aparser.add_argument('--base-package-file', '-b',
                             action='store',
                             default='sandbox/tools/packaging/build/package_configs/<os>/<sku>/base*_packages.cfg',
                             nargs='+',
                             help='Config files specifying base packages info')
        aparser.add_argument('--depends-package-file', '-d',
                             action='store',
                             default='sandbox/tools/packaging/build/package_configs/<os>/<sku>/depends*_packages.cfg',
                             nargs='+',
                             help='Config files specifying dependant pacakges info')
        aparser.add_argument('--contrail-package-file', '-f',
                             action='store',
                             default='sandbox/tools/packaging/build/package_configs/<os>/<sku>/contrail*_packages.cfg',
                             nargs='+',
                             help='Config files specifying Contrail packages info')
        aparser.add_argument('--make-targets', '-t',
                             action='store',
                             default=None,
                             nargs='+',
                             help='List of Contrail make targets to build')
        aparser.add_argument('--make-targets-file', '-T',
                             action='store',
                             default=None,
                             help='Line seperated text file containing list of \
                                   make targets')
        aparser.add_argument('--fail-on-error', '-e',
                             action='store_true',
                             help='Aborts Packager from continuing when make fails')
        aparser.add_argument('--post-job', '-j',
                             action='store',
                             default=None,
                             help='Script to execute after Packaging is successfully complete')
        aparser.add_argument('--populate-defaults',
                             action='store_true',
                             help='Populates packager arguments with default values\
                                   and prints')
        aparser.parse_args(self.unparsed_args)
        self.parser = aparser

def main():
    args = PackagerArgParser(__doc__, VERSION, sys.argv[1:])
    args.parse()

    # Define except hook to redirect all erros to file
    sys.excepthook = lambda tp, v, tb: log.error('ERROR', exc_info=(tp,v,tb))

    log.info('Received CLI: %s' %" ".join(sys.argv))
    log.info('')
    log.info('Arguments from config file')
    log.info(args.cliargs['config'])
    args.banner(args.get_config_file_args())
    log.info('Working with Argument Set: ')
    args.banner(args.cliargs)
    log.info('')
    time.sleep(3)
    log.info('')
    start = datetime.datetime.now()

    # Packager
    platform_info = Utils.get_platform_info(args.cliargs['os_version'])
    packager = __import__('%s_packager' % platform_info['default'][0])
    packer = packager.Packager(**args.cliargs)

    # Build
    try:
        packer.ks_build()
    except:
        packer.exec_status = 1
        log.error('** Packager Failed **')
        raise
    else:
        if packer.exec_status != 0:
            sys.exit(packer.exec_status)
    finally:
        log.info('Copying available built ' \
                 'packages to (%s)' %packer.artifacts_dir)
        packer.copy_to_artifacts()
        if packer.exec_status != 0:
            log.info('*' * 78)
            log.info('Packager completed with ERRORs...')
            log.info('Reprinting ALL ERRORS...')
            log.reprint_errors()
            log.error('View detailed logs at (%s)' % args.cliargs['logfile'])
        elif args.cliargs['post_job']:
            log.info('Running Post Job')
            packer.exec_cmd(args.cliargs['post_job'])
        duration = datetime.datetime.now() - start
        log.info('Execution Duration: %s' %str(duration))
    log.info('Packaging Complete!')


# ** MAIN **

if __name__ == '__main__':
    main()
