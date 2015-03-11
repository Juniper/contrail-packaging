#!/usr/bin/python

doc = """\
Node manager listens to process state change events and 
other flag value change events to provide advanced service 
management functionality.

Description of Node manager options:
--rules: Rules file to use for processing events
--nodetype: Type of node which nodemgr is managing
--discovery_server: IP address of Discovery Server
--discovery_port arg(=5998): Port of Discovery Server

Rules files looks like following:
====================
{ "Rules": [
    {"process_name": "contrail-query-engine", "process_state": "PROCESS_STATE_FATAL", "action": "supervisorctl -s http://localhost:9002 stop contrail-analytics-api"},
    {"process_name": "contrail-query-engine", "process_state": "PROCESS_STATE_STOPPED", "action": "supervisorctl -s http://localhost:9002 stop contrail-analytics-api"},
    {"processname": "contrail-collector", "process_state": "PROCESS_STATE_RUNNING", "action": "/usr/bin/echo collector is starting >> /tmp/log"},
    {"flag_name": "test", "flag_value":"true", "action": "/usr/bin/echo flag test is set true >> /tmp/log.1"}
     ]
}
====================

"""

from gevent import monkey; monkey.patch_all()
import os
import sys
import socket
import subprocess
import json
import time
import datetime
import platform
import select
import gevent
import ConfigParser
import supervisor.xmlrpc
import xmlrpclib

from ConfigParser import NoOptionError

from supervisor import childutils

from pysandesh.sandesh_base import *
from pysandesh.sandesh_session import SandeshWriter
from pysandesh.gen_py.sandesh_trace.ttypes import SandeshTraceRequest 
from sandesh_common.vns.ttypes import Module, NodeType
from sandesh_common.vns.constants import ModuleNames, NodeTypeNames,\
    Module2NodeType, INSTANCE_ID_DEFAULT 
from subprocess import Popen, PIPE
from StringIO import StringIO

def usage():
    print doc
    sys.exit(255)

class EventListenerProtocolNodeMgr(childutils.EventListenerProtocol):
    def wait(self, stdin=sys.stdin, stdout=sys.stdout):
        self.ready(stdout)
        while 1:
            gevent.sleep(1)
            if select.select([sys.stdin,],[],[], 1)[0]:
                line = stdin.readline()
                if line is not None:
                    sys.stderr.write("wokeup and found a line\n")
                    break
                else:
                    sys.stderr.write("wokeup from select just like that\n")
        headers = childutils.get_headers(line)
        payload = stdin.read(int(headers['len']))
        return headers, payload

listener_nodemgr = EventListenerProtocolNodeMgr()

class process_stat:
    def __init__(self, node_type, pname):
        self.start_count = 0
        self.stop_count = 0
        self.exit_count = 0
        self.start_time = ''
        self.exit_time = ''
        self.stop_time = ''
        self.core_file_list = []
        self.last_exit_unexpected = False
        self.process_state = 'PROCESS_STATE_STOPPED'

        # In cases where there can be multiple node status UVEs for a single
        # node type, group the processes that need to go in each UVE. For
        # vrouter, node status UVEs are sent for contrail-vrouter-agent and
        # one each for each instance of contrail-tor-agent.
        # Here, identify the group to which the process belongs. Also, the
        # name associated with the Node Status UVE for this group.
        if (node_type == 'contrail-vrouter'):
            (self.group, self.name) = self.get_vrouter_process_info(pname)
            # sys.stderr.write('Process stat group : ' + self.group + ' name : ' + self.name)
        else:
            self.group = 'default'
            self.name = socket.gethostname()

    # Read the ini files in supervisord_vrouter_files to match against proc_name.
    # From the matching file, get the config file name (argument to contrail-tor-agent).
    # Each contrail-tor-agent instance belongs to a different group, while other
    # processes (contrail-vrouter-agent, contrail-nodemgr and openstack-nova-compute)
    # belong to one group.
    def get_vrouter_process_info(self, proc_name):
        for root, dirs, files in os.walk("/etc/contrail/supervisord_vrouter_files"):
            for file in files:
                if file.endswith(".ini"):
                    filename = '/etc/contrail/supervisord_vrouter_files/' + file
                    data = StringIO('\n'.join(line.strip() for line in open(filename)))
                    Config = ConfigParser.SafeConfigParser()
                    Config.readfp(data)
                    sections = Config.sections()
                    if not sections[0]:
                        sys.stderr.write("Section not present in the ini file : " + filename + "\n")
                        continue
                    name = sections[0].split(':')
                    if len(name) < 2:
                        sys.stderr.write("Incorrect section name in the ini file : " + filename + "\n")
                        continue
                    if name[1] == proc_name:
                        command = Config.get(sections[0], "command")
                        if not command:
                            sys.stderr.write("Command not present in the ini file : " + filename + "\n")
                            continue
                        args = command.split()
                        if (args[0] == '/usr/bin/contrail-tor-agent'):
                            try:
                                index = args.index('--config_file')
                                agent_name = self.get_vrouter_tor_agent_name(args[index + 1])
                                return (proc_name, agent_name)
                            except Exception, err:
                                sys.stderr.write("Tor Agent command does not have config file : " + command + "\n")
        return ('vrouter_group', socket.gethostname())
    #end get_vrouter_process_info

    # Read agent_name from vrouter-tor-agent conf file
    def get_vrouter_tor_agent_name(self, conf_file):
        tor_agent_name = None
        if conf_file:
            try:
                data = StringIO('\n'.join(line.strip() for line in open(conf_file)))
                Config = ConfigParser.SafeConfigParser()
                Config.readfp(data)
            except Exception, err:
                sys.stderr.write("Error reading file : " + conf_file +
                                 " Error : " + str(err) + "\n")
                return tor_agent_name
            tor_agent_name = Config.get("DEFAULT", "agent_name")
        return tor_agent_name
    #end get_vrouter_tor_agent_name

class EventManager:
    rules_data = []
    group_names = []
    process_state_db = {}
    FAIL_STATUS_DUMMY       = 0x1
    FAIL_STATUS_DISK_SPACE  = 0x2
    FAIL_STATUS_SERVER_PORT = 0x4
    FAIL_STATUS_NTP_SYNC    = 0x8

    def __init__(self, rules, node_type='contrail-analytics'):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.rules_data = rules 
        self.max_cores = 4
        self.max_old_cores = 3
        self.max_new_cores = 1
        self.node_type = node_type
        self.all_core_file_list = []
        self.core_dir_modified_time = 0
        self.tick_count = 0
        self.fail_status_bits = 0
        self.prev_fail_status_bits = 1

        if (node_type == 'contrail-vrouter'):
            os_nova_comp = process_stat(node_type, 'openstack-nova-compute')
            (os_nova_comp_state, error_value) = Popen("openstack-status | grep openstack-nova-compute | cut -d ':' -f2", shell=True, stdout=PIPE).communicate()
            os_nova_comp.process_state = os_nova_comp_state.strip()
            if (os_nova_comp.process_state == 'active'):
                os_nova_comp.process_state = 'PROCESS_STATE_RUNNING'
                os_nova_comp.start_time = str(int(time.time()*1000000))
                os_nova_comp.start_count += 1
            if (os_nova_comp.process_state == 'dead'):
                os_nova_comp.process_state = 'PROCESS_STATE_FATAL'
            sys.stderr.write('Openstack Nova Compute status:' + os_nova_comp.process_state + "\n")
            self.process_state_db['openstack-nova-compute'] = os_nova_comp

        # Initialize process data structure
        if (node_type == 'contrail-analytics'):
            self.supervisor_serverurl = "unix:///tmp/supervisord_analytics.sock"
        if (node_type == 'contrail-config'):
            self.supervisor_serverurl = "unix:///tmp/supervisord_config.sock"
        if (node_type == 'contrail-control'):
            self.supervisor_serverurl = "unix:///tmp/supervisord_control.sock"
        if (node_type == 'contrail-vrouter'):
            self.supervisor_serverurl = "unix:///tmp/supervisord_vrouter.sock"
        if (node_type == 'contrail-database'):
            self.supervisor_serverurl = "unix:///tmp/supervisord_database.sock"

        proxy = xmlrpclib.ServerProxy('http://127.0.0.1',
                transport=supervisor.xmlrpc.SupervisorTransport(None, None, serverurl=self.supervisor_serverurl))
        # Add all current processes to make sure nothing misses the radar
        for proc_info in proxy.supervisor.getAllProcessInfo():
            if (proc_info['name'] != proc_info['group']):
                proc_name = proc_info['group']+ ":" + proc_info['name']
            else:
                proc_name = proc_info['name']
            process_stat_ent = process_stat(self.node_type, proc_name)
            process_stat_ent.process_state = "PROCESS_STATE_" + proc_info['statename']
            if (process_stat_ent.process_state  ==
                    'PROCESS_STATE_RUNNING'):
                process_stat_ent.start_time = str(proc_info['start']*1000000)
                process_stat_ent.start_count += 1
            self.process_state_db[proc_name] = process_stat_ent
            sys.stderr.write("\nAdding:" + str(proc_info) + "\n")
    #end __init__

    def send_nodemgr_process_status(self):
        if (self.node_type == 'contrail-config'):
            from cfgm_common.uve.cfgm_cpuinfo.ttypes \
                import NodeStatusUVE, NodeStatus
            from cfgm_common.uve.cfgm_cpuinfo.process_info.ttypes \
                import ProcessStatus, ProcessState
            from cfgm_common.uve.cfgm_cpuinfo.process_info.constants import \
                ProcessStateNames
            module_id = ModuleNames[Module.CONFIG_NODE_MGR]

        if (self.node_type == 'contrail-control'):
            from control_node.control_node.ttypes \
                import NodeStatusUVE, NodeStatus
            from control_node.control_node.process_info.ttypes \
                import ProcessStatus, ProcessState
            from control_node.control_node.process_info.constants import \
                ProcessStateNames
            module_id = ModuleNames[Module.CONTROL_NODE_MGR]

        if (self.node_type == 'contrail-vrouter'):
            from vrouter.vrouter.ttypes import \
                NodeStatusUVE, NodeStatus
            from vrouter.vrouter.process_info.ttypes import \
                ProcessStatus, ProcessState
            from vrouter.vrouter.process_info.constants import \
                ProcessStateNames
            module_id = ModuleNames[Module.COMPUTE_NODE_MGR]

        if (self.node_type == 'contrail-analytics'):
            from analytics.ttypes import \
                NodeStatusUVE, NodeStatus
            from analytics.process_info.ttypes import \
                ProcessStatus, ProcessState
            from analytics.process_info.constants import \
                ProcessStateNames
            module_id = ModuleNames[Module.ANALYTICS_NODE_MGR]

        if (self.node_type == 'contrail-database'):
            from database.sandesh.database.ttypes import \
                NodeStatusUVE, NodeStatus
            from database.sandesh.database.process_info.ttypes import \
                ProcessStatus, ProcessState
            from database.sandesh.database.process_info.constants import \
                ProcessStateNames
            module_id = ModuleNames[Module.DATABASE_NODE_MGR]
 
        if (self.prev_fail_status_bits != self.fail_status_bits):
            self.prev_fail_status_bits = self.fail_status_bits
            fail_status_bits = self.fail_status_bits
            instance_id = INSTANCE_ID_DEFAULT
            if fail_status_bits:
                state = ProcessStateNames[ProcessState.NON_FUNCTIONAL]
                description = ""
                if fail_status_bits & self.FAIL_STATUS_DISK_SPACE:
                    description += "Disk for analytics db is too low, cassandra stopped."
                if fail_status_bits & self.FAIL_STATUS_SERVER_PORT:
                    if description != "":
                        description += " "
                    description += "Cassandra state detected DOWN."
                if fail_status_bits & self.FAIL_STATUS_NTP_SYNC:
                    if description != "":
                        description += " "
                    description += "NTP state unsynchronized."
            else:
                state = ProcessStateNames[ProcessState.FUNCTIONAL]
                description = ''
            process_status = ProcessStatus(module_id = module_id, instance_id = instance_id, state = state,
                description = description)
            process_status_list = []
            process_status_list.append(process_status)
            node_status = NodeStatus(name = socket.gethostname(),
                process_status = process_status_list)
            node_status_uve = NodeStatusUVE(data = node_status)
            sys.stderr.write('Sending UVE:' + str(node_status_uve))
            node_status_uve.send()

    def check_ntp_status(self):
        ntp_status_cmd = 'ntpq -n -c pe | grep "^*"'
        proc = Popen(ntp_status_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        (output, errout) = proc.communicate()
        if proc.returncode != 0:
            self.fail_status_bits |= self.FAIL_STATUS_NTP_SYNC
        else:
            self.fail_status_bits &= ~self.FAIL_STATUS_NTP_SYNC
        self.send_nodemgr_process_status()

    def send_process_state(self, pname, pstate, pheaders, sandeshconn):
        # update process stats
        if pname in self.process_state_db.keys():
            proc_stat = self.process_state_db[pname]
        else:
            proc_stat = process_stat(self.node_type, pname)
            if not proc_stat.group in self.group_names:
                self.group_names.append(proc_stat.group)

        proc_stat.process_state = pstate

        send_uve = False
        if (pstate == 'PROCESS_STATE_RUNNING'):
            proc_stat.start_count += 1
            proc_stat.start_time = str(int(time.time()*1000000))
            send_uve = True

        if (pstate == 'PROCESS_STATE_STOPPED'):
            proc_stat.stop_count += 1
            send_uve = True
            proc_stat.stop_time = str(int(time.time()*1000000))
            proc_stat.last_exit_unexpected = False

        if (pstate == 'PROCESS_STATE_EXITED'):
            proc_stat.exit_count += 1
            send_uve = True
            proc_stat.exit_time = str(int(time.time()*1000000))
            if not(int(pheaders['expected'])):
                self.stderr.write(pname + " with pid:" + pheaders['pid'] + " exited abnormally\n")
                proc_stat.last_exit_unexpected = True
                # check for core file for this exit
                find_command_option = "find /var/crashes -name core.[A-Za-z]*."+ pheaders['pid'] + "*"
                self.stderr.write("find command option for cores:" + find_command_option + "\n")
                (corename, stderr) = Popen(find_command_option.split(), stdout=PIPE).communicate()
                self.stderr.write("core file: " + corename + "\n")

                if ((corename is not None) and (len(corename.rstrip()) >= 1)):
                    # before adding to the core file list make sure that we do not have too many cores
                    sys.stderr.write('core_file_list:'+str(proc_stat.core_file_list)+", self.max_cores:"+str(self.max_cores)+"\n")
                    if (len(proc_stat.core_file_list) == self.max_cores):
                        # get rid of old cores
                        sys.stderr.write('max # of cores reached:' + str(self.max_cores) + "\n")
                        core_files_to_be_deleted = proc_stat.core_file_list[self.max_old_cores:(self.max_cores - self.max_new_cores+1)]
                        sys.stderr.write('deleting core file list:' + str(core_files_to_be_deleted) + "\n")
                        for core_file in core_files_to_be_deleted:
                            sys.stderr.write('deleting core file:' + core_file + "\n")
                            try:
                                os.remove(core_file)
                            except:
                                pass
                        # now delete the list as well
                        del proc_stat.core_file_list[self.max_old_cores:(self.max_cores - self.max_new_cores+1)]
                    # now add the new core to the core file list
                    proc_stat.core_file_list.append(corename.rstrip())
                    sys.stderr.write("# of cores for " + pname + ":" + str(len(proc_stat.core_file_list)) + "\n")

        # update process state database
        self.process_state_db[pname] = proc_stat
        #for key in self.process_state_db:
        #    sys.stderr.write("After:Core file list of " + key + ":" + str(self.process_state_db[key].core_file_list) + "\n")
        f = open('/var/log/contrail/process_state' + self.node_type + ".json", 'w')
        f.write(json.dumps(self.process_state_db, default=lambda obj: obj.__dict__))

        if not(send_uve):
            return

        if (send_uve):
            self.send_process_state_db(sandeshconn, [proc_stat.group])

    # send UVE for updated process state database
    def send_process_state_db(self, sandeshconn, group_names):
        # code to import appropriate sandesh odules based on node-type
        if (self.node_type == 'contrail-config'):
            from cfgm_common.uve.cfgm_cpuinfo.ttypes \
                import NodeStatusUVE, NodeStatus
            from cfgm_common.uve.cfgm_cpuinfo.process_info.ttypes \
                import ProcessInfo

        if (self.node_type == 'contrail-control'):
            from control_node.control_node.ttypes \
                import NodeStatusUVE, NodeStatus
            from control_node.control_node.process_info.ttypes \
                import ProcessInfo

        if (self.node_type == 'contrail-vrouter'):
            from vrouter.vrouter.ttypes import \
                NodeStatusUVE, NodeStatus
            from vrouter.vrouter.process_info.ttypes import \
                ProcessInfo

        if (self.node_type == 'contrail-analytics'):
            from analytics.ttypes import \
                NodeStatusUVE, NodeStatus
            from analytics.process_info.ttypes import \
                ProcessInfo

        if (self.node_type == 'contrail-database'):
            from database.sandesh.database.ttypes import \
                NodeStatusUVE, NodeStatus
            from database.sandesh.database.process_info.ttypes import \
                ProcessInfo

        name = socket.gethostname()
        for group in group_names:
            process_infos = []
            for key in self.process_state_db:
                pstat = self.process_state_db[key]
                if (pstat.group != group):
                    continue
                process_info = ProcessInfo()
                process_info.process_name = key
                process_info.process_state = pstat.process_state
                process_info.start_count = pstat.start_count
                process_info.stop_count = pstat.stop_count
                process_info.exit_count = pstat.exit_count
                process_info.last_start_time = pstat.start_time
                process_info.last_stop_time = pstat.stop_time
                process_info.last_exit_time = pstat.exit_time
                process_info.core_file_list = pstat.core_file_list
                process_infos.append(process_info)
                name = pstat.name

            if not process_infos:
                continue

            # send node UVE
            node_status = NodeStatus()
            node_status.name = name
            node_status.process_info = process_infos
            node_status.all_core_file_list = self.all_core_file_list
            node_status_uve = NodeStatusUVE(data = node_status)
            sys.stderr.write('Sending UVE:' + str(node_status_uve))
            node_status_uve.send()
    # end send_process_state_db

    def database_periodic(self):
        from database.sandesh.database.ttypes import \
            DatabaseUsageStats, DatabaseUsageInfo, DatabaseUsage

        (linux_dist, x, y) = platform.linux_distribution()
        if (linux_dist == 'Ubuntu'):
            (disk_space_used, error_value) = Popen("set `df -Pk \`grep -A 1 'data_file_directories:'  /etc/cassandra/cassandra.yaml | grep '-' | cut -d'-' -f2 \`/ContrailAnalytics | grep %` && echo $3 | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
            (disk_space_available, error_value) = Popen("set `df -Pk \`grep -A 1 'data_file_directories:'  /etc/cassandra/cassandra.yaml | grep '-' | cut -d'-' -f2\`/ContrailAnalytics | grep %` && echo $4  | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
            (analytics_db_size, error_value) = Popen("set `du -skL \`grep -A 1 'data_file_directories:'  /etc/cassandra/cassandra.yaml | grep '-' | cut -d'-' -f2\`/ContrailAnalytics` && echo $1 | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
        else:
            (disk_space_used, error_value) = Popen("set `df -Pk \`grep -A 1 'data_file_directories:'  /etc/cassandra/conf/cassandra.yaml | grep '-' | cut -d'-' -f2 \`/ContrailAnalytics | grep %` && echo $3 | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
            (disk_space_available, error_value) = Popen("set `df -Pk \`grep -A 1 'data_file_directories:'  /etc/cassandra/conf/cassandra.yaml | grep '-' | cut -d'-' -f2\`/ContrailAnalytics | grep %` && echo $4  | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
            (analytics_db_size, error_value) = Popen("set `du -skL \`grep -A 1 'data_file_directories:'  /etc/cassandra/conf/cassandra.yaml | grep '-' | cut -d'-' -f2\`/ContrailAnalytics` && echo $1 | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
        db_stat = DatabaseUsageStats()
        db_info = DatabaseUsageInfo()
        try:
            db_stat.disk_space_used_1k = int(disk_space_used)
            db_stat.disk_space_available_1k = int(disk_space_available)
            db_stat.analytics_db_size_1k = int(analytics_db_size)
        except ValueError:
            sys.stderr.write("Failed to get database usage" + "\n")
        else:
            db_info.name = socket.gethostname()
            db_info.database_usage = db_stat
            db_info.database_usage_stats = [db_stat]
            usage_stat = DatabaseUsage(data=db_info)
            usage_stat.send()
        
        cassandra_cli_cmd = "cassandra-cli --host " + self.hostip + " --batch  < /dev/null | grep 'Connected to:'"
        proc = Popen(cassandra_cli_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        (output, errout) = proc.communicate()
        if proc.returncode != 0:
            self.fail_status_bits |= self.FAIL_STATUS_SERVER_PORT
        else:
            self.fail_status_bits &= ~self.FAIL_STATUS_SERVER_PORT
        self.send_nodemgr_process_status()

    # end database_periodic

    def send_all_core_file(self, sandeshconn):
        stat_command_option = "stat --printf=%Y /var/crashes"
        modified_time = Popen(stat_command_option.split(), stdout=PIPE).communicate()
        if modified_time[0] == self.core_dir_modified_time:
            return
        self.core_dir_modified_time = modified_time[0]
        ls_command_option = "ls /var/crashes"
        (corename, stderr) = Popen(ls_command_option.split(), stdout=PIPE).communicate()
        self.all_core_file_list = corename.split('\n')[0:-1]
        self.send_process_state_db(sandeshconn, self.group_names)

    def runforever(self, sandeshconn, test=False):
    #sys.stderr.write(str(self.rules_data['Rules'])+'\n')
        prev_current_time = int(time.time())    
        while 1:
            gevent.sleep(1)
            # we explicitly use self.stdin, self.stdout, and self.stderr
            # instead of sys.* so we can unit test this code
            headers, payload = listener_nodemgr.wait(self.stdin, self.stdout)

            #self.stderr.write("headers:\n" + str(headers) + '\n')
            #self.stderr.write("payload:\n" + str(payload) + '\n')

            pheaders, pdata = childutils.eventdata(payload+'\n')
            #self.stderr.write("pheaders:\n" + str(pheaders)+'\n')
            #self.stderr.write("pdata:\n" + str(pdata))

            # check for process state change events
            if headers['eventname'].startswith("PROCESS_STATE"):
                self.stderr.write("process:" + pheaders['processname'] + "," + "groupname:" + pheaders['groupname'] + "," + "eventname:" + headers['eventname'] + '\n')
                pname = pheaders['processname']
                if (pheaders['processname'] != pheaders['groupname']):
                    pname = pheaders['groupname'] + ":" + pheaders['processname']
                self.send_process_state(pname, headers['eventname'], pheaders, sandeshconn)
                for rules in self.rules_data['Rules']:
                    if 'processname' in rules:
                        if ((rules['processname'] == pheaders['groupname']) and (rules['process_state'] == headers['eventname'])):
                            self.stderr.write("got a hit with:" + str(rules) + '\n')
                            # do not make async calls
                            try:
                                ret_code = subprocess.call([rules['action']], 
                                    shell=True, stdout=self.stderr, 
                                    stderr=self.stderr)
                            except Exception as e:
                                self.stderr.write('Failed to execute action: ' \
                                    + rules['action'] + ' with err ' + str(e) + '\n')
                            else:
                                if ret_code:
                                    self.stderr.write('Execution of action ' + \
                                        rules['action'] + ' returned err ' + \
                                        str(ret_code) + '\n')
            # check for flag value change events
            if headers['eventname'].startswith("PROCESS_COMMUNICATION"):
                flag_and_value = pdata.partition(":")
                self.stderr.write("Flag:" + flag_and_value[0] + " Value:" + flag_and_value[2] + "\n")
                for rules in self.rules_data['Rules']:
                    if 'flag_name' in rules:
                        #self.stderr.write("evaluating:" + str(rules) + '\n')
                        if ((rules['flag_name'] == flag_and_value[0]) and (rules['flag_value'].strip() == flag_and_value[2].strip())):
                            self.stderr.write("got a hit with:" + str(rules) + '\n')
                            cmd_and_args = ['/usr/bin/bash', '-c' , rules['action']]
                            subprocess.Popen(cmd_and_args)
            
            # do periodic events
            if headers['eventname'].startswith("TICK_60"):
                self.tick_count += 1
                # send other core file
                self.send_all_core_file(sandeshconn)
                # typical ntp sync time is about 3, 4 min - first time, we scan only after 5 min
                if self.tick_count > 5:
                    self.check_ntp_status()
                # check for openstack nova compute status
                if (self.node_type == "contrail-vrouter"):
                    os_nova_comp = self.process_state_db['openstack-nova-compute']
                    (os_nova_comp_state, error_value) = Popen("openstack-status | grep openstack-nova-compute | cut -d ':' -f2", shell=True, stdout=PIPE).communicate()
                    if (os_nova_comp_state.strip() == 'active'):
                        os_nova_comp_state = 'PROCESS_STATE_RUNNING'
                    if (os_nova_comp_state.strip() == 'dead'):
                        os_nova_comp_state = 'PROCESS_STATE_FATAL'
                    if (os_nova_comp_state.strip() == 'inactive'):
                        os_nova_comp_state = 'PROCESS_STATE_STOPPED'
                    if (os_nova_comp.process_state != os_nova_comp_state):
                        os_nova_comp.process_state = os_nova_comp_state.strip()
                        sys.stderr.write('Openstack Nova Compute status changed to:' + os_nova_comp.process_state + "\n")
                        if (os_nova_comp.process_state == 'PROCESS_STATE_RUNNING'):
                            os_nova_comp.start_time = str(int(time.time()*1000000))
                            os_nova_comp.start_count += 1
                        if (os_nova_comp.process_state == 'PROCESS_STATE_FATAL'):
                            os_nova_comp.exit_time = str(int(time.time()*1000000))
                            os_nova_comp.exit_count += 1
                        if (os_nova_comp.process_state == 'PROCESS_STATE_STOPPED'):
                            os_nova_comp.stop_time = str(int(time.time()*1000000))
                            os_nova_comp.stop_count += 1
                        self.process_state_db['openstack-nova-compute'] = os_nova_comp
                        self.send_process_state_db(sandeshconn, 'vrouter_group')
                    else:
                        sys.stderr.write('Openstack Nova Compute status unchanged at:' + os_nova_comp.process_state + "\n")
                        
                    self.process_state_db['openstack-nova-compute'] = os_nova_comp
                elif (self.node_type == 'contrail-database'):
                    self.database_periodic()

                current_time = int(time.time())
                #sys.stderr.write("Time changed %d \n",abs(current_time - prev_current_time)
                if ((abs(current_time - prev_current_time)) > 300):
                    #update all process start_times with the updated time
                    #Compute the elapsed time and subtract them from current time to get updated values
                    sys.stderr.write("Time lapse detected " + str(abs(current_time - prev_current_time)) + "\n")
                    for key in self.process_state_db:
                        pstat = self.process_state_db[key]
                        if pstat.start_time is not '':
                            pstat.start_time = str((int(current_time - (prev_current_time-((int)(pstat.start_time))/1000000)))*1000000)
                        if (pstat.process_state == 'PROCESS_STATE_STOPPED'):
                            if pstat.stop_time is not '':
                                pstat.stop_time = str(int(current_time - (prev_current_time-((int)(pstat.stop_time))/1000000))*1000000)
                        if (pstat.process_state == 'PROCESS_STATE_EXITED'):
                            if pstat.exit_time is not '':
                                pstat.exit_time = str(int(current_time - (prev_current_time-((int)(pstat.exit_time))/1000000))*1000000)
                        # update process state database
                        self.process_state_db[key] = pstat
                    #sys.stderr.write("Info being written"+str(self.process_state_db))
                    try:
                        f = open('/var/log/contrail/process_state' + self.node_type + ".json", 'w')
                        f.write(json.dumps(self.process_state_db, default=lambda obj: obj.__dict__))
                    except:
                        sys.stderr.write("Unable to write json")
                        pass
                    self.send_process_state_db(sandeshconn, self.group_names)
                prev_current_time = int(time.time())

            listener_nodemgr.ok(self.stdout)

def main(argv=sys.argv):
# Parse Arguments
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--rules", 
                        default = '', 
                        help = 'Rules file to use for processing events')
    parser.add_argument("--nodetype", 
                        default = 'contrail-analytics', 
                        help = 'Type of node which nodemgr is managing')
    parser.add_argument("--discovery_server", 
                        default = socket.gethostname(),
                        help = 'IP address of Discovery Server')
    parser.add_argument("--collectors",
                        default = '', 
                        help = 'Collector addresses in format ip1:port1 ip2:port2')
    parser.add_argument("--discovery_port", 
                        type = int,
                        default = 5998, 
                        help = 'Port of Discovery Server')
    try:
        _args = parser.parse_args()
    except:
        usage()
    rule_file = _args.rules
    node_type = _args.nodetype
    discovery_server = _args.discovery_server
    sys.stderr.write("Discovery server: " + discovery_server + "\n")
    discovery_port = _args.discovery_port
    sys.stderr.write("Discovery port: " + str(discovery_port) + "\n")
    if _args.collectors is "":
        collector_addr = []
    else:
        collector_addr = _args.collectors.split()
    sys.stderr.write("Collector address: " + str(collector_addr) + "\n")
#done parsing arguments
    
    if not 'SUPERVISOR_SERVER_URL' in os.environ:
        sys.stderr.write('Node manager must be run as a supervisor event '
                         'listener\n')
        sys.stderr.flush()
        return

    if rule_file == "":
	if (node_type == 'contrail-analytics'):
	    rule_file = "/etc/contrail/supervisord_analytics_files/contrail-analytics.rules"
	if (node_type == 'contrail-config'):
	    rule_file = "/etc/contrail/supervisord_config_files/contrail-config.rules" 
	if (node_type == 'contrail-control'):
	    rule_file = "/etc/contrail/supervisord_control_files/contrail-control.rules"
	if (node_type == 'contrail-vrouter'):
	    rule_file = "/etc/contrail/supervisord_vrouter_files/contrail-vrouter.rules"
	if (node_type == 'contrail-database'):
	    rule_file = "/etc/contrail/supervisord_database_files/contrail-database.rules"
    if rule_file is "":
        sys.stderr.write('Node manager must be invoked with a rules file\n')
        sys.stderr.flush()
        return

    json_file = open(rule_file)
    json_data = json.load(json_file)
    prog = EventManager(json_data, node_type)

    #initialize sandesh
    if (node_type is 'contrail-analytics'):
        # since this is local node, wait for sometime to let collector come up
        import time
	try:
            import discovery.client as client
        except:
            import discoveryclient.client as client
        module = Module.ANALYTICS_NODE_MGR
        module_name = ModuleNames[module]
        node_type = Module2NodeType[module]
        node_type_name = NodeTypeNames[node_type]
        instance_id = INSTANCE_ID_DEFAULT
        #Read collector info from the conf file
        #If conf file is indented ConfigParser cannot read, so stripping the contents
        import ConfigParser
        from StringIO import StringIO
        data = StringIO('\n'.join(line.strip() for line in open('/etc/contrail/contrail-collector.conf')))
        Config = ConfigParser.SafeConfigParser()
        Config.readfp(data)
        if discovery_server == socket.gethostname():
            try:
                discovery_server = Config.get("DISCOVERY", "server")
            except NoOptionError as e:
                sys.stderr.write("ERROR: " + str(e) + '\n')
            #Hack becos of Configparser and the conf file format itself
            try:
                discovery_server = discovery_server[:discovery_server.index('#')].strip()
            except:
                discovery_server = discovery_server.strip()
        try:
            discovery_port = Config.get("DISCOVERY", "port")
        except NoOptionError as e:
            sys.stderr.write("ERROR: " + str(e) + '\n')
        #Hack becos of Configparser and the conf file format itself
        try:
            discovery_port = discovery_port[:discovery_port.index('#')].strip()
        except Exception:
            pass
        _disc= client.DiscoveryClient(discovery_server, discovery_port, module_name)
        # ubuntu packaging is different, figure out where the generated files 
        # are installed
        try:
            from opserver.sandesh.analytics.ttypes import *
            sandesh_pkg_dir = 'opserver.sandesh'
        except:
            from analytics.ttypes import *
            sandesh_pkg_dir = 'analytics'
        sandesh_global.init_generator(module_name, socket.gethostname(), 
            node_type_name, instance_id, collector_addr,
            module_name, 8104, [sandesh_pkg_dir],_disc)
        sandesh_global.set_logging_params(enable_local_log=True)

    if (node_type == 'contrail-config'):
        try:
            import discovery.client as client
        except:
            import discoveryclient.client as client

        # since this may be a local node, wait for sometime to let collector come up
        import time
        # read discovery client info from config file 
        import ConfigParser
        module = Module.CONFIG_NODE_MGR
        module_name = ModuleNames[module]
        node_type = Module2NodeType[module]
        node_type_name = NodeTypeNames[node_type]
        instance_id = INSTANCE_ID_DEFAULT
        Config = ConfigParser.ConfigParser()
        Config.read("/etc/contrail/contrail-api.conf")
        try:
            discovery_server = Config.get("DEFAULTS", "disc_server_ip")
        except NoOptionError as e:
            sys.stderr.write("ERROR: " + str(e) + '\n')
        #Hack becos of Configparser and the conf file format itself
        try:
            discovery_server = discovery_server[:discovery_server.index('#')].strip()
        except:
            discovery_server = discovery_server.strip()
        try:
            discovery_port = Config.get("DEFAULTS", "disc_server_port")
        except NoOptionError as e:
            sys.stderr.write("ERROR: " + str(e) + '\n')
        #Hack becos of Configparser and the conf file format itself
        try:
            discovery_port = discovery_port[:discovery_port.index('#')].strip()
        except Exception:
            pass
        sys.stderr.write("Updated discovery server: " + discovery_server + "\n")
        sys.stderr.write("Updated discovery port: " + str(discovery_port) + "\n")
        _disc= client.DiscoveryClient(discovery_server, discovery_port, module_name)
        sandesh_global.init_generator(module_name, socket.gethostname(), 
            node_type_name, instance_id, collector_addr, module_name, 
            8100, ['cfgm_common.uve'], _disc)
        #sandesh_global.set_logging_params(enable_local_log=True)

    if (node_type == 'contrail-control'):
        try:
            import discovery.client as client
        except:
            import discoveryclient.client as client

        # since this may be a local node, wait for sometime to let collector come up
        import time
        import ConfigParser
        module = Module.CONTROL_NODE_MGR
        module_name = ModuleNames[module]
        node_type = Module2NodeType[module]
        node_type_name = NodeTypeNames[node_type]
        instance_id = INSTANCE_ID_DEFAULT
        from StringIO import StringIO
        data = StringIO('\n'.join(line.strip() for line in open('/etc/contrail/contrail-control.conf')))
        Config = ConfigParser.SafeConfigParser()
        Config.readfp(data)
        if discovery_server == socket.gethostname():
            try:
                discovery_server = Config.get("DISCOVERY", "server")
            except NoOptionError as e:
                sys.stderr.write("ERROR: " + str(e) + '\n')
            try:
                discovery_server = discovery_server[:discovery_server.index('#')].strip()
            except:
                discovery_server = discovery_server.strip()
        try:
            discovery_port = Config.get("DISCOVERY", "port")
        except NoOptionError as e:
            sys.stderr.write("ERROR: " + str(e) + '\n')
        #Hack becos of Configparser and the conf file format itself
        try:
            discovery_port = discovery_port[:discovery_port.index('#')].strip()
        except Exception:
            pass
        _disc= client.DiscoveryClient(discovery_server, discovery_port, module_name)
        sandesh_global.init_generator(module_name, socket.gethostname(), 
            node_type_name, instance_id, collector_addr, module_name, 
            8101, ['control_node.control_node'], _disc)
        #sandesh_global.set_logging_params(enable_local_log=True)

    if (node_type == 'contrail-vrouter'):
        try:
            import discovery.client as client
        except:
            import discoveryclient.client as client

        # since this may be a local node, wait for sometime to let collector come up
        import time
        module = Module.COMPUTE_NODE_MGR
        module_name = ModuleNames[module]
        node_type = Module2NodeType[module]
        node_type_name = NodeTypeNames[node_type]
        instance_id = INSTANCE_ID_DEFAULT
        #Read the discovery server info from the conf file 
        import ConfigParser
        from StringIO import StringIO
        data = StringIO('\n'.join(line.strip() for line in open('/etc/contrail/contrail-vrouter-agent.conf')))
        Config = ConfigParser.SafeConfigParser()
        Config.readfp(data)
        if discovery_server == socket.gethostname():
            try:
                discovery_server = Config.get("DISCOVERY", "server")
            except NoOptionError as e:
                sys.stderr.write("ERROR: " + str(e) + '\n')
            try:
                discovery_server = discovery_server[:discovery_server.index('#')].strip()
            except:
                discovery_server = discovery_server.strip()
        try:
            discovery_port = Config.get("DISCOVERY", "port")
        except NoOptionError as e:
            sys.stderr.write("ERROR: " + str(e) + '\n')
        #Hack becos of Configparser and the conf file format itself
        try:
            discovery_port = discovery_port[:discovery_port.index('#')].strip()
        except Exception:
            pass
        _disc= client.DiscoveryClient(discovery_server, discovery_port, module_name)
        sandesh_global.init_generator(module_name, socket.gethostname(), 
            node_type_name, instance_id, collector_addr, module_name, 
            8102, ['vrouter.vrouter'], _disc)
        #sandesh_global.set_logging_params(enable_local_log=True)
    
    if (node_type == 'contrail-database'):
        try:
            import discovery.client as client
        except:
            import discoveryclient.client as client

        from database.sandesh.database.ttypes import \
            NodeStatusUVE, NodeStatus
        from database.sandesh.database.process_info.ttypes import \
            ProcessInfo, ProcessStatus, ProcessState
        from database.sandesh.database.process_info.constants import \
            ProcessStateNames

        module = Module.DATABASE_NODE_MGR
        module_name = ModuleNames[module]
        node_type = Module2NodeType[module]
        node_type_name = NodeTypeNames[node_type]
        instance_id = INSTANCE_ID_DEFAULT
        #Read the discovery server info from the conf file 
        import ConfigParser
        from StringIO import StringIO
        data = StringIO('\n'.join(line.strip() for line in open('/etc/contrail/contrail-database-nodemgr.conf')))
        Config = ConfigParser.SafeConfigParser()
        Config.readfp(data)
        if discovery_server == socket.gethostname():
            try:
                discovery_server = Config.get("DISCOVERY", "server")
            except NoOptionError as e:
                sys.stderr.write("ERROR: " + str(e) + '\n')
            try:
                discovery_server = discovery_server[:discovery_server.index('#')].strip()
            except:
                discovery_server = discovery_server.strip()
        try:
            discovery_port = Config.get("DISCOVERY", "port")
        except NoOptionError as e:
            sys.stderr.write("ERROR: " + str(e) + '\n')
        #Hack becos of Configparser and the conf file format itself
        try:
            discovery_port = discovery_port[:discovery_port.index('#')].strip()
        except Exception:
            pass
        _disc= client.DiscoveryClient(discovery_server, discovery_port, module_name)
        sandesh_global.init_generator(module_name, socket.gethostname(),
            node_type_name, instance_id, [], module_name,
            8103, ['database.sandesh'], _disc)
        #sandesh_global.set_logging_params(enable_local_log=True)

        try:
            prog.hostip = Config.get("DEFAULT", "hostip")
        except:
            prog.hostip = '127.0.0.1'

        (linux_dist, x, y) = platform.linux_distribution()
        if (linux_dist == 'Ubuntu'):
            (disk_space_used, error_value) = Popen("set `df -Pk \`grep -A 1 'data_file_directories:'  /etc/cassandra/cassandra.yaml | grep '-' | cut -d'-' -f2 \`/ContrailAnalytics | grep %` && echo $3 | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
            (disk_space_available, error_value) = Popen("set `df -Pk \`grep -A 1 'data_file_directories:'  /etc/cassandra/cassandra.yaml | grep '-' | cut -d'-' -f2\`/ContrailAnalytics | grep %` && echo $4  | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
            (analytics_db_size, error_value) = Popen("set `du -skL \`grep -A 1 'data_file_directories:'  /etc/cassandra/cassandra.yaml | grep '-' | cut -d'-' -f2\`/ContrailAnalytics` && echo $1 | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
        else:
            (disk_space_used, error_value) = Popen("set `df -Pk \`grep -A 1 'data_file_directories:'  /etc/cassandra/conf/cassandra.yaml | grep '-' | cut -d'-' -f2 \`/ContrailAnalytics | grep %` && echo $3 | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
            (disk_space_available, error_value) = Popen("set `df -Pk \`grep -A 1 'data_file_directories:'  /etc/cassandra/conf/cassandra.yaml | grep '-' | cut -d'-' -f2\`/ContrailAnalytics | grep %` && echo $4  | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
            (analytics_db_size, error_value) = Popen("set `du -skL \`grep -A 1 'data_file_directories:'  /etc/cassandra/conf/cassandra.yaml | grep '-' | cut -d'-' -f2\`/ContrailAnalytics` && echo $1 | cut -d'%' -f1", shell=True, stdout=PIPE).communicate()
        disk_space_total = int(disk_space_used) + int(disk_space_available)
        try:
            min_disk_opt = Config.get("DEFAULT", "minimum_diskGB")
            min_disk = int(min_disk_opt)
        except:
            min_disk = 0
        if (disk_space_total/(1024*1024) < min_disk):
            from sandesh_common.vns.constants import SERVICE_CONTRAIL_DATABASE

            cmd_str = "service " + SERVICE_CONTRAIL_DATABASE + " stop"
            (ret_value, error_value) = Popen(cmd_str, shell=True, stdout=PIPE).communicate()
            prog.fail_status_bits |= prog.FAIL_STATUS_DISK_SPACE

    # we have to send the first time, as the clients like contrail-status etc.
    # expect functional status from all processes
    prog.send_nodemgr_process_status()
    prog.send_process_state_db(sandesh_global, prog.group_names) # send first list of processes
    gevent.joinall([gevent.spawn(prog.runforever, sandesh_global)])

if __name__ == '__main__':
    main()
