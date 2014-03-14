#!/usr/bin/env python
''' Generic Library for RedHat Packager scripts'''

import logging

from common import BasePackager

log = logging.getLogger("pkg.%s" %__name__)


class Packager(BasePackager):
    ''' Redhat Packager '''
    def ks_build(self):
        self.setup_env()
        self.create_pkg_list_file()
        self.make_pkgs()
        self.verify_built_pkgs_exists(skips=['contrail-install-packages'])
        self.copy_built_pkg_files(skips=['contrail-install-packages'])
        self.createrepo()
        self.create_tgz(self.pkgs_tgz, self.pkg_repo)
        self.create_contrail_pkg()
        self.verify_built_pkgs_exists(['contrail-install-packages'])        
        self.copy_built_pkg_files(extra_dirs=self.store, ['contrail-install-packages'])
        self.copy_pkg_files(self.base_pkgs)
        self.create_comps_xml()
        ks_file = self.create_ks()
        self.createrepo(extraargs='-g comps.xml')
        self.run_pungi(ks_file)
        self.create_log()
        self.create_git_ids()
