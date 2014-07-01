#!/usr/bin/env python
''' Generic Library for UBUNTU Packager scripts'''

import logging

from common import BasePackager

log = logging.getLogger("pkg")


class Packager(BasePackager):
    ''' Ubuntu Packager '''
    def exec_steps(self):
        '''Packager Steps'''
        self.setup_env()
        self.create_pkg_list_file()
        self.make_pkgs()
        self.verify_built_pkgs_exists(skips=self.meta_pkg,
                                      recursion=False)
        self.copy_built_pkg_files(skips=self.meta_pkg)
        self.create_pkgs_tgz()
        self.create_contrail_pkg()
        self.verify_built_pkgs_exists(self.meta_pkg,
                                      recursion=False)
        self.create_log()
        self.create_git_ids()
        self.cleanup_store()

