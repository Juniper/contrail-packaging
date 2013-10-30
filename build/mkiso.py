
import nightly
import shutil, sys, os, glob, datetime
import argparse, ConfigParser
import platform

class MakeISO (nightly.NightlyBuilder):
    def __init__ (self, args):
        self._plat = platform.platform()
        self.iso_args, self.rpms = None, None
        self.parse_iso_args (args)
        bid = ''
        if self.iso_args.nightly:
            bid = '-B ' + self.iso_args.nightly
        if not os.path.isdir (self.iso_args.repo_dir):
            self.run_shell('mkdir -p %s' %(self.iso_args.repo_dir))    
        # call nightly with
        # -t ~/build/sandbox/target/ -a -i 12 -s ~/build/sandbox/ -w ~/build/sandbox/ctrlplane -m /cs-shared/builder/RPMS/ -C /cs-shared/builder/cache/ -k
        super (MakeISO, self).__init__ (
                '-t %s -a -i %d -s %s -w %s -m %s -C %s -k %s' % (
                    self.iso_args.repo_dir, self.iso_args._id, 
                    self.iso_args.iso_dir, self.iso_args.workspace,
                    self.iso_args.master, self.iso_args.cache, bid))
       
    def replace_rpms (self):
        for f in self.rpms:
            n = self.rpm_get_name (f)
            flist = filter (lambda x: self.rpm_name_check (n, x),
                glob.glob (os.path.join (self.repo_dir, "%s*.rpm" % n)))
            for fx in flist:
                os.remove (fx)
            shutil.copy (f, self.repo_dir)
            self._latest[n] = f
            print 'added %s removed %s' % (f, str (flist))

        print "Create the SOURCES directory."
        self.run_shell('mkdir -p %s' %   (
                       os.path.expanduser('~/rpmbuild/SOURCES')))

        if 'contrail-setup' not in [self.rpm_get_name(rpm) for rpm in self.rpms]:
            rpm_path = '/cs-shared/builder/%s/contrail-install-packages*.rpm' % self.iso_args.nightly
            ctrlplane_root =  self.run_shell('git rev-parse --show-toplevel')
            self.run_shell('mkdir -p %s/tmp && cd %s/tmp && rpm2cpio %s | cpio -i --make-directories' %
                           (self.repo_dir, self.repo_dir, rpm_path)) 
            self.run_shell('cd %s/tmp/opt/contrail/ && mv contrail_installer.tgz %s' % 
                           (self.repo_dir, ctrlplane_root))
            self.run_shell('rm -rf %s/tmp' % self.repo_dir)

    def parse_iso_args (self, args):
        ''' cli args in a flat string '''
        conf_parser = argparse.ArgumentParser(add_help = False)
        
        conf_parser.add_argument("-c", "--conf_file",
                                 help="Specify config file", metavar="FILE")
        args, remaining_argv = conf_parser.parse_known_args(args.split())

        if 'fc17' in self._plat:
            _master = '/cs-shared/builder/RPMS',
            _cache = '/cs-shared/builder/cache',
        if 'el6' in self._plat:
            _master = '/cs-shared/builder/centos64_os/RPMS'
            _cache  = '/cs-shared/builder/centos64_os/cache'
        defaults = {
            'repo_dir' :        os.path.expanduser ('~/rpmbuild/my-repo'),
            'master' :          _master,
            'cache' :           _cache,
            '_id' :             int(datetime.datetime.now().strftime(
                                   "%y%m%d%H%M")),
            'iso_dir' :         os.path.expanduser ('~/rpmbuild/my-myiso'),
            'btag' :            os.environ['USER'],
            'workspace' : 	os.path.realpath (os.path.join (
                                   os.path.dirname (sys.argv[0]), '..', '..')),
            'nightly' :         'LATEST'
        }

        if args.conf_file:
            config = ConfigParser.SafeConfigParser()
            config.read([args.conf_file])
            defaults.update(dict(config.items("DEFAULTS")))

        # Override with CLI options
        # Don't surpress add_help here so it will handle -h
        parser = argparse.ArgumentParser(
            # Inherit options from config_parser
            parents=[conf_parser],
            # print script description with -h/--help
            description=__doc__,
            # Don't mess with format of description
            formatter_class=argparse.RawDescriptionHelpFormatter,
            )
        
        parser.set_defaults(**defaults)

        parser.add_argument('-t', "--target_dir", dest="target_dir",
               help = "target rpm repo")
        parser.add_argument('-a', "--all", action="store_true",
               dest="all", help = "build everything")
        parser.add_argument('-f', "--force", action="store_true",
               dest="force", help = "ignore check for git-id")
        #group = parser.add_mutually_exclusive_group ()
        parser.add_argument('-i', "--id", type=int, 
               dest="_id", help = "build id")
        parser.add_argument('-s', "--store", 
               dest="store", help = "build store id")
        parser.add_argument('-C', "--cache", 
               dest="cache", help = "build store cache")
        parser.add_argument('-m', "--master", 
               dest="master", help = "master to symlink to")
        parser.add_argument('-k', "--skipbuild", action="store_true",
                default=False, dest="skipbuild", help = "skip build")
        parser.add_argument('-b', "--build_tag", 
               dest="btag", help = "build tag for iso")
        parser.add_argument('-w', "--workspace", 
               dest="workspace", help= "Location of ctrlplane source code")
        parser.add_argument('-B', "--build_id", 
               dest="nightly", help= "Bypass to pick by nightly id /cs-shared/builder assumed")
        usage=parser.format_usage()
        parser.usage= usage.rstrip().replace('usage: ','') + " /path/to/rpm /path/to/rpm ..."
        
        self.iso_args, self.rpms = parser.parse_known_args(remaining_argv)
        if 'el6' in self._plat:
            self.iso_args.nightly = 'centos64_os/' + self.iso_args.nightly

if __name__ == '__main__':
    mkiso = MakeISO (' '.join (sys.argv[1:]))
    mkiso.build ()

