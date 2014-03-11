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

from libs.packager.utils import Utils
from templates import comps_xml

# Import packager based on distribution
sys.path.append(os.path.abspath(os.path.join('libs', 'packager')))
PLATFORM = platform.dist()[0].lower()
packager = __import__('%s_packager' %PLATFORM)

log = logging.getLogger("pkg.%s" %__name__)

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
        dist = list(platform.dist())
        dist = [dist[0].lower()] + dist[1:]
        cwd = os.getcwd()
        timestamp = time.strftime('%m%d%y%H%M%S')
        logname = 'packager_{id}_%s.log' %timestamp
        logfile = os.path.join(cwd, 'logs', logname)
        pkg_file_dir = os.path.join(cwd, 'pkg_configs')
        base_pkg_file = 'base_*_pkgs.cfg'
        deps_pkg_file = 'depends_*_pkgs.cfg'
        cont_pkg_file = 'contrail_packages.cfg'
        usrhome = os.path.expanduser('~')
        cmd = os.popen('repo info contrail-controller | grep "Mount path"|cut -f3 -d" "')
        git_local_repo = os.path.dirname(cmd.read().strip('\n'))
        if git_local_repo == '':
            raise RuntimeError('Cant find Git local Repo. Seems repo command is not available...')
        cache_base_dir = os.path.join(os.path.sep, 'cs-shared', 'builder', 'cache')
        skuname = 'grizzly'
        if dist[0] == 'ubuntu':
            skuname= 'havana'
            default_targets = ['openstack-all', 'contrail-all']
        else:
            default_targets = ['thirdparty-all', 'openstack-all', 'contrail-all']

        self.defaults = {
            'build_id'              : random.randint(1000, 9999), 
            'sku'                   : skuname,
            'branch'                : None, 
            'iso_prefix'            : 'contrail',     
            'store_dir'             : os.path.join(usrhome, 'packager_store'),
            'absolute_package_dir'  : None,
            'contrail_package_dir'  : None,
            'base_package_file'     : [os.path.join(pkg_file_dir, dist[0], '{skuname}', base_pkg_file)],
            'depends_package_file'  : [os.path.join(pkg_file_dir, dist[0], '{skuname}', deps_pkg_file)],
            'contrail_package_file' : [os.path.join(pkg_file_dir, dist[0], '{skuname}', cont_pkg_file)],
            'make_targets'          : [],
            'make_targets_file'     : None,
            'loglevel'              : 'DEBUG',
            'logfile'               : logfile,
            'log_config'            : os.path.join(cwd, 'logger', 'logging.cfg'),
            'git_local_repo'        : git_local_repo,
            'comps_xml_template'    : comps_xml.template,
            'default_targets'       : default_targets,
            'cache_base_dir'        : [cache_base_dir],
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
        # Update store dir
        ns_cliargs.store_dir = ns_cliargs.store_dir.format(id=ns_cliargs.build_id)
        # Create log file
        ns_cliargs.logfile = self.defaults['logfile'].format(id=ns_cliargs.build_id)
        if not os.path.isdir(os.path.dirname(ns_cliargs.logfile)):
            os.makedirs(os.path.dirname(ns_cliargs.logfile))
        logging.config.fileConfig(self.defaults['log_config'],
                                  defaults={'loglevel': self.defaults['loglevel'], 
                                            'logfile': ns_cliargs.logfile})

        # update sku in package files
        ns_cliargs.base_package_file = [base_file.format(skuname=ns_cliargs.sku) for \
                                        base_file in ns_cliargs.base_package_file]
        ns_cliargs.base_package_file = self.get_files_by_pattern(ns_cliargs.base_package_file)

        ns_cliargs.depends_package_file = [deps_file.format(skuname=ns_cliargs.sku) for \
                                           deps_file in ns_cliargs.depends_package_file]
        ns_cliargs.depends_package_file = self.get_files_by_pattern(ns_cliargs.depends_package_file)

        ns_cliargs.contrail_package_file = [cont_file.format(skuname=ns_cliargs.sku) for \
                                            cont_file in ns_cliargs.contrail_package_file]
        ns_cliargs.contrail_package_file = self.get_files_by_pattern(ns_cliargs.contrail_package_file)

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


    def define_args(self):
        ''' Define arguments for packager script '''
        cparser = argparse.ArgumentParser(add_help=False)
        cparser.add_argument('--config', '-c',
                             action='store',
                             default=os.path.abspath('config.cfg'),
                             help='Config File for the Packager')
        file_ns, rargs = cparser.parse_known_args(self.unparsed_args)
        self.cfg_file = file_ns.config
        aparser = argparse.ArgumentParser(parents=[cparser],
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description=self.desc)
        aparser.add_argument('--version', '-v',
                             action='version',
                             version=self.version,
                             help='Print version and exit')
        aparser.add_argument('--build-id', '-i',
                             action='store',
                             help='Build ID of the new packages')
        aparser.add_argument('--sku',
                             action='store',
                             help='Specify Openstack release')
        aparser.add_argument('--branch',
                             action='store',
                             help='Specify GIT branch name')
        aparser.add_argument('--store-dir', '-s',
                             action='store',
                             help='Directory Location to which new packages be saved')
        aparser.add_argument('--cache-base-dir', '-C',
                             action='store',
                             nargs='+',
                             help='Base directory location where OS and third\
                                   party packages are available.\
                                   packager will check files in \
                                   base_cache_dir/distribution/sku/. eg\
                                   /cs-shared/builder/cache/centos64/grizzly/')
        aparser.add_argument('--absolute-package-dir', '-a',
                             action='store',
                             nargs='+',
                             help='Absolute Directory Location where OS and third\
                                   party packages are available')
        aparser.add_argument('--contrail-package-dir', '-P',
                             action='store',
                             nargs='+',
                             help='Directory Location where pre-maked Contrail packages\
                                   are available')
        aparser.add_argument('--base-package-file', '-b',
                             action='store',
                             nargs='+',
                             help='Config files specifying base packages info')
        aparser.add_argument('--depends-package-file', '-d',
                             action='store',
                             nargs='+',
                             help='Config files specifying dependant pacakges info')
        aparser.add_argument('--contrail-package-file', '-f',
                             action='store',
                             nargs='+',
                             help='Config files specifying Contrail packages info')
        aparser.add_argument('--make-targets', '-t',
                             action='store',
                             nargs='+',
                             help='List of Contrail make targets to build')
        aparser.add_argument('--make-targets-file', '-T',
                             action='store',
                             help='Line seperated text file containing list of \
                                   make targets')
        aparser.add_argument('--iso-prefix', '-n',
                             action='store',
                             help='Prefix name of the ISO image\
                                   eg: <isoprefix>-<buildid>-x86_64-DVD.iso')
        aparser.parse_args(self.unparsed_args)
        self.parser = aparser


# ** MAIN **

if __name__ == '__main__':
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
    packer = packager.Packager(**args.cliargs)

    # Build
    try:
        packer.ks_build()
    except:
        raise
    finally:
        log.info('Copying available built ' \
                 'packages to (%s)' %packer.artifacts_dir)
        packer.copy_to_artifacts()

    duration = datetime.datetime.now() - start
    log.info('Execution Duration: %s' %str(duration))
    log.info('Packaging Complete!')
