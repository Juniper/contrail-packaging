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
import getpass
import random
import pprint
import datetime
import logging.config
import pdb

from libs.packager.utils import Utils
from templates import comps_xml

# Import packager based on distribution
sys.path.append(os.path.abspath(os.path.join('libs', 'packager')))
PLATFORM = platform.dist()[0].lower()
packager = __import__('%s_packager'%PLATFORM)

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
    def is_file_exists(filename):
        if not os.path.isfile(filename):
            raise RuntimeError('file (%s) does not exists' %filename)
        return filename

    @staticmethod
    def is_dir_exists(dirname):
        if not os.path.isdir(dirname):
            raise RuntimeError('Directory (%s) does not exists' %dirname)
        return dirname

    def set_cli_defaults(self):
        usrname = getpass.getuser()
        dist = list(platform.dist())
        dist = [dist[0].lower()] + dist[1:]
        cwd = os.getcwd()
        timestamp = time.strftime('%m%d%y%H%M%S')
        logname = 'packager_{id}_%s.log' %timestamp
        logfile = os.path.join(cwd, 'logs', logname)
        pkg_file_dir = os.path.join(cwd, 'pkg_configs')
        base_pkg_file = 'base_%s_pkgs.cfg' %("_".join(dist[:2]))
        deps_pkg_file = 'depends_%s_pkgs.cfg' %("_".join(dist[:2]))
        cont_pkg_file = 'contrail_packages.cfg'
        usrhome = os.path.expanduser('~')
        cmd = os.popen('repo info contrail-controller | grep "Mount path"|cut -f3 -d" "')
        git_local_repo = os.path.dirname(cmd.read().strip('\n'))
        sku = 'grizzly'

        
        self.defaults = {
            'build_id'              : random.randint(1000, 9999), 
            'sku'                   : sku,
            'branch'                : None, 
            'iso_prefix'            : 'contrail',     
            'store_dir'             : os.path.join(usrhome, '%s_{id}' %usrname, 
                                                   'store', '{id}'),
            'package_dir'           : None,
            'contrail_package_dir'  : None,
            'base_package_file'     : os.path.join(pkg_file_dir, dist[0], sku, base_pkg_file),
            'depends_package_file'  : os.path.join(pkg_file_dir, dist[0], sku, deps_pkg_file),
            'contrail_package_file' : os.path.join(pkg_file_dir, dist[0], sku, cont_pkg_file),
            'make_targets'          : [],
            'make_targets_file'     : None,
            'loglevel'              : 'DEBUG',
            'logfile'               : logfile,
            'log_config'            : os.path.join(cwd, 'logger', 'logging.cfg'),
            'git_local_repo'        : git_local_repo,
            'comps_xml_template'    : comps_xml.template,
            'default_targets'       : ['thirdparty-all', 'openstack-all', 'contrail-all'],
        }
  
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
        aparser.add_argument('--iso-prefix', '-n',
                             action='store',
                             help='Prefix name of the ISO image')
        aparser.add_argument('--store-dir', '-s',
                             action='store',
                             help='Directory Location to which new packages be saved')
        aparser.add_argument('--package-dir', '-p',
                             action='store',
                             type=lambda fn: self.is_dir_exists(fn),
                             help='Directory Location where OS and third party packages\
                                   are available')
        aparser.add_argument('--contrail-package-dir', '-P',
                             action='store',
                             type=lambda fn: self.is_dir_exists(fn),
                             help='Directory Location where pre-maked Contrail packages\
                                   are available')
        aparser.add_argument('--base-package-file', '-b',
                             action='store',
                             type=lambda fn: self.is_file_exists(fn),
                             help='Config files specifying base packages info')
        aparser.add_argument('--depends-package-file', '-d',
                             action='store',
                             type=lambda fn: self.is_file_exists(fn),
                             help='Config files specifying dependant pacakges info')
        aparser.add_argument('--contrail-package-file', '-f',
                             action='store',
                             type=lambda fn: self.is_file_exists(fn),
                             help='Config files specifying Contrail packages info')
        aparser.add_argument('--make-targets', '-t',
                             action='store',
                             nargs='+',
                             help='List of Contrail make targets to build')
        aparser.add_argument('--make-targets-file', '-T',
                             action='store',
                             type=lambda fn: self.is_file_exists(fn),
                             help='Line seperated text file containing list of \
                                   make targets')
        aparser.parse_args(self.unparsed_args)
        self.parser = aparser


######## MAIN ##############
args = PackagerArgParser(__doc__, VERSION, sys.argv[1:])
args.parse()

# Define except hook to redirect all erros to file
sys.excepthook = lambda tp, v, tb: log.error('ERROR', exc_info=(tp,v,tb))

log.info('Received CLI: %s' %" ".join(sys.argv))
log.info('')
log.info('Working with Argument Set: ')
log.info('\n%s' %pprint.pformat(args.cliargs, indent=4))
log.info('')
time.sleep(3)
log.info('')
start = datetime.datetime.now()

# Packager
packer = packager.Packager(**args.cliargs)

# Build
packer.ks_build()

duration = datetime.datetime.now() - start
log.info('Execution Duration: %s' %str(duration))
log.info('Packaging Complete!')
