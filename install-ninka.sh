#!/usr/bin/env bash

set -e

if [ $# -ne 1 ]; then
    echo "usage: install-ninka.sh <prefix>"
    echo "   prefix: the prefix of the install. e.g. /opt/kss will install the"
    echo "           executable in /opt/kss/bin"
    exit 255
fi

prefix=$1

echo "Installing ninka in $prefix"

perl -MCPAN -e "install IO::CaptureOutput" PREFIX="$prefix"

cwd=$(pwd)
tmpdir=$(mktemp -d /tmp/ninka-installer-XXXXXX)
cd "$tmpdir"
git clone https://github.com/dmgerman/ninka.git
cd ninka
perl Makefile.PL PREFIX="$prefix"
make
make install
cd "$cwd"
if [ -d "$tmpdir" ]; then
    rm -rf "$tmpdir"
fi
echo "Done"
