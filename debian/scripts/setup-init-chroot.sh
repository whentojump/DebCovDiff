#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $THIS_DIR/common.sh

INSTR_OPTION=${INSTR_OPTION:-"clang-mcdc"}
SBUILD_DISTRO=${SBUILD_DISTRO:-"bookworm"}

sbuild &> /dev/null

if [ $? -eq 127 ]; then
    say "sbuild command not found"
    exit 1
fi

if [ -d /srv/chroot/$SBUILD_DISTRO-amd64-sbuild-$INSTR_OPTION/ ]; then
    say "chroot already exists"
    exit 0
fi

DEBIAN_ARCHIVE=$(jq -r .debian_archive $THIS_DIR/../../diff/config.json)

echo > /tmp/sources.list << EOF
deb $DEBIAN_ARCHIVE bookworm main
deb-src $DEBIAN_ARCHIVE bookworm main
EOF

sudo sbuild-createchroot                                    \
     --chroot-suffix="-sbuild-$INSTR_OPTION"                \
     --source-template=/tmp/sources.list                    \
     $SBUILD_DISTRO                                         \
     /srv/chroot/$SBUILD_DISTRO-amd64-sbuild-$INSTR_OPTION/ \
     $DEBIAN_ARCHIVE

rm -f /tmp/sources.list

sudo mv /etc/schroot/chroot.d/$SBUILD_DISTRO-amd64-sbuild-$INSTR_OPTION* \
        /etc/schroot/chroot.d/$SBUILD_DISTRO-amd64-sbuild-$INSTR_OPTION

sudo sed -i 's|union-type=overlay|# union-type=overlay|' \
            /etc/schroot/chroot.d/$SBUILD_DISTRO-amd64-sbuild-$INSTR_OPTION
