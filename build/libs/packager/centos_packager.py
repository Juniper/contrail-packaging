#!/usr/bin/env python
''' Generic Library for CENTOS Packager scripts'''

import logging
from common import BasePackager, TestExecution

log = logging.getLogger("pkg.%s" %__name__)


class Packager(BasePackager):
    def ks_build(self):
        self.create_git_repo()
        self.setup_env()
        self.make_pkgs()
        self.verify_built_pkgs_exists(skips=['contrail-install-packages'])
        self.copy_built_pkg_files(self.pkg_repo, skips=['contrail-install-packages'])
        self.createrepo(self.pkg_repo)
        self.create_tgz(self.pkgs_tgz, self.pkg_repo)
        self.create_contrail_pkg()
        self.verify_built_pkgs_exists(['contrail-install-packages'])        
        self.copy_built_pkg_files(self.pkg_repo, ['contrail-install-packages'])
        self.copy_pkg_files(self.base_pkgs, self.pkg_repo)
        self.create_comps_xml()
        ks_file = self.create_ks()
        self.createrepo (self.pkg_repo, extraargs='-g comps.xml')
        self.run_pungi(ks_file)
        log.info('Packaging Complete!')
        if self.fabenv:
            self.test_run()
