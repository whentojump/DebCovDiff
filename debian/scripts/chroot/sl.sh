#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo
gcc -v
echo

################################################################################

echo

TERM="xterm" ./$EXECUTABLE

echo

################################################################################

echo
BINARY=$EXECUTABLE $THIS_DIR/common/get-coverage.sh
echo
