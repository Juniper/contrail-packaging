#!/bin/sh

cd /usr/local/ 
wget http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
tar -zxvf apache-maven-3.0.5-bin.tar.gz
export CATALINA_HOME=/usr/share/tomcat6/
chown -R mganley:slt $CATALINA_HOME



