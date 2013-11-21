#!/usr/bin/env python
#

from lxml import etree as ET
import glob
import re
import subprocess
import shlex

DEBUG=0

ver = ""

modulenames = glob.glob ('*.rpm')


if DEBUG:
	print modulenames

root = ET.Element("ivy-module")
root.set ('version', '2.0')

info = ET.SubElement(root, "info")
info.set ('organisation', 'juniper.net')
info.set ('module', 'Centos64_os')

dep = ET.SubElement(root, "dependencies")

for idx, name in enumerate(modulenames):
	name = name[:-4]
	ver = re.search ('(.*-?.*)-(\d+.*)-(.*)\.(.*$)', name)
	art = ET.SubElement(dep, "dependency")
	art.set ('org', "juniper.net")
	if ver:
		#art.set ('whole', name)
		art.set ('name', str(ver.group(1)))
		revnum = str(ver.group(2)) + "-" + str(ver.group(3)) + "." + str(ver.group(4))
		art.set ('rev', revnum)
	# Now create the individual ivy.xml files to publish
	pub = ET.Element("ivy-module")
	pub.set ('version', '2.0')
	info = ET.SubElement(pub, "info")
	info.set ('organisation', 'juniper.net')
	info.set ('module', str(ver.group(1)))
	pub1 = ET.SubElement(pub, "publications")
	art1 = ET.SubElement(pub1, "artifact")
	art1.set ('ext', "rpm")
	art1.set ('type', "bin")
	if ver:
		#pub1.set ('whole', name)
		art1.set ('name', str(ver.group(1)))
		# art.set ('revision', revnum)
	tree = ET.ElementTree(pub)
	tree.write ('ivytmp.xml')
	
	# Do the publish 

	execstring = "java -jar /opt/apache-ivy-2.3.0/ivy-2.3.0.jar -overwrite -publish ssd-maven -settings ivysettings.xml -ivy ivytmp.xml -revision " + revnum + " -publishpattern \"./[artifact]-" + revnum + ".[ext]\" "

	args = shlex.split(execstring)
	ret = subprocess.call (args)

# print ET.tostring(root, pretty_print = True)
tree = ET.ElementTree(root)
tree.write ('ivy.xml', pretty_print = True)


print "Done"

