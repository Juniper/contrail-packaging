#!/usr/bin/env python
''' Pull Packages used in ../../build/nightly.py and Create
    a file using the packages list
'''

import sys
import os
sys.path.append(os.path.join(os.getcwd() + '/../../build/'))
import nightly

# Defaults
rpm_list_file = 'rpm_list.txt'
pkg_list = []

packages = nightly.NightlyBuilder.package_list

for each in packages:
    pkg_list += each.pkgs

fid = open(rpm_list_file, 'w')
fid.write("\n".join(pkg_list))
fid.flush()
fid.close()
print "%s file has been created" %rpm_list_file
