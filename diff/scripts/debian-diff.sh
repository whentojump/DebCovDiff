#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
START_WITH=${START_WITH:-"test"}

DIFF_PY_OPTS=""

if [[ $SHOW_SOURCE == 1 ]]; then
    DIFF_PY_OPTS="--show-source"
fi
if [[ -n "$LOG_LEVEL" ]]; then
    DIFF_PY_OPTS="--log-level $LOG_LEVEL $DIFF_PY_OPTS"
fi
if [[ $ALL_METRICS == 1 ]]; then
    DIFF_PY_OPTS="--all-metrics $DIFF_PY_OPTS"
fi

cd /var/lib/sbuild/build

mkdir -p $1 $1-log

PREV_LOG_ID=$(ls $1-log/*.diff_log.txt 2>/dev/null | sort -n | tail -1)

if [[ -z "$PREV_LOG_ID" ]]; then
    PREV_LOG_ID=0
else
    PREV_LOG_ID=$(basename $PREV_LOG_ID .diff_log.txt)
fi

NEW_LOG_ID=$((PREV_LOG_ID + 1))

if [[ $START_WITH != "diff" ]]; then

    THIS_LOG_ID=$NEW_LOG_ID

    START_WITH=$START_WITH \
    INSTR_OPTION=gcc-mcdc \
    DEB_BUILD_OPTIONS="nocheck nostrip" \
    DEB_BUILD_PROFILES="nocheck nostrip" \
    $REPO_DIR/debian/scripts/build-package.sh $1 |& tee $1-log/$THIS_LOG_ID.gcc_build_log.txt
    RET=$?
    if [[ $RET -ne 0 ]]; then
        echo "GCC build-package.sh: $RET"
        exit 1
    fi

    START_WITH=$START_WITH \
    INSTR_OPTION=clang-mcdc \
    DEB_BUILD_OPTIONS="nocheck nostrip" \
    DEB_BUILD_PROFILES="nocheck nostrip" \
    $REPO_DIR/debian/scripts/build-package.sh $1 |& tee $1-log/$THIS_LOG_ID.clang_build_log.txt
    RET=$?
    if [[ $RET -ne 0 ]]; then
        echo "Clang build-package.sh: $RET"
        exit 1
    fi
else
    THIS_LOG_ID=$PREV_LOG_ID
fi

$THIS_DIR/../diff.py \
--all-inconsistency-csv $1-log/$THIS_LOG_ID.inconsistent.csv \
--total-num-csv $1-log/$THIS_LOG_ID.compared.csv \
$DIFF_PY_OPTS \
deb $1 |&\
tee $1-log/$THIS_LOG_ID.diff_log.txt
