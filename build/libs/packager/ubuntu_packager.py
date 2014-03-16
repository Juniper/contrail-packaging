#!/usr/bin/env python
''' Generic Library for UBUNTU Packager scripts'''

import logging

from common import BasePackager

log = logging.getLogger("pkg.%s" %__name__)


class Packager(BasePackager):
    ''' Ubuntu Packager '''
    def ks_build(self):
        self.meta_pkgs = ['contrail-install-packages', \
                          'contrail-openstack-storage']
        self.setup_env()
        self.create_pkg_list_file()
        self.make_pkgs()
        self.verify_built_pkgs_exists(skips=self.meta_pkgs)
        self.copy_built_pkg_files(skips=self.meta_pkgs)
        self.create_pkgs_tgz()
        self.create_contrail_pkg(*self.meta_pkgs)
        self.verify_built_pkgs_exists(self.meta_pkgs)
        self.copy_built_pkg_files(self.meta_pkgs, extra_dirs=self.store)
        self.copy_pkg_files(self.base_pkgs)
        self.create_log()
        self.create_git_ids()
