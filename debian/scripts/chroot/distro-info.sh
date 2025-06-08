#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo
gcc -v
echo

################################################################################

echo

LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE
LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE --help
LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE --all
LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE --devel
LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE --lts
LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE --stable
LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE --supported
LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE --unsupported
LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE --lts --date=2018-01-01

echo

################################################################################

echo
BINARY=$EXECUTABLE $THIS_DIR/common/get-coverage.sh
echo
