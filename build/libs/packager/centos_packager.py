#!/usr/bin/env python
''' Generic Library for CENTOS Packager scripts'''

import logging

from common import BasePackager

log = logging.getLogger("pkg")
        
class Packager(BasePackager):
    ''' Centos Packager '''
    def exec_steps(self):
        '''Packager Steps'''
        self.setup_env()
        self.create_pkg_list_file()
        self.make_pkgs()
        self.verify_built_pkgs_exists(skips=self.meta_pkg)
        self.copy_built_pkg_files(skips=self.meta_pkg)
        self.createrepo()
        self.create_pkgs_tgz()
        self.create_contrail_pkg()
        self.verify_built_pkgs_exists(self.meta_pkg)
        self.copy_built_pkg_files(self.meta_pkg,
                                  extra_dirs=self.store)
        self.create_comps_xml()
        ks_file = self.create_ks()
        self.createrepo(extraargs='-g comps.xml')
        self.run_pungi(ks_file)
        self.create_log()
        self.create_git_ids()
