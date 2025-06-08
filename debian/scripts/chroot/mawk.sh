#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo
gcc -v
echo

################################################################################

echo
cat $CHROOT_HOOK_PATH/common/unix-utils-test-input.txt | ./$EXECUTABLE 'NR%3==1'
echo

################################################################################

echo
BINARY=$EXECUTABLE $THIS_DIR/common/get-coverage.sh
echo
