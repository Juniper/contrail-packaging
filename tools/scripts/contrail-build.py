#!/usr/bin/env /usr/bin/python
"""
Copyright (c) 2013, Juniper Networks, Inc.
All rights reserved.
Author : Michael Ganley

Build wrapper script.
"""

import argparse
import os
import sys
import shlex
import subprocess
import shutil


manifestRealPath = ""



class ContrailBuild(object):
    """ contrailBuild class to parse and execute the build commands """

    def __init__(self, options):
        global manifestRealPath
        self.opt = options
        if self.opt.manifest_file:
            manifestRealPath = os.path.realpath(self.opt.manifest_file)
            if self.opt.build_num:
                print 'Error: Cannot specify both a build number and manifest file to create sandbox'
                sys.exit(1)
            if self.opt.branch_name:
                print 'Error: Cannot specify both a branch name and manifest file'
                sys.exit(1)

        if not self.opt.arch_type == 'centos64_os':
            print 'Error: Only centos64_os is only architecture that is currently supported'
            sys.exit(1)

        required_commands = ["package", "all", "iso"]
        if self.opt.command in required_commands:
            if not self.opt.build_num:
                if not self.opt.tag_name:
                    print "Error: Package/Iso commands need either build number or tag"
                    sys.exit(1)

        """ Make sure we are in sandbox """
        if self.opt.command != 'sandbox':
            if not os.path.exists(".repo"):
                path = str(self.opt.sandbox_name)
                path += '/.repo'
                if not os.path.exists(path):
                    print 'Error cannot find sandbox'
                    sys.exit(1)
                os.chdir (self.opt.sandbox_name)


    def sandbox(self):
        """
        Now finish up with the repo sync command
        """
        if DEBUG:
            print 'sandbox got called'

        """
        Create the sandbox and do the repo init
        """
        print "Creating Sandbox "
        command = 'repo init -u '
        command += str(self.opt.manifest_url)
        if self.opt.branch_name:
            command += " -m manifest-"
            command += str(self.opt.branch_name)
            command += ".xml"
        if not os.path.exists(self.opt.sandbox_name):
            os.mkdir (self.opt.sandbox_name)
        os.chdir (self.opt.sandbox_name)
        execute(command,ignore_errors=False)

        """
        Manipulate the manifest.xml file based on the build number if there
        """

        if self.opt.manifest_file:
            print "Using supplied manifest file"
            shutil.copyfile (manifestRealPath, ".repo/manifest.xml")

        if self.opt.build_num:
            print "Using supplied build number"
            buildArchive = '/volume/junosv-storage01/contrail/'
            if not os.path.isdir(buildArchive):
	        print "Can't find the build archive:", buildArchive
                sys.exit(1)
            if self.opt.branch_name:
                buildArchive += str(self.opt.branch_name)
                buildArchive += '/'
            else:
                buildArchive += 'mainline/'
            buildArchive += str(self.opt.build_num)
            buildArchive += '/'
            buildArchive += "manifest.xml"
            shutil.copyfile (buildArchive, ".repo/manifest.xml")

        print "Syncing repositories.... this could take some time"
        print "log is checkout.log"
        f = open("checkout.log", mode='w')
        data = execute("repo sync", ignore_errors=False)
        f.write (str(data))
        f.close()



    def build(self):
        if DEBUG:
            print 'build got called'

        print "Fetching third party libraries"
        print "Log is fetch.log"

        f = open("fetch.log", mode='w')

        data = execute("python third_party/fetch_packages.py", ignore_errors=False)
        f.write (str(data))

        data = execute("python distro/third_party/fetch_packages.py", ignore_errors=False)
        f.write (str(data))
        f.close()

        print "Running top level build"
        print "Log is build.log"

        f = open("build.log", mode='w')
        data = execute("scons", ignore_errors=False)
        f.write (str(data))
        f.close()

    def package(self):
        if DEBUG:
            print "Package got called"

        current_dir = os.getcwd()

        command = "make TAG="
        if self.opt.build_num:
            command += str(self.opt.build_num)
        else:
            command += str(self.opt.tag_name)
        command += " all"

        f = open("package.log", mode='w')
        print "log is package.log"
        print "Packaging Contrail.... this could take awhile"
        os.chdir ('tools/packaging/common/rpm')
        data = execute(command, ignore_errors=False)
        f.write (str(data))

        print "Packaging OpenStack"
        os.chdir (current_dir)
        os.chdir ('tools/packaging/openstack')
        data = execute(command, ignore_errors=False)
        f.write (str(data))

        print "Packaging Third Pary"
        os.chdir (current_dir)
        os.chdir ('tools/packaging/third_party')
        data = execute(command, ignore_errors=False)
        f.write (str(data))
        f.close()

def execute(command, ignore_errors=False):
    """ Function to execute shell command and return the output """

    if DEBUG:
        print 'DEBUG: %s' % (command)
    pipe = subprocess.Popen(shlex.split(command),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            close_fds=True)

    data = pipe.stdout.read()
    rc = pipe.wait()
    cwd = os.getcwd()
    if rc and not ignore_errors:
        print 'Error : Working directory : %s' % (cwd)
        print 'Error : Failed to execute command: %s\n%s' % (command, data)
        sys.exit(1)
    return data.strip()

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def parse_options(args):
    """ Parse command line arguments """
    parser = argparse.ArgumentParser(description='Contrail build wrapper script ')

    parser.add_argument('-v', '--verbose', dest='debug', action='store_true',
                        help='Enable verbose mode')

    parser.add_argument('-m', '--manifest', nargs='?', dest='manifest_file',
                        help='Manifest Filename,')

    parser.add_argument('-s', '--sandbox', nargs='?', dest='sandbox_name',
                        default='sandbox',
                        help='New directory name for the sandbox, default : %(default)s')

    parser.add_argument('-u', '--url', dest='manifest_url',
                        default='git@github.com:Juniper/contrail-vnc-private',
                        help='Repository URL to download the manifest file, default : %(default)s')

    parser.add_argument('-n', '--number', nargs='?', dest='build_num',
                        help='Build number to get manifest from')

    parser.add_argument('-b', '--branch', nargs='?', dest='branch_name',
                        help='Branch to use to fetch manifest file')

    parser.add_argument('-t', '--tag', nargs='?', dest='tag_name',
                        help='Tag to use when creating packages')

    parser.add_argument('-a', '--arch', nargs='?', dest='arch_type',
                        default='centos64_os',
                        help='Branch to use to fetch manifest file')

    subparsers = parser.add_subparsers(title='ContrailBuild Commands',
                                       description='Select one command',
                                       dest='command')

    parser_sandbox = subparsers.add_parser('sandbox',
                                           description='Creates sandbox from either manifest file or build number')
    parser_build = subparsers.add_parser('build', description='Do a build in the sandbox created')
    parser_package = subparsers.add_parser('package', description='Package build')
    parser_all = subparsers.add_parser('all', description='Perform all the functions: sandbox, build, package')

    opt = parser.parse_args(args)
    return opt


if __name__ == '__main__':
    options = parse_options(sys.argv[1:])
    DEBUG = options.debug
    build = ContrailBuild(options)

    """ Test to make sure all our commands exist """

	
    if not cmd_exists("git"):
        print "Missing git command"
	sys.exit(1)
 
    if not cmd_exists("repo"):
        print "Missing git command"
	sys.exit(1)

    if not cmd_exists("scons"):
	print "Missing scons command"
	sys.exit(1)

    if build.opt.command == 'sandbox':
        build.sandbox()
        sys.exit(0)

    if build.opt.command == 'build':
        build.build()
        sys.exit(0)

    if build.opt.command == 'package':
        build.package()
        sys.exit(0)

    if build.opt.command == 'all':
        build.sandbox()
        build.build()
        build.package()
        sys.exit(0)

    print "Unknown command: ", build.opt.command
    sys.exit(1)
