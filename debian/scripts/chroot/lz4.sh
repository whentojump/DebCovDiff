#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo
gcc -v
echo

################################################################################

echo

for i in `seq 7`; do
    seq 1 40 | LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE > /tmp/compressed
done

for i in `seq 3`; do
    cat /tmp/compressed | LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE -d > /dev/null
done

rm -f /tmp/compressed

echo

################################################################################

echo
BINARY=$EXECUTABLE $THIS_DIR/common/get_coverage.sh
echo
