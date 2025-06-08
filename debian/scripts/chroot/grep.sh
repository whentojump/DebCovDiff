#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo
gcc -v
echo

################################################################################

echo

printf abcdef | LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE abc
printf abcdef | LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE xyz

echo

################################################################################

echo
BINARY=$EXECUTABLE $THIS_DIR/common/get-coverage.sh
echo
