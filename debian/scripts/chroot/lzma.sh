#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo
gcc -v
echo

################################################################################

echo

# Otherwise it will use the older libstdc++ from chroot's distro and prompt:
# "./lzma-9.22/debian/lzma/usr/bin/lzmp: /lib/x86_64-linux-gnu/libstdc++.so.6:
# version `GLIBCXX_3.4.32' not found (required by ./lzma-9.22/debian/lzma/usr/bin/lzmp)"
export LD_LIBRARY_PATH="/opt/gcc-latest/lib64"

for i in `seq 7`; do
    printf "hello" | LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE > /tmp/compressed
done

for i in `seq 3`; do
    cat /tmp/compressed | LLVM_PROFILE_FILE="$(uuidgen).profraw" ./$EXECUTABLE -cd > /dev/null
done

rm -f /tmp/compressed

echo

################################################################################

echo
BINARY=$EXECUTABLE $THIS_DIR/common/get-coverage.sh
echo
