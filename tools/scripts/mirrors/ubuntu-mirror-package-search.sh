#!/bin/bash
if [ -z $1 ]; then
    echo "ERROR: Package name is missing"
    echo "Usage: ./ubuntu-mirror-package-search <package-name>"
    exit 2
fi

set -x
aptly package show -with-files -with-references $1
