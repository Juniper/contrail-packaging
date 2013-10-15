#!/usr/bin/env python
#

import github
from lxml import etree as ET
import base64


privates = ["contrail-vnc-private" ]
DEBUG=0


# Get the existing manifest from github
# and update with sha hashes


# REPLACE WITH YOUR USER ID AND KEY
agh = github.Github('mganley', '83236c3a4678abeda0cf2235552cac8a6b75ab9f')

repo = agh.get_user(login="Juniper").get_repo(name=privates[0])
contentFile = repo.get_contents("default.xml")

# print contentFile.encoding
if DEBUG:
	root = ET.parse("default.xml").getroot()
else:
	root = ET.fromstring (base64.b64decode(contentFile.content))


for demo in root.iter('project'):
	reponame = demo.get('name')
	remote = demo.get('remote')
	print reponame, remote
	if remote == "github" :
		repo = agh.get_user(login="Juniper").get_repo(name=reponame)
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

