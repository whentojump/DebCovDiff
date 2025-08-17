#!/bin/bash

export ALL_METRICS=1
export LOG_LEVEL=warning
export SHOW_SOURCE=1

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
script_version=$( cd $THIS_DIR; git log --pretty='format:%h "%s"' -n 1 )

start_date=$( date )
start_timestamp=$( date +%s )

print_time_diff() {
    t1=$1
    t2=$2

    diff=$(( t2 - t1 ))

    hours=$(( diff / 3600 ))
    minutes=$(( (diff % 3600) / 60 ))
    seconds=$(( diff % 60 ))

    printf "%d:%d:%d\n" $hours $minutes $seconds
}

print_time_diff() {
    t1=$1
    t2=$2

    diff=$(( t2 - t1 ))

    hours=$(( diff / 3600 ))
    minutes=$(( (diff % 3600) / 60 ))
    seconds=$(( diff % 60 ))

    printf "%02d:%02d:%02d\n" $hours $minutes $seconds
}

summary() {
    echo
    echo
    echo "================================================================="
    echo "Hostname:           $( hostname )"
    # If it's on CloudLab we would have this utility to get some information
    # about the hardware
    if command -v geni-get >& /dev/null; then
        cloudlab_hardware=`geni-get portalmanifest | xmllint - --xpath "string(/*[local-name() = 'rspec']/*[local-name() = 'node']/*[local-name() = 'vnode']/@hardware_type)"`
        echo "Hardware:           $cloudlab_hardware"
    else
        echo "Hardware:           not on CloudLab"
    fi
    echo "Start date:         $start_date"
    echo "Now:                $( date )"
    current_timestamp=$( date +%s )
    echo "Duration:           $( print_time_diff $start_timestamp $current_timestamp )"
    echo "Script version:     $script_version"
    echo "Toolchain version:"
    echo
    schroot -c bookworm-amd64-sbuild-gcc-mcdc -d / -- sh -c "gcc -v"
    echo
    schroot -c bookworm-amd64-sbuild-clang-mcdc -d / -- sh -c "gcc -v"
    echo
    echo "================================================================="
}

abort() {
    summary
    exit 1
}

mapfile -t PACKAGE_LIST < $DIFF_WORKDIR/ase25/tables-and-figures/scripts/data/select/selection_7_success.txt

REPEAT=$(jq -r .repeat $THIS_DIR/../config.json)

if [[ $AUTO_TESTS == "1" ]]; then
    PACKAGE_LIST=(
        "bzip2"
        "debianutils"
        "distro-info"
        "file"
        "ifupdown"
        "lsof"
        "lzo2"
        "mawk"
        "procps"
        "psmisc"
    )
fi

# For developing and testing this script itself
if [[ $DEV == "1" ]]; then
    PACKAGE_LIST=( "hostname" )
fi

if [[ $( ls /var/lib/sbuild/build/ | wc -l ) != 0 ]]; then
    echo "Directory /var/lib/sbuild/build/ is not empty."
    exit 1
fi

# The script invocation chain looks like:
#
#                                                           download_source
#   debian-batch.sh ──► debian-diff.sh ──► build-package.sh ───────────────► sbuild(1)
#                 │                        ▲              │ build/test/diff
#                 └────────────────────────┘              └────────────────► schroot(1)
#
# In the first run of sl package ("download_source" mode) we are invoking
# sbuild(1) which won't provide an interactive shell and sl tests will mess
# up the terminal. On the other hand in later runs ("test" mode), we are
# invoking schroot(1) which does provide an interactive shell and sl tests
# pretty much looks like being run on the host environment. The problem is
# these two types of run would result in different terminal size thus
# inaccuracy in differential testing. Therefore we build sl package separately
# and then run all tests in a consistent mode.

if [[ " ${PACKAGE_LIST[@]} " =~ " sl " ]]; then
    echo
    echo "Building sl package separately"
    echo
    INSTR_OPTION=clang-mcdc START_WITH="download_source" DEB_BUILD_OPTIONS="nocheck" $DIFF_WORKDIR/$REPO_NAME/debian/scripts/build-package.sh sl >& /dev/null < /dev/null
    # Handling Ctrl + C:
    #
    # - For builds ("download_source" mode), *sbuild(1)* intercepts signals.
    #   So here in this outermost caller script we don't trap signals, let
    #   sbuild(1) finish its own graceful shutdown, and exit the whole script
    #   by checking exit code.
    # - For tests ("test" mode), schroot(1) doesn't intercept signals and would
    #   otherwise get killed by Ctrl + C. So here in this outermost caller script
    #   *we* trap signals to still print the start and end dates.
    ret=$?
    if [[ $ret -ne 0 ]]; then
        echo "build-package.sh: $ret"
        abort
    fi
    INSTR_OPTION=gcc-mcdc START_WITH="download_source" DEB_BUILD_OPTIONS="nocheck" $DIFF_WORKDIR/$REPO_NAME/debian/scripts/build-package.sh sl >& /dev/null < /dev/null
    ret=$?
    if [[ $ret -ne 0 ]]; then
        echo "build-package.sh: $ret"
        abort
    fi
fi

for p in "${PACKAGE_LIST[@]}"; do
    if [[ $p == "sl" ]]; then
        continue
    fi
    START_WITH="download_source" $DIFF_WORKDIR/$REPO_NAME/diff/scripts/debian-diff.sh $p
    ret=$?
    if [[ $ret -ne 0 ]]; then
        echo "debian-diff.sh: $ret"
        abort
    fi
done

# Experiments suggest "download_source" vs. "test" mode can cause coverage
# differences for reasons yet unclear. So run all tests in a consistent mode.
for p in "${PACKAGE_LIST[@]}"; do
    sudo rm -rf /var/lib/sbuild/build/$p
    sudo rm -rf /var/lib/sbuild/build/$p-log
done

trap 'abort' SIGINT

for i in `seq 1 $REPEAT`; do
    for p in "${PACKAGE_LIST[@]}"; do
        START_WITH="test" $DIFF_WORKDIR/$REPO_NAME/diff/scripts/debian-diff.sh $p
        ret=$?
        if [[ $ret -ne 0 ]]; then
            echo "debian-diff.sh: $ret"
            abort
        fi
    done
done

summary >& /var/lib/sbuild/build/debian-batchrun-summary.txt

renamed_dir=$( mktemp -d /var/lib/sbuild/build-$( date +'%m-%d' )-XXXX )
cp -r /var/lib/sbuild/build/* $renamed_dir
cat $renamed_dir/debian-batchrun-summary.txt
rm -f /var/lib/sbuild/build-latest
ln -sf $renamed_dir /var/lib/sbuild/build-latest

exit 0
