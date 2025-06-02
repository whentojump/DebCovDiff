#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo
gcc -v
echo

################################################################################

echo

cp $PROJECT_ROOT/examples/simple.c app.c

cp $PROJECT_ROOT/debian/liblzo2-2/lib/x86_64-linux-gnu/liblzo2.so{.2.0.0,}

gcc -I$PROJECT_ROOT/debian/liblzo2-dev/usr/include \
    -I$PROJECT_ROOT \
    app.c \
    -L$PROJECT_ROOT/debian/liblzo2-2/lib/x86_64-linux-gnu \
    -llzo2 \
    -o app

LD_LIBRARY_PATH=$PROJECT_ROOT/debian/liblzo2-2/lib/x86_64-linux-gnu \
    ./app

echo

################################################################################

echo
BINARY=$LIBRARY $THIS_DIR/common/get_coverage.sh
echo
