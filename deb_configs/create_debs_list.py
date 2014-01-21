#!/usr/bin/env python
"""
Copyright (c) 2014, Juniper Networks, Inc.
All rights reserved.
Author : Michael Ganley

Build wrapper script.
"""

''' Create Debs list '''

import os
import os.path
import sys
from ConfigParser import SafeConfigParser

pkgs_file = os.path.join('tools', 'packaging', 'deb_configs', 'contrail.cfg')
deblist_file = sys.argv[1]
if deblist_file == None:
    deblist_file = os.path.abspath('debs_list.txt')

def create_contrail_support_files():
    parser = SafeConfigParser()
    if os.path.isfile(pkgs_file) and os.lstat(pkgs_file).st_size != 0:
        parser.read(pkgs_file)
        print 'INFO: Creating %s file' %deblist_file
        with open(deblist_file, 'w') as fid:
            fid.writelines('\n'.join(sorted(parser.sections())))
    else:
        print 'ERROR: Unable to retrieve packages list from cfg file (%s)' %pkgs_file
        raise IOError('Packages cfg file (%s) is either not present or empty' %pkgs_file)

if __name__ == '__main__':
    create_contrail_support_files()
