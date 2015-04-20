USE cmon;

set @cid:=1;

INSERT IGNORE INTO cmon_cluster_counters(id, var, enabled)  VALUES (1,'ABORTS','1'),(2,'COMBINED','1'),(3,'COMMITS','1'),(4,'OPERATIONS','1'),(5,'RANGE_SCANS','1'),(6,'READS_ALL','1'),(7,'SIMPLE_READS','1'),(8,'TABLE_SCANS','1'),(9,'TRANSACTIONS','1'),(10,'WRITES','1');

DELETE FROM cmon_mysql_counters;
DELETE FROM cmon_mysql_graphs;
DELETE FROM cluster_event_types;
INSERT IGNORE INTO `cluster_event_types` VALUES ('ArbitResult'),('ArbitState'),('CM_REGCONF'),('CM_REGREF'),('CommunicationClosed'),('CommunicationOpened'),('Connected'),('ConnectedApiVersion'),('CopyDict'),('CopyFragDone'),('CopyFragsCompleted'),('CopyFragsStared'),('Disconnected'),('FIND_NEIGHBOURS'),('GCP_TakeoverCompleted'),('GCP_TakeoverStarted'),('LCP_TakeoverCompleted'),('LCP_TakeoverStarted'),('LocalCheckpointCompleted'),('LocalCheckpointStarted'),('NodeFailCompleted'),('NODE_FAILREP'),('StartCompleted'),('StartPhaseCompleted'),('StartREDOLog'),('StopCompleted'),('StopStarted');
INSERT IGNORE INTO `cluster_severity_types` VALUES ('ALERT'),('CRITICAL'),('DEBUG'),('ERROR'),('INFO'),('WARNING');

INSERT IGNORE INTO `cmon_mysql_graphs` VALUES (1,'ABORTED_CLIENTS'),(2,'ABORTED_CONNECTS'),(3,'QUERIES'),(4,'OPENED_TABLES'),(7,'CREATED_TMP_DISK_TABLES'),(8,'CREATED_TMP_TABLES'),(5,'THREADS_CONNECTED'),(6,'THREADS_RUNNING'); 
INSERT IGNORE INTO `cmon_cluster_graphs` VALUES (1,'COMBINED'),(5,'COMMITS'),(2,'OPERATIONS'),(4,'RANGE_SCANS'),(6,'READS_ALL'),(8,'SIMPLE_READS'),(3,'TRANSACTIONS'),(7,'WRITES');


delete from mysql_states;

INSERT IGNORE INTO mysql_states(id,name,description) VALUES(0, 'MYSQL_OK', 'OK');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(1, 'MYSQL_DISCONNECTED', 'MySQL Server is disconnected');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(2, 'MYSQL_REPL_LAG', 'Replication is lagging behind');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(3, 'MYSQL_REPL_FAILED', 'Replication is stopped');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(4, 'MYSQL_REPL_ACTION_NEEDED', 'Check IO and SQL Thread, slave may have to be rebuilt.');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(5, 'MYSQL_REPL_REBUILD_NEEDED', 'Rebuild slave is needed');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(6, 'MYSQL_REPL_REBUILDING', 'Rebuilding slave');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(7, 'MYSQL_REPL_REBUILD_FAILED', 'Rebuild slave failed - try again');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(8, 'MYSQL_REPL_FASTFORWARD', 'Skipping ahead to a good position - data will be lost');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(9, 'MYSQL_REPL_USER_STOPPED', 'User initiated stop of slave');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(10, 'MYSQL_REPL_RESUME_SLAVE', 'Slave can be resumed now');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(11, 'MYSQL_GALERA_FAILED', 'Galera failed on node');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(12, 'MYSQL_GALERA_NODE_RECOVERY', 'Node recovery needed<br/>giving Galera a chance first');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(13, 'MYSQL_GALERA_CLUSTER_RECOVERY', 'Cluster recovery needed<br/>giving Galera a chance first<br/>Check /var/log/cmon.log');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(14, 'MYSQL_GALERA_READ_ONLY', 'Read-only');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(15, 'MYSQL_GALERA_NODE_RECOVERING', 'Galera node recovery in progress');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(16, 'MYSQL_GALERA_CLUSTER_RECOVERING', 'Galera cluster recovery in progress');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(17, 'MYSQL_GALERA_USER_SHUTDOWN', 'User initiated shutdown');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(18, 'MYSQL_CLUSTER_NOT_CONNECTED', 'Node not connected to NDB!<br/>Check http://support.severalnines.com/entries/21854907-node-not-connected-to-ndb for suggestions.');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(19, 'MYSQL_USER_SHUTDOWN', 'User initiated shutdown');
INSERT IGNORE INTO mysql_states(id,name,description) VALUES(20, 'MYSQL_GALERA_BLOCKED', 'Galera recovery blocked');


INSERT IGNORE INTO cmon_daily_job(cid,exectime,command) VALUES(1,'02:00',0);


INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'CPU_WARNING', '80');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'CPU_CRITICAL', '90');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'RAM_WARNING', '80');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'RAM_CRITICAL', '90');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'DISKSPACE_WARNING', '80');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'DISKSPACE_CRITICAL', '90');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'SWAPSPACE_WARNING', '5');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'SWAPSPACE_CRITICAL', '20');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'MYSQLMEMORY_WARNING', '80');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'MYSQLMEMORY_CRITICAL', '90');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'CMON_USE_MAIL', '0');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'CMON_MAIL_SENDER', '');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'ENABLE_DBGROWTH', '1');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'HTTP_PROXY', '');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'CCBINDIR', '');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'CMON_DB', 'cmon');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'SSH_OPTS_BG', '');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'MULTI_TENANT', 'yes');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'MYSQL_REPLICATION_AUTO_FAILOVER', '1');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'BACKUP_RETENTION', '7');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'GALERA_PORT', '4567');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'QUERY_SAMPLE_INTERVAL', '1');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'LONG_QUERY_TIME', '0.5');
INSERT IGNORE INTO cmon_configuration(cid, param, value) VALUES(@cid,'LOG_QUERIES_NOT_USING_INDEXES', '1');

