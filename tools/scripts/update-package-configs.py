#!/usr/bin/env python
"""
DRAFT VERSION, USE WITH CAUTION

Usage:
./update-package-configs.py /path/to/existing/package-config <update-config>

"""

import os
import re
import sys
from ConfigParser import SafeConfigParser

def get_as_list(elm):
    return [elm] if type(elm) is str and elm else elm

def str_to_list(tstr, force=False):
    ''' convert string separated with comma into a list '''
    tstr = tstr.replace('\n', '')
    sstr = [sstr.strip() for sstr in tstr.split(',')]
    if force:
        return sstr
    else:
        return tstr if tstr.rfind(',') < 0 else sstr
            
def parse_cfg_file(cfg_files, additems=None):
    ''' parse the given config files and return a dictionary
        with sections as keys and its items as dictionary items
    '''
    parsed_dict = {}
    sections = []
    cfg_files = get_as_list(cfg_files)
    for cfg_file in cfg_files:
        parser = SafeConfigParser()
        parsed_files = parser.read(cfg_file)
        if cfg_file not in parsed_files:
            raise RuntimeError('Unable to parse (%s), '
                               'No such file or invalid format' %cfg_file)
        common_sections = list(set(parser.sections()) & \
                               set(sections))
        if len(common_sections) != 0:
            raise RuntimeError('Duplication Section Error while parsing '
                       '(%s): %s' %(cfg_file, "\n".join(common_sections)))
        for sect in parser.sections():
            parsed_dict[sect] = dict((iname, str_to_list(ival)) \
                                   for iname, ival in parser.items(sect))
            if additems != None:
                for item in additems.keys():
                    parsed_dict[sect][item] = copy.deepcopy(additems[item])
        sections.extend(parser.sections())
        del parser
    return parsed_dict

existing_config = sys.argv[1]
new_config = sys.argv[2]
existing_pkgs = parse_cfg_file(existing_config)
new_pkgs = parse_cfg_file(new_config)

outfile = 'update_cmds'
try:
    os.unlink(outfile)
except:
    pass

matched_count = 0
unmatched_count = 0
fid = open(outfile, 'w+')
for newpkg in new_pkgs:
    pkg_file = new_pkgs[newpkg]['file']
    pkg_name = pkg_file.split('_')[0]
    pattern = re.compile('%s_.*' % pkg_name)
    matches = filter(pattern.match, existing_pkgs.keys())
    if len(matches) > 1:
        raise RuntimeError('More than one package with same name found for package (%s):\n(%s)' % (pkg_name, '\n'.join(matches)))
    if len(matches) == 0:
        unmatched_count += 1
        print "WARNING: No match found for package (%s)." % pkg_name
        continue
    #fid.write('crudini --del %s %s\n' % (existing_config, matches[0]))
    fid.write('crudini --set %s %s %s [%s]\n' %(existing_config, matches[0], 'magic_section', newpkg))
    if '%' in new_pkgs[newpkg]['file']:
      filename = new_pkgs[newpkg]['file'].replace('%', '%%')
    else:
      filename = new_pkgs[newpkg]['file']
    fid.write('crudini --set %s %s %s %s\n' %(existing_config, matches[0], 'file', filename))
    fid.write('crudini --set %s %s %s %s\n' %(existing_config, matches[0], 'md5', new_pkgs[newpkg]['md5']))
    fid.write('crudini --set %s %s %s %s\n\n\n' %(existing_config, matches[0], 'source', new_pkgs[newpkg]['source']))
    #fid.write('crudini --set --inplace %s %s %s \"%s\"\n\n\n' %(existing_config, newpkg, 'package_type', ", ".join(existing_pkgs[matches[0]]['package_type'])))
    matched_count += 1
    fid.flush()
fid.close()


print 'Check (%s) file' % outfile
print 'Matched (%s) - Unmatched (%s)' % (matched_count, unmatched_count)

os.system('chmod 755 %s && ./%s' % (outfile, outfile))

section_pattern = '\n\n\[.*\]\n'
magic_pattern = '\nmagic_section = \[(.*)\]'
with open(existing_config, 'r') as fid:
   contents = fid.read()

def update_section(section):
    sect_name = re.match(section_pattern, section)
    new_sect_m = re.search(magic_pattern, section)
    new_sect_name = new_sect_m.groups()[0]
    out1 = section.replace(sect_name.group(), '\n\n[%s]\n' % new_sect_name)
    out2 = re.sub(magic_pattern, '', out1)
    return out2

sections = re.findall(section_pattern, contents)
for index in range(len(sections)):
    try:
        section = sections[index]
        next_section = sections[index+1]
        section_index = contents.index(section)
        next_section_index = contents.index(next_section)
        section_slice = contents[section_index:next_section_index]
    except IndexError:
        section = sections[index]
        section_index = contents.index(section)
        section_slice = contents[section_index:]
    if re.search(magic_pattern, section_slice):
        updated_section = update_section(section_slice)
        #contents = re.sub(section_slice, updated_section, contents)
        contents = contents.replace(section_slice, updated_section)

with open('new_%s' % existing_config, 'w') as fid:
    fid.write(contents)
    fid.write('\n')

