#!/usr/bin/env python
#

import github
import lxml.etree as ET
import base64


privates = ["contrail-vnc-private" ]


# Get the existing manifest from github
# and update with sha hashes


# REPLACE WITH YOUR USER ID AND KEY
agh = github.Github('mganley', '<insert key here>')

repo = agh.get_user(login="Juniper").get_repo(name=privates[0])
contentFile = repo.get_contents("default.xml")

# print contentFile.encoding
root = ET.fromstring (base64.b64decode(contentFile.content))


for demo in root.iter('project'):
	reponame = demo.get('name')
	repo = agh.get_user(login="Juniper").get_repo(name=reponame)
	print repo.name
	#print repo.updated_at.strftime("%A, %d. %B %Y %I:%M%p")
	#print "last commit to repo"
	commits=repo.get_commits()[0]
	#print commits.sha
	#print commits.committer.login
	demo.set ('version', commits.sha)
	#print "\n"


# print ET.tostring(root, pretty_print = True)
tree = ET.ElementTree(root)
tree.write ('ec-manifest.xml')


print "Done"

