#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $THIS_DIR/common.sh

INSTR_OPTION=${INSTR_OPTION:-"clang-mcdc"}
SBUILD_DISTRO=${SBUILD_DISTRO:-"bookworm"}
CHROOT_NAME=$SBUILD_DISTRO-amd64-sbuild-$INSTR_OPTION

if [[ ! -z $SBUILD_WORKDIR && -d $SBUILD_WORKDIR ]]; then
    cd $SBUILD_WORKDIR
fi

if [[ -n "$CUSTOM_SBUILD_PREFIX" ]]; then
    SBUILD_PATH="$CUSTOM_SBUILD_PREFIX/bin"
    PERL5LIB="$CUSTOM_SBUILD_PREFIX/lib"
else
    SBUILD_PATH="/usr/bin"
    PERL5LIB=""
fi

CHROOT_HOOK_PREFIX="/opt/DebCovDiff"
sudo rm -rf /srv/chroot/${CHROOT_NAME}${CHROOT_HOOK_PREFIX}
sudo mkdir -p /srv/chroot/${CHROOT_NAME}${CHROOT_HOOK_PREFIX}/bin
sudo cp -r $THIS_DIR/chroot/* /srv/chroot/${CHROOT_NAME}${CHROOT_HOOK_PREFIX}/bin

if ! grep nocheck <<< "$DEB_BUILD_PROFILES" > /dev/null; then
    DEB_BUILD_PROFILES="nocheck $DEB_BUILD_PROFILES"
fi
if ! grep nocheck <<< "$DEB_BUILD_OPTIONS" > /dev/null; then
    DEB_BUILD_OPTIONS="nocheck $DEB_BUILD_OPTIONS"
fi
if ! grep nostrip <<< "$DEB_BUILD_PROFILES" > /dev/null; then
    DEB_BUILD_PROFILES="nostrip $DEB_BUILD_PROFILES"
fi
if ! grep nostrip <<< "$DEB_BUILD_OPTIONS" > /dev/null; then
    DEB_BUILD_OPTIONS="nostrip $DEB_BUILD_OPTIONS"
fi

get_project_root() {
    local pkg="$1"
    num_records=$(grep "^Package: $pkg\$" $THIS_DIR/../Sources | wc -l)
    if [[ $num_records != 1 ]]; then
        echo "$num_records records for $pkg found in Sources.gz"
        exit 1
    fi
    # E.g. traceroute has "Version:" field "1:2.1.2-1" in its metadata
    # transform it to "traceroute-2.1.2"
    version_string=$( cat $THIS_DIR/../Sources |
        awk -v pkg="$pkg" '
            $1 == "Package:" && $2 == pkg { found=1 }
            found && $1 == "Version:" { print $2; exit }
        ' |
        cut -d: -f2 |
        rev | cut -d- -f2- | rev )
    echo "$pkg-$version_string"
}

PROJECT_ROOT=$(get_project_root $1)
source $THIS_DIR/test-plan-diff.sh

if [[ -f $THIS_DIR/chroot/$1.$INSTR_OPTION.mk ]]; then
    STARTING_BUILD_HOOK="
        $STARTING_BUILD_HOOK
        # This suffix somehow cannot be .bak...
        mv $MAKEFILE $MAKEFILE.original
        cp $CHROOT_HOOK_PREFIX/bin/$1.$INSTR_OPTION.mk $MAKEFILE
        # This hook is run as root if part of sbuild. Chown to get less trouble
        chown $(id -nu):$(id -ng) $MAKEFILE $MAKEFILE.original
    "
fi

if [[ "$INSTR_OPTION" == "clang-mcdc" || "$INSTR_OPTION" == "clang-scc" ]]; then
    if [[ "$INSTR_OPTION" == "clang-mcdc" ]]; then
        LLVM_COV_FLAGS="--show-branches=count --show-mcdc --show-mcdc-summary"
    else
        LLVM_COV_FLAGS="--show-branches=count"
    fi

    if [[ -n "$EXECUTABLE" || -n "$LIBRARY" ]]; then
        if [[ -f $THIS_DIR/chroot/$1.sh ]]; then
            PACKAGE_SPECIFIC_SCRIPT=$1.sh
        else
            PACKAGE_SPECIFIC_SCRIPT=common/default.sh
        fi
        FINISHED_BUILD_HOOK="
            PROJECT_ROOT=$PROJECT_ROOT       \\
            EXECUTABLE=$EXECUTABLE           \\
            EXECUTABLE2=$EXECUTABLE2         \\
            EXECUTABLE3=$EXECUTABLE3         \\
            EXECUTABLE4=$EXECUTABLE4         \\
            EXECUTABLE5=$EXECUTABLE5         \\
            ARGS='$ARGS'                     \\
            ARGS2='$ARGS2'                   \\
            ARGS3='$ARGS3'                   \\
            ARGS4='$ARGS4'                   \\
            ARGS5='$ARGS5'                   \\
            LD_LIBRARY_PATH=$LD_LIBRARY_PATH \\
            LIBRARY=$LIBRARY                 \\
            LLVM_COV_FLAGS='$LLVM_COV_FLAGS' \\
            INSTR_OPTION=$INSTR_OPTION       \\
            $CHROOT_HOOK_PREFIX/bin/$PACKAGE_SPECIFIC_SCRIPT
        "
    fi
elif [[ "$INSTR_OPTION" == "gcc-mcdc" || "$INSTR_OPTION" == "gcc-gcov" ]]; then
    if [[ "$INSTR_OPTION" == "gcc-mcdc" ]]; then
        GCOV_FLAGS="-b -c --conditions"
    else
        GCOV_FLAGS="-b -c"
    fi

    if [[ -n "$EXECUTABLE" || -n "$LIBRARY" ]]; then
        if [[ -f $THIS_DIR/chroot/$1.sh ]]; then
            PACKAGE_SPECIFIC_SCRIPT=$1.sh
        else
            PACKAGE_SPECIFIC_SCRIPT=common/default.sh
        fi
        FINISHED_BUILD_HOOK="
            $CHROOT_HOOK_PREFIX/bin/common/gcov-pre-tests.sh;
            PROJECT_ROOT=$PROJECT_ROOT       \\
            EXECUTABLE=$EXECUTABLE           \\
            EXECUTABLE2=$EXECUTABLE2         \\
            EXECUTABLE3=$EXECUTABLE3         \\
            EXECUTABLE4=$EXECUTABLE4         \\
            EXECUTABLE5=$EXECUTABLE5         \\
            ARGS='$ARGS'                     \\
            ARGS2='$ARGS2'                   \\
            ARGS3='$ARGS3'                   \\
            ARGS4='$ARGS4'                   \\
            ARGS5='$ARGS5'                   \\
            LD_LIBRARY_PATH=$LD_LIBRARY_PATH \\
            LIBRARY=$LIBRARY                 \\
            GCOV_FLAGS='$GCOV_FLAGS'         \\
            INSTR_OPTION=$INSTR_OPTION       \\
            $CHROOT_HOOK_PREFIX/bin/$PACKAGE_SPECIFIC_SCRIPT
        "
    fi
fi

# This hook is run as root, making coverage data, reports etc owned by root.
FINISHED_BUILD_HOOK="
    $FINISHED_BUILD_HOOK
    echo; gcc -v
    echo; id
    echo ---
    find . ! \( -user $(id -nu) -a -group $(id -ng) \)
    echo ---; echo 'Fix file ownership (1)'; echo ---
    chown -R $(id -nu):$(id -ng) .
    find . ! \( -user $(id -nu) -a -group $(id -ng) \)
    echo ---
"

STARTING_BUILD_HOOK="
    $STARTING_BUILD_HOOK
    echo; gcc -v
    echo; id
    echo
"

# Use predictable build directory names, in the format of <package>-{gcc,clang}-
# <id>, where <id> increases monotonically

if [[ $INSTR_OPTION == gcc* ]]; then
    CC=gcc
elif [[ $INSTR_OPTION == clang* ]]; then
    CC=clang
fi

PREV_ID=$(
    ls -d /var/lib/sbuild/build/$1-$CC-* 2>/dev/null                          |\
    sed "s|/var/lib/sbuild/build/$1-$CC-||"                                   |\
    sort -n | tail -1
)

if [[ -z "$PREV_ID" ]]; then
    PREV_ID=0
    START_WITH="download_source"
fi

if [[ $START_WITH == "download_source" ]]; then

    NEW_ID=$((PREV_ID + 1))
    BUILD_PATH="/build/$1-$CC-$NEW_ID"
    HOST_BUILD_PATH="/var/lib/sbuild/$BUILD_PATH"

    DEB_BUILD_OPTIONS=$DEB_BUILD_OPTIONS                                       \
    DEB_BUILD_PROFILES=$DEB_BUILD_PROFILES                                     \
    PERL5LIB=$PERL5LIB                                                         \
    $SBUILD_PATH/sbuild $1 -v -d $SBUILD_DISTRO                                \
        --chroot $CHROOT_NAME                                                  \
        --build-path=$BUILD_PATH                                               \
        `# Hook 1: host`                                                       \
        `#--pre-build-commands="true"`                                         \
        `# Hook 2: chroot`                                                     \
        `#--chroot-setup-commands="true"`                                      \
        `# Hook 3: chroot`                                                     \
        `# At this step we are at /<<BUILDDIR>>, e.g. /build/sl-nZDlZB`        \
        --starting-build-commands="$STARTING_BUILD_HOOK"                       \
        `# Hook 4: chroot`                                                     \
        `# At this step we are at /<<BUILDDIR>>, e.g. /build/sl-nZDlZB`        \
        --finished-build-commands="$FINISHED_BUILD_HOOK"                       \
        `# Hook 5: chroot`                                                     \
        `#--chroot-cleanup-commands="true"`                                    \
        `# Hook 6: host`                                                       \
        `#--post-build-commands="true"`                                        \
        `# The below flags skip some irrelevant steps`                         \
        --no-run-lintian                                                       \
        --no-apt-update --no-apt-upgrade --no-apt-distupgrade                  \
        `# Persist intermediate build results and dependency packages`         \
        --purge-build=never                                                    \
        `# This may cause trouble for some packages... e.g. vim`               \
        --purge-deps=never                                                     \
        `# Destroy the one-off chroot session created for this`                \
        `# invocation of sbuild`                                               \
        --purge-session=always

    RET=$?
    if [[ $RET -ne 0 ]]; then
        echo "sbuild: $RET"
        exit 1
    fi

    # The majority of sbuild is run as non-root user but some final steps
    # would create *.changes owned by root
    echo ---
    find $HOST_BUILD_PATH ! \( -user $(id -nu) -a -group $(id -ng) \)
    echo ---
    echo 'Fix file ownership (2)'
    sudo chown -R $(id -nu):$(id -ng) $HOST_BUILD_PATH
    echo ---
    find $HOST_BUILD_PATH ! \( -user $(id -nu) -a -group $(id -ng) \)
    echo ---
else

    BUILD_PATH="/build/$1-$CC-$PREV_ID"
    HOST_BUILD_PATH="/var/lib/sbuild/$BUILD_PATH"

    # build: (1) remove previous coverage data but keep *.gcno
    #        (2) incremental build and overwrite some *.gcno
    #        (3) test
    # test:  (1) remove previous coverage data but keep *.gcno
    #        (2) test

    schroot -c $CHROOT_NAME                                                    \
            -u root                                                            \
            -d $BUILD_PATH                                                     \
            -- sh -c "$CHROOT_HOOK_PREFIX/bin/common/clean-coverage.sh"

    if [[ $START_WITH == "build" ]]; then

        # In case *.mk files are modified
        schroot -c $CHROOT_NAME                                                \
                -u root                                                        \
                -d $BUILD_PATH                                                 \
                -- sh -c "$STARTING_BUILD_HOOK"

        schroot -c $CHROOT_NAME                                                \
                -u $(id -nu)                                                   \
                -d $BUILD_PATH                                                 \
                -- sh -c "cd $PROJECT_ROOT
                          export DEB_BUILD_OPTIONS=\"$DEB_BUILD_OPTIONS\"
                          export DEB_BUILD_PROFILES=\"$DEB_BUILD_PROFILES\"
                          $CHROOT_HOOK_PREFIX/bin/common/rebuild.sh $1"

    fi

    schroot -c $CHROOT_NAME                                                    \
            -u $(id -nu)                                                       \
            -d $BUILD_PATH                                                     \
            -- sh -c "$FINISHED_BUILD_HOOK"

    # So far observe nothing
    echo ---
    find $HOST_BUILD_PATH ! \( -user $(id -nu) -a -group $(id -ng) \)
    echo ---
    echo 'Fix file ownership (3)'
    sudo chown -R $(id -nu):$(id -ng) $HOST_BUILD_PATH
    echo ---
    find $HOST_BUILD_PATH ! \( -user $(id -nu) -a -group $(id -ng) \)
    echo ---
fi
