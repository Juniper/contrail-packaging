#!/usr/bin/env python
#
#

from lxml import etree as ET
import base64


xenRepos = ["contrail-build", "contrail-vrouter", "contrail-third-party", 
	    "contrail-controller", "contrail-packaging"]

DEBUG = 0

root = ET.parse("manifest.xml").getroot()

for demo in root.iter('project'):
    reponame = demo.get('name')
    remote = demo.get('remote')
    if DEBUG:
        print reponame, remote

    found = 0
    for item in xenRepos:
        if reponame == item:
            found = 1

    if not found:
        demo.getparent().remove(demo)

print ET.tostring(root, pretty_print=True)
tree = ET.ElementTree(root)
tree.write('xen-manifest.xml')

print "Done"

