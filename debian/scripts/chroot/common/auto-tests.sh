#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo
gcc -v
echo

################################################################################

pwd
pushd $PROJECT_ROOT
pwd

# The coverage mapping in these executables or shared objects are known to cause
# assertion failures or segmentation faults. Thus use the one downloaded from
# the distribution which is not instrumented.

if [[ "$PACKAGE_NAME" == "coreutils" ]]; then
    cp /usr/bin/tail ./src/tail
    cp /usr/bin/ptx ./src/ptx
    cp /usr/bin/tail ./debian/coreutils/usr/bin/tail
    cp /usr/bin/ptx ./debian/coreutils/usr/bin/ptx
fi

if [[ "$PACKAGE_NAME" == "file" ]]; then
    cp /usr/lib/x86_64-linux-gnu/libmagic.so.1.0.0 ./src/.libs/libmagic.so.1.0.0
    cp /usr/lib/x86_64-linux-gnu/libmagic.so.1.0.0 ./debian/tmp/usr/lib/x86_64-linux-gnu/libmagic.so.1.0.0
fi

if [[ "$PACKAGE_NAME" == "util-linux" ]]; then
    cp /usr/bin/lscpu .libs/lscpu
    cp /usr/bin/lslogins .libs/lslogins
    cp /usr/bin/lscpu debian/util-linux/usr/bin/lscpu
    cp /usr/bin/lslogins debian/util-linux/usr/bin/lslogins
    cp /usr/bin/lscpu debian/tmp/usr/bin/lscpu
    cp /usr/bin/lslogins debian/tmp/usr/bin/lslogins
fi

echo @@@@@@@@ Checking autopkgtest existence @@@@@@@@
if [[ -d debian/tests ]]; then
    echo FOUND
    ls debian/tests
else
    echo NOT FOUND
fi
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo
echo @@@@@@@@ Attempting dh_auto_test @@@@@@@@
rm -rf llvm-cov-profraw
mkdir -p llvm-cov-profraw
export LLVM_PROFILE_FILE="$( realpath llvm-cov-profraw/%h-%p.profraw )"
/usr/bin/time -o dh_auto_test.time.txt -v dh_auto_test |& tee dh_auto_test.log > /dev/null
if [[ -s dh_auto_test.log ]]; then
    if grep -q 'dh_auto_test: error: Please specify the compatibility level in debian/compat or via Build-Depends: debhelper-compat (= X)' dh_auto_test.log >& /dev/null; then
        # So far encountered in "debianutils" package which seems to not support
        # dh_auto_test at all. Execute autopkgtest in an ad-hoc way.
        if [[ "$PACKAGE_NAME" == "debianutils" ]]; then
            export PATH_BACKUP=$PATH
            export PATH=`realpath .`:$PATH
            bash debian/tests/smoke
            export PATH=$PATH_BACKUP
        fi
    else
    echo SOME OUTPUT
    head dh_auto_test.log
    echo ...
    tail dh_auto_test.log
    grep Elapsed dh_auto_test.time.txt
    fi
else
    echo NO OUTPUT
fi
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

popd

################################################################################

echo
BINARY=$EXECUTABLE $THIS_DIR/get-coverage.sh
echo
