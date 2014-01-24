###### DEFAULT CONFIG FILE FOR PACKAGER #######

import os
import sys
import random
import tempfile
import platform
import getpass
import time
import logging
import logging.config
import multiprocessing

PACKAGER_ROOT    = os.path.abspath('.')
PACKAGER_CONFIGS = os.path.abspath('pkg_configs')
PACKAGER_LOGGER  = os.path.abspath('logger')

def get_uniq_id(prefix, retries=30):
     ''' Get an Unique ID based on prefix_id directory availability '''
     notfound = 0
     while retries > 0:
         id = random.randint(10, 1000)
         if not os.path.isdir(os.path.abspath('%s_%s' %(prefix, id))):
             notfound = 0
             break
         else:
             notfound = 1
             retries -= 1
         if notfound:
             raise IOError('Unable to find an unique name based on dir availability')
     return id

def create_dir(dirname):
    os.makedirs(dirname)
    return dirname

timestamp     = time.strftime('%m%d%y%H%M%S')
usrname       = getpass.getuser()
usrhome       = os.path.expanduser('~')
id            = get_uniq_id(os.path.join(usrhome, usrname))
udir          = os.path.join(usrhome, '%s_%s' %(usrname, id))
cwd           = os.path.abspath('.')
dist          = platform.dist()
logname       = 'pkg_{id}_%s.log' %timestamp
logfile       = os.path.join(cwd, 'logs', logname)
stream        = sys.stdout
base_pkg_file = 'base_' + dist[0] + '_%s_pkgs.cfg' %dist[1]
deps_pkg_file = 'depends_' + dist[0] + '_%s_pkgs.cfg' %dist[1]
log_cfg_file  = os.path.join(PACKAGER_LOGGER, 'logging.cfg')
git_lrepo     = os.path.join(usrhome, '%s_{id}' %usrname, 'local_repo')
gitdir        = os.path.join(PACKAGER_ROOT, '.git')
pkg_types     = {'ubuntu': 'deb', 'centos': 'rpm', 'redhat': 'rpm', 'fedora': 'rpm'}
pkg_type      = pkg_types[dist[0]]

gitconfig     = '''
[color]
    ui = auto
[branch]
    autosetuprebase = always
[user]
    name  = {user}
    email = {user}@juniper.net
'''.lstrip('\n').format(user=usrname)

comps_xml_template = '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE comps PUBLIC "-//Red Hat, Inc.//DTD Comps info//EN" "comps.dtd">
<comps>
        
  <group>
   <id>core</id>
   <default>false</default>
   <uservisible>true</uservisible>
   <display_order>1024</display_order>
   <name>core</name>
   <description>Contrail Distro </description>
    <packagelist>
{pkgsinfo}
      <packagereq type="mandatory">contrail-install-packages</packagereq>
    </packagelist>
  </group>
</comps>'''.strip('\n')
    
CLI_DEFAULTS = {
    'skip_build'             : False,
    'jenkins'                : False,
    'install_local_repo'     : False,
    'id'                     : id,
    'build_name'             : usrname,
    'store'                  : os.path.join(usrhome, '%s_{id}' %usrname, 'store'), 
    'pkg_dirs'               : None,
    'cont_pkg_dirs'          : None,
    'base_pkg_files'         : os.path.join(PACKAGER_CONFIGS, dist[0], base_pkg_file),
    'deps_pkg_files'         : os.path.join(PACKAGER_CONFIGS, dist[0], deps_pkg_file),
    'cont_pkg_files'         : os.path.join(PACKAGER_CONFIGS, 'contrail', '%s_packages.cfg' %dist[0]),
    'no_parallel_make'       : False,
    'fab_env'                : None,
    'exec'                   : None,
    'git_local_repo'         : None, #updated based on install_git_repo and git_lrepo var
    'git_url'                : 'git@github.com:Juniper/contrail-vnc-private',
    'git_fetch_pkgdirs'      : ['third_party', os.path.join('distro', 'third_party')],
    'log_level'              : 'DEBUG',
    'make_targets'           : ['thirdparty-all', 'openstack-all', 'contrail-all'],
    'make_targets_file'      : None,    
    'no_sync_repo'           : False,
}

NAMEMAP = {
    '$WRAPPER$'            : r'(<<([^>>]*)>>)+',
    'TIMESTAMP'            : timestamp,
    'USER'                 : usrname,
    'GIT_LOCAL_REPO'       : '-RUNTIME-',
    'RECOMMEND_POOL_SIZE'  : '%s' %multiprocessing.cpu_count(),
}
