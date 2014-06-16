#!/usr/bin/env python
#

import sys
import github
from lxml import etree as ET
import base64


privates = ["contrail-vnc-private"]
DEBUG = 1

if DEBUG:
    github_user = "Juniper"
else:
    github_user = "Juniper"

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
# Should be the first (and only) argument
if len(sys.argv) < 2:
    print "usage: fix-manifest.py <manifest.xml filename>"
    exit(1)

root = ET.parse(str(sys.argv[1])).getroot()
time = sys.argv[2]
for demo in root.iter('project'):
    reponame = demo.get('name')
    remote = demo.get('remote')
    print reponame, remote
    if remote == "github":
        repo = agh.get_user(login=github_user).get_repo(name=reponame)
        #print repo.updated_at.strftime("%A, %d. %B %Y %I:%M%p")
        dbranch = demo.get('revision')
        if (dbranch):
            githubBranch = repo.get_branch(branch=dbranch)
            commits = githubBranch.commit
        else:
            commits = repo.get_commits()[0]
        if DEBUG:
            print commits.sha
            print commits.commit.committer.date
            print "\n"
        while str(commits.commit.committer.date) > time:
            commits = commits.parents[0]
            if DEBUG:
                print commits.sha
                print commits.commit.committer.date
                print "\n"


        demo.set('revision', commits.sha)

print ET.tostring(root, pretty_print=True)
tree = ET.ElementTree(root)
tree.write('ec-manifest.xml')

print "Done"

