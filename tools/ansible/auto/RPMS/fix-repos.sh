#!/bin/sh

# Get rid of all the repos definitions.   Soon to be replaced by ones 
# we install
cd /etc/yum.repos.d
mkdir sav
mv *.repo sav
yum clean all

