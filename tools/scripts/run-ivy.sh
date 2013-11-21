#!/bin/bash


java -jar /opt/apache-ivy-2.3.0/ivy-2.3.0.jar -settings ./ivysettings.xml -ivy ivy.xml  -retrieve /ecbuilds/CI/centos64_os/"[artifact]-[revision].[ext]"
