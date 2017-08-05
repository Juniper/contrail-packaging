#!/bin/sh

set -x

[ $# -ge 2 ] || {
	echo "Usage: debian/setup-config.sh nova-conf.dist etc/nova/nova.conf.sample" >&2
	exit 1
}

distconf=$1
sample=$2
# 
sed -i '/^[^#[]/{s/^/#/; s/ //g}; /^#[^ ]/s/ = /=/' $sample

while read name eq value; do
	test "$name" && test "$value" || continue
	sed -i "0,/^# *$name=/{s!^# *$name=.*!$name=$value!}" $sample
done < $distconf
