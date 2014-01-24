#!/usr/bin/env python
''' Python Packager Script to Make Packages and Create an ISO '''
VERSION = 1.0

import os
import argparse
import sys
import textwrap
import logging
import time
import platform
from pprint import pprint

from libs.packager.utils import Utils
sys.path.append(os.path.abspath(os.path.join('libs', 'packager')))
packager = __import__('%s_packager'%platform.dist()[0])

log = logging.getLogger("pkg.%s" %__name__)

class PackagerArgParser(Utils):
    def __init__(self, desc, version, args):
        self.unparsed_args = args
        self.parser        = None
        self.cliargs       = {}
        self.version       = version
        desc               = textwrap.fill(textwrap.dedent(desc).strip(), width=79)
        self.desc          = 'Description:\n%s\n%s\n\n' %(desc, '-' * 79)
        self.parse_args()

    @staticmethod
    def is_file_exists(filename):
        if not os.path.isfile(filename):
            raise RuntimeError('file (%s) doesnot exists' %filename)
        return filename

    def validate_args(self):
        self.is_file_exists(self.cliargs['cfg_file'])

    def parse(self):
        parser = argparse.ArgumentParser(add_help=False,
                                         parents=[self.parser])
        cfg_file = self.import_file(self.cfg_file)
        parser.set_defaults(**cfg_file.CLI_DEFAULTS)
        ns_cliargs = parser.parse_args(self.unparsed_args)
        # update git local repo dir       
        if ns_cliargs.install_local_repo and ns_cliargs.git_local_repo is None:
            ns_cliargs.git_local_repo = cfg_file.git_lrepo.format(id=ns_cliargs.id)
        elif ns_cliargs.install_local_repo is False and ns_cliargs.git_local_repo is None:
            cmd = os.popen('repo info contrail-controller | grep "Mount path"|cut -f3 -d" "')
            ns_cliargs.git_local_repo = cmd.read().strip('\n')

        # update logger and create required env
        logfile = cfg_file.logfile.format(id=ns_cliargs.id)
        if not os.path.isdir(os.path.dirname(logfile)):
            self.create_dir(os.path.dirname(logfile))

        logging.config.fileConfig(cfg_file.log_cfg_file,
                                  defaults={'loglevel': ns_cliargs.log_level, 
                                            'logfile': logfile}
                                 )
        self.cliargs = dict(ns_cliargs._get_kwargs())
        self.validate_args()

    def parse_args(self):
        cparser = argparse.ArgumentParser(add_help=False)
        cparser.add_argument('--cfg-file',
                             action='store',
                             default=os.path.abspath('config.py'),
                             help='Config File for the Packager')
        file_ns, rargs = cparser.parse_known_args(self.unparsed_args)
        self.cfg_file = file_ns.cfg_file
        gparser = argparse.ArgumentParser(add_help=False)
        flag_group = gparser.add_argument_group('Flags')
        flag_group.add_argument('--skip-build',
                                action='store_true',
                                help='Skip making Individual packages except\
                                      contrail-install-pacakages')
        flag_group.add_argument('--jenkins',
                                action='store_true',
                                help='True if Jenkins triggered the build')
        flag_group.add_argument('--install-local-repo',
                                action='store_true',
                                help='Perform Repo init locally and run fetch-package')
        flag_group.add_argument('--no-sync-repo',
                                action='store_true',
                                help='Do not try to sync repo')
                                
        aparser = argparse.ArgumentParser(parents=[gparser, cparser],
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          description=self.desc)
        aparser.add_argument('--version', '-v',
                             action='version',
                             version=self.version,
                             help='Print version and exit')
        aparser.add_argument('--id', '-i',
                             action='store',
                             help='BUILD ID')
        aparser.add_argument('--store', '-s',
                             action='store',
                             help='Location of save built pkgs')
        aparser.add_argument('--pkg-dirs', '-r',
                             action='store',
                             nargs='+',
                             help='Location of OS and Deps pkgs')
        aparser.add_argument('--cont-pkg-dirs', '-cr',
                             action='store',
                             nargs='+',
                             help='Location of Contrail pkgs')
        aparser.add_argument('--base-pkg-files', '-bf',
                             action='store',
                             nargs='+',
                             type=lambda fn: self.is_file_exists(fn),
                             help='Config files specifying base packages info')
        aparser.add_argument('--deps-pkg-files', '-df',
                             action='store',
                             nargs='+',
                             type=lambda fn: self.is_file_exists(fn),
                             help='Config files specifying dependant pacakges info')
        aparser.add_argument('--cont-pkg-files', '-cf',
                             action='store',
                             nargs='+',
                             type=lambda fn: self.is_file_exists(fn),
                             help='Config files specifying Contrail packages info')
        aparser.add_argument('--fab-env', '-fab',
                             action='store',
                             help='Location of fabric-utils directory')
        aparser.add_argument('--exec',
                             action='store',
                             nargs='+',
                             help='Execution to start from fab')
        aparser.add_argument('--git-repo-name',
                             action='store',
                             help='Name of GitHub Repo to sync')
        aparser.add_argument('--git-login',
                             action='store',
                             help='Login Credential for Git. Eg. git@github.com')
        aparser.add_argument('--git-local-repo',
                             action='store',
                             help='Name of Github local repo dir')
        aparser.add_argument('--git-fetch-pkgdirs',
                             action='store',
                             nargs='*',
                             help='Git dirs in which fetch package has to be executed')
        aparser.add_argument('--make-targets',
                             action='store',
                             nargs='+',
                             help='List of targets to make')
        aparser.add_argument('--make-targets-file',
                             action='store',
                             help='Line seperated text file containing list of make targets')
        aparser.parse_args(self.unparsed_args)
        self.parser = aparser


######## MAIN ##############

args = PackagerArgParser(__doc__, VERSION, sys.argv[1:])
args.parse()

#sys.stdout = PkgStdout(log, logging.DEBUG)
#sys.stderr = PkgStdout(log, logging.DEBUG)
log.info('Executing:')
log.info('Received CLI: %s' %" ".join(sys.argv))
log.info('')
log.info('Working with Argument Set: ')
log.info(pprint(args.cliargs, indent=4))
log.info('')
time.sleep(3)
log.info("")

# Packager
packer = packager.Packager(**args.cliargs)

# Make RPMS
packer.ks_build()
