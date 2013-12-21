#!/usr/bin/env python
#

import github
from lxml import etree as ET
import base64


privates = ["contrail-vnc-private" ]
DEBUG=0


if DEBUG:
    github_user="mganley"
else:
    github_user="Juniper"

# Get the existing manifest from github
# and update with sha hashes


# REPLACE WITH YOUR USER ID AND KEY

agh = github.Github('mganley', '83236c3a4678abeda0cf2235552cac8a6b75ab9f')


# repo = agh.get_user(login=github_user).get_repo(name=privates[0])

#
# Don't want to fetch the manifest directly.   Will do that via 
# repo init -u 
# We will limit this tool to just manipulating the manifest.xml file
# contentFile = repo.get_contents("default.xml")
# print contentFile.encoding

# Now parse the manifest.xml file.
root = ET.parse("manifest.xml").getroot()

for demo in root.iter('project'):
	reponame = demo.get('name')
	remote = demo.get('remote')
	print reponame, remote
	if remote == "github" :
		repo = agh.get_user(login=github_user).get_repo(name=reponame)
		print repo.name
		#print repo.updated_at.strftime("%A, %d. %B %Y %I:%M%p")
		dbranch = demo.get('revision')
		if (dbranch) :
			githubBranch = repo.get_branch(branch=dbranch)
			commits=githubBranch.commit
		else:
			commits=repo.get_commits()[0]
			#print commits.sha
			#print commits.committer.login
			#print "\n"
		demo.set ('revision', commits.sha)

print ET.tostring(root, pretty_print = True)
tree = ET.ElementTree(root)
tree.write ('ec-manifest.xml')


print "Done"

