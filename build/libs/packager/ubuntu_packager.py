#!/usr/bin/env python
''' Generic Library for UBUNTU Packager scripts'''

import logging

from common import BasePackager

log = logging.getLogger("pkg.%s" %__name__)


class Packager(BasePackager):
    ''' Ubuntu Packager '''
    def ks_build(self):
        self.setup_env()
        self.create_pkg_list_file()
        self.make_pkgs()
        self.verify_built_pkgs_exists(skips=['contrail-install-packages'])
        self.copy_built_pkg_files(self.pkg_repo, skips=['contrail-install-packages'])
        self.create_tgz(self.pkgs_tgz, self.pkg_repo)
        self.create_contrail_pkg()
        self.verify_built_pkgs_exists(['contrail-install-packages'])        
        self.copy_built_pkg_files([self.store, self.pkg_repo], 
                                  ['contrail-install-packages'])
        self.copy_pkg_files(self.base_pkgs, self.pkg_repo)
        self.create_log()
        self.create_git_ids()
