#
# Regular cron jobs for the nova-docker package
#
0 4	* * *	root	[ -x /usr/bin/nova-docker_maintenance ] && /usr/bin/nova-docker_maintenance
