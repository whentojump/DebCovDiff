#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $THIS_DIR/common.sh

SBUILD_DISTRO=${SBUILD_DISTRO:-"bookworm"}

INSTR_OPTION_LIST=("clang-mcdc" "gcc-mcdc")

for INSTR_OPTION in "${INSTR_OPTION_LIST[@]}"; do
    if ! schroot -l 2>/dev/null |\
         grep -q "chroot:$SBUILD_DISTRO-amd64-sbuild-$INSTR_OPTION"; then

        INSTR_OPTION=$INSTR_OPTION SBUILD_DISTRO=$SBUILD_DISTRO $THIS_DIR/setup-init-chroot.sh
        RET=$?
        if [[ $RET -ne 0 ]]; then
            echo "./setup-init-chroot.sh: $RET"
            exit 1
        fi
        say "chroot for [$INSTR_OPTION] is downloaded"

    else
        say "chroot for [$INSTR_OPTION] already exists"
        exit 1
    fi
done
