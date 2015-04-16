CREATE DATABASE IF NOT EXISTS cmon CHARACTER SET latin1;
USE cmon;

DROP PROCEDURE IF EXISTS sp_cmon_deletehost;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deletehost(_cid integer, _hostid integer)
SQL SECURITY INVOKER
BEGIN
   DELETE FROM cmon_log WHERE cid=_cid AND hostid=_hostid;
   DELETE FROM alarm_hosts WHERE cid=_cid AND hostid=_hostid;
   DELETE FROM cluster_configuration WHERE cid=_cid AND hid=_hostid;	
   DELETE FROM cpu_info WHERE cid=_cid AND hostid=_hostid;
   DELETE FROM cpu_stats WHERE cid=_cid AND id=_hostid;
   DELETE FROM cpu_stats_history WHERE cid=_cid AND id=_hostid;
   DELETE FROM disk_stats WHERE cid=_cid AND id=_hostid;
   DELETE FROM disk_stats_history WHERE cid=_cid AND id=_hostid;
   DELETE FROM net_stats WHERE cid=_cid AND hostid=_hostid;
   DELETE FROM net_stats_history WHERE cid=_cid AND id=_hostid;
   DELETE FROM ram_stats WHERE cid=_cid AND id=_hostid;
   DELETE FROM ram_stats_history WHERE cid=_cid AND id=_hostid;
   DELETE FROM galera_status WHERE cid=_cid AND hostid=_hostid;
   DELETE FROM hosts WHERE cid=_cid AND id=_hostid;
   DELETE FROM processes WHERE cid=_cid and hid=_hostid;
   DELETE FROM top WHERE cid=_cid AND hostid=_hostid;
   CALL sp_cmon_deletemysql(_cid, _hostid);
END;
||
DELIMITER ;



DROP PROCEDURE IF EXISTS sp_cmon_deletemysql;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deletemysql(_cid integer, _hostid integer)
SQL SECURITY INVOKER
BEGIN
   DECLARE _nodeid INTEGER;	
   SELECT nodeid INTO _nodeid FROM mysql_server m WHERE m.cid=_cid AND m.id=_hostid;
   DELETE FROM processes WHERE cid=_cid and hid=_hostid and process='mysqld_safe';
   DELETE FROM alarm WHERE cid=_cid AND nodeid=_hostid;	
   DELETE FROM cluster_configuration WHERE cid=_cid AND hid=_hostid AND filename='my.cnf';	
   DELETE FROM mysql_slave_status WHERE cid=_cid AND serverid in (SELECT serverid FROM mysql_server WHERE cid=_cid AND id=_hostid);
   DELETE FROM galera_status WHERE cid=_cid AND hostid=_hostid;
   DELETE FROM mysql_advisor WHERE cid=_cid AND nodeid=_hostid;
   DELETE FROM mysql_memory_usage WHERE cid=_cid AND nodeid=_hostid;
   DELETE FROM mysql_advisor_history WHERE cid=_cid AND nodeid=_nodeid;
   DELETE FROM mysql_advisor_reco WHERE cid=_cid AND nodeid=_nodeid;	
   DELETE FROM mysql_performance_results WHERE cid=_cid AND hostid=_nodeid;
   DELETE FROM mysql_processlist WHERE cid=_cid AND id=_nodeid;
   DELETE FROM mysql_query_histogram WHERE cid=_cid AND id=_nodeid;
   DELETE FROM mysql_repl_link WHERE cid=_cid and hostid=_nodeid;
   DELETE FROM mysql_slow_queries WHERE cid=_cid AND id=_nodeid;
   DELETE FROM mysql_statistics WHERE cid=_cid AND id=_nodeid;
   DELETE FROM mysql_statistics_hour WHERE cid=_cid AND id=_nodeid;
   DELETE FROM mysql_statistics_history WHERE cid=_cid AND id=_nodeid;
   DELETE FROM mysql_variables WHERE cid=_cid AND id=_nodeid;
   DELETE FROM mysql_server WHERE cid=_cid AND id=_hostid;
END;
||
DELIMITER ;



DROP PROCEDURE IF EXISTS sp_cmon_movehost;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_movehost(_cid integer, _hostid integer)
SQL SECURITY INVOKER
BEGIN	    
   UPDATE hosts SET cid=_cid WHERE id=_hostid;
   UPDATE processes SET cid=_cid and hid=_hostid;
/*   UPDATE top SET cid=_cid WHERE hostid=_hostid;*/
   DELETE FROM top WHERE hostid=_hostid;
   UPDATE alarm_hosts SET cid=_cid WHERE hostid=_hostid;
   UPDATE cluster_configuration SET cid=_cid WHERE hid=_hostid;	
   UPDATE cpu_info SET cid=_cid WHERE hostid=_hostid;
   UPDATE cpu_stats SET cid=_cid WHERE id=_hostid;
   UPDATE cpu_stats_history SET cid=_cid WHERE id=_hostid;
   UPDATE disk_stats SET cid=_cid WHERE id=_hostid;
   UPDATE disk_stats_history SET cid=_cid WHERE id=_hostid;
   UPDATE net_stats SET cid=_cid WHERE hostid=_hostid;
   UPDATE net_stats_history SET cid=_cid WHERE id=_hostid;
   UPDATE ram_stats SET cid=_cid WHERE id=_hostid;
   UPDATE ram_stats_history SET cid=_cid WHERE id=_hostid;
   UPDATE galera_status SET cid=_cid WHERE hostid=_hostid;
   CALL sp_cmon_movemysql(_cid, _hostid);
END;
||
DELIMITER ;



DROP PROCEDURE IF EXISTS sp_cmon_movemysql;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_movemysql(_cid integer, _hostid integer)
SQL SECURITY INVOKER
BEGIN
   UPDATE IGNORE alarm SET cid=_cid WHERE nodeid=_hostid;	
   UPDATE IGNORE cluster_configuration SET cid=_cid  WHERE hid=_hostid AND filename='my.cnf';	
   UPDATE IGNORE mysql_slave_status  SET cid=_cid  WHERE serverid in (SELECT serverid FROM mysql_server WHERE  id=_hostid);
   UPDATE IGNORE mysql_advisor SET cid=_cid  WHERE nodeid=_hostid;
   UPDATE IGNORE mysql_memory_usage SET cid=_cid  WHERE nodeid=_hostid;
   UPDATE IGNORE mysql_advisor_history SET cid=_cid  WHERE nodeid=_hostid;
   UPDATE IGNORE mysql_advisor_reco SET cid=_cid  WHERE nodeid=_hostid;	
   UPDATE IGNORE mysql_performance_results SET cid=_cid WHERE hostid=_hostid;
   UPDATE IGNORE mysql_processlist SET cid=_cid WHERE id=_hostid;
   UPDATE IGNORE mysql_query_histogram SET cid=_cid WHERE id=_hostid;
   UPDATE IGNORE mysql_repl_link SET cid=_cid WHERE hostid=_hostid;
   UPDATE IGNORE mysql_server SET cid=_cid WHERE id=_hostid;
   UPDATE IGNORE mysql_slow_queries SET cid=_cid WHERE id=_hostid;
   UPDATE IGNORE mysql_statistics SET cid=_cid WHERE id=_hostid;
   UPDATE IGNORE mysql_statistics_hour SET cid=_cid WHERE id=_hostid;
   UPDATE IGNORE mysql_variables SET cid=_cid WHERE id=_hostid;
END;
||
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_cmon_deletecluster;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deletecluster(_cid integer)
SQL SECURITY INVOKER
BEGIN
   DECLARE done TINYINT DEFAULT 0;
   DECLARE _table CHAR(64);
   DECLARE cur CURSOR FOR select distinct table_name from information_schema.columns where column_name='cid' and table_schema='cmon';
   DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
   OPEN cur;
   read_loop: LOOP
       FETCH FROM cur INTO _table;
       IF done THEN LEAVE read_loop; END IF;
       call sp_delete_chunks(_table, _cid, 65536);
   /* 
       SET @s = CONCAT('DELETE FROM  ', _table ,' WHERE cid= ', _cid );
       PREPARE stmt FROM @s;
       EXECUTE stmt;
  */
   END LOOP;
   CLOSE cur;  
  
   DELETE FROM cluster WHERE id=_cid;
   DELETE FROM cluster_state WHERE id=_cid;
   DELETE FROM cmon_log WHERE cid=_cid;
END;
||
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_cmon_deletecpu;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deletecpu(_cid integer, _hostid integer)
SQL SECURITY INVOKER 
BEGIN
   DECLARE _avg FLOAT; 
   DECLARE _coreid INTEGER; 
   DECLARE done TINYINT DEFAULT 0;
   DECLARE cur CURSOR FOR SELECT coreid FROM cpu_stats WHERE cid=_cid AND id=_hostid;
   DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
   OPEN cur;
   read_loop: LOOP
       FETCH FROM cur INTO _coreid;
       IF done THEN LEAVE read_loop; END IF;
       SELECT IFNULL(avg(usr+sys+iowait),0) into _avg   FROM cpu_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 48 HOUR)  AND report_ts <= DATE_SUB(NOW(), INTERVAL 24 HOUR)  AND id=_hostid AND coreid=_coreid AND cid=_cid;
         
       DELETE  FROM cpu_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 48 HOUR)  AND report_ts <= DATE_SUB(NOW(), INTERVAL 24 HOUR)  AND id=_hostid AND coreid=_coreid AND cid=_cid AND (usr+sys+iowait)<_avg*0.9;
   END LOOP;
   CLOSE cur;  

END;
||
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_delete_chunks;
delimiter //
CREATE PROCEDURE `sp_delete_chunks`(table_name VARCHAR(255), cid INT, num_rows INT)
BEGIN
  SET @table_name = table_name;
  SET @cid_ = cid;
  SET @num_rows_ = num_rows;

  loop_label:  LOOP
    SET @z = NULL;
    SET @sql_text2 = concat('SELECT COUNT(cid) INTO @z FROM ',@table_name,' WHERE cid=',@cid_,' LIMIT ',@num_rows_);
    PREPARE stmt2 FROM @sql_text2;
    EXECUTE stmt2;
    DEALLOCATE PREPARE stmt2;

    If @z is null THEN
      LEAVE loop_label;
    ELSEIF @z = "" THEN
      LEAVE loop_label;
    ELSEIF @z = 0 THEN
      LEAVE loop_label;
    END IF;

    SET @sql_text3 = concat('DELETE FROM ',@table_name,' WHERE cid=', @cid_,' LIMIT ', @num_rows_);
    PREPARE stmt3 FROM @sql_text3;
    EXECUTE stmt3;
    DEALLOCATE PREPARE stmt3;

    SET @a = @z;
    SELECT SLEEP(0.2);
  END LOOP;

  SET @sql_text4 = concat('DELETE FROM ',@table_name,' WHERE cid=', @cid_);
  PREPARE stmt4 FROM @sql_text4;
  EXECUTE stmt4;
  DEALLOCATE PREPARE stmt4;
END
//

delimiter ;


DROP PROCEDURE IF EXISTS sp_delete_where;
delimiter //
CREATE PROCEDURE `sp_delete_where`(table_name VARCHAR(255), where_clause VARCHAR(255), num_rows INT)
BEGIN
  SET @table_name = table_name;
  SET @where_clause = where_clause;
  SET @num_rows_ = num_rows;

  loop_label:  LOOP
    SET @z = NULL;
    SET @sql_text2 = concat('SELECT COUNT(cid) INTO @z FROM ',@table_name,' ', @where_clause , ' LIMIT ',@num_rows_);
    PREPARE stmt2 FROM @sql_text2;
    EXECUTE stmt2;
    DEALLOCATE PREPARE stmt2;

    If @z is null THEN
      LEAVE loop_label;
    ELSEIF @z = "" THEN
      LEAVE loop_label;
    ELSEIF @z = 0 THEN
      LEAVE loop_label;
    END IF;

    SET @sql_text3 = concat('DELETE FROM ' ,@table_name,' ', @where_clause , ' LIMIT ',@num_rows_);
    PREPARE stmt3 FROM @sql_text3;
    EXECUTE stmt3;
    DEALLOCATE PREPARE stmt3;

    SET @a = @z;
    SELECT SLEEP(0.2);
  END LOOP;

  SET @sql_text4 = concat('DELETE FROM ',@table_name,' ', @where_clause );
  PREPARE stmt4 FROM @sql_text4;
  EXECUTE stmt4;
  DEALLOCATE PREPARE stmt4;
END
//

delimiter ;


DROP PROCEDURE IF EXISTS sp_cmon_deletenet;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deletenet(_cid integer, _hostid integer)
SQL SECURITY INVOKER 
BEGIN
   DECLARE _avg INTEGER;  
   DECLARE _interface CHAR(16); 
   DECLARE done TINYINT DEFAULT 0;
   DECLARE cur CURSOR FOR SELECT interface FROM net_stats WHERE cid=_cid AND hostid=_hostid;
   DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
   OPEN cur;
   read_loop: LOOP
       FETCH FROM cur INTO _interface;
       IF done THEN LEAVE read_loop; END IF; 
       SELECT round(IFNULL(avg(tx_bytes_sec+rx_bytes_sec),0)) into _avg    FROM net_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 48 HOUR)  AND report_ts <= DATE_SUB(NOW(), INTERVAL 24 HOUR)  AND id=_hostid AND interface=_interface AND cid=_cid;
        
       DELETE FROM net_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 48 HOUR)  AND report_ts <= DATE_SUB(NOW(), INTERVAL 24 HOUR)  AND id=_hostid AND interface=_interface AND cid=_cid AND (rx_bytes_sec + tx_bytes_sec)<_avg*0.9;
   END LOOP;
   CLOSE cur;  

END;
||
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_cmon_deletedisk;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deletedisk(_cid integer, _hostid integer)
SQL SECURITY INVOKER 
BEGIN
   DECLARE _avg INTEGER;  
   DECLARE _disk_name CHAR(32); 
   DECLARE done TINYINT DEFAULT 0;
   DECLARE cur CURSOR FOR SELECT disk_name FROM disk_stats WHERE cid=_cid AND id=_hostid;
   DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
   OPEN cur;
   read_loop: LOOP
       FETCH FROM cur INTO _disk_name;
       IF done THEN LEAVE read_loop; END IF; 
       SELECT round(IFNULL(avg(_sectors_written+_sectors_read),0)) into _avg FROM disk_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 48 HOUR)  AND report_ts <= DATE_SUB(NOW(), INTERVAL 24 HOUR)  AND id=_hostid AND disk_name=_disk_name AND cid=_cid;
        
       DELETE FROM disk_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 48 HOUR)  AND report_ts <= DATE_SUB(NOW(), INTERVAL 24 HOUR)  AND id=_hostid AND disk_name=_disk_name AND cid=_cid AND (_sectors_written + _sectors_read)<_avg*0.9;
   END LOOP;
   CLOSE cur;  

END;
||
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_cmon_deleteram;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deleteram(_cid integer, _hostid integer)
SQL SECURITY INVOKER 
BEGIN
   DECLARE _avg INTEGER;  
   SELECT round(IFNULL(avg(free_bytes),0)) into _avg FROM ram_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 48 HOUR)  AND report_ts <= DATE_SUB(NOW(), INTERVAL 24 HOUR)  AND id=_hostid AND cid=_cid;
   DELETE FROM ram_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 48 HOUR)  AND report_ts <= DATE_SUB(NOW(), INTERVAL 24 HOUR)  AND id=_hostid AND cid=_cid AND  free_bytes<_avg;

END;
||
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_cmon_deleteresources;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deleteresources(_cid integer)
SQL SECURITY INVOKER 
BEGIN
   DECLARE _host INTEGER;
   DECLARE done TINYINT DEFAULT 0;
   DECLARE cur CURSOR FOR SELECT id FROM hosts WHERE cid=_cid;
   DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
   OPEN cur;
   read_loop: LOOP
       FETCH FROM cur INTO _host;
       IF done THEN LEAVE read_loop; END IF; 
         call sp_cmon_deleteram(_cid,_host);
         call sp_cmon_deletedisk(_cid,_host);
         call sp_cmon_deletenet(_cid,_host);
         call sp_cmon_deletecpu(_cid,_host);
   END LOOP;   
   SELECT id INTO _host FROM hosts WHERE cid=_cid LIMIT 1;	
   CLOSE cur;  
END;
||
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_cmon_deleteresources_all;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_deleteresources_all()
SQL SECURITY INVOKER 
BEGIN
   DECLARE _cid INTEGER;
   DECLARE done TINYINT DEFAULT 0;
   DECLARE cur CURSOR FOR SELECT id FROM cluster;
   DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
   OPEN cur;
   read_loop: LOOP
       FETCH FROM cur INTO _cid;
       IF done THEN LEAVE read_loop; END IF; 
         call sp_cmon_deleteresources(_cid);
   END LOOP;
   SELECT id INTO _cid FROM cluster LIMIT 1;   
   CLOSE cur;  
END;
||
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_cmon_purge_history;
DELIMITER ||
CREATE PROCEDURE  sp_cmon_purge_history()
SQL SECURITY INVOKER
BEGIN
   DECLARE _cid INTEGER;
   DECLARE done TINYINT DEFAULT 0;
   DECLARE purge_interval char(255) DEFAULT '7';
   DECLARE purge_interval_daily char(255) DEFAULT '7';
   DECLARE purge_interval_minute char(255) DEFAULT '65';
   DECLARE purge_query_histogram char(255) DEFAULT '1';
   DECLARE cur CURSOR FOR SELECT id FROM cluster;
   DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
   OPEN cur;
   read_loop: 
       LOOP FETCH FROM cur INTO _cid;
         IF done THEN 
	     LEAVE read_loop; 
         END IF;
         call sp_cmon_deleteresources(_cid);
         SELECT ifnull(value,7) INTO purge_interval FROM cmon_configuration WHERE param='PURGE' and cid=_cid LIMIT 1;
         SELECT ifnull(value,7) INTO purge_interval_daily FROM cmon_configuration WHERE param='PURGE' and cid=_cid LIMIT 1;       
	 SELECT IFNULL((SELECT value  FROM cmon_configuration WHERE param='PURGE_QUERY_HISTOGRAM' and cid=_cid LIMIT 1),1) INTO purge_query_histogram;
         DELETE FROM ndbinfo_logbuffers_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL  purge_interval_daily DAY);
         DELETE FROM memory_usage_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL  purge_interval_daily DAY);
         DELETE FROM ndbinfo_logspaces_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL  purge_interval_daily DAY);
         DELETE FROM cpu_stats_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL  purge_interval_daily DAY);
         DELETE FROM ram_stats_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL  purge_interval_daily DAY);
         DELETE FROM disk_stats_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval_daily DAY);
         DELETE FROM diskdata_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval_daily DAY);
         DELETE FROM mysql_global_statistics_history WHERE cid=_cid AND  report_ts <= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL purge_interval_daily DAY));
         DELETE FROM mysql_statistics_history WHERE cid=_cid AND  report_ts <= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL purge_interval_daily DAY));
         DELETE FROM mysql_advisor_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval_daily DAY);
         DELETE FROM expression_result_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval_daily DAY);
         DELETE FROM mysql_performance_results WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM net_stats_history WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM cmon_job WHERE cid=_cid AND  report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM cmon_job_message WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM cluster_log WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM backup_log WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM restore_log WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM cmon_log WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL 25 HOUR);
         DELETE FROM backup WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM restore WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval DAY);
         DELETE FROM alarm_log WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval_daily DAY);
         DELETE FROM mysql_query_histogram WHERE cid=_cid AND ts <= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL purge_query_histogram DAY));
         DELETE FROM mysql_slow_queries WHERE cid=_cid AND report_ts <= DATE_SUB(NOW(), INTERVAL purge_interval_daily DAY);	
	 DELETE FROM db_growth WHERE cid=_cid AND report_ts <= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 366 DAY));	      
	 DELETE FROM table_growth WHERE cid=_cid AND report_ts <= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 366 DAY));	      
   END LOOP;
   SELECT id INTO _cid FROM cluster LIMIT 1;
   CLOSE cur;
END;
||
DELIMITER ;

DROP EVENT IF EXISTS e_clear_tables;
delimiter ||
CREATE EVENT e_clear_tables
   ON SCHEDULE
     EVERY 1 DAY STARTS '2011-09-01 03:00:00'
   COMMENT 'Clears out tables each day at 3am.'
   DO
     BEGIN
       DECLARE days_left int(11);
       DECLARE _severity char(255);
       DECLARE _description char(255);
   
      
     SELECT TIMESTAMPDIFF(DAY,NOW(),STR_TO_DATE(exp_date,'%d/%m/%Y')) INTO days_left FROM license;
     call sp_cmon_purge_history();
     CALL sp_cmon_deleteresources_all();

    IF (days_left  <= 30 AND days_left > 0)
    THEN
      
    SET _severity='WARNING'; 
    SET _description=Concat('Your license will expire within ',days_left,' days');

    ELSEIF (days_left <= 0)  
    THEN

    SET _severity='CRITICAL'; 
    SET _description='Your license has expired';
     
    END IF;

    IF ((days_left  <= 30  AND days_left > 0) OR (days_left <= 0))
    THEN

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(1,
           0,
           'LICENSE',
           'LICENSE EXPIRY DATE',
           DEFAULT,
           DEFAULT ,
           DEFAULT,
           DEFAULT,
           DEFAULT,
           _severity,
           DEFAULT,
           _description,
	   'Renew your license',
           DEFAULT,
           NOW()
         )ON DUPLICATE KEY UPDATE description=_description, severity=_severity, report_ts=NOW(); 
  
      ELSE
         DELETE FROM alarm WHERE cid=1 AND nodeid=0 AND component='LICENSE';   
      END IF; 

    END
||
delimiter ;


DROP TABLE IF EXISTS `alarm`;
CREATE TABLE IF NOT EXISTS  `alarm` (
  `alarm_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `component` char(64) NOT NULL DEFAULT '',
  `alarm_name` char(64) NOT NULL DEFAULT '',
  `alarm_count` int(11) NOT NULL DEFAULT '0',
  `alarm_sent` int(11) NOT NULL DEFAULT '0',
  `alarm_sent_count` int(11) NOT NULL DEFAULT '0',
  `alarm_last_sent` datetime DEFAULT NULL,
  `cluster_state` char(64) DEFAULT NULL,
  `severity` enum('WARNING','CRITICAL','INFO') DEFAULT 'WARNING',
  `exit_message` char(255) DEFAULT NULL,
  `description` char(255) DEFAULT NULL,
  `recommendation` char(255) DEFAULT NULL,
  `hostname` char(128) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ignored` int(11) DEFAULT '0',
  `hostid` int(11) DEFAULT '0',
  PRIMARY KEY (`alarm_id`),
  UNIQUE KEY `cid` (`cid`,`nodeid`,`component`,`alarm_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `simple_alarm`;
CREATE TABLE IF NOT EXISTS  `simple_alarm` (
  `alarm_id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` bigint unsigned  NOT NULL DEFAULT '0',
  `alarm_source` enum('ALARM_SOURCE_HOST','ALARM_SOURCE_MONGODB','ALARM_SOURCE_MYSQL','ALARM_SOURCE_GALERA','ALARM_SOURCE_MYSQLCLUSTER', 'ALARM_SOURCE_PROCESS', 'ALARM_SOURCE_DB','ALARM_SOURCE_CLUSTER') DEFAULT 'ALARM_SOURCE_HOST',
  `alarm_source_string` varchar(128) NOT NULL DEFAULT '',
  `alarm_type` int(11) NOT NULL DEFAULT '0',
  `alarm_name` varchar(128) NOT NULL DEFAULT '',
  `alarm_cnt` int(11) NOT NULL DEFAULT '0',
  `email_sent` int(11) NOT NULL DEFAULT '0',
  `snmp_sent` int(11) NOT NULL DEFAULT '0',
  `message` varchar(512) DEFAULT '',
  `recommendation` varchar(512) DEFAULT '',
  `severity` enum('WARNING','CRITICAL') DEFAULT 'WARNING',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ignored` int(11) DEFAULT '0',
  `hostid` int(11) DEFAULT '0',
  `nodeid` int(11) DEFAULT '0',
  PRIMARY KEY (`alarm_id`),
  UNIQUE KEY `cid` (`cid`,`id`,`alarm_source`,`alarm_type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `simple_email`;
CREATE TABLE IF NOT EXISTS  `simple_email` (
  `alarm_id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `message` text,
  `subject` varchar(512) DEFAULT '',
  `receipients` varchar(256) DEFAULT '',
  `email_sent` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `retry_count` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`alarm_id`),
  KEY `cid` (`cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `db_notifications`;
CREATE TABLE IF NOT EXISTS  `db_notifications` (
  `alarm_id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `rule` varchar(255) NOT NULL DEFAULT '',
  `advise` varchar(255) NOT NULL DEFAULT '',
  `severity` int(11) NOT NULL DEFAULT '0',
  `val`  bigint NOT NULL DEFAULT '0',
  `warning`  bigint NOT NULL DEFAULT '80',
  `critical`  bigint NOT NULL DEFAULT '90',
  `ignored` int(11) DEFAULT '0',
  `last_seen` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  
  `process_type` enum('NDB','MYSQL','MONGO','MEMCACHED') DEFAULT 'MYSQL',
  UNIQUE KEY `cid` (`cid`,`nodeid`,`rule`),
  PRIMARY KEY (alarm_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `alarm_hosts`;
CREATE TABLE IF NOT EXISTS `alarm_hosts` (
  `hostid` int(11) NOT NULL DEFAULT '0',
  `cid` int(11) NOT NULL DEFAULT '1',
  `component` varchar(255) NOT NULL DEFAULT '',
  `alarm_name` varchar(255) NOT NULL DEFAULT '',
  `alarm_count` int(11) NOT NULL DEFAULT '0',
  `severity` varchar(255) NOT NULL DEFAULT '',
  `description` char(255) DEFAULT NULL DEFAULT '',
  `hostname` varchar(255) NOT NULL DEFAULT '',
  `recommendation` varchar(255) NOT NULL DEFAULT '',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `alarm_sent` int(11) DEFAULT '0',
  `alarm_sent_count` int(11) DEFAULT '0',
  `alarm_id` int(11) NOT NULL AUTO_INCREMENT,
  `exit_message` char(8) DEFAULT 'N/A',
  `cluster_state` char(8) DEFAULT 'N/A',
  `alarm_last_sent` datetime DEFAULT NULL,
  `ignored` int(11) DEFAULT '0',
  `nodeid` int(11) DEFAULT '0',
  PRIMARY KEY (`alarm_id`),
  UNIQUE KEY `cid` (`cid`,`hostid`,`alarm_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `alarm_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alarm_id` int(11) NOT NULL DEFAULT '0',
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `component` char(64) NOT NULL DEFAULT '',
  `alarm_name` char(64) NOT NULL DEFAULT '',
  `alarm_count` int(11) NOT NULL DEFAULT '0',
  `alarm_sent` int(11) NOT NULL DEFAULT '0',
  `alarm_sent_count` int(11) NOT NULL DEFAULT '0',
  `cluster_state` char(64) DEFAULT NULL,
  `severity` char(64) DEFAULT NULL,
  `exit_message` char(255) DEFAULT NULL,
  `description` char(255) DEFAULT NULL,
  `recommendation` char(255) DEFAULT NULL,
  `hostname` char(128) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `alarm_id` (`alarm_id`),
  KEY `cid` (`cid`, `nodeid`, `report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;


CREATE TABLE IF NOT EXISTS `backup` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `backupid` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `master_nodeid` int(11) NOT NULL DEFAULT '0',
  `mgm_nodeid` int(11) NOT NULL DEFAULT '0',
  `status` char(255) DEFAULT NULL,
  `error` int(11) NOT NULL DEFAULT '0',
  `start_gci` int(11) DEFAULT '0',
  `stop_gci` int(11) DEFAULT '0',
  `records` bigint(20) unsigned DEFAULT '0',
  `log_records` bigint(20) unsigned DEFAULT '0',
  `bytes` bigint(20) unsigned DEFAULT '0',
  `log_bytes` bigint(20) unsigned DEFAULT '0',
  `directory` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`backupid`),
  KEY `report_ts` (`report_ts`),
  KEY `backup_cid_status` (`cid`,`status`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `backup_log` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `backupid` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` char(255) DEFAULT NULL,
  `error` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `report_ts` (`report_ts`),
  KEY `backupid` (`backupid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



CREATE TABLE IF NOT EXISTS `backup_schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `weekday` int(11) DEFAULT '1',
  `exectime` char(8) DEFAULT '',
  `last_exec` datetime DEFAULT NULL ,
  `backupdir` char(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `backup_method` enum('ndb','mysqldump','xtrabackupfull','xtrabackupincr') DEFAULT 'mysqldump',
  `backup_host` char(255) DEFAULT 'none',
  `cc_storage` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`cid`),
  UNIQUE KEY `cid` (`cid`,`weekday`,`exectime`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;



CREATE TABLE IF NOT EXISTS `cluster` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `connectstring` char(255) DEFAULT NULL,
  `type` enum('mysqlcluster','replication','galera','mysql_single') DEFAULT NULL,
  `name` char(255) DEFAULT NULL,
  `scriptsdir` char(255) DEFAULT NULL,
  `description` char(255) DEFAULT NULL,
  `feature_ts` int(11) DEFAULT '0',
  `deployed_version` int(11) DEFAULT '0',
  `config_version` int(11) DEFAULT '0',
  `config_change` enum('RRM', 'RR','RRI','NONE') DEFAULT 'NONE',
  `process_mgmt` int(11) DEFAULT '0',
  `feature_ndbinfo` int(11) DEFAULT '0',
  `feature_ndbinfo_dp` int(11) DEFAULT '0',
  `parent_id` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `connectstring` (`connectstring`),
  UNIQUE KEY `name` (`name`),
  KEY `type_cid` (`type`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;



CREATE TABLE IF NOT EXISTS `cluster_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `groupid` int(11) NOT NULL DEFAULT '0',
  `variable` char(255) NOT NULL DEFAULT '',
  `grp` char(255) DEFAULT NULL,
  `value` char(255) DEFAULT NULL,
  `version` int(11) NOT NULL DEFAULT '1',
  `filename` varchar(255) DEFAULT NULL,
  `configured` tinyint(4) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,`cid`,`variable`),
  KEY `cid` (`cid`,`variable`,`groupid`),
  KEY `cid_2` (`cid`,`version`,`groupid`),
  KEY `cid_3` (`cid`,`filename`,`version`,`groupid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

DROP TABLE IF EXISTS ndb_config;
CREATE TABLE IF NOT EXISTS `ndb_config` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `var` varchar(255) NOT NULL DEFAULT '',
  `value` varchar(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`var`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

DROP TABLE IF EXISTS cluster_configuration;
CREATE TABLE IF NOT EXISTS `cluster_configuration` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hid` int(11) NOT NULL DEFAULT '0',
  `crc` int(11) unsigned NOT NULL DEFAULT '0',
  `has_change` tinyint(4) DEFAULT '0',
  `filename` varchar(255) DEFAULT NULL,
  `fullpath` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `size` int(11) unsigned DEFAULT '0',
  `data` text,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`hid`,`filename`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

DROP TABLE IF EXISTS cluster_configuration_templates;
CREATE TABLE IF NOT EXISTS `cluster_configuration_templates` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `crc` int(11) unsigned NOT NULL DEFAULT '0',
  `filename` varchar(255) DEFAULT NULL,
  `fullpath` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `size` int(11) unsigned DEFAULT '0',
  `status` int(11) unsigned DEFAULT '0',
  `data` text,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`, `filename`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;



CREATE TABLE IF NOT EXISTS `cluster_event_types` (
  `event` char(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`event`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `cluster_log` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `source_nodeid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `severity` enum('DEBUG','INFO','WARNING','ERROR','CRITICAL','ALERT') DEFAULT NULL,
  `loglevel` int(11) NOT NULL DEFAULT '0',
  `event` char(255) DEFAULT NULL,
  `message` char(255) DEFAULT NULL,
  PRIMARY KEY (`id`,`cid`),
  KEY `cid_ix` (`cid`,`id`),
  KEY `report_ts` (`report_ts`),
  KEY `severity` (`severity`),
  KEY `event` (`event`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE IF NOT EXISTS `cluster_severity_types` (
  `severity` char(255) NOT NULL,
  PRIMARY KEY (`severity`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `cluster_state` (
  `id` int(11) NOT NULL DEFAULT '0',
  `status` enum('MGMD_NO_CONTACT','STARTED','NOT_STARTED','DEGRADED','FAILURE','SHUTTING_DOWN','RECOVERING','STARTING','UNKNOWN', 'STOPPED') DEFAULT NULL,
  `previous_status` enum('MGMD_NO_CONTACT','STARTED','NOT_STARTED','DEGRADED','FAILURE','SHUTTING_DOWN','RECOVERING','STARTING','UNKNOWN','STOPPED') DEFAULT NULL,
  `c_restarts` int(11) NOT NULL DEFAULT '0',
  `uptime` bigint(20) DEFAULT '0',
  `downtime` bigint(20) DEFAULT '0',
  `sla_starttime` datetime DEFAULT NULL,
  `sla_started` int(11) DEFAULT '0',
  `mc_lcp_status` varchar(255) DEFAULT '',
  `mc_lcp_time` timestamp NOT NULL DEFAULT 0,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `replication_state` int(11) DEFAULT '0',
  `prev_replication_state` int(11) DEFAULT '0',
  `msg` varchar(512) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `cluster_statistics` (
  `id` int(11) NOT NULL DEFAULT '0',
  `operations` bigint(11) DEFAULT '0',
  `transactions` bigint(20) DEFAULT '0',
  `commits` bigint(20) DEFAULT '0',
  `writes` bigint(20) DEFAULT '0',
  `reads_all` bigint(20) DEFAULT '0',
  `simple_reads` bigint(20) DEFAULT '0',
  `aborts` bigint(20) DEFAULT '0',
  `attrinfo` bigint(20) DEFAULT '0',
  `table_scans` bigint(20) DEFAULT '0',
  `range_scans` bigint(20) DEFAULT '0',
  `reads_received` bigint(20) DEFAULT '0',
  `local_reads` bigint(20) DEFAULT '0',
  `local_writes` bigint(20) DEFAULT '0',
  `local_reads_sent` bigint(20) DEFAULT '0',
  `remote_reads_sent` bigint(20) DEFAULT '0',
  `reads_not_found` bigint(20) DEFAULT '0',
  `table_scans_received` bigint(20) DEFAULT '0',
  `local_table_scans_sent` bigint(20) DEFAULT '0',
  `range_scans_received` bigint(20) DEFAULT '0',
  `local_range_scans_sent` bigint(20) DEFAULT '0',
  `remote_range_scans_sent` bigint(20) DEFAULT '0',
  `scan_batches_returned` bigint(20) DEFAULT '0',
  `scan_rows_returned` bigint(20) DEFAULT '0',
  `pruned_range_scans_received` bigint(20) DEFAULT '0',
  `const_pruned_range_scans_received` bigint(20) DEFAULT '0',
  `lqhkey_overload` bigint(20) DEFAULT '0',
  `lqhkey_overload_tc` bigint(20) DEFAULT '0',
  `lqhkey_overload_subscriber` bigint(20) DEFAULT '0',
  `lqhkey_overload_reader` bigint(20) DEFAULT '0',
  `lqhkey_overload_node_peer` bigint(20) DEFAULT '0',
  `lqhkey_overload_node_subscriber` bigint(20) DEFAULT '0',
  `lqhscan_slowdowns` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `cluster_statistics_history` (
  `id` int(11) NOT NULL DEFAULT '0',
  `operations` bigint(11) DEFAULT '0',
  `transactions` bigint(20) DEFAULT '0',
  `commits` bigint(20) DEFAULT '0',
  `writes` bigint(20) DEFAULT '0',
  `reads_all` bigint(20) DEFAULT '0',
  `simple_reads` bigint(20) DEFAULT '0',
  `aborts` bigint(20) DEFAULT '0',
  `attrinfo` bigint(20) DEFAULT '0',
  `table_scans` bigint(20) DEFAULT '0',
  `range_scans` bigint(20) DEFAULT '0',
  `reads_received` bigint(20) DEFAULT '0',
  `local_reads_sent` bigint(20) DEFAULT '0',
  `local_reads` bigint(20) DEFAULT '0',
  `local_writes` bigint(20) DEFAULT '0',
  `remote_reads_sent` bigint(20) DEFAULT '0',
  `reads_not_found` bigint(20) DEFAULT '0',
  `table_scans_received` bigint(20) DEFAULT '0',
  `local_table_scans_sent` bigint(20) DEFAULT '0',
  `range_scans_received` bigint(20) DEFAULT '0',
  `local_range_scans_sent` bigint(20) DEFAULT '0',
  `remote_range_scans_sent` bigint(20) DEFAULT '0',
  `scan_batches_returned` bigint(20) DEFAULT '0',
  `scan_rows_returned` bigint(20) DEFAULT '0',
  `pruned_range_scans_received` bigint(20) DEFAULT '0',
  `const_pruned_range_scans_received` bigint(20) DEFAULT '0',
  `lqhkey_overload` bigint(20) DEFAULT '0',
  `lqhkey_overload_tc` bigint(20) DEFAULT '0',
  `lqhkey_overload_subscriber` bigint(20) DEFAULT '0',
  `lqhkey_overload_reader` bigint(20) DEFAULT '0',
  `lqhkey_overload_node_peer` bigint(20) DEFAULT '0',
  `lqhkey_overload_node_subscriber` bigint(20) DEFAULT '0',
  `lqhscan_slowdowns` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,report_ts)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

DROP TRIGGER IF EXISTS ut_cluster_statistics;
DROP TRIGGER IF EXISTS it_cluster_statistics;


DROP TABLE IF EXISTS `cmon_todo`;
CREATE TABLE IF NOT EXISTS  `cmon_todo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `message` text,
  `obj` varchar(64),	
  `extra` varchar(255),
  `cnt` int(11) NOT NULL DEFAULT '1',
  `completed` tinyint(4) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `cid` (`cid`, `obj`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `cmon_cluster_counters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `var` char(64) DEFAULT NULL,
  `enabled` char(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `counter` (`var`,`enabled`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;





CREATE TABLE IF NOT EXISTS `cmon_cluster_graphs` (
  `graphid` int(11) NOT NULL AUTO_INCREMENT,
  `graph` char(64) DEFAULT NULL,
  PRIMARY KEY (`graphid`),
  KEY `graph` (`graph`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;





CREATE TABLE IF NOT EXISTS `cmon_configuration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '0',
  `param` char(255) NOT NULL DEFAULT '',
  `value` char(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,`param`),
  UNIQUE KEY `cid` (`cid`,`param`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;



DROP TABLE IF EXISTS `cmon_host_log`;
CREATE TABLE IF NOT EXISTS `cmon_host_log` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostname` varchar(255) NOT NULL DEFAULT '',
  `filename` varchar(255) NOT NULL DEFAULT '',
  `jobid` int(11) NOT NULL DEFAULT '0',
  `result_len` int(11) NOT NULL DEFAULT '0',
  `result` longblob,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hostid` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT '',
  `tag` varchar(255) DEFAULT 'mysql',
  PRIMARY KEY (`cid`,`hostname`,`filename`),
  UNIQUE KEY `ix_cidhostid` (`cid`,`hostid`,`filename`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `cmon_job` (
  `jobid` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `jobspec` varchar(8192) DEFAULT NULL,
  `status_txt` varchar(255) DEFAULT NULL,
  `status` enum('DEFINED','DEQUEUED','RUNNING','RUNNING_EXT' ,'ABORTED','FINISHED','FAILED') DEFAULT 'DEFINED',
  `exit_code` int(11) DEFAULT '0',
  `checked` int(11) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `parent_jobid` int(11) DEFAULT '0',
  `user_id` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`jobid`,`cid`),
  KEY (`parent_jobid`,`cid`),
  KEY `clusterid` (`cid`,`status`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE IF NOT EXISTS `cmon_job_message` (
  `messageid` int(11) NOT NULL AUTO_INCREMENT,
  `jobid` int(11) NOT NULL DEFAULT '0',
  `cid` int(11) NOT NULL DEFAULT '1',
  `message` varchar(255) DEFAULT NULL,
  `exit_code` int(11) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`messageid`,`jobid`,`cid`),
  KEY `clusterid` (`jobid`,`cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;


DROP TABLE IF EXISTS `cmon_mysql_counters`;
CREATE TABLE IF NOT EXISTS `cmon_mysql_counters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `var` varchar(64) DEFAULT NULL,
  `crc` bigint(20) unsigned  NOT NULL DEFAULT '0',
  `enabled` tinyint(4) DEFAULT '0',
  `active`  tinyint(4) DEFAULT '0',
  `gauge`  tinyint(4) DEFAULT '0',
  `rrd_gauge`  tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`crc`,`var`),
  UNIQUE KEY (`var`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;


CREATE TABLE IF NOT EXISTS `cmon_galera_counters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `var` varchar(64) DEFAULT NULL,
  `enabled` tinyint(4) DEFAULT '0',
  `active`  tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`var`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE IF NOT EXISTS `cmon_mysql_graphs` (
  `graphid` int(11) NOT NULL AUTO_INCREMENT,
  `graph` char(64) DEFAULT NULL,
  PRIMARY KEY (`graphid`),
  KEY `graph` (`graph`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE IF NOT EXISTS `cmon_schema_uploads` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) NOT NULL DEFAULT '',
  `category` varchar(64) NOT NULL DEFAULT '',
  `db` varchar(64) NOT NULL DEFAULT '',
  `md5sum` varchar(1024) NOT NULL DEFAULT '',
  `filesize` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `type` enum('datafile','trigger') DEFAULT 'datafile',
  PRIMARY KEY (`id`),
  KEY `category` (`category`),
  KEY `db` (`db`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE IF NOT EXISTS `cmon_status` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `owner` char(255) DEFAULT NULL,
  `mode` enum('ACTIVE','STANDBY') DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE if not exists `cmon_uploads` (
  `cid` int(11),
  `packageid` int(11) NOT NULL DEFAULT '0',
  `filename` varchar(255) NOT NULL DEFAULT '',
  `path` varchar(255) NOT NULL DEFAULT '',
  `cluster_type` varchar(64) NOT NULL DEFAULT '',
  `version_tag` varchar(64) NOT NULL DEFAULT '',
  `md5sum` varchar(1024) NOT NULL DEFAULT '',
  `filesize` int(11) NOT NULL DEFAULT '0',
  `selected` int(11) DEFAULT 0,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`packageid`,`filename`),
  KEY `ix_cluster_type` (`cid`, `cluster_type`, `packageid`),
  KEY `version_tag` (`version_tag`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `cmon_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` char(255) DEFAULT NULL,
  `password` char(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `username` (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE IF NOT EXISTS `configurator_nodemap` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `hostname` char(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `cpu_info` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL DEFAULT '0',
  `n_cores` int(11) NOT NULL DEFAULT '0',
  `speed_mhz` double NOT NULL DEFAULT '0',
  `model` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`cid`,`hostid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `cpu_stats` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `coreid` int(11) NOT NULL DEFAULT '65535',
  `loadavg1` float NOT NULL DEFAULT '0',
  `loadavg5` float NOT NULL DEFAULT '0',
  `loadavg15` float NOT NULL DEFAULT '0',
  `sys` float NOT NULL DEFAULT '0',
  `usr` float NOT NULL DEFAULT '0',
  `idle` float NOT NULL DEFAULT '0',
  `iowait` float NOT NULL DEFAULT '0',
  `uptime` float NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`,`coreid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `cpu_stats_history` (
  `cid` int(11) NOT NULL DEFAULT '11',
  `id` int(11) NOT NULL DEFAULT '0',
  `coreid` int(11) NOT NULL DEFAULT '65535',
  `loadavg1` float NOT NULL DEFAULT '0',
  `loadavg5` float NOT NULL DEFAULT '0',
  `loadavg15` float NOT NULL DEFAULT '0',
  `sys` float NOT NULL DEFAULT '0',
  `usr` float NOT NULL DEFAULT '0',
  `idle` float NOT NULL DEFAULT '0',
  `iowait` float NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`,`coreid`,`report_ts`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_cpu_stats`;
DELIMITER //
CREATE TRIGGER `it_cpu_stats` AFTER INSERT ON `cpu_stats`
 FOR EACH ROW BEGIN

   	DECLARE _cpu_usage float;
	DECLARE _hostname varchar(255);
        DECLARE _cpu_warning char(255);
        DECLARE _cpu_critical char(255);
        DECLARE _severity char(255);
        DECLARE _core char(16);
       
       IF ((NEW.usr + NEW.sys + NEW.iowait) >= 0 ) 
       THEN


                IF ( NEW.coreid = 65535 ) 
                THEN
		SELECT round(IFNULL(avg(sys+usr+iowait),0)) INTO _cpu_usage FROM cpu_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 15 MINUTE) AND id=NEW.id AND coreid=NEW.coreid AND cid=NEW.cid;
                  
                SELECT value INTO _cpu_warning FROM cmon_configuration WHERE param='CPU_WARNING' AND cid=NEW.cid;
                
                SELECT value INTO _cpu_critical FROM cmon_configuration WHERE param='CPU_CRITICAL' AND cid=NEW.cid;
                   
                IF ( NEW.coreid = 65535 ) 
                THEN
                   set _core='(all CPUs)';
                ELSE
                   set _core=concat('(core ', NEW.coreid,')');
                END IF;
                
		IF (_cpu_usage >= _cpu_warning && _cpu_usage < _cpu_critical)
    			THEN		
				

                                SET _severity='WARNING'; 


				

		ELSEIF (_cpu_usage >= _cpu_critical)
    		       THEN
				

                                SET _severity='CRITICAL'; 


	 			

	       ELSEIF (_cpu_usage < _cpu_warning)
    			THEN

				DELETE FROM alarm_hosts WHERE hostid=NEW.id AND cid=NEW.cid AND alarm_name=concat('Excessive CPU Usage ', _core);


	       END IF;

               IF ((_cpu_usage >= _cpu_warning && _cpu_usage < _cpu_critical)||(_cpu_usage >= _cpu_critical))
               THEN
                        
	       SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.id AND cid=NEW.cid;
               
               INSERT INTO alarm_hosts    (hostid,
                            				    cid,
                                                            alarm_name,
                            				    component,
                            				    alarm_count,
			    				    severity,
		            				    description,
                            				    hostname,
                            				    recommendation,
                                                            report_ts,
                                                            alarm_sent,
                                                            alarm_sent_count
                           			            )
    				VALUES			   (NEW.id,
           						    NEW.cid,
           					            concat('Excessive CPU Usage ', _core) ,
                                                            'CPU',
                                                            1,
 							    _severity,
                                                            Concat ('Average CPU utilization the last 15 minutes for ',_hostname,' is ',_cpu_usage,' percent'),
                                                            _hostname,
	                                                    'Add Node to Offload CPU',
                                                            NOW(),
                                                            DEFAULT,
                                                            DEFAULT
                                                            ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1, description= Concat ('Average CPU utilization the last 15 minutes for ',_hostname,' is ',_cpu_usage,' percent'), report_ts=now(), severity=_severity;
               END IF; 
            END IF;
          END IF;
END
//

DELIMITER ;
DROP TRIGGER IF EXISTS `ut_cpu_stats`;
DELIMITER //
CREATE TRIGGER `ut_cpu_stats` AFTER UPDATE ON `cpu_stats` FOR EACH ROW BEGIN

        DECLARE _cpu_usage float;
        DECLARE _hostname varchar(255);
        DECLARE _cpu_warning char(255);
        DECLARE _cpu_critical char(255);
        DECLARE _severity char(255);
        DECLARE _core char(16);
        IF ((NEW.usr + NEW.sys + NEW.iowait) >= 0 ) 
       THEN    

           IF ( NEW.coreid = 65535 ) 
           THEN
                SELECT round(IFNULL(avg(sys+usr+iowait),0)) INTO _cpu_usage FROM cpu_stats_history WHERE report_ts >= DATE_SUB(NOW(), INTERVAL 15 MINUTE) AND id=NEW.id AND coreid=NEW.coreid AND cid=NEW.cid;

                SELECT value INTO _cpu_warning FROM cmon_configuration WHERE param='CPU_WARNING' AND cid=NEW.cid;

                SELECT value INTO _cpu_critical FROM cmon_configuration WHERE param='CPU_CRITICAL' AND cid=NEW.cid;

                IF ( NEW.coreid = 65535 )
                THEN
                   set _core='(all CPUs)';
                ELSE
                   set _core=concat('(core ', NEW.coreid,')');
                END IF;
    
                IF (_cpu_usage >= _cpu_warning && _cpu_usage < _cpu_critical)
                    THEN


                                SET _severity='WARNING';




                ELSEIF (_cpu_usage >= _cpu_critical)
                       THEN


                                SET _severity='CRITICAL';




               ELSEIF (_cpu_usage < _cpu_warning)
                        THEN

                                DELETE FROM alarm_hosts WHERE hostid=NEW.id AND cid=NEW.cid AND alarm_name=concat('Excessive CPU Usage ', _core);


               END IF;
               IF ((_cpu_usage >= _cpu_warning && _cpu_usage < _cpu_critical)||(_cpu_usage >= _cpu_critical))
               THEN

               SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.id AND cid=NEW.cid;

               INSERT INTO alarm_hosts    (hostid,
                                                            cid,
                                                            alarm_name,
                                                            component,
                                                            alarm_count,
                                                            severity,
                                                            description,
                                                            hostname,
                                                            recommendation,
                                                            report_ts,
                                                            alarm_sent,
                                                            alarm_sent_count
                                                            )
                                VALUES                     (NEW.id,
                                                            NEW.cid,
                                                            concat('Excessive CPU Usage ', _core) ,
                                                            'CPU',
                                                            1,
                                                            _severity,
                                                            Concat ('Average CPU utilization the last 15 minutes for ',_hostname,' is ',_cpu_usage,' percent'),
                                                            _hostname,
                                                            'Add Node to Offload CPU',
                                                            NOW(),
                                                            DEFAULT,
                                                            DEFAULT
                                                            ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1, description= Concat ('Average CPU utilization the last 15 minutes for ',_hostname,' is ',_cpu_usage,' percent'), report_ts=now(), severity=_severity;
               END IF;
          END IF;
       END IF;
END
//

DELIMITER ;

CREATE TABLE IF NOT EXISTS `database_conf` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `version` int(11) NOT NULL DEFAULT '1',
  `section` varchar(255) NOT NULL DEFAULT '',
  `param` varchar(255) NOT NULL DEFAULT '',
  `value` varchar(255) DEFAULT NULL,
  `filename` varchar(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`version`,`section`,`param`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;




DROP TABLE IF EXISTS `diskdata`;
CREATE TABLE IF NOT EXISTS `diskdata` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `file_name` varchar(4096) NOT NULL DEFAULT '',
  `ts_name` varchar(512) NOT NULL DEFAULT '',
  `type` char(64) NOT NULL DEFAULT '',
  `logfile_group_name` char(64) NOT NULL DEFAULT '',
  `free_extents` bigint(20) unsigned NOT NULL DEFAULT '0',
  `total_extents` bigint(20) unsigned NOT NULL DEFAULT '0',
  `extent_size` bigint(20) unsigned NOT NULL DEFAULT '0',
  `initial_size` bigint(20) unsigned NOT NULL DEFAULT '0',
  `maximum_size` bigint(20) unsigned NOT NULL DEFAULT '0',
  `undo_buffer_size` bigint(20) unsigned NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`file_name`(512))
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_diskdata`;
DROP TRIGGER IF EXISTS `ut_diskdata`;

DROP TABLE IF EXISTS `diskdata_history`;
CREATE TABLE IF NOT EXISTS `diskdata_history` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `file_name` varchar(4096) NOT NULL DEFAULT '',
  `ts_name` varchar(512) NOT NULL DEFAULT '',
  `type` char(64) NOT NULL DEFAULT '',
  `logfile_group_name` char(64) NOT NULL DEFAULT '',
  `free_extents` bigint(20) unsigned NOT NULL DEFAULT '0',
  `total_extents` bigint(20) unsigned NOT NULL DEFAULT '0',
  `extent_size` bigint(20) unsigned NOT NULL DEFAULT '0',
  `initial_size` bigint(20) unsigned NOT NULL DEFAULT '0',
  `maximum_size` bigint(20) unsigned NOT NULL DEFAULT '0',
  `undo_buffer_size` bigint(20) unsigned NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`, `file_name`(512), `report_ts`),
  KEY `idx_diskhistory_free` (`free_extents`), 
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;




CREATE TABLE IF NOT EXISTS `disk_stats` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL DEFAULT '0',
  `disk_name` char(32) NOT NULL DEFAULT '',
  `_reads` int(11) DEFAULT '0',
  `_reads_merged` int(11) DEFAULT '0',
  `_sectors_read` bigint(20) unsigned DEFAULT '0',
  `_writes` int(11) DEFAULT '0',
  `_writes_merged` int(11) DEFAULT '0',
  `_sectors_written` bigint(20) unsigned DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `mount_point` varchar(128) DEFAULT NULL,
  `free_bytes` bigint(20) DEFAULT '0',
  `total_bytes` bigint(20) DEFAULT '0',
  `await` double DEFAULT '0',
  `svctm` double DEFAULT '0',
  `util` double DEFAULT '0',
  PRIMARY KEY (`cid`,`id`,`disk_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_disk_stats`;
DELIMITER //
CREATE TRIGGER `it_disk_stats` AFTER INSERT ON `disk_stats`
 FOR EACH ROW BEGIN

    DECLARE _diskspace_usage float;
    DECLARE _hostname varchar(255);
    DECLARE _diskspace_warning char(255);
    DECLARE _diskspace_critical char(255);
    DECLARE _severity char(255);


                SELECT IFNULL(round(100-(free_bytes/total_bytes)*100),0) INTO _diskspace_usage FROM disk_stats WHERE id=NEW.id AND cid=NEW.cid AND disk_name=NEW.disk_name;

                SELECT value INTO _diskspace_warning FROM cmon_configuration WHERE param='DISKSPACE_WARNING' AND cid=NEW.cid;
                
                SELECT value INTO _diskspace_critical FROM cmon_configuration WHERE param='DISKSPACE_CRITICAL' AND cid=NEW.cid;

    
      IF (_diskspace_usage >= _diskspace_warning && _diskspace_usage < _diskspace_critical)
    			THEN	

               	
			 SET _severity='WARNING'; 
	


		ELSEIF (_diskspace_usage >= _diskspace_critical)
    		       THEN

				
             SET _severity='CRITICAL'; 

	       
        ELSEIF (_diskspace_usage < _diskspace_warning)
    			THEN
				DELETE FROM alarm_hosts WHERE hostid=NEW.id AND cid=NEW.cid AND alarm_name= CONCAT('Excessive DISKSPACE Usage (', NEW.disk_name , ')');
	       END IF;

        IF ((_diskspace_usage >= _diskspace_warning && _diskspace_usage < _diskspace_critical)||(_diskspace_usage >= _diskspace_critical))
               THEN
               

               SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.id AND cid=NEW.cid;
               
        END IF;



END
//
DELIMITER ;
DROP TRIGGER IF EXISTS `ut_disk_stats`;
DELIMITER //
CREATE TRIGGER `ut_disk_stats` AFTER UPDATE ON `disk_stats`
 FOR EACH ROW BEGIN

    DECLARE _diskspace_usage float;
    DECLARE _hostname varchar(255);
    DECLARE _diskspace_warning char(255);
    DECLARE _diskspace_critical char(255);
    DECLARE _severity char(255);


                SELECT IFNULL(round(100-(free_bytes/total_bytes)*100),0) INTO _diskspace_usage FROM disk_stats WHERE id=NEW.id AND cid=NEW.cid AND disk_name=NEW.disk_name;

                SELECT value INTO _diskspace_warning FROM cmon_configuration WHERE param='DISKSPACE_WARNING' AND cid=NEW.cid;
                
                SELECT value INTO _diskspace_critical FROM cmon_configuration WHERE param='DISKSPACE_CRITICAL' AND cid=NEW.cid;

      IF (_diskspace_usage >= _diskspace_warning && _diskspace_usage < _diskspace_critical)
    			THEN	

               	
			 SET _severity='WARNING'; 
	


		ELSEIF (_diskspace_usage >= _diskspace_critical)
    		       THEN

				
             SET _severity='CRITICAL'; 

	       
        ELSEIF (_diskspace_usage < _diskspace_warning)
    			THEN
				DELETE FROM alarm_hosts WHERE hostid=NEW.id AND cid=NEW.cid AND alarm_name= CONCAT('Excessive DISKSPACE Usage (', NEW.disk_name , ')');


	       END IF;

        IF ((_diskspace_usage >= _diskspace_warning && _diskspace_usage < _diskspace_critical)||(_diskspace_usage >= _diskspace_critical))
               THEN
               

               SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.id AND cid=NEW.cid;
               
               
                
               INSERT INTO alarm_hosts    (hostid,
                            				    cid,
                                                            alarm_name,
                            				    component,
                            				    alarm_count,
			    				    severity,
		            				    description,
                            				    hostname,
                            				    recommendation,
                                                            report_ts,
                                                            alarm_sent,
                                                            alarm_sent_count
                           			            )
    				VALUES			   (NEW.id,
           						    NEW.cid,
           					            CONCAT('Excessive DISKSPACE Usage (', NEW.disk_name , ')'),
                                                            'DISKSPACE',
                                                            1,
                                                            _severity,
                                                            Concat ('DISKSPACE Utilization for ',_hostname,' is ',_diskspace_usage,' percent'),
                                                            _hostname,
	                                                    'Upgrade Node with more DISKSPACE',
                                                            NOW(),
                                                            DEFAULT,
                                                            DEFAULT
                                                            )ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1, severity=_severity, report_ts=now(), description=Concat ('DISKSPACE Utilization for '        ,_hostname,' is ',_diskspace_usage,' percent');

        END IF;



END
//
DELIMITER ;



CREATE TABLE IF NOT EXISTS `disk_stats_history` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL DEFAULT '0',
  `disk_name` char(32) NOT NULL DEFAULT '',
  `_reads` int(11) DEFAULT '0',
  `_reads_merged` int(11) DEFAULT '0',
  `_sectors_read` bigint(20) unsigned DEFAULT '0',
  `_writes` int(11) DEFAULT '0',
  `_writes_merged` int(11) DEFAULT '0',
  `_sectors_written` bigint(20) unsigned DEFAULT '0',
  `free_bytes` bigint(20) DEFAULT '0',
  `total_bytes` bigint(20) DEFAULT '0',
  `await` double DEFAULT '0',
  `svctm` double DEFAULT '0',
  `util` double DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`,`disk_name`,`report_ts`),
  KEY `idx_diskstatshistory_writes` (`_writes`),
  KEY `idx_diskstats_free` (`free_bytes`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `email_notification` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '0',
  `fname` char(255) DEFAULT NULL,
  `lname` char(255) DEFAULT NULL,
  `email` char(255) DEFAULT NULL,
  `groupid` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_email` (`email`),
  KEY `ix_fname_email` (`fname`,`email`),
  KEY `ix_cid` (`cid`,`groupid`),
  KEY `ix_lname_email` (`lname`,`email`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE  IF NOT EXISTS `hosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostname` varchar(255) NOT NULL DEFAULT '',
  `ping_status` int(11) NOT NULL DEFAULT '0',
  `ping_time` int(11) NOT NULL DEFAULT '0',
  `ip` varchar(255) NOT NULL DEFAULT '',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `msg` varchar(255) NOT NULL DEFAULT '',
  `cmon_version` varchar(16) DEFAULT NULL,
  `cmon_status` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `wall_clock_time` bigint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`cid`),
  UNIQUE KEY `hostname` (`hostname`,`cid`),
  UNIQUE KEY `ip` (`ip`,`cid`),
  UNIQUE KEY `hostname_ip` (`hostname`,`ip`,`cid`),
  KEY `cid` (`cid`,`ping_time`,`ping_status`)
) ENGINE=InnoDB;




CREATE TABLE IF NOT EXISTS `mailserver` (
  `username` char(64) DEFAULT NULL,
  `password` char(128) DEFAULT NULL,
  `base64_username` char(255) DEFAULT NULL,
  `from_email` char(128) DEFAULT NULL,
  `base64_password` char(255) DEFAULT NULL,
  `smtpserver` char(64) NOT NULL DEFAULT '',
  `smtpport` int(11) DEFAULT NULL,
  `use_ssl` int(11) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`smtpserver`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `memory_usage` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `pg_used_im` int(11) DEFAULT '0',
  `pg_used_dm` int(11) DEFAULT '0',
  `pg_tot_im` int(11) DEFAULT '0',
  `pg_tot_dm` int(11) DEFAULT '0',
  `pg_sz_dm` int(11) DEFAULT '0',
  `pg_sz_im` int(11) DEFAULT '0',
  `dm_used_mb` int(11) DEFAULT '0',
  `im_used_mb` int(11) DEFAULT '0',
  `dm_total_mb` int(11) DEFAULT '0',
  `im_total_mb` int(11) DEFAULT '0',
  PRIMARY KEY (`cid`,`nodeid`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_memory_usage`;
DELIMITER //
CREATE TRIGGER `it_memory_usage` AFTER INSERT ON `memory_usage`
 FOR EACH ROW BEGIN

    DECLARE dm_memory_usage float;
    DECLARE im_memory_usage float;
    DECLARE _hostname varchar(255);
    DECLARE _node_type varchar(255);
    DECLARE _cluster_state varchar(255);
    DECLARE _indexmemory_warning char(255);
    DECLARE _indexmemory_critical char(255);
    DECLARE _datamemory_warning char(255);
    DECLARE _datamemory_critical char(255);
    DECLARE _severity char(255);
    DECLARE _alarm_count int(11);
    DECLARE _pg_used_im int(20);
    DECLARE _pg_used_dm int(20);
    DECLARE _pg_tot_im int(20);
    DECLARE _pg_tot_dm int(20);
    DECLARE _pg_sz_dm int(20);
    DECLARE _pg_sz_im int(20);
    DECLARE _dm_used_mb int(20);
    DECLARE _im_used_mb int(20);
    DECLARE _dm_total_mb int(20);
    DECLARE _im_total_mb int(20);
    

                SELECT IFNULL((dm_used_mb  / dm_total_mb)*100,0) INTO dm_memory_usage FROM memory_usage WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
                SELECT IFNULL((im_used_mb  / im_total_mb)*100,0) INTO im_memory_usage FROM memory_usage WHERE nodeid=NEW.nodeid AND cid=NEW.cid;

                SELECT IFNULL(sum(pg_used_im),0),IFNULL(sum(pg_used_dm),0),IFNULL(sum(pg_tot_im),0),IFNULL(sum(pg_tot_dm),0),IFNULL(sum(pg_sz_dm),0),IFNULL(sum(pg_sz_im),0),IFNULL(sum(dm_used_mb),0),IFNULL(sum(im_used_mb),0),IFNULL(sum(dm_total_mb),0),IFNULL(sum(im_total_mb),0) INTO _pg_used_im,_pg_used_dm,_pg_tot_im,_pg_tot_dm,_pg_sz_dm,_pg_sz_im,_dm_used_mb,_im_used_mb,_dm_total_mb,_im_total_mb FROM memory_usage WHERE cid=NEW.cid;  

                SELECT value INTO _indexmemory_warning FROM cmon_configuration WHERE param='INDEXMEMORY_WARNING' AND cid=NEW.cid;
                SELECT value INTO _indexmemory_critical FROM cmon_configuration WHERE param='INDEXMEMORY_CRITICAL' AND cid=NEW.cid;                                                         
                
                SELECT value INTO _datamemory_warning FROM cmon_configuration WHERE param='DATAMEMORY_WARNING ' AND cid=NEW.cid;
                SELECT value INTO _datamemory_critical FROM cmon_configuration WHERE param='DATAMEMORY_CRITICAL' AND cid=NEW.cid;

    INSERT IGNORE INTO memory_usage_history(cid, 
                                    nodeid, 
                                    report_ts, 
                                    pg_used_im, 
                                    pg_used_dm, 
                                    pg_tot_im, 
                                    pg_tot_dm, 
                                    pg_sz_dm, 
                                    pg_sz_im, 
                                    dm_used_mb, 
                                    im_used_mb, 
                                    dm_total_mb, 
                                    im_total_mb)
    VALUES( NEW.cid, 
            NEW.nodeid, 
            NEW.report_ts, 
            NEW.pg_used_im, 
            NEW.pg_used_dm, 
            NEW.pg_tot_im, 
            NEW.pg_tot_dm, 
            NEW.pg_sz_dm, 
            NEW.pg_sz_im, 
            NEW.dm_used_mb, 
            NEW.im_used_mb, 
            NEW.dm_total_mb, 
            NEW.im_total_mb);
    

    INSERT IGNORE INTO memory_usage_history(cid, 
                                    nodeid, 
                                    report_ts, 
                                    pg_used_im, 
                                    pg_used_dm, 
                                    pg_tot_im, 
                                    pg_tot_dm, 
                                    pg_sz_dm, 
                                    pg_sz_im, 
                                    dm_used_mb, 
                                    im_used_mb, 
                                    dm_total_mb, 
                                    im_total_mb)
    VALUES( NEW.cid, 
            0, 
            NEW.report_ts, 
            _pg_used_im, 
            _pg_used_dm, 
            _pg_tot_im, 
            _pg_tot_dm, 
            _pg_sz_dm, 
            _pg_sz_im, 
            _dm_used_mb, 
            _im_used_mb, 
            _dm_total_mb, 
            _im_total_mb);

   IF (dm_memory_usage  >= _datamemory_warning && dm_memory_usage < _datamemory_critical)
    THEN

    SET _severity='WARNING'; 


   ELSEIF (dm_memory_usage >= _datamemory_critical)  
    THEN

    SET _severity='CRITICAL'; 



   ELSEIF (dm_memory_usage < _datamemory_warning)
    THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
        
	DELETE FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name='Data Memory Usage' AND component=_node_type;
   
    END IF;

   IF ((dm_memory_usage  >= _datamemory_warning && dm_memory_usage < _datamemory_critical)||(dm_memory_usage >= _datamemory_critical))
   THEN
        SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.nodeid AND cid=NEW.cid;
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;

        SELECT status INTO _cluster_state FROM cluster_state where id=NEW.cid;

        SELECT COUNT(*) as count INTO _alarm_count FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name='Data Memory Usage' AND component=_node_type;
               
        SET _alarm_count=_alarm_count+1;

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(NEW.cid,
           NEW.nodeid,
           _node_type,
           'Data Memory Usage',
           _alarm_count,
           DEFAULT ,
             DEFAULT,
              DEFAULT,
              _cluster_state,
           _severity,
              DEFAULT,
           Concat ('Data Memory Utilization is ',dm_memory_usage,' percent'),
	   Concat ('Increase Data Memory on Node'),
           _hostname,
           NOW()
         ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,cluster_state=_cluster_state,hostname=_hostname, report_ts=now(), severity=_severity, description=Concat ('Data Memory Utilization is ',dm_memory_usage,' percent');

   END IF;


    IF (im_memory_usage  >= _indexmemory_warning && im_memory_usage < _indexmemory_critical)
    THEN
  
    SET _severity='WARNING'; 

 
    ELSEIF (im_memory_usage >= _indexmemory_critical)
    THEN

    SET _severity='CRITICAL'; 


    ELSEIF (im_memory_usage < _indexmemory_warning)
    THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
	DELETE FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name='Index Memory Usage' AND component=_node_type;


    END IF;

    IF ((im_memory_usage  >= _indexmemory_warning && im_memory_usage < _indexmemory_critical)||(im_memory_usage >= _indexmemory_critical))
    THEN
        SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.nodeid AND cid=NEW.cid;
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;

        SELECT status INTO _cluster_state FROM cluster_state where id=NEW.cid;

        SELECT COUNT(*) as count INTO _alarm_count FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name='Index Memory Usage' AND component=_node_type;
               
        SET _alarm_count=_alarm_count+1;

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(NEW.cid,
           NEW.nodeid,
           _node_type,
           'Index Memory Usage',
           _alarm_count,
           DEFAULT ,
             DEFAULT,
              DEFAULT,
              _cluster_state,
           _severity,
              DEFAULT,
           Concat ('Index Memory Utilization is ',im_memory_usage,' percent'),
	   Concat ('Increase Index Memory on Node'),
           _hostname,
           NOW()
         ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,cluster_state=_cluster_state,hostname=_hostname,report_ts=now(), severity=_severity, description=Concat ('Index Memory Utilization is ',im_memory_usage,' percent');

    END IF;

    

END
//
DELIMITER ;
DROP TRIGGER IF EXISTS `ut_memory_usage`;
DELIMITER //
CREATE TRIGGER `ut_memory_usage` AFTER UPDATE ON `memory_usage`
 FOR EACH ROW BEGIN

    DECLARE dm_memory_usage float;
    DECLARE im_memory_usage float;
    DECLARE _hostname varchar(255);
    DECLARE _node_type varchar(255);
    DECLARE _cluster_state varchar(255);
    DECLARE _indexmemory_warning char(255);
    DECLARE _indexmemory_critical char(255);
    DECLARE _datamemory_warning char(255);
    DECLARE _datamemory_critical char(255);
    DECLARE _severity char(255);
    DECLARE _alarm_count int(11);
    DECLARE _pg_used_im int(20);
    DECLARE _pg_used_dm int(20);
    DECLARE _pg_tot_im int(20);
    DECLARE _pg_tot_dm int(20);
    DECLARE _pg_sz_dm int(20);
    DECLARE _pg_sz_im int(20);
    DECLARE _dm_used_mb int(20);
    DECLARE _im_used_mb int(20);
    DECLARE _dm_total_mb int(20);
    DECLARE _im_total_mb int(20);
    

                SELECT IFNULL((dm_used_mb  / dm_total_mb)*100,0) INTO dm_memory_usage FROM memory_usage WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
                SELECT IFNULL((im_used_mb  / im_total_mb)*100,0) INTO im_memory_usage FROM memory_usage WHERE nodeid=NEW.nodeid AND cid=NEW.cid;

                SELECT IFNULL(sum(pg_used_im),0),IFNULL(sum(pg_used_dm),0),IFNULL(sum(pg_tot_im),0),IFNULL(sum(pg_tot_dm),0),IFNULL(sum(pg_sz_dm),0),IFNULL(sum(pg_sz_im),0),IFNULL(sum(dm_used_mb),0),IFNULL(sum(im_used_mb),0),IFNULL(sum(dm_total_mb),0),IFNULL(sum(im_total_mb),0) INTO _pg_used_im,_pg_used_dm,_pg_tot_im,_pg_tot_dm,_pg_sz_dm,_pg_sz_im,_dm_used_mb,_im_used_mb,_dm_total_mb,_im_total_mb FROM memory_usage WHERE cid=NEW.cid;  

                SELECT value INTO _indexmemory_warning FROM cmon_configuration WHERE param='INDEXMEMORY_WARNING' AND cid=NEW.cid;
                SELECT value INTO _indexmemory_critical FROM cmon_configuration WHERE param='INDEXMEMORY_CRITICAL' AND cid=NEW.cid;                                                         
                
                SELECT value INTO _datamemory_warning FROM cmon_configuration WHERE param='DATAMEMORY_WARNING ' AND cid=NEW.cid;
                SELECT value INTO _datamemory_critical FROM cmon_configuration WHERE param='DATAMEMORY_CRITICAL' AND cid=NEW.cid;

    INSERT IGNORE INTO memory_usage_history(cid, 
                                    nodeid, 
                                    report_ts, 
                                    pg_used_im, 
                                    pg_used_dm, 
                                    pg_tot_im, 
                                    pg_tot_dm, 
                                    pg_sz_dm, 
                                    pg_sz_im, 
                                    dm_used_mb, 
                                    im_used_mb, 
                                    dm_total_mb, 
                                    im_total_mb)
    VALUES( NEW.cid, 
            NEW.nodeid, 
            NEW.report_ts, 
            NEW.pg_used_im, 
            NEW.pg_used_dm, 
            NEW.pg_tot_im, 
            NEW.pg_tot_dm, 
            NEW.pg_sz_dm, 
            NEW.pg_sz_im, 
            NEW.dm_used_mb, 
            NEW.im_used_mb, 
            NEW.dm_total_mb, 
            NEW.im_total_mb);
    

    INSERT IGNORE INTO memory_usage_history(cid, 
                                    nodeid, 
                                    report_ts, 
                                    pg_used_im, 
                                    pg_used_dm, 
                                    pg_tot_im, 
                                    pg_tot_dm, 
                                    pg_sz_dm, 
                                    pg_sz_im, 
                                    dm_used_mb, 
                                    im_used_mb, 
                                    dm_total_mb, 
                                    im_total_mb)
    VALUES( NEW.cid, 
            0, 
            NEW.report_ts, 
            _pg_used_im, 
            _pg_used_dm, 
            _pg_tot_im, 
            _pg_tot_dm, 
            _pg_sz_dm, 
            _pg_sz_im, 
            _dm_used_mb, 
            _im_used_mb, 
            _dm_total_mb, 
            _im_total_mb);

   IF (dm_memory_usage  >= _datamemory_warning && dm_memory_usage < _datamemory_critical)
    THEN

    SET _severity='WARNING'; 


   ELSEIF (dm_memory_usage >= _datamemory_critical)  
    THEN

    SET _severity='CRITICAL'; 



   ELSEIF (dm_memory_usage < _datamemory_warning)
    THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
        
	DELETE FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name='Data Memory Usage' AND component=_node_type;
   
    END IF;

   IF ((dm_memory_usage  >= _datamemory_warning && dm_memory_usage < _datamemory_critical)||(dm_memory_usage >= _datamemory_critical))
   THEN
        SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.nodeid AND cid=NEW.cid;
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;

        SELECT status INTO _cluster_state FROM cluster_state where id=NEW.cid;

        SELECT COUNT(*) as count INTO _alarm_count FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name='Data Memory Usage' AND component=_node_type;
               
        SET _alarm_count=_alarm_count+1;

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(NEW.cid,
           NEW.nodeid,
           _node_type,
           'Data Memory Usage',
           _alarm_count,
           DEFAULT ,
             DEFAULT,
              DEFAULT,
              _cluster_state,
           _severity,
              DEFAULT,
           Concat ('Data Memory Utilization is ',dm_memory_usage,' percent'),
	   Concat ('Increase Data Memory on Node'),
           _hostname,
           NOW()
         ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,cluster_state=_cluster_state,hostname=_hostname, report_ts=now(), severity=_severity, description=Concat ('Data Memory Utilization is ',dm_memory_usage,' percent');

   END IF;


    IF (im_memory_usage  >= _indexmemory_warning && im_memory_usage < _indexmemory_critical)
    THEN
  
    SET _severity='WARNING'; 

 
    ELSEIF (im_memory_usage >= _indexmemory_critical)
    THEN

    SET _severity='CRITICAL'; 


    ELSEIF (im_memory_usage < _indexmemory_warning)
    THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
	DELETE FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name='Index Memory Usage' AND component=_node_type;


    END IF;

    IF ((im_memory_usage  >= _indexmemory_warning && im_memory_usage < _indexmemory_critical)||(im_memory_usage >= _indexmemory_critical))
    THEN
        SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.nodeid AND cid=NEW.cid;
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;

        SELECT status INTO _cluster_state FROM cluster_state where id=NEW.cid;

        SELECT COUNT(*) as count INTO _alarm_count FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name='Index Memory Usage' AND component=_node_type;
               
        SET _alarm_count=_alarm_count+1;

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(NEW.cid,
           NEW.nodeid,
           _node_type,
           'Index Memory Usage',
           _alarm_count,
           DEFAULT ,
             DEFAULT,
              DEFAULT,
              _cluster_state,
           _severity,
              DEFAULT,
           Concat ('Index Memory Utilization is ',im_memory_usage,' percent'),
	   Concat ('Increase Index Memory on Node'),
           _hostname,
           NOW()
         ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,cluster_state=_cluster_state,hostname=_hostname,                report_ts=now(), severity=_severity, description=Concat ('Index Memory Utilization is ',im_memory_usage,' percent');

    END IF;

    

END
//
DELIMITER ;



CREATE TABLE IF NOT EXISTS `memory_usage_history` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `report_ts` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `pg_used_im` int(11) DEFAULT '0',
  `pg_used_dm` int(11) DEFAULT '0',
  `pg_tot_im` int(11) DEFAULT '0',
  `pg_tot_dm` int(11) DEFAULT '0',
  `pg_sz_dm` int(11) DEFAULT '0',
  `pg_sz_im` int(11) DEFAULT '0',
  `dm_used_mb` int(11) DEFAULT '0',
  `im_used_mb` int(11) DEFAULT '0',
  `dm_total_mb` int(11) DEFAULT '0',
  `im_total_mb` int(11) DEFAULT '0',
  PRIMARY KEY (`cid`,`nodeid`,`report_ts`),
  KEY `idx_memoryhistory_used` (`dm_used_mb`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS mysql_explains;
CREATE TABLE IF NOT EXISTS `mysql_explains` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `qid` bigint(20) unsigned NOT NULL DEFAULT '0',
  `partid` int(11) NOT NULL DEFAULT '0',
  `xid` int(11) NOT NULL DEFAULT '0',
  `xpartitions` varchar(64) NOT NULL DEFAULT '',
  `xselect_type` varchar(64) NOT NULL DEFAULT '',
  `xtable` varchar(64) NOT NULL DEFAULT '',
  `xtype` varchar(64) NOT NULL DEFAULT '',
  `xpossible_keys` varchar(255) NOT NULL DEFAULT '',
  `xkey` varchar(128) NOT NULL DEFAULT '',
  `xkey_len` int(11) NOT NULL DEFAULT '0',
  `xref` varchar(128) NOT NULL DEFAULT '',
  `xrows` int(11) NOT NULL DEFAULT '0',
  `xfiltered` varchar(8) NOT NULL DEFAULT '',
  `xextra` varchar(255) NOT NULL DEFAULT '',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`qid`,`partid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `mysql_global_statistics` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `var` varchar(64) NOT NULL DEFAULT '',
  `value` varchar(64) DEFAULT '0',
  `value1` varchar(64) DEFAULT '0',
  `value2` varchar(64) DEFAULT '0',
  `value3` varchar(64) DEFAULT '0',
  `report_ts` bigint(20) unsigned DEFAULT '0',
  `report_ts1` bigint(20) unsigned DEFAULT '0',
  `report_ts2` bigint(20) unsigned DEFAULT '0',
  `report_ts3` bigint(20) unsigned DEFAULT '0',
  PRIMARY KEY (`cid`,`var`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_mysql_global_statistics`;
DROP TRIGGER IF EXISTS `ut_mysql_global_statistics`;



/*DROP TABLE IF EXISTS `mysql_global_statistics_history`;*/
CREATE TABLE IF NOT EXISTS `mysql_global_statistics_history` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `var` varchar(64) NOT NULL DEFAULT '',
  `value` bigint(20) unsigned DEFAULT '0',
  `report_ts` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`cid`,`var`,`report_ts`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `mysql_global_statistics_hour`;
CREATE TABLE IF NOT EXISTS `mysql_global_statistics_hour` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `var` varchar(64) NOT NULL DEFAULT '',
  `value` varchar(64) DEFAULT '0',
  `report_ts` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`cid`,`var`,`report_ts`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*DROP TABLE IF EXISTS `mysql_statistics_history`;*/
CREATE TABLE IF NOT EXISTS `mysql_statistics_history` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `var` varchar(64) NOT NULL DEFAULT '',
  `value` bigint(20) unsigned DEFAULT '0',
  `report_ts` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`cid`,`id`,`var`,`report_ts`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/* DROP TABLE IF EXISTS `mysql_statistics_hour`; */
CREATE TABLE IF NOT EXISTS `mysql_statistics_hour` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `var` varchar(64) NOT NULL DEFAULT '',
  `value` varchar(64) DEFAULT '0',
  `report_ts` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`cid`,`id`,`var`,`report_ts`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;




DROP TABLE IF EXISTS `mysql_master_status`;
CREATE TABLE IF NOT EXISTS `mysql_master_status` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `serverid` int(11) NOT NULL DEFAULT '0',
  `File` varchar(255) DEFAULT NULL,
  `Position` bigint(20) DEFAULT '0',
  `Binlog_Do_Db` varchar(255) DEFAULT NULL,
  `Binlog_Ignore_Db` varchar(255) DEFAULT NULL,
  `Executed_Gtid_Set` varchar(255) DEFAULT '',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`serverid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `mysql_performance_meta` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `username` varchar(255) NOT NULL DEFAULT '',
  `password` varchar(255) DEFAULT '',
  `db` varchar(255) DEFAULT 'test',
  `socket` varchar(255) DEFAULT '',
  `status` varchar(255) DEFAULT '<empty>',
  `threads` int(11) DEFAULT '1',
  `runtime` int(11) DEFAULT '10',
  `periodicity` int(11) DEFAULT '300',
  PRIMARY KEY (`cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `mysql_performance_probes` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `probeid` int(11) NOT NULL DEFAULT '0',
  `err_no` int(11) NOT NULL DEFAULT '0',
  `active` int(11) NOT NULL DEFAULT '0',
  `statement` blob ,
  `err_msg` varchar(1024) DEFAULT '',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`probeid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `mysql_performance_results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL DEFAULT '0',
  `probeid` int(11) NOT NULL DEFAULT '0',
  `threads` int(11) NOT NULL DEFAULT '0',
  `connpool` int(11) NOT NULL DEFAULT '0',
  `exec_count` int(11) NOT NULL DEFAULT '0',
  `rows` int(11) NOT NULL DEFAULT '0',
  `avg` int(11) NOT NULL DEFAULT '0',
  `stdev_avg` int(11) NOT NULL DEFAULT '0',
  `max` int(11) NOT NULL DEFAULT '0',
  `pct` int(11) NOT NULL DEFAULT '0',
  `tps` int(11) NOT NULL DEFAULT '0',
  `stdev_tps` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,`cid`,`hostid`,`probeid`),
  KEY `cid` (`cid`,`hostid`,`probeid`,`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;




DROP TABLE IF EXISTS `mysql_processlist`;
CREATE TABLE IF NOT EXISTS `mysql_processlist` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `qid` bigint(20) NOT NULL DEFAULT '0',
  `user` varchar(255) NOT NULL DEFAULT '',
  `host` varchar(64) NOT NULL DEFAULT '',
  `db` varchar(64) NOT NULL DEFAULT '',
  `command` varchar(16) NOT NULL DEFAULT '',
  `time` int(11) NOT NULL DEFAULT '0',
  `state` varchar(128) NOT NULL DEFAULT '',
  `info` longtext,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`,`qid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `mysql_repl_bw` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `serverid` int(11) NOT NULL DEFAULT '0',
  `total_binlog_bytes` int(11) NOT NULL DEFAULT '0',
  `total_relay_bytes` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,`cid`,`serverid`),
  KEY `cid` (`cid`,`serverid`,`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;




DROP TABLE IF EXISTS `mysql_repl_link`;
CREATE TABLE IF NOT EXISTS `mysql_repl_link` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0', 
  `serverid` int(11) NOT NULL DEFAULT '0',
  `masterid` int(11) DEFAULT '0',
  `io_state` enum('REPL_IO_STARTED','REPL_IO_CONNECTING','REPL_IO_STOPPED','REPL_IO_NOT_DEF') DEFAULT 'REPL_IO_NOT_DEF',
  `sql_state` enum('REPL_SQL_STARTED','REPL_SQL_STOPPED','REPL_SQL_NOT_DEF') DEFAULT 'REPL_SQL_NOT_DEF',
  `seconds_behind` int(11) NOT NULL DEFAULT '0',
  `running` int(11) NOT NULL DEFAULT '0',
  `current_state` char(255) NOT NULL DEFAULT '',
  `previous_state` char(255) NOT NULL DEFAULT '',
  `expected_state` char(255) NOT NULL DEFAULT '',
  `binlog_growth` int(11) NOT NULL DEFAULT '0',
  `relay_growth` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `connected` tinyint(4) NOT NULL DEFAULT '0',
  `msg` char(255) NOT NULL DEFAULT '',
  `read_master_log_pos` bigint(20) DEFAULT '0',
  `exec_master_log_pos` bigint(20) DEFAULT '0',
  `curr_state` int(11) DEFAULT '0',
  `slave_sync` int(11) DEFAULT '0',
  `link_state` int(11) DEFAULT '0',
  PRIMARY KEY (`cid`, `nodeid`,`serverid`),
  KEY `cid` (`cid`,`hostid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `mysql_replication_recovery` (
  `id` int(11) AUTO_INCREMENT NOT NULL,
  `cid` int(11) NOT NULL DEFAULT '1',
  `serverid` int(11) NOT NULL DEFAULT '0',
  `master_hostname` varchar(255) DEFAULT NULL,
  `target_hostname` varchar(255) DEFAULT NULL,
  `master_port` int(11) DEFAULT '3306',
  `target_port` int(11) DEFAULT '3306',
  `master_logpos` bigint(20) DEFAULT '0',
  `master_logfile` varchar(255) DEFAULT NULL,
  `recovery_opt` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`cid`,`serverid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `mysql_server` (
  `id` int(11) NOT NULL DEFAULT '0', 
  `cid` int(11) NOT NULL DEFAULT '0', 
  `serverid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) DEFAULT '0',
  `hostname` char(255) NOT NULL DEFAULT '',
  `username` char(255) NOT NULL DEFAULT '',
  `password` char(255) NOT NULL DEFAULT '',
  `version` char(255) NOT NULL DEFAULT 'Unknown',
  `role` enum('none','master','slave','multi') DEFAULT 'none',
  `port` int(11) NOT NULL DEFAULT '3306',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `connected` tinyint(4) NOT NULL DEFAULT '0',
  `msg` char(255) NOT NULL DEFAULT '', 
  `failures` int(11) DEFAULT '0',
  `status` int(11) DEFAULT '0',
  `progress_acct` bigint(20) NOT NULL DEFAULT '0',	
  `affinity` bigint(20) NOT NULL DEFAULT '0',	
  PRIMARY KEY (`id`,`cid`,`serverid`),
  UNIQUE KEY `hostname` (`hostname`,`port`),
  KEY `cid` (`cid`,`serverid`),
  KEY `cid2` (`cid`,`nodeid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;




DROP TABLE IF EXISTS `mysql_slave_status`;
CREATE TABLE IF NOT EXISTS `mysql_slave_status` (
  `cid` int(11) NOT NULL DEFAULT '1', 
  `nodeid` int(11) NOT NULL DEFAULT '0', 
  `serverid` int(11) NOT NULL DEFAULT '0', 
  `epoch` bigint(20) NOT NULL DEFAULT '0',
  `Slave_IO_State` char(64) DEFAULT NULL,
  `Master_Host` varchar(255) DEFAULT NULL,
  `Master_User` varchar(255) DEFAULT NULL,
  `Master_Port` int(11) DEFAULT '0',
  `Connect_Retry` int(11) DEFAULT '0',
  `Master_Log_File` char(64) DEFAULT NULL,
  `Read_Master_Log_Pos` int(11) DEFAULT '0',
  `Relay_Log_File` char(64) DEFAULT NULL,
  `Relay_Log_Pos` int(11) DEFAULT '0',
  `Relay_Master_Log_File` char(64) DEFAULT NULL,
  `Slave_IO_Running` char(64) DEFAULT NULL,
  `Slave_SQL_Running` char(64) DEFAULT NULL,
  `Replicate_Do_DB` varchar(512) DEFAULT NULL,
  `Replicate_Ignore_DB` varchar(512) DEFAULT NULL,
  `Replicate_Do_Table` varchar(1024) DEFAULT NULL,
  `Replicate_Ignore_Table` varchar(1024) DEFAULT NULL,
  `Replicate_Wild_Do_Table` varchar(1024) DEFAULT NULL,
  `Replicate_Wild_Ignore_Table` varchar(1024) DEFAULT NULL,
  `Last_Errno` int(11) DEFAULT '0',
  `Last_Error` varchar(1024) DEFAULT NULL,
  `Skip_Counter` int(11) DEFAULT '0',
  `Exec_Master_Log_Pos` int(11) DEFAULT '0',
  `Relay_Log_Space` int(11) DEFAULT '0',
  `Until_Condition` char(128) DEFAULT 'None',
  `Until_Log_File` char(64) DEFAULT NULL,
  `Until_Log_Pos` int(11) DEFAULT '0',
  `Master_SSL_Allowed` char(64) DEFAULT 'No',
  `Master_SSL_CA_File` char(64) DEFAULT NULL,
  `Master_SSL_CA_Path` char(64) DEFAULT NULL,
  `Master_SSL_Cert` char(64) DEFAULT NULL,
  `Master_SSL_Cipher` char(64) DEFAULT NULL,
  `Master_SSL_Key` char(64) DEFAULT NULL,
  `Seconds_Behind_Master` char(64) DEFAULT NULL,
  `Master_SSL_Verify_Server_Cert` char(64) DEFAULT 'No',
  `Last_IO_Errno` int(11) DEFAULT '0',
  `Last_IO_Error` varchar(1024) DEFAULT NULL,
  `Last_SQL_Errno` int(11) DEFAULT '0',
  `Last_SQL_Error` varchar(1024) DEFAULT NULL,
  `Master_Bind` char(128) DEFAULT '0.0.0.0',
  `Replicate_Ignore_Server_Ids` char(128) DEFAULT NULL,
  `Master_Server_Id` int(11) DEFAULT NULL,
  `Master_UUID` char(64) DEFAULT NULL,
  `Master_Info_File` varchar(128) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `SQL_Delay` int(11) DEFAULT '0',
  `SQL_Remaining_Delay` varchar(64) DEFAULT NULL,
  `Slave_SQL_Running_State` varchar(255) DEFAULT NULL,
  `Master_Retry_Count` int(11) DEFAULT '86400',
  `Last_IO_Error_Timestamp` varchar(32) DEFAULT NULL,
  `Last_SQL_Error_Timestamp` varchar(32) DEFAULT NULL,
  `Master_SSL_Crl` varchar(255) DEFAULT '',
  `Master_SSL_Crlpath` varchar(255) DEFAULT '',
  `Retrieved_Gtid_Set` varchar(255) DEFAULT '',
  `Executed_Gtid_Set` varchar(255) DEFAULT '',
  `Auto_Position` varchar(255) DEFAULT '',
  PRIMARY KEY (`cid`, `nodeid`,`serverid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS mysql_slow_queries;
CREATE TABLE IF NOT EXISTS `mysql_slow_queries` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `qid` bigint(20) unsigned NOT NULL DEFAULT '0',
  `cnt` bigint(20) unsigned NOT NULL DEFAULT '0',
  `user` varchar(64) NOT NULL DEFAULT '',
  `host` varchar(64) NOT NULL DEFAULT '',
  `db` varchar(64) NOT NULL DEFAULT '',
  `command` varchar(16) DEFAULT '',
  `time` double DEFAULT '0',
  `state` varchar(16) DEFAULT '',
  `info` longtext ,
  `canonical` longtext ,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `lock_time` double DEFAULT '0',
  `rows_sent` int(10) unsigned DEFAULT '0',
  `rows_examined` int(10) unsigned DEFAULT '0',
  `total_time` double DEFAULT '0',
  `total_lock_time` double DEFAULT '0',
  PRIMARY KEY (`cid`,`id`,`qid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;


DROP TABLE IF EXISTS mysql_query_histogram;
CREATE TABLE IF NOT EXISTS `mysql_query_histogram` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `qid` bigint(20) unsigned NOT NULL DEFAULT '0',
  `cnt` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ts` bigint(20) unsigned NOT NULL DEFAULT '0',
  `query_time` double DEFAULT '0',
  `lock_time` double DEFAULT '0',	
  PRIMARY KEY (`cid`,`id`,`qid`,`ts`),
  KEY (`cid`,`id`, `ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

DROP TABLE IF EXISTS mysql_statistics;
CREATE TABLE IF NOT EXISTS `mysql_statistics` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `var` varchar(64) NOT NULL DEFAULT '',
  `value` varchar(64) DEFAULT '0',
  `value1` varchar(64) DEFAULT '0',
  `value2` varchar(64) DEFAULT '0',
  `value3` varchar(64) DEFAULT '0',
  `report_ts` bigint(20) NOT NULL DEFAULT '0',
  `report_ts1` bigint(20) NOT NULL DEFAULT '0',
  `report_ts2` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `report_ts3` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`cid`,`id`,`var`),
  KEY `id` (`id`,`var`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TABLE IF EXISTS mysql_statistics_tm;
CREATE TABLE IF NOT EXISTS `mysql_statistics_tm` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `sampleid` bigint(20) unsigned DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `var` varchar(64) NOT NULL DEFAULT '',
  `value` varchar(64) DEFAULT '0',
  `report_ts` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`cid`,`sampleid`,`nodeid`,`var`),
  KEY `report_ts` (`cid`,`report_ts`, `nodeid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `mysql_innodb_status` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `status` TEXT,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

DROP TRIGGER IF EXISTS `it_mysql_statistics`;
DROP TRIGGER IF EXISTS `ut_mysql_statistics`;


CREATE TABLE IF NOT EXISTS `mysql_variables` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `var` char(64) NOT NULL DEFAULT '',
  `value` varchar(2048) NOT NULL DEFAULT '',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`,`var`),
  KEY `var` (`var`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `ndbinfo_diskpagebuffer` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `block_instance` int(11) NOT NULL DEFAULT '0',
  `pages_written` bigint(20) DEFAULT '0',
  `pages_written_lcp` bigint(20) DEFAULT '0',
  `pages_read` bigint(20) DEFAULT '0',
  `log_waits` bigint(20) DEFAULT '0',
  `page_requests_direct_return` bigint(20) DEFAULT '0',
  `page_requests_wait_queue` bigint(20) DEFAULT '0',
  `page_requests_wait_io` bigint(20) DEFAULT '0',
  `hit_ratio` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



CREATE TABLE IF NOT EXISTS `ndbinfo_logbuffers` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `log_type` char(9) NOT NULL DEFAULT '',
  `log_id` int(11) NOT NULL DEFAULT '0',
  `log_part` int(11) NOT NULL DEFAULT '0',
  `total` bigint(20) DEFAULT '0',
  `used` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`log_type`,`log_part`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_ndbinfo_logbuffers`;
DELIMITER //
CREATE TRIGGER `it_ndbinfo_logbuffers` AFTER INSERT ON `ndbinfo_logbuffers`
 FOR EACH ROW BEGIN


    DECLARE _usage bigint (20); 
    DECLARE _hostname varchar(255);
    DECLARE _node_type varchar(255);
    DECLARE _cluster_state varchar(255);
    DECLARE _redobuffer_warning char(255);
    DECLARE _redobuffer_critical char(255);
    DECLARE _alarm_count int(11);
    DECLARE _severity char(255);
 


    SELECT IFNULL((used  / total)*100,0) INTO _usage
    FROM ndbinfo_logbuffers 
    WHERE cid = NEW.cid AND nodeid = NEW.nodeid AND log_type = NEW.log_type AND log_part = NEW.log_part
    GROUP BY cid, nodeid, log_type, log_part;

    SELECT value INTO _redobuffer_warning FROM cmon_configuration WHERE param='REDOBUFFER_WARNING' AND cid=NEW.cid;
                
    SELECT value INTO _redobuffer_critical FROM cmon_configuration WHERE param='REDOBUFFER_CRITICAL' AND cid=NEW.cid;


    INSERT INTO ndbinfo_logbuffers_history(cid,
                                           nodeid,
                                           log_type,
                                           total,
                                           used,
                                           report_ts)
    VALUES(NEW.cid,
           NEW.nodeid,
           NEW.log_type,
           NEW.total,
           NEW.used,
           NEW.report_ts);


    IF (_usage >= _redobuffer_warning && _usage < _redobuffer_critical)
    THEN
    
    SET _severity='WARNING'; 




    ELSEIF (_usage >= _redobuffer_critical)
    THEN
    
    SET _severity='CRITICAL'; 


    ELSEIF (_usage < _redobuffer_warning)
    THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
	DELETE FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name=NEW.log_type AND component=_node_type;


    END IF;

    IF ((_usage >= _redobuffer_warning && _usage < _redobuffer_critical)||(_usage >= _redobuffer_critical))
   THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
        SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.nodeid AND cid=NEW.cid;
        SELECT status INTO _cluster_state FROM cluster_state where id=NEW.cid;

        SELECT COUNT(*) as count INTO _alarm_count FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name=NEW.log_type AND component=_node_type;
               
        SET _alarm_count=_alarm_count+1;

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(NEW.cid,
           NEW.nodeid,
           _node_type,
           NEW.log_type,
           _alarm_count,
           DEFAULT ,
             DEFAULT,
              DEFAULT,
              _cluster_state,
           _severity,
              DEFAULT,
           Concat (NEW.log_type, ' Log Buffer utilization is ',_usage,' percent'),
	   Concat ('Increase ',NEW.log_type,' Buffer'),
           _hostname,
           NOW()
         ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,cluster_state=_cluster_state,hostname=_hostname,severity=_severity,report_ts=now(), description=Concat (NEW.log_type, ' Log Buffer utilization is ',_usage,' percent');

   END IF;

    

END
//
DELIMITER ;
DROP TRIGGER IF EXISTS `ut_ndbinfo_logbuffers`;
DELIMITER //
CREATE TRIGGER `ut_ndbinfo_logbuffers` AFTER UPDATE ON `ndbinfo_logbuffers`
 FOR EACH ROW BEGIN


    DECLARE _usage bigint (20); 
    DECLARE _hostname varchar(255);
    DECLARE _node_type varchar(255);
    DECLARE _cluster_state varchar(255);
    DECLARE _redobuffer_warning char(255);
    DECLARE _redobuffer_critical char(255);
    DECLARE _alarm_count int(11);
    DECLARE _severity char(255);
 


    SELECT IFNULL((used  / total)*100,0) INTO _usage
    FROM ndbinfo_logbuffers 
    WHERE cid = NEW.cid AND nodeid = NEW.nodeid AND log_type = NEW.log_type AND log_part = NEW.log_part
    GROUP BY cid, nodeid, log_type, log_part;

    SELECT value INTO _redobuffer_warning FROM cmon_configuration WHERE param='REDOBUFFER_WARNING' AND cid=NEW.cid;
                
    SELECT value INTO _redobuffer_critical FROM cmon_configuration WHERE param='REDOBUFFER_CRITICAL' AND cid=NEW.cid;


    INSERT INTO ndbinfo_logbuffers_history(cid,
                                           nodeid,
                                           log_type,
                                           total,
                                           used,
                                           report_ts)
    VALUES(NEW.cid,
           NEW.nodeid,
           NEW.log_type,
           NEW.total,
           NEW.used,
           NEW.report_ts);


    IF (_usage >= _redobuffer_warning && _usage < _redobuffer_critical)
    THEN
    
    SET _severity='WARNING'; 




    ELSEIF (_usage >= _redobuffer_critical)
    THEN
    
    SET _severity='CRITICAL'; 


    ELSEIF (_usage < _redobuffer_warning)
    THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
	DELETE FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name=NEW.log_type AND component=_node_type;


    END IF;

    IF ((_usage >= _redobuffer_warning && _usage < _redobuffer_critical)||(_usage >= _redobuffer_critical))
   THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
        SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.nodeid AND cid=NEW.cid;
        SELECT status INTO _cluster_state FROM cluster_state where id=NEW.cid;

        SELECT COUNT(*) as count INTO _alarm_count FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name=NEW.log_type AND component=_node_type;
               
        SET _alarm_count=_alarm_count+1;

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(NEW.cid,
           NEW.nodeid,
           _node_type,
           NEW.log_type,
           _alarm_count,
           DEFAULT ,
             DEFAULT,
              DEFAULT,
              _cluster_state,
           _severity,
              DEFAULT,
           Concat (NEW.log_type, ' Log Buffer utilization is ',_usage,' percent'),
	   Concat ('Increase ',NEW.log_type,' Buffer'),
           _hostname,
           NOW()
         ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,cluster_state=_cluster_state,hostname=_hostname, severity=_severity,report_ts=now(), description=Concat (NEW.log_type, ' Log Buffer utilization is ',_usage,' percent');


   END IF;

    

END
//
DELIMITER ;



CREATE TABLE IF NOT EXISTS `ndbinfo_logbuffers_history` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `log_type` char(9) NOT NULL DEFAULT '',
  `total` bigint(20) DEFAULT '0',
  `used` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`log_type`,`report_ts`),
  KEY `idx_redobufferhistory_used` (`used`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `ndbinfo_logspaces` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `log_type` char(9) NOT NULL DEFAULT '',
  `log_id` int(11) NOT NULL DEFAULT '0',
  `log_part` int(11) NOT NULL DEFAULT '0',
  `total` bigint(20) DEFAULT '0',
  `used` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`log_type`,`log_part`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_ndbinfo_logspaces`;
DELIMITER //
CREATE TRIGGER `it_ndbinfo_logspaces` AFTER INSERT ON `ndbinfo_logspaces`
 FOR EACH ROW BEGIN


    DECLARE _usage bigint (20); 
    DECLARE _hostname varchar(255);
    DECLARE _node_type varchar(255);
    DECLARE _cluster_state varchar(255);
    DECLARE _redolog_warning char(255);
    DECLARE _redolog_critical char(255);
    DECLARE _alarm_count int(11);
    DECLARE _severity char(255);



    SELECT IFNULL((used  / total)*100,0) INTO _usage
    FROM ndbinfo_logspaces 
    WHERE cid = NEW.cid AND nodeid = NEW.nodeid AND log_type = NEW.log_type AND log_part = NEW.log_part
    GROUP BY cid, nodeid, log_type, log_part;


    SELECT value INTO _redolog_warning FROM cmon_configuration WHERE param='REDOLOG_WARNING' AND cid=NEW.cid;
                
    SELECT value INTO _redolog_critical FROM cmon_configuration WHERE param='REDOLOG_CRITICAL' AND cid=NEW.cid;


    INSERT INTO ndbinfo_logspaces_history(cid,
                                           nodeid,
                                           log_type,
                                           total,
                                           used,
                                           report_ts)
    VALUES(NEW.cid,
           NEW.nodeid,
           NEW.log_type,
           NEW.total,
           NEW.used,
           NEW.report_ts);


    IF (_usage >= _redolog_warning && _usage < _redolog_critical)
    THEN
    
    SET _severity='WARNING'; 




    ELSEIF (_usage >= _redolog_critical)
    THEN
    
    SET _severity='CRITICAL'; 


    ELSEIF (_usage < _redolog_warning)
    THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
	DELETE FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name=NEW.log_type AND component=_node_type;


    END IF;

    IF ((_usage >= _redolog_warning && _usage < _redolog_critical)||(_usage >= _redolog_critical))
   THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
        SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.nodeid AND cid=NEW.cid;
        SELECT status INTO _cluster_state FROM cluster_state where id=NEW.cid;

        SELECT COUNT(*) as count INTO _alarm_count FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name=NEW.log_type AND component=_node_type;
               
        SET _alarm_count=_alarm_count+1;

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(NEW.cid,
           NEW.nodeid,
           _node_type,
           NEW.log_type,
           _alarm_count,
           DEFAULT ,
             DEFAULT,
              DEFAULT,
              _cluster_state,
           _severity,
              DEFAULT,
           Concat (NEW.log_type, ' Log utilization is ',_usage,' percent'),
	   Concat ('Increase ',NEW.log_type,' Log'),
           _hostname,
           NOW()
         ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,cluster_state=_cluster_state,hostname=_hostname, severity=_severity,report_ts=now(), description=(NEW.log_type, ' Log utilization is ',_usage,' percent');

   END IF;

    

END
//
DELIMITER ;
DROP TRIGGER IF EXISTS `ut_ndbinfo_logspaces`;
DELIMITER //
CREATE TRIGGER `ut_ndbinfo_logspaces` AFTER UPDATE ON `ndbinfo_logspaces`
 FOR EACH ROW BEGIN


    DECLARE _usage bigint (20); 
    DECLARE _hostname varchar(255);
    DECLARE _node_type varchar(255);
    DECLARE _cluster_state varchar(255);
    DECLARE _redolog_warning char(255);
    DECLARE _redolog_critical char(255);
    DECLARE _alarm_count int(11);
    DECLARE _severity char(255);



    SELECT IFNULL((used  / total)*100,0) INTO _usage
    FROM ndbinfo_logspaces 
    WHERE cid = NEW.cid AND nodeid = NEW.nodeid AND log_type = NEW.log_type AND log_part = NEW.log_part
    GROUP BY cid, nodeid, log_type, log_part;


    SELECT value INTO _redolog_warning FROM cmon_configuration WHERE param='REDOLOG_WARNING' AND cid=NEW.cid;
                
    SELECT value INTO _redolog_critical FROM cmon_configuration WHERE param='REDOLOG_CRITICAL' AND cid=NEW.cid;


    INSERT INTO ndbinfo_logspaces_history(cid,
                                           nodeid,
                                           log_type,
                                           total,
                                           used,
                                           report_ts)
    VALUES(NEW.cid,
           NEW.nodeid,
           NEW.log_type,
           NEW.total,
           NEW.used,
           NEW.report_ts);


    IF (_usage >= _redolog_warning && _usage < _redolog_critical)
    THEN
    
    SET _severity='WARNING'; 




    ELSEIF (_usage >= _redolog_critical)
    THEN
    
    SET _severity='CRITICAL'; 


    ELSEIF (_usage < _redolog_warning)
    THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
	DELETE FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name=NEW.log_type AND component=_node_type;


    END IF;

    IF ((_usage >= _redolog_warning && _usage < _redolog_critical)||(_usage >= _redolog_critical))
   THEN
        SELECT node_type INTO _node_type FROM node_state WHERE nodeid=NEW.nodeid AND cid=NEW.cid;
        SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.nodeid AND cid=NEW.cid;
        SELECT status INTO _cluster_state FROM cluster_state where id=NEW.cid;

        SELECT COUNT(*) as count INTO _alarm_count FROM alarm WHERE nodeid=NEW.nodeid AND cid=NEW.cid AND alarm_name=NEW.log_type AND component=_node_type;
               
        SET _alarm_count=_alarm_count+1;

    INSERT INTO alarm                      (cid,
                                           nodeid,
                                           component,
                                           alarm_name,
					   alarm_count,
                                           alarm_sent,
                                           alarm_sent_count,
                                           alarm_last_sent,
                                           cluster_state,
					   severity,
                                           exit_message,
					   description,
                                           recommendation,
                                           hostname,
                                           report_ts
                                           )
    VALUES(NEW.cid,
           NEW.nodeid,
           _node_type,
           NEW.log_type,
           _alarm_count,
           DEFAULT ,
             DEFAULT,
              DEFAULT,
              _cluster_state,
           _severity,
              DEFAULT,
           Concat (NEW.log_type, ' Log utilization is ',_usage,' percent'),
	   Concat ('Increase ',NEW.log_type,' Log'),
           _hostname,
           NOW()
         ) ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,cluster_state=_cluster_state,hostname=_hostname, severity=_severity,report_ts=now(), description=(NEW.log_type, ' Log utilization is ',_usage,' percent');

   END IF;

    

END
//
DELIMITER ;



CREATE TABLE IF NOT EXISTS `ndbinfo_logspaces_history` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `log_type` char(9) NOT NULL DEFAULT '',
  `total` bigint(20) DEFAULT '0',
  `used` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`log_type`,`report_ts`),
  KEY `idx_redospacehistory_used` (`used`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `net_stats` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL DEFAULT '0',
  `interface` char(16) NOT NULL DEFAULT '',
  `tx_bytes_sec` int(11) NOT NULL DEFAULT '0',
  `rx_bytes_sec` int(11) NOT NULL DEFAULT '0',
  `tx_errors` int(11) NOT NULL DEFAULT '0',
  `rx_errors` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`hostid`,`interface`),
  KEY `report_ts` (`report_ts`),
  KEY `idx_netstats_tx` (`tx_bytes_sec`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_net_stats`;
DROP TRIGGER IF EXISTS `ut_net_stats`;



CREATE TABLE IF NOT EXISTS `net_stats_history` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `id` int(11) NOT NULL DEFAULT '0',
  `interface` char(16) NOT NULL DEFAULT '',
  `tx_bytes_sec` int(11) NOT NULL DEFAULT '0',
  `rx_bytes_sec` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`,`interface`,`report_ts`),
  KEY `idx_report_ts` (`report_ts`, `cid`),
  KEY `idx_netstats_tx` (`tx_bytes_sec`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `node_state` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `status` enum('STARTED','NOT_STARTED','SINGLEUSER','RESUME','RESTARTING','SHUTTING_DOWN','NO_CONTACT','STARTING','UNKNOWN','CONNECTED','DISCONNECTED') DEFAULT NULL,
  `node_type` enum('NDBD','API','NDB_MGMD') DEFAULT NULL,
  `nodegroup` int(11) DEFAULT NULL,
  `host` char(32) DEFAULT NULL,
  `version` char(64) DEFAULT NULL,
  `disconnects` int(11) DEFAULT '0',
  `start_phase` int(11) DEFAULT '0',
  `uptime` int(11) DEFAULT '0',
  `failed_restarts` int(11) DEFAULT '0',
  `startok` int(11) DEFAULT '0',
  `hostid` int(11) DEFAULT '0',
  `start_mode` enum('NR','INR') DEFAULT 'NR',
  `last_disconnect` datetime DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`),
  KEY `node_type` (`node_type`,`nodeid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `node_statistics` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `operations` bigint(20) DEFAULT '0',
  `transactions` bigint(20) DEFAULT '0',
  `commits` bigint(20) DEFAULT '0',
  `writes` bigint(20) DEFAULT '0',
  `reads_all` bigint(20) DEFAULT '0',
  `simple_reads` bigint(20) DEFAULT '0',
  `aborts` bigint(20) DEFAULT '0',
  `attrinfo` bigint(20) DEFAULT '0',
  `table_scans` bigint(20) DEFAULT '0',
  `range_scans` bigint(20) DEFAULT '0',
  `reads_received` bigint(20) DEFAULT '0',
  `local_reads_sent` bigint(20) DEFAULT '0',
  `local_writes` bigint(20) DEFAULT '0',
  `local_reads` bigint(20) DEFAULT '0',
  `remote_reads_sent` bigint(20) DEFAULT '0',
  `reads_not_found` bigint(20) DEFAULT '0',
  `table_scans_received` bigint(20) DEFAULT '0',
  `local_table_scans_sent` bigint(20) DEFAULT '0',
  `range_scans_received` bigint(20) DEFAULT '0',
  `local_range_scans_sent` bigint(20) DEFAULT '0',
  `remote_range_scans_sent` bigint(20) DEFAULT '0',
  `scan_batches_returned` bigint(20) DEFAULT '0',
  `scan_rows_returned` bigint(20) DEFAULT '0',
  `pruned_range_scans_received` bigint(20) DEFAULT '0',
  `const_pruned_range_scans_received` bigint(20) DEFAULT '0',
  `lqhkey_overload` bigint(20) DEFAULT '0',
  `lqhkey_overload_tc` bigint(20) DEFAULT '0',
  `lqhkey_overload_subscriber` bigint(20) DEFAULT '0',
  `lqhkey_overload_reader` bigint(20) DEFAULT '0',
  `lqhkey_overload_node_peer` bigint(20) DEFAULT '0',
  `lqhkey_overload_node_subscriber` bigint(20) DEFAULT '0',
  `lqhscan_slowdowns` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `node_statistics_history` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `operations` bigint(20) DEFAULT '0',
  `transactions` bigint(20) DEFAULT '0',
  `commits` bigint(20) DEFAULT '0',
  `writes` bigint(20) DEFAULT '0',
  `reads_all` bigint(20) DEFAULT '0',
  `simple_reads` bigint(20) DEFAULT '0',
  `aborts` bigint(20) DEFAULT '0',
  `attrinfo` bigint(20) DEFAULT '0',
  `table_scans` bigint(20) DEFAULT '0',
  `range_scans` bigint(20) DEFAULT '0',
  `reads_received` bigint(20) DEFAULT '0',
  `local_reads_sent` bigint(20) DEFAULT '0',
  `local_writes` bigint(20) DEFAULT '0',
  `local_reads` bigint(20) DEFAULT '0',
  `remote_reads_sent` bigint(20) DEFAULT '0',
  `reads_not_found` bigint(20) DEFAULT '0',
  `table_scans_received` bigint(20) DEFAULT '0',
  `local_table_scans_sent` bigint(20) DEFAULT '0',
  `range_scans_received` bigint(20) DEFAULT '0',
  `local_range_scans_sent` bigint(20) DEFAULT '0',
  `remote_range_scans_sent` bigint(20) DEFAULT '0',
  `scan_batches_returned` bigint(20) DEFAULT '0',
  `scan_rows_returned` bigint(20) DEFAULT '0',
  `pruned_range_scans_received` bigint(20) DEFAULT '0',
  `const_pruned_range_scans_received` bigint(20) DEFAULT '0',
  `lqhkey_overload` bigint(20) DEFAULT '0',
  `lqhkey_overload_tc` bigint(20) DEFAULT '0',
  `lqhkey_overload_subscriber` bigint(20) DEFAULT '0',
  `lqhkey_overload_reader` bigint(20) DEFAULT '0',
  `lqhkey_overload_node_peer` bigint(20) DEFAULT '0',
  `lqhkey_overload_node_subscriber` bigint(20) DEFAULT '0',
  `lqhscan_slowdowns` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`report_ts`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


DROP TRIGGER IF EXISTS `it_node_statistics`;
DELIMITER //
CREATE TRIGGER `it_node_statistics` BEFORE INSERT ON `node_statistics`
 FOR EACH ROW BEGIN

   	DECLARE _operations bigint(20);
	DECLARE _transactions bigint(20);
        DECLARE _commits bigint(20);
        DECLARE _writes bigint(20);
        DECLARE _reads_all bigint(20);
        DECLARE _simple_reads bigint(20);
        DECLARE _aborts bigint(20);
        DECLARE _attrinfo bigint(20);
        DECLARE _table_scans bigint(20);
        DECLARE _range_scans bigint(20);
        DECLARE _reads_received bigint(20);
        DECLARE _local_reads_sent bigint(20);
        DECLARE _local_reads bigint(20);
        DECLARE _local_writes bigint(20);
        DECLARE _remote_reads_sent bigint(20);
        DECLARE _reads_not_found bigint(20);
        DECLARE _table_scans_received bigint(20);
        DECLARE _local_table_scans_sent bigint(20);
        DECLARE _range_scans_received bigint(20);
        DECLARE _local_range_scans_sent bigint(20);
        DECLARE _remote_range_scans_sent bigint(20);
        DECLARE _scan_batches_returned bigint(20);
        DECLARE _scan_rows_returned bigint(20);
        DECLARE _pruned_range_scans_received bigint(20);
        DECLARE _const_pruned_range_scans_received bigint(20);
         
        SELECT IFNULL(operations,0),IFNULL(transactions,0),IFNULL(commits,0),IFNULL(writes,0),IFNULL(reads_all,0),IFNULL(simple_reads,0),IFNULL(aborts,0),IFNULL(attrinfo,0),IFNULL(table_scans,0),IFNULL(range_scans,0),IFNULL(reads_received,0),IFNULL(local_reads_sent,0),IFNULL(local_reads,0), IFNULL(local_writes,0), IFNULL(remote_reads_sent,0),IFNULL(reads_not_found,0),IFNULL(table_scans_received,0),IFNULL(local_table_scans_sent,0),IFNULL(range_scans_received,0),IFNULL(local_range_scans_sent,0),IFNULL(remote_range_scans_sent,0),IFNULL(scan_batches_returned,0),IFNULL(scan_rows_returned,0),IFNULL(pruned_range_scans_received,0),IFNULL(const_pruned_range_scans_received,0) INTO _operations,_transactions,_commits,_writes,_reads_all,_simple_reads,_aborts,_attrinfo,_table_scans,_range_scans,_reads_received,_local_reads_sent,_local_reads, _local_writes,  _remote_reads_sent,_reads_not_found,_table_scans_received,_local_table_scans_sent,_range_scans_received,_local_range_scans_sent,_remote_range_scans_sent,_scan_batches_returned,_scan_rows_returned,_pruned_range_scans_received,_const_pruned_range_scans_received FROM node_statistics WHERE cid  =NEW.cid AND nodeid=NEW.nodeid; 
                                                      


                 REPLACE INTO node_statistics_history               ( cid,  
                                                                        nodeid,                              
								        operations,                        
									transactions,                      
									commits,                           
									writes,                            
									reads_all,                         
									simple_reads,                      
									aborts,                            
									attrinfo,                          
									table_scans,                       
									range_scans,                       
									reads_received,                    
									local_reads,                  
									local_writes,                  
									local_reads_sent,                  
									remote_reads_sent,                 
									reads_not_found,                   
									table_scans_received,              
									local_table_scans_sent,            
									range_scans_received,              
									local_range_scans_sent,            
									remote_range_scans_sent,           
									scan_batches_returned,             
									scan_rows_returned,                
									pruned_range_scans_received,       
									const_pruned_range_scans_received, 
									report_ts

									)

              VALUES                            		      ( NEW.cid,    
                                                                        NEW.nodeid,                            
								        NEW.operations-_operations,                        
									NEW.transactions-_transactions,                      
									NEW.commits-_commits,                           
									NEW.writes-_writes,                            
									NEW.reads_all-_reads_all,                         
									NEW.simple_reads-_simple_reads,                      
									NEW.aborts-_aborts,                            
									NEW.attrinfo-_attrinfo,                          
									NEW.table_scans-_table_scans,                       
									NEW.range_scans-_range_scans,                       
									NEW.reads_received-_reads_received,                    
									NEW.local_reads-_local_reads,                  
									NEW.local_writes-_local_writes,                  
									NEW.local_reads_sent-_local_reads_sent,                  
									NEW.remote_reads_sent-_remote_reads_sent,                 
									NEW.reads_not_found-_reads_not_found,                   
									NEW.table_scans_received-_table_scans_received,              
									NEW.local_table_scans_sent-_local_table_scans_sent,            
									NEW.range_scans_received-_range_scans_received,              
									NEW.local_range_scans_sent-_local_range_scans_sent,            
									NEW.remote_range_scans_sent-_remote_range_scans_sent,           
									NEW.scan_batches_returned-_scan_batches_returned,             
									NEW.scan_rows_returned-_scan_rows_returned,                
									NEW.pruned_range_scans_received-_pruned_range_scans_received,       
									NEW.const_pruned_range_scans_received-_const_pruned_range_scans_received, 
									NEW.report_ts

									) ;                     

		

               

				


	       

END
//
DELIMITER ;
DROP TRIGGER IF EXISTS `ut_node_statistics`;
DELIMITER //
CREATE TRIGGER `ut_node_statistics` BEFORE UPDATE ON `node_statistics`
 FOR EACH ROW BEGIN

   	DECLARE _operations bigint(20);
	DECLARE _transactions bigint(20);
        DECLARE _commits bigint(20);
        DECLARE _writes bigint(20);
        DECLARE _reads_all bigint(20);
        DECLARE _simple_reads bigint(20);
        DECLARE _aborts bigint(20);
        DECLARE _attrinfo bigint(20);
        DECLARE _table_scans bigint(20);
        DECLARE _range_scans bigint(20);
        DECLARE _reads_received bigint(20);
        DECLARE _local_reads bigint(20);
        DECLARE _local_writes bigint(20);
        DECLARE _local_reads_sent bigint(20);
        DECLARE _remote_reads_sent bigint(20);
        DECLARE _reads_not_found bigint(20);
        DECLARE _table_scans_received bigint(20);
        DECLARE _local_table_scans_sent bigint(20);
        DECLARE _range_scans_received bigint(20);
        DECLARE _local_range_scans_sent bigint(20);
        DECLARE _remote_range_scans_sent bigint(20);
        DECLARE _scan_batches_returned bigint(20);
        DECLARE _scan_rows_returned bigint(20);
        DECLARE _pruned_range_scans_received bigint(20);
        DECLARE _const_pruned_range_scans_received bigint(20);
         
        SELECT IFNULL(operations,0),IFNULL(transactions,0),IFNULL(commits,0),IFNULL(writes,0),IFNULL(reads_all,0),IFNULL(simple_reads,0),IFNULL(aborts,0),IFNULL(attrinfo,0),IFNULL(table_scans,0),IFNULL(range_scans,0),IFNULL(reads_received,0),IFNULL(local_reads_sent,0),IFNULL(local_reads,0), IFNULL(local_writes,0) ,IFNULL(remote_reads_sent,0),IFNULL(reads_not_found,0),IFNULL(table_scans_received,0),IFNULL(local_table_scans_sent,0),IFNULL(range_scans_received,0),IFNULL(local_range_scans_sent,0),IFNULL(remote_range_scans_sent,0),IFNULL(scan_batches_returned,0),IFNULL(scan_rows_returned,0),IFNULL(pruned_range_scans_received,0),IFNULL(const_pruned_range_scans_received,0) INTO _operations,_transactions,_commits,_writes,_reads_all,_simple_reads,_aborts,_attrinfo,_table_scans,_range_scans,_reads_received,_local_reads_sent,_local_reads, _local_writes,  _remote_reads_sent,_reads_not_found,_table_scans_received,_local_table_scans_sent,_range_scans_received,_local_range_scans_sent,_remote_range_scans_sent,_scan_batches_returned,_scan_rows_returned,_pruned_range_scans_received,_const_pruned_range_scans_received FROM node_statistics WHERE cid  =NEW.cid AND nodeid=NEW.nodeid; 
                                                      


                 REPLACE INTO node_statistics_history               ( cid,  
                                                                        nodeid,                              
								        operations,                        
									transactions,                      
									commits,                           
									writes,                            
									reads_all,                         
									simple_reads,                      
									aborts,                            
									attrinfo,                          
									table_scans,                       
									range_scans,                       
									reads_received,                    
									local_reads_sent,                  
									local_reads,                  
									local_writes,                  
									remote_reads_sent,                 
									reads_not_found,                   
									table_scans_received,              
									local_table_scans_sent,            
									range_scans_received,              
									local_range_scans_sent,            
									remote_range_scans_sent,           
									scan_batches_returned,             
									scan_rows_returned,                
									pruned_range_scans_received,       
									const_pruned_range_scans_received, 
									report_ts

									)

              VALUES                            		      ( NEW.cid,    
                                                                        NEW.nodeid,                            
								        NEW.operations-_operations,                        
									NEW.transactions-_transactions,                      
									NEW.commits-_commits,                           
									NEW.writes-_writes,                            
									NEW.reads_all-_reads_all,                         
									NEW.simple_reads-_simple_reads,                      
									NEW.aborts-_aborts,                            
									NEW.attrinfo-_attrinfo,                          
									NEW.table_scans-_table_scans,                       
									NEW.range_scans-_range_scans,                       
									NEW.reads_received-_reads_received,                    
									NEW.local_reads_sent-_local_reads_sent,                  
									NEW.local_reads-_local_reads,                  
									NEW.local_writes-_local_writes,                  
									NEW.remote_reads_sent-_remote_reads_sent,                 
									NEW.reads_not_found-_reads_not_found,                   
									NEW.table_scans_received-_table_scans_received,              
									NEW.local_table_scans_sent-_local_table_scans_sent,            
									NEW.range_scans_received-_range_scans_received,              
									NEW.local_range_scans_sent-_local_range_scans_sent,            
									NEW.remote_range_scans_sent-_remote_range_scans_sent,           
									NEW.scan_batches_returned-_scan_batches_returned,             
									NEW.scan_rows_returned-_scan_rows_returned,                
									NEW.pruned_range_scans_received-_pruned_range_scans_received,       
									NEW.const_pruned_range_scans_received-_const_pruned_range_scans_received, 
									NEW.report_ts

									) ;                     

		

               

				


	       

END
//
DELIMITER ;


DROP TABLE  IF EXISTS `processes`;

CREATE TABLE  IF NOT EXISTS `processes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `hid` int(11) NOT NULL DEFAULT '0',
  `nodeid` int(11) DEFAULT '0',
  `process` char(255) NOT NULL DEFAULT '',
  `exec_cmd` char(255) NOT NULL DEFAULT '',
  `pidfile` char(255) NOT NULL DEFAULT '',
  `pgrep_expr` varchar(255) DEFAULT '',
  `failed_restarts` int(11) DEFAULT '0',
  `status` int(11) DEFAULT '0',
  `active` tinyint(11) DEFAULT '1',
  `custom` tinyint(11) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `msg` char(255) DEFAULT '',
  PRIMARY KEY (`id`,`cid`),
  UNIQUE KEY `cid` (`cid`,`hid`,`process`,`pidfile`),
  KEY (`nodeid`,`cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `ram_stats` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL DEFAULT '0',
  `total_bytes` int(11) DEFAULT NULL,
  `free_bytes` int(11) DEFAULT NULL,
  `buffers_bytes` int(11) DEFAULT NULL,
  `cached_bytes` int(11) DEFAULT NULL,
  `swap_total_bytes` int(11) DEFAULT NULL,
  `swap_free_bytes` int(11) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`),
  KEY `idx_ramstats_tx` (`free_bytes`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



DROP TRIGGER IF EXISTS `it_ram_stats`;
DELIMITER //
CREATE TRIGGER `it_ram_stats` AFTER INSERT ON `ram_stats`
 FOR EACH ROW BEGIN

   	DECLARE _ram_usage float;
        DECLARE _swap_used int(11);
	DECLARE _hostname varchar(255);
        DECLARE _ram_warning char(255);
        DECLARE _ram_critical char(255);
        DECLARE _severity char(255);
        DECLARE _alarm_count int(11);

                

		SELECT IFNULL(round(100-((free_bytes+buffers_bytes+cached_bytes)/total_bytes)*100),0), IF(IFNULL((swap_total_bytes-swap_free_bytes),0)>1024,1,0) INTO _ram_usage, _swap_used FROM ram_stats WHERE id=NEW.id AND cid=NEW.cid;

                SELECT value INTO _ram_warning FROM cmon_configuration WHERE param='RAM_WARNING' AND cid=NEW.cid;
                
                SELECT value INTO _ram_critical FROM cmon_configuration WHERE param='RAM_CRITICAL' AND cid=NEW.cid;



		IF (_ram_usage >= _ram_warning && _ram_usage < _ram_critical)
    			THEN		

 
                         SET _severity='WARNING'; 

				


		ELSEIF (_ram_usage >= _ram_critical)
    		       THEN

                       
                       SET _severity='CRITICAL'; 


                ELSEIF (_ram_usage < _ram_warning)
    			THEN

				DELETE FROM alarm_hosts WHERE hostid=NEW.id AND cid=NEW.cid AND alarm_name='Excessive RAM Usage';


	       END IF;
          
               SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.id AND cid=NEW.cid;

               IF ((_ram_usage >= _ram_warning && _ram_usage < _ram_critical)||(_ram_usage >= _ram_critical))
               THEN
              
                  
               INSERT INTO alarm_hosts    (hostid,
                            				    cid,
                                                            alarm_name,
                            				    component,
                            				    alarm_count,
			    				    severity,
		            				    description,
                            				    hostname,
                            				    recommendation,
                                                            report_ts,
                                                            alarm_sent,
                                                            alarm_sent_count
                           			            )
    				VALUES			   (NEW.id,
           						    NEW.cid,
           					            'Excessive RAM Usage',
                                                            'RAM',
           						    1,
                                                            _severity,
                                                            Concat ('RAM Utilization for ',_hostname,' is ',_ram_usage,' percent'),
                                                            _hostname,
	                                                    'Upgrade Node with more RAM',
                                                            NOW(),
                                                            DEFAULT,
                                                            DEFAULT
                                                           )ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1, severity=_severity, report_ts=now(), description=CONCAT('RAM Utilization for ',_hostname,' is ',_ram_usage,' percent');          

               END IF; 

/*
               IF (_swap_used > 0)
               THEN
                     INSERT INTO alarm_hosts    (hostid,
                                                            cid,
                                                            alarm_name,
                                                            component,
                                                            alarm_count,
                                                            severity,
                                                            description,
                                                            hostname,
                                                            recommendation,
                                                            report_ts,
                                                            alarm_sent,
                                                            alarm_sent_count
                                                            )
                                VALUES                     (NEW.id,
                                                            NEW.cid,
                                                            'SWAP space used',
                                                            'RAM',
                                                            1,
                                                            'WARNING',
                                                            Concat (_hostname,' is swapping'),
                                                            _hostname,
                                                            'Upgrade Node with more RAM, check MYSQL configuration',
                                                            NOW(),
                                                            DEFAULT,
                                                            DEFAULT
                                                            )ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1, severity='WARNING', description=Concat (_hostname,' is swapping'),report_ts=now();
               
               ELSE
		   DELETE FROM alarm_hosts WHERE hostid=NEW.id AND cid=NEW.cid AND alarm_name='SWAP space used'; 
               END IF;
*/
END
//
DELIMITER ;
DROP TRIGGER IF EXISTS `ut_ram_stats`;
DELIMITER //
CREATE TRIGGER `ut_ram_stats` AFTER UPDATE ON `ram_stats`
 FOR EACH ROW BEGIN

   	DECLARE _ram_usage float;
        DECLARE _swap_used int(11);
	DECLARE _hostname varchar(255);
        DECLARE _ram_warning char(255);
        DECLARE _ram_critical char(255);
        DECLARE _severity char(255);
        DECLARE _alarm_count int(11);

                

		SELECT IFNULL(round(100-(free_bytes/total_bytes)*100),0), IF(IFNULL((swap_total_bytes-swap_free_bytes),0)>1024*1024,1,0)  INTO _ram_usage, _swap_used FROM ram_stats WHERE id=NEW.id AND cid=NEW.cid;

                SELECT value INTO _ram_warning FROM cmon_configuration WHERE param='RAM_WARNING' AND cid=NEW.cid;
                
                SELECT value INTO _ram_critical FROM cmon_configuration WHERE param='RAM_CRITICAL' AND cid=NEW.cid;

		IF (_ram_usage >= _ram_warning && _ram_usage < _ram_critical)
    			THEN		

 
                         SET _severity='WARNING'; 

				


		ELSEIF (_ram_usage >= _ram_critical)
    		       THEN

                       
                       SET _severity='CRITICAL'; 


                ELSEIF (_ram_usage < _ram_warning)
    			THEN

				DELETE FROM alarm_hosts WHERE hostid=NEW.id AND cid=NEW.cid AND alarm_name='Excessive RAM Usage';


	       END IF;
               SELECT hostname INTO _hostname FROM hosts WHERE id=NEW.id AND cid=NEW.cid;

               IF ((_ram_usage >= _ram_warning && _ram_usage < _ram_critical)||(_ram_usage >= _ram_critical))
               THEN
              
                  
               INSERT INTO alarm_hosts    (hostid,
                            				    cid,
                                                            alarm_name,
                            				    component,
                            				    alarm_count,
			    				    severity,
		            				    description,
                            				    hostname,
                            				    recommendation,
                                                            report_ts,
                                                            alarm_sent,
                                                            alarm_sent_count
                           			            )
    				VALUES			   (NEW.id,
           						    NEW.cid,
           					            'Excessive RAM Usage',
                                                            'RAM',
           						    1,
                                                            _severity,
                                                            Concat ('RAM Utilization for ',_hostname,' is ',_ram_usage,' percent'),
                                                            _hostname,
	                                                    'Upgrade Node with more RAM',
                                                            NOW(),
                                                            DEFAULT,
                                                            DEFAULT
                                                            )ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1, severity=_severity, report_ts=now(), description=CONCAT('RAM Utilization for ',_hostname,' is ',_ram_usage,' percent');

               END IF; 
/*
				
               IF ((_swap_used > 0))
               THEN
                     INSERT INTO alarm_hosts    (hostid,
                                                            cid,
                                                            alarm_name,
                                                            component,
                                                            alarm_count,
                                                            severity,
                                                            description,
                                                            hostname,
                                                            recommendation,
                                                            report_ts,
                                                            alarm_sent,
                                                            alarm_sent_count
                                                            )
                                VALUES                     (NEW.id,
                                                            NEW.cid,
                                                            'SWAP space used',
                                                            'RAM',
                                                            1,
                                                            'WARNING',
                                                            Concat (_hostname,' is swapping'),
                                                            _hostname,
                                                            'Upgrade Node with more RAM',
                                                            NOW(),
                                                            DEFAULT,
                                                            DEFAULT
                                                            )ON DUPLICATE KEY UPDATE alarm_count=alarm_count+1,severity='WARNING', description=Concat (_hostname,' is swapping'), report_ts=now();

               ELSE
                   DELETE FROM alarm_hosts WHERE hostid=NEW.id AND cid=NEW.cid AND alarm_name='SWAP space used';    
               END IF;

*/
	       

END
//
DELIMITER ;



CREATE TABLE IF NOT EXISTS `ram_stats_history` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL DEFAULT '0',
  `total_bytes` int(11) DEFAULT NULL,
  `free_bytes` int(11) DEFAULT NULL,
  `buffers_bytes` int(11) DEFAULT NULL,
  `cached_bytes` int(11) DEFAULT NULL,
  `swap_total_bytes` int(11) DEFAULT NULL,
  `swap_free_bytes` int(11) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`id`,`report_ts`),
  KEY `idx_ramstats_tx` (`free_bytes`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `restore` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `backupid` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `master_nodeid` int(11) NOT NULL DEFAULT '0',
  `ndb_nodeid` int(11) NOT NULL DEFAULT '0',
  `status` char(255) DEFAULT NULL,
  `error` int(11) NOT NULL DEFAULT '0',
  `records` bigint(20) unsigned DEFAULT '0',
  `log_records` bigint(20) unsigned DEFAULT '0',
  `bytes` bigint(20) unsigned DEFAULT '0',
  `log_bytes` bigint(20) unsigned DEFAULT '0',
  `n_tables` int(10) unsigned DEFAULT '0',
  `n_tablespaces` int(10) unsigned DEFAULT '0',
  `n_logfilegroups` int(10) unsigned DEFAULT '0',
  `n_datafiles` int(10) unsigned DEFAULT '0',
  `n_undofiles` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`backupid`,`ndb_nodeid`),
  KEY `report_ts` (`report_ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





CREATE TABLE IF NOT EXISTS `restore_log` (
  `cid` int(11) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `backupid` int(11) NOT NULL DEFAULT '0',
  `master_nodeid` int(11) NOT NULL DEFAULT '0',
  `mgm_nodeid` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` char(255) DEFAULT NULL,
  `error` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `report_ts` (`report_ts`),
  KEY `backupid` (`backupid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;


CREATE TABLE IF NOT EXISTS `schema_object` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `tableid` int(11) NOT NULL DEFAULT '0',
  `type` char(64) DEFAULT NULL,
  `state` char(16) DEFAULT NULL,
  `logging` enum('yes','no') DEFAULT NULL,
  `temp` enum('yes','no') DEFAULT NULL,
  `name` char(255) DEFAULT NULL,
  `db` char(255) DEFAULT NULL,
  `schema_name` char(64) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,`cid`),
  KEY `cid` (`cid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1  ;

CREATE TABLE IF NOT EXISTS `license` (
  `email` char(255) DEFAULT NULL,
  `company` char(255) DEFAULT NULL,
  `exp_date` char(255) DEFAULT NULL,
  `lickey` char(255)  DEFAULT NULL,
  PRIMARY KEY (`email`,`company`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1  ;


CREATE TABLE IF NOT EXISTS `cmon_mysql_users` (
  `userid` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) DEFAULT NULL,
  `cmd` char(16) DEFAULT NULL,
  `user` varchar(128) DEFAULT NULL,
  `hostname` varchar(128) DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL,
  `success` varchar(2048) DEFAULT NULL,
  `failed` varchar(2048) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cmdlong` varchar(255) DEFAULT '',
  `realcmd` varchar(255) DEFAULT '',
  `dropped` int(11) DEFAULT '0',
  PRIMARY KEY (`userid`),
  UNIQUE KEY `cid` (`cid`,`cmd`,`user`,`hostname`,`password`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1  ;

CREATE TABLE IF NOT EXISTS `cmon_mysql_grants` (
  `grantid` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '0',
  `userhost` varchar(260) DEFAULT NULL,
  `user` varchar(260) DEFAULT NULL,
  `host` varchar(260) DEFAULT NULL,
  `privlist` varchar(1024) DEFAULT NULL,
  `privlist_crc` int(11) unsigned DEFAULT NULL,
  `db` varchar(128) DEFAULT NULL,
  `success` varchar(2048) DEFAULT NULL,
  `failed` varchar(2048) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `realcmd` varchar(1024) DEFAULT '',
  `dropped` int(11) DEFAULT '0',
  PRIMARY KEY (`grantid`,`cid`),
  UNIQUE KEY `privlist_crc` (`privlist_crc`,`db`,`userhost`),
  KEY `cid` (`cid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1  ;


CREATE TABLE IF NOT EXISTS `cmon_mysql_manual_grants` (
  `grantid` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '0',
  `_grant` varchar(1024) DEFAULT NULL,
  `grant_crc` int(11) unsigned DEFAULT NULL,
  `success` varchar(2048) DEFAULT NULL,
  `failed` varchar(2048) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dropped` int(11) DEFAULT '0',
  PRIMARY KEY (`grantid`,`cid`),
  UNIQUE KEY `grant_crc` (`cid`,`grant_crc`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1  ;
 
DROP TABLE IF EXISTS cmon_log;
CREATE TABLE IF NOT EXISTS `cmon_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '0',
  `hostid` int(11) NOT NULL DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `message` varchar(2048) DEFAULT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `loglevel` enum('INFO','WARNING','ERROR','ALERT', 'CRITICAL', 'DEBUG', 'UNKNOWN') DEFAULT 'INFO',
  PRIMARY KEY (`id`),
  KEY (`cid`,`report_ts`),
  KEY (`cid`,`hostid`,`report_ts`, `loglevel`),
  KEY (`cid`,`hostid`,`loglevel`)
) ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `cmon_local_mysql_job` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '0',
  `hostid` int(11) NOT NULL DEFAULT '0',
  `cmd` varchar(1024) DEFAULT NULL,
  `callback` varchar(1024) DEFAULT NULL,
  `executed` int(11) DEFAULT '0',
  `callerid` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`cid`,`hostid`),
  KEY (`cid`,`hostid`, `executed`),
  KEY (`callerid`)
) ENGINE=MyISAM;

CREATE TABLE IF NOT EXISTS `cmon_sw_package` (
  `cid` int(11) NOT NULL,
  `packageid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `rpm` int(11) DEFAULT 0,
  `selected` integer default 0,
  PRIMARY KEY (`packageid`,`cid`),
  UNIQUE KEY (`cid`,`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `top`;
CREATE TABLE IF NOT EXISTS `top` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL DEFAULT '0',
  `processid` int(11) NOT NULL DEFAULT '0',
  `user` varchar(64) DEFAULT NULL,
  `priority` int(11) NOT NULL DEFAULT '0',
  `nice` bigint  NOT NULL DEFAULT '0',
  `virt` varchar(16) DEFAULT NULL,
  `res` varchar(16) DEFAULT NULL,
  `shr` varchar(16) DEFAULT NULL,
  `state` char(4) DEFAULT NULL,
  `cpu` float NOT NULL  DEFAULT '0',
  `mem` float NOT NULL  DEFAULT '0',
  `time` varchar(32) DEFAULT NULL,
  `command` varchar(64) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`hostid`,`processid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE  IF NOT EXISTS `galera_status` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL  DEFAULT '0',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `var` char(64) DEFAULT NULL ,
  `value` bigint(20) unsigned DEFAULT '0',
  `value1` bigint(20) unsigned DEFAULT '0',
  `value2` bigint(20) unsigned DEFAULT '0',
  `value3` bigint(20) unsigned DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `report_ts1` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `report_ts2` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `report_ts3` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `value_txt` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`cid`,`hostid`,`var`),
  KEY `id` (`hostid`,`var`)
) ENGINE=MyISAM ;


DROP TABLE IF EXISTS `galera_status_history`;
/*
CREATE TABLE  IF NOT EXISTS `galera_status_history` (
  `cid` int(11) NOT NULL,
  `hostid` int(11) NOT NULL,
  `nodeid` int(11) NOT NULL,
  `var` char(64) NOT NULL,
  `value` bigint(20) unsigned DEFAULT '0',
  `report_ts` bigint(20) unsigned DEFAULT '0',
  `value_txt` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`cid`,`hostid`,`var`, `report_ts`),
  KEY `id` (`hostid`,`var`),
  KEY(`report_ts`, `cid`)
) ENGINE=MyISAM ;
*/
DROP TRIGGER IF EXISTS `it_galera_status`;
DROP TRIGGER IF EXISTS `ut_galera_status`;

CREATE TABLE IF NOT EXISTS `mysql_backup` (
  `backupid` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `storage_host` varchar(255) DEFAULT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `mysql_type` enum('mysql','galera') DEFAULT NULL,
  `directory` varchar(255) DEFAULT '',
  `filename` varchar(255) DEFAULT '',
  `size` bigint(20) DEFAULT '0',
  `error` int(11) DEFAULT '0',
  `status` enum('completed','failed','running','pending') DEFAULT 'pending',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `backup_type` enum('full','incremental') DEFAULT 'full',
  `lsn` bigint(20) DEFAULT '0',
  `parentid` int(11) NOT NULL DEFAULT '0',
  `backup_method` enum('xtrabackup','mysqldump') DEFAULT 'mysqldump',
  `md5sum` varchar(255) DEFAULT '',
  `logfile` text ,
  `cc_storage` tinyint(4) DEFAULT '0',
  `compressed` tinyint(4) DEFAULT '1',
  PRIMARY KEY (`backupid`,`cid`),
  KEY `cid` (`cid`,`report_ts`),
  KEY `cid_2` (`cid`,`mysql_type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `mysql_advisor`;
CREATE TABLE IF NOT EXISTS `mysql_advisor` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `module` varchar(32) DEFAULT NULL DEFAULT '',
  `rule_name` varchar(64) NOT NULL DEFAULT '',
  `advise` varchar(512) DEFAULT NULL,
  `value` bigint(20) DEFAULT '0',
  `warn` bigint(20) DEFAULT '0',
  `crit` bigint(20) DEFAULT '0',
  `status` int(11) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`rule_name`)
) ENGINE=MyISAM;



DROP TABLE IF EXISTS `mysql_table_advisor`;
CREATE TABLE IF NOT EXISTS `mysql_table_advisor` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `xdb` varchar(64) DEFAULT NULL,
  `tbl` varchar(64) DEFAULT NULL,	
  `xengine` varchar(64) DEFAULT NULL,	
  `nopk` int(11) NOT NULL DEFAULT '0',
  `ftidx` int(11) NOT NULL DEFAULT '0',
  `gsidx` int(11) NOT NULL DEFAULT '0',
  `alter_stmt` varchar(512) DEFAULT NULL,	
  `is_myisam` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`cid`,`xdb`,`tbl`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `mysql_duplindex_advisor`;
CREATE TABLE IF NOT EXISTS `mysql_duplindex_advisor` (
  `id` int(11) auto_increment NOT NULL,
  `cid` int(11) NOT NULL DEFAULT '1',
  `xdb` varchar(64) DEFAULT NULL,
  `tbl` varchar(64) DEFAULT NULL,	
  `red_idx` varchar(255) DEFAULT NULL,	
  `cols_in_redidx` varchar(255) DEFAULT NULL,
  `idx` varchar(255) DEFAULT NULL,
  `cols_in_idx` varchar(255) DEFAULT NULL,
  `advise` varchar(512) DEFAULT NULL,
  KEY (`cid`,`xdb`,`tbl`, `red_idx`),
  PRIMARY KEY(id)
) ENGINE=InnoDB;


DROP TABLE IF EXISTS `mysql_selindex_advisor`;
CREATE TABLE IF NOT EXISTS `mysql_selindex_advisor` (
  `id` int(11) auto_increment NOT NULL,
  `cid` int(11) NOT NULL DEFAULT '1',
  `xdb` varchar(64) DEFAULT NULL,	
  `tbl` varchar(64) DEFAULT NULL,	
  `idx` varchar(64) DEFAULT NULL,	
  `fname` varchar(64) DEFAULT NULL,	
  `seq` integer NOT NULL DEFAULT '0',	
  `cols` integer NOT NULL DEFAULT '0',	
  `card` integer NOT NULL DEFAULT '0',	
  `xrows` integer NOT NULL DEFAULT '0',	
  `sel_pct` double NOT NULL DEFAULT '0',	
  KEY (`cid`,`xdb`,`tbl`, `idx`),
  PRIMARY KEY(id)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `mysql_memory_usage`;
CREATE TABLE IF NOT EXISTS `mysql_memory_usage` (
  `cid` int(11) NOT NULL  DEFAULT '1',	
  `nodeid` int(11) NOT NULL  DEFAULT '0',	
  `system_memory` bigint(20) DEFAULT '0',
  `total_memory` bigint(20) DEFAULT '0',
  `max_memory_used` bigint(20) DEFAULT '0',
  `max_memory_curr` bigint(20) DEFAULT '0',
  `global_memory` bigint(20) DEFAULT '0',
  `memory_per_thread` bigint(20) DEFAULT '0',
  `memory_per_thread_curr` bigint(20) DEFAULT '0',
  `memory_per_thread_max_used` bigint(20) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`)) ENGINE=MyISAM;




CREATE TABLE IF NOT EXISTS `mysql_advisor_history` (
  `cid` int(11) NOT NULL DEFAULT '1',	
  `nodeid` int(11) NOT NULL DEFAULT '0',	
  `module` varchar(32) DEFAULT NULL DEFAULT '',
  `rule_name` varchar(64) NOT NULL DEFAULT '',
  `advise` varchar(512) DEFAULT NULL,
  `value` bigint(20) DEFAULT '0',
  `threshold` bigint(20) DEFAULT '0',
  `status` int(11) DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`nodeid`,`report_ts`,`rule_name`),
  KEY `report_ts` (report_ts, cid)
) ENGINE=MyISAM;


DROP TRIGGER IF EXISTS `it_mysql_advisor_history`;
/*
DELIMITER //
CREATE TRIGGER `it_mysql_advisor_history` AFTER INSERT ON `mysql_advisor`
 FOR EACH ROW BEGIN
    INSERT INTO mysql_advisor_history(cid,
                                 nodeid, 
                                 module,
                                 rule_name, 
                                 advise,
                                 value,
                                 threshold,
                                 status,
                                report_ts)
    VALUES( NEW.cid,
            NEW.nodeid,
            NEW.module,
            NEW.rule_name, 
            NEW.advise,
            NEW.value,
            NEW.threshold,
            NEW.status,
            NEW.report_ts);
END
//
DELIMITER ;
*/

CREATE TABLE IF NOT EXISTS `mysql_advisor_reco` (
  `cid` int(11) NOT NULL DEFAULT '1',	
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `param` varchar(64) DEFAULT NULL,
  `recommended` bigint(20) DEFAULT '0',
  `actual` bigint(20) DEFAULT '0',
  `diff` bigint(20) DEFAULT '0',
  PRIMARY KEY (`cid`,`nodeid`,`param`)
) ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `mysql_states` (
  `id` int(11) PRIMARY KEY NOT NULL,
  `name` varchar(32) NOT NULL DEFAULT '',
  `description` varchar(128) DEFAULT NULL
) ENGINE=MyISAM;

CREATE TABLE IF NOT EXISTS `cmon_daily_job` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `exectime` char(8) DEFAULT NULL,
  `last_exec` datetime DEFAULT NULL,
  `command` int(11) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,`cid`),
  UNIQUE KEY `cid` (`cid`,`exectime`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `db_growth_hashmap` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hashkey` bigint(20) unsigned DEFAULT '0',
  `val` varchar(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`hashkey`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

CREATE TABLE IF NOT EXISTS `table_growth_hashmap` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `hashkey` bigint(20) unsigned DEFAULT '0',
  `val` varchar(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`,`hashkey`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;



CREATE TABLE IF NOT EXISTS `db_growth` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `dbname_hash` bigint(20) unsigned DEFAULT NULL,
  `xrows` bigint(20) unsigned DEFAULT '0',
  `index_length` bigint(20) UNSIGNED  DEFAULT '0',
  `data_length` bigint(20) UNSIGNED  DEFAULT '0',
  `yearday` smallint(11) UNSIGNED  DEFAULT '0',
  `xyear` smallint(11) UNSIGNED  DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`, `dbname_hash`, `yearday` )
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

CREATE TABLE IF NOT EXISTS `table_growth` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `dbname_hash` bigint(20) unsigned DEFAULT NULL,
  `tablename_hash` bigint(20) unsigned  DEFAULT NULL,
  `xengine` VARCHAR(64) DEFAULT 'N/A',
  `xrows` bigint(20) unsigned DEFAULT '0',
  `index_length` bigint(20) unsigned  DEFAULT '0',
  `data_length` bigint(20) unsigned DEFAULT '0',
  `yearday`smallint(11) UNSIGNED  DEFAULT '0',
  `xyear` smallint(11) UNSIGNED  DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`, `dbname_hash`, `tablename_hash`, `yearday` )
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;


CREATE TABLE IF NOT EXISTS `haproxy_server` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `status` int(11) DEFAULT '2',
  `lb_host` varchar(255) NOT NULL DEFAULT '',
  `lb_name` varchar(255) NOT NULL DEFAULT '',
  `lb_port` int(11) NOT NULL DEFAULT '0',
  `lb_admin` varchar(255) DEFAULT NULL,
  `lb_password` varchar(255) DEFAULT NULL,
  `add_hook` varchar(512) DEFAULT NULL,
  `delete_hook` varchar(512) DEFAULT NULL,
  `server_addr` varchar(255) DEFAULT '',
  PRIMARY KEY (`cid`,`lb_name`,`lb_host`,`lb_port`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `keepalived` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `keepalived_addr` varchar(255) NOT NULL DEFAULT '',
  `virtual_ip` varchar(255) NOT NULL DEFAULT '',
  `haproxy_addr1` varchar(255) NOT NULL DEFAULT '',
  `haproxy_addr2` varchar(255) NOT NULL DEFAULT '',
  `name` varchar(255) NOT NULL DEFAULT '',	
  `comment` varchar(255) NOT NULL DEFAULT '',	  
  PRIMARY KEY (`cid`,`keepalived_addr`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `galera_garbd_proc` (
  `cid` int(11) NOT NULL DEFAULT '1',
  `status` int(11) DEFAULT '2',
  `hostname` varchar(255) DEFAULT NULL,
  `cluster_address` varchar(255) DEFAULT NULL,
  `cluster_name` varchar(255) DEFAULT NULL,
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(`cid`, `hostname`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `user_events` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cid` int(10) unsigned NOT NULL DEFAULT '1',
  `category` int(10) unsigned DEFAULT NULL,
  `custom_data` varchar(255) DEFAULT NULL,
  `comment` varchar(1024) DEFAULT NULL,
  `ts` bigint(20) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cid` (`cid`,`ts`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

CREATE TABLE IF NOT EXISTS `user_event_categories` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cid` int(10) unsigned NOT NULL DEFAULT '1',
  `category` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cid` (`cid`,`category`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `ext_proc` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cid` int(10) unsigned NOT NULL DEFAULT '1',
  `hostname` varchar(255) DEFAULT NULL,
  `bin` varchar(255) DEFAULT NULL,
  `opts` varchar(512) DEFAULT NULL,
  `cmd` varchar(256) DEFAULT NULL,
  `proc_name` varchar(64) DEFAULT NULL,
  `status` int(10) unsigned NOT NULL DEFAULT '1',
  `port` int(10) unsigned NOT NULL DEFAULT '0',
  `active` int(10) unsigned NOT NULL DEFAULT '1',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cid` (`cid`,`hostname`,`proc_name`),
  KEY `cid_2` (`cid`,`proc_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `memcache_statistics`;
CREATE TABLE IF NOT EXISTS `memcache_statistics` (
  `cid` int(10) unsigned NOT NULL DEFAULT '1',
  `hostname` varchar(255) NOT NULL DEFAULT '',
  `port` int(10) unsigned NOT NULL DEFAULT '11211',
  `pid` bigint(20) unsigned DEFAULT '0',
  `uptime` bigint(20) unsigned DEFAULT '0',
  `time_` bigint(20) unsigned DEFAULT '0',
  `version` varchar(64) DEFAULT '',
  `libevent` varchar(64) DEFAULT '',
  `pointer_size` bigint(20) unsigned DEFAULT '0',
  `rusage_user` decimal(10,6) DEFAULT '0.000000',
  `rusage_system` decimal(10,6) DEFAULT '0.000000',
  `daemon_connections` bigint(20) unsigned DEFAULT '0',
  `curr_connections` bigint(20) unsigned DEFAULT '0',
  `total_connections` bigint(20) unsigned DEFAULT '0',
  `connection_structures` bigint(20) unsigned DEFAULT '0',
  `cmd_get` bigint(20) unsigned DEFAULT '0',
  `cmd_set` bigint(20) unsigned DEFAULT '0',
  `cmd_flush` bigint(20) unsigned DEFAULT '0',
  `auth_cmds` bigint(20) unsigned DEFAULT '0',
  `auth_errors` bigint(20) unsigned DEFAULT '0',
  `get_hits` bigint(20) unsigned DEFAULT '0',
  `get_misses` bigint(20) unsigned DEFAULT '0',
  `delete_misses` bigint(20) unsigned DEFAULT '0',
  `delete_hits` bigint(20) unsigned DEFAULT '0',
  `incr_misses` bigint(20) unsigned DEFAULT '0',
  `incr_hits` bigint(20) unsigned DEFAULT '0',
  `decr_misses` bigint(20) unsigned DEFAULT '0',
  `decr_hits` bigint(20) unsigned DEFAULT '0',
  `cas_misses` bigint(20) unsigned DEFAULT '0',
  `cas_hits` bigint(20) unsigned DEFAULT '0',
  `cas_badval` bigint(20) unsigned DEFAULT '0',
  `bytes_read` bigint(20) unsigned DEFAULT '0',
  `bytes_written` bigint(20) unsigned DEFAULT '0',
  `limit_maxbytes` bigint(20) unsigned DEFAULT '0',
  `accepting_conns` bigint(20) unsigned DEFAULT '0',
  `listen_disabled_num` bigint(20) unsigned DEFAULT '0',
  `rejected_conns` bigint(20) unsigned DEFAULT '0',
  `threads` bigint(20) unsigned DEFAULT '0',
  `conn_yields` bigint(20) unsigned DEFAULT '0',
  `evictions` bigint(20) unsigned DEFAULT '0',
  `curr_items` bigint(20) unsigned DEFAULT '0',
  `total_items` bigint(20) unsigned DEFAULT '0',
  `bytes` bigint(20) unsigned DEFAULT '0',
  `reclaimed` bigint(20) unsigned DEFAULT '0',
  `engine_maxbytes` bigint(20) unsigned DEFAULT '0',
  `rusage_user_g` decimal(10,6) DEFAULT '0.000000',
  `rusage_system_g` decimal(10,6) DEFAULT '0.000000',
  `daemon_connections_g` bigint(20) unsigned DEFAULT '0',
  `curr_connections_g` bigint(20) unsigned DEFAULT '0',
  `total_connections_g` bigint(20) unsigned DEFAULT '0',
  `connection_structures_g` bigint(20) unsigned DEFAULT '0',
  `cmd_get_g` bigint(20) unsigned DEFAULT '0',
  `cmd_set_g` bigint(20) unsigned DEFAULT '0',
  `cmd_flush_g` bigint(20) unsigned DEFAULT '0',
  `auth_cmds_g` bigint(20) unsigned DEFAULT '0',
  `auth_errors_g` bigint(20) unsigned DEFAULT '0',
  `get_hits_g` bigint(20) unsigned DEFAULT '0',
  `get_misses_g` bigint(20) unsigned DEFAULT '0',
  `delete_misses_g` bigint(20) unsigned DEFAULT '0',
  `delete_hits_g` bigint(20) unsigned DEFAULT '0',
  `incr_misses_g` bigint(20) unsigned DEFAULT '0',
  `incr_hits_g` bigint(20) unsigned DEFAULT '0',
  `decr_misses_g` bigint(20) unsigned DEFAULT '0',
  `decr_hits_g` bigint(20) unsigned DEFAULT '0',
  `cas_misses_g` bigint(20) unsigned DEFAULT '0',
  `cas_hits_g` bigint(20) unsigned DEFAULT '0',
  `cas_badval_g` bigint(20) unsigned DEFAULT '0',
  `bytes_read_g` bigint(20) unsigned DEFAULT '0',
  `bytes_written_g` bigint(20) unsigned DEFAULT '0',
  `listen_disabled_num_g` bigint(20) unsigned DEFAULT '0',
  `rejected_conns_g` bigint(20) unsigned DEFAULT '0',
  `conn_yields_g` bigint(20) unsigned DEFAULT '0',
  `evictions_g` bigint(20) unsigned DEFAULT '0',
  `total_items_g` bigint(20) unsigned DEFAULT '0',
  `reclaimed_g` bigint(20) unsigned DEFAULT '0',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cmd_touch` bigint(20) unsigned DEFAULT '0',
  `cmd_touch_g` bigint(20) unsigned DEFAULT '0',
  `evicted_unfetched` bigint(20) unsigned DEFAULT '0',
  `evicted_unfetched_g` bigint(20) unsigned DEFAULT '0',
  `expired_unfetched_g` bigint(20) unsigned DEFAULT '0',
  `expired_unfetched` bigint(20) unsigned DEFAULT '0',
  `hash_bytes` bigint(20) unsigned DEFAULT '0',
  `hash_is_expanding` bigint(20) unsigned DEFAULT '0',
  `hash_power_level` bigint(20) unsigned DEFAULT '0',
  `reserved_fds` bigint(20) unsigned DEFAULT '0',
  `touch_hits` bigint(20) unsigned DEFAULT '0',
  `touch_hits_g` bigint(20) unsigned DEFAULT '0',
  `touch_misses_g` bigint(20) unsigned DEFAULT '0',
  `touch_misses` bigint(20) unsigned DEFAULT '0',
  PRIMARY KEY (`cid`,`hostname`)
) ENGINE=MyISAM;

CREATE TABLE IF NOT EXISTS `cmon_cron` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `min_` varchar(16) DEFAULT '*',
  `hour_` varchar(16) DEFAULT '*',
  `dow_` varchar(16) DEFAULT '*',
  `dom_` varchar(16) DEFAULT '*',
  `month_` varchar(16) DEFAULT '*',
  `year_` varchar(16) DEFAULT '*',
  `hostname` varchar(255) DEFAULT '127.0.0.1',
  `external_cmd` varchar(512) DEFAULT NULL,
  `internal_cmd` varchar(512) DEFAULT NULL,
  `description` varchar(512) NOT NULL DEFAULT '',
  `create_job` tinyint(4) NOT NULL DEFAULT '0',
  `run_at_startup` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM;


 CREATE TABLE IF NOT EXISTS `expression_group` (
  `id` int(11) AUTO_INCREMENT NOT NULL,
  `cid` int(11) NOT NULL DEFAULT '1',
  `name` varchar(128) DEFAULT NULL,
  `db` varchar(128) DEFAULT NULL,
  `comment` varchar(256) DEFAULT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(id),
  KEY(cid, name)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

INSERT IGNORE INTO expression_group(id, cid, name, created) VALUES(1,1,'CONNECTIONS', NOW());
INSERT IGNORE INTO expression_group(id, cid, name, created) VALUES(2,1,'INNODB', NOW());
INSERT IGNORE INTO expression_group(id, cid, name, created) VALUES(3,1,'BUFFERS', NOW());

DROP TABLE IF EXISTS expression;
CREATE TABLE `expression` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cid` int(11) NOT NULL DEFAULT '1',
  `groupid` int(11) NOT NULL DEFAULT '0',
  `expression` varchar(512) DEFAULT NULL,
  `result_var` varchar(128) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `comment` varchar(256) DEFAULT NULL,
  `advise` varchar(256) DEFAULT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `gt_trigger` int(11) NOT NULL DEFAULT '1', /**trigger if val is greater than, 0=lower than*/
  PRIMARY KEY (`id`),
  KEY `cid` (`cid`,`groupid`),
  KEY `cid_2` (`cid`,`result_var`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

INSERT IGNORE INTO expression(id, cid, groupid, expression, result_var,advise) VALUES(1,1,1,'threads_connected*100/max_connections', '% connections used', 'Increase max_connections or lower number of connections from applications.');
INSERT IGNORE INTO expression(id, cid, groupid, expression, result_var,advise) VALUES(2,1,3,'open_tables*100/table_open_cache', '% table_open_cahe used', 'Increase table_open_cache.');
INSERT IGNORE INTO expression(id, cid, groupid, expression, result_var,advise) VALUES(3,1,2,'Innodb_buffer_pool_wait_free*100/Innodb_buffer_pool_write_requests', '% innodb_buffer_pool_wait for free.', '');
INSERT IGNORE INTO expression(id, cid, groupid, expression, result_var,advise) VALUES(4,1,2,'Innodb_log_waits*100/Innodb_log_writes', '% innodb_log_waits', 'Problems writing transaction log - check disk subsystem.');
INSERT IGNORE INTO expression(id, cid, groupid, gt_trigger, expression, result_var,advise) VALUES(5,1,2,0,'1000-(10*Innodb_buffer_pool_reads/Innodb_buffer_pool_read_requests)', '% innodb_buffer_pool_size hit ratio','Increase innodb_buffer_pool_size.');
INSERT IGNORE INTO expression(id, cid, groupid, gt_trigger, expression, result_var,advise) VALUES(6,1,3,1,'Created_tmp_disk_tables*100/(Created_tmp_tables+Created_tmp_disk_tables)', '% temporary tables written to disk','Increase max_heap_table_size and tmp_table_size - make sure they are equal.');
INSERT IGNORE INTO expression(id, cid, groupid, gt_trigger, expression, result_var,advise) VALUES(7,1,3,1,'100*Binlog_cache_disk_use/Binlog_cache_use', '% transactions exceeding binlog_cache_size','Increase binlog_cache_size.');
INSERT IGNORE INTO expression(id, cid, groupid, gt_trigger, expression, result_var,advise) VALUES(8,1,1,1,'100*Max_used_connections/Max_connections', '% of max connections ever used','Increase max_connections or lower number of connections from applications.');


DROP TABLE IF EXISTS expression_trigger;
CREATE TABLE IF NOT EXISTS `expression_trigger` (
  `expressionid` int(11) NOT NULL DEFAULT '1', 
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL DEFAULT '0' /* 0 = all hosts*/,
  `nodeid` int(11) NOT NULL DEFAULT '0' /* 0 = all nodes*/,
  `warning` int(11) NOT NULL DEFAULT '80',
  `critical` int(11) NOT NULL DEFAULT '90',
  `active` int(11) NOT NULL DEFAULT '1',
  `notify` int(11) NOT NULL DEFAULT '1',
  `alarm_created` int(11) NOT NULL DEFAULT '0',
  `alarm_created_threshold` int(11) NOT NULL DEFAULT '0',
  `max_threshold_breaches` int(11) NOT NULL DEFAULT '3',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(cid, expressionid, nodeid)  
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(1,1,2, 80,90);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(1,1,3, 80,90);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(1,1,4, 85,95);

INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(2,1,2, 80,90);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(2,1,3, 80,90);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(2,1,4, 80,90);

INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(3,1,2, 1,5);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(3,1,3, 1,5);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(3,1,4, 1,5);


INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(4,1,2, 1,5);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(4,1,3, 1,5);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(4,1,4, 1,5);

INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(5,1,2, 990,900);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(5,1,3, 990,900);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(5,1,4, 990,900);

INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(6,1,2,15,20);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(6,1,3,15,20);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(6,1,4,15,20);

INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(7,1,2,20,40);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(7,1,3,20,40);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(7,1,4,20,40);

INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(8,1,2, 80,90);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(8,1,3, 80,90);
INSERT IGNORE INTO expression_trigger(expressionid, cid, nodeid,warning, critical) VALUES(8,1,4, 80,90);

/*DROP TABLE IF EXISTS expression_result;*/
CREATE TABLE IF NOT EXISTS `expression_result` (
  `expressionid` int(11) NOT NULL DEFAULT '1', 
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `warning` int(11) NOT NULL DEFAULT '80',
  `critical` int(11) NOT NULL DEFAULT '90',
  `val` varchar(32) NOT NULL DEFAULT '',
  `errmsg` varchar(32) NOT NULL DEFAULT '',
  `severity` enum('OK', 'WARNING','CRITICAL') DEFAULT 'OK',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(expressionid, cid, nodeid)  
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*DROP TABLE IF EXISTS expression_result_history;*/
CREATE TABLE IF NOT EXISTS `expression_result_history` (
  `expressionid` int(11) NOT NULL DEFAULT '1', 
  `cid` int(11) NOT NULL DEFAULT '1',
  `hostid` int(11) NOT NULL DEFAULT '1',
  `nodeid` int(11) NOT NULL DEFAULT '0',
  `warning` int(11) NOT NULL DEFAULT '80',
  `critical` int(11) NOT NULL DEFAULT '90',
  `val` varchar(32) NOT NULL DEFAULT '',
  `report_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(expressionid, cid, nodeid, report_ts)  
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `metainfo` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `cid` int(11) DEFAULT NULL,
    `hostid` int(11) DEFAULT NULL,
    `nodeid` int(11) DEFAULT NULL,
    `attribute` varchar(250) NOT NULL,
    `value` varchar(250) NOT NULL,
    `description` varchar(250) DEFAULT '',
    PRIMARY KEY (`id`),
    UNIQUE KEY `cid` (`cid`,`hostid`,`nodeid`,`attribute`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*

get all expression results history:

select m.hostname, m.port, er.nodeid, er.hostid, result_var, expression, val, er.report_ts from expression e, expression_trigger et , expression_result_history er, mysql_server m where e.id=er.expressionid and er.expressionid=et.expressionid and er.nodeid=et.nodeid  and e.cid=er.cid and et.cid=er.cid  and m.cid=er.cid and m.nodeid=er.nodeid and m.nodeid=et.nodeid and e.cid=1;


filtration on particular expressions -> good for plotting an expression within a time range (time range not show here but should be on expression_result_history.report_ts)

select m.hostname, m.port, er.nodeid, er.hostid, result_var, expression, val, er.report_ts from expression e, expression_trigger et , expression_result_history er, mysql_server m where e.id=er.expressionid and er.expressionid=et.expressionid and er.nodeid=et.nodeid  and e.cid=er.cid and et.cid=er.cid  and m.cid=er.cid and m.nodeid=er.nodeid and m.nodeid=et.nodeid and e.cid=1 and e.result_var='% innodb log waits';


filtration on particular expressions -> good for plotting an expression within a time range 

select m.hostname, m.port, er.nodeid, er.hostid, result_var, expression, val, er.report_ts from expression e, expression_trigger et , expression_result_history er, mysql_server m where e.id=er.expressionid and er.expressionid=et.expressionid and er.nodeid=et.nodeid  and e.cid=er.cid and et.cid=er.cid  and m.cid=er.cid and m.nodeid=er.nodeid and m.nodeid=et.nodeid and e.cid=1 and e.result_var='% innodb log waits' and er.report_ts between date_sub(now(), interval 1 hour) and now();


filtration on a particular server (the mysql.nodeid also works here):

select m.hostname, m.port, er.nodeid, er.hostid, result_var, expression, val, er.report_ts from expression e, expression_trigger et , expression_result_history er, mysql_server m where e.id=er.expressionid and er.expressionid=et.expressionid and er. nodeid=et.nodeid  and e.cid=er.cid and et.cid=er.cid  and m.cid=er.cid and m.nodeid=er.nodeid and m.nodeid=et.nodeid and m.hostname='10.177.197.223' and e.cid=1;
 
get current expression results --> summary screenn

select m.hostname, m.port, er.nodeid, er.hostid, result_var, expression, val,report_ts from expression e, expression_trigger et , expression_result er, mysql_server m where e.id=er.expressionid and er.expressionid=et.expressionid and er.nodeid=et.nodeid  and e.cid=er.cid and et.cid=er.cid  and m.cid=er.cid and m.nodeid=er.nodeid and m.nodeid=et.nodeid and e.cid=1;
*/
