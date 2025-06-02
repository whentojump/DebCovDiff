#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $THIS_DIR/common.sh

SBUILD_DISTRO=${SBUILD_DISTRO:-"bookworm"}

INSTR_OPTION_LIST=("clang-mcdc" "gcc-mcdc")

# This is used in LLVM install path
LLVM_UNDER_TEST_VERSION=20

HOST_GCC_PREFIX=$DIFF_WORKDIR/.build-gcc/install
HOST_LLVM_PREFIX=$DIFF_WORKDIR/.build-llvm/install

if ! id -nG | grep -q sbuild; then
    say "User is not in sbuild group (you probably need to log out and back in, or run newgrp)"
    exit 0
fi

for INSTR_OPTION in "${INSTR_OPTION_LIST[@]}"; do
    CHROOT_NAME=$SBUILD_DISTRO-amd64-sbuild-$INSTR_OPTION

    if [[ -f /srv/chroot/$CHROOT_NAME/etc/CONFIGURED ]]; then
        say "the chroot for [$INSTR_OPTION] seems already configured"
        continue
    fi

    if [[ $INSTR_OPTION == clang* ]]; then
        say "install LLVM dependencies to the chroot for [$INSTR_OPTION]"
        # Not always necessary. Depends on how LLVM was built.
        sbuild-apt $CHROOT_NAME apt-get install \
            libxml2 libz3-4 libedit2 libcurl4 > /dev/null
    fi

    say "install distro's Clang and LLVM to the chroot for [$INSTR_OPTION] (so that we can hold it later)"
    sbuild-apt $CHROOT_NAME apt-get install clang llvm > /dev/null

    # The installation paths are following https://apt.llvm.org/ and
    # https://jwakely.github.io/pkg-gcc-latest/ respectively

    case "${INSTR_OPTION}" in
    clang*)
        sudo rm -rf /srv/chroot/$CHROOT_NAME/usr/lib/llvm-$LLVM_UNDER_TEST_VERSION
        sudo cp -r $HOST_LLVM_PREFIX /srv/chroot/$CHROOT_NAME/usr/lib/llvm-$LLVM_UNDER_TEST_VERSION
        say "LLVM (re)installed to the chroot for [$INSTR_OPTION]"
        ;;
    gcc*)
        sudo rm -rf /srv/chroot/$CHROOT_NAME/opt/gcc-latest
        sudo cp -r $HOST_GCC_PREFIX /srv/chroot/$CHROOT_NAME/opt/gcc-latest
        say "GCC (re)installed to the chroot for [$INSTR_OPTION]"
        ;;
    esac

    # Note seen from the host the below symlinks might be broken (depending on
    # where LLVM is installed on host). But seen within the chroot they are
    # rightly pointing to what we've just copied into chroot.

    # libclang-cpp.so and libLLVM.so seem irrelevant to our purposes thus not
    # linked in the below step.

    if [[ $INSTR_OPTION == clang* ]]; then
        sudo rm -f /srv/chroot/$CHROOT_NAME/usr/bin/clang
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/clang /srv/chroot/$CHROOT_NAME/usr/bin/real-clang
        sudo rm -f /srv/chroot/$CHROOT_NAME/usr/bin/clang++
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/clang++ /srv/chroot/$CHROOT_NAME/usr/bin/real-clang++
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/lld /srv/chroot/$CHROOT_NAME/usr/bin/lld
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/ld.lld /srv/chroot/$CHROOT_NAME/usr/bin/ld.lld
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/llvm-ar /srv/chroot/$CHROOT_NAME/usr/bin/llvm-ar
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/llvm-nm /srv/chroot/$CHROOT_NAME/usr/bin/llvm-nm
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/llvm-strip /srv/chroot/$CHROOT_NAME/usr/bin/llvm-strip
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/llvm-objcopy /srv/chroot/$CHROOT_NAME/usr/bin/llvm-objcopy
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/llvm-objdump /srv/chroot/$CHROOT_NAME/usr/bin/llvm-objdump
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/llvm-readelf /srv/chroot/$CHROOT_NAME/usr/bin/llvm-readelf
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/llvm-cov /srv/chroot/$CHROOT_NAME/usr/bin/llvm-cov
        sudo ln -sf /usr/lib/llvm-$LLVM_UNDER_TEST_VERSION/bin/llvm-profdata /srv/chroot/$CHROOT_NAME/usr/bin/llvm-profdata

        say "LLVM symlinks created in the chroot for [$INSTR_OPTION]"
    fi

    cd /srv/chroot/$CHROOT_NAME/usr/bin

    case "${SBUILD_DISTRO}" in
    bookworm)
        NATIVE_GCC_VERSION="12"
        NATIVE_LLVM_VERSION_MIN="13"
        NATIVE_LLVM_VERSION_MAX="16"
        ;;
    jammy)
        NATIVE_GCC_VERSION="11"
        NATIVE_LLVM_VERSION_MIN="11"
        NATIVE_LLVM_VERSION_MAX="15"
        ;;
    esac

    if ! [ -d backup ]; then
        sudo mkdir -p backup
        sudo mv g++-$NATIVE_GCC_VERSION backup
        sudo mv gcc-$NATIVE_GCC_VERSION backup
        sudo mv cpp-$NATIVE_GCC_VERSION backup
        sudo mv g++ gcc cpp backup
    fi

    # /usr/bin/cc -> /etc/alternatives/cc -> /usr/bin/gcc, so we don't have
    # explicitly create a symlink for cc.

    case "${INSTR_OPTION}" in
    clang*)
        sudo ln -sf clang++ g++-$NATIVE_GCC_VERSION
        sudo ln -sf clang gcc-$NATIVE_GCC_VERSION
        sudo ln -sf clang cpp-$NATIVE_GCC_VERSION
        sudo ln -sf clang++ g++
        sudo ln -sf clang gcc
        sudo ln -sf clang cpp
        sudo tee clang > /dev/null << 'EOF'
#!/bin/bash

# Do not print anything in this script or some build systems would fail.

REAL_CLANG=${REAL_CLANG:-"/usr/bin/real-clang"}

declare -a CC_ARGS
for var in "$@"; do
    case "$var" in
        -O0|-O|-O1|-O2|-O3|-Oz|-Og|-Os|-Ofast)
            continue
            ;;
        -O*)
            echo "$var is not seen before"
            exit 1
            ;;
    esac
    CC_ARGS[${#CC_ARGS[@]}]="$var"
done

$REAL_CLANG "${CC_ARGS[@]}"
EOF
        sed 's|real-clang|real-clang++|' clang | sudo tee clang++ > /dev/null
        sudo chmod +x clang clang++
        ;;
    gcc*)
        sudo tee gcc > /dev/null << 'EOF'
#!/bin/bash

# Do not print anything in this script or some build systems would fail.

REAL_GCC=${REAL_GCC:-"/opt/gcc-latest/bin/gcc"}

declare -a CC_ARGS
for var in "$@"; do
    case "$var" in
        -O0|-O|-O1|-O2|-O3|-Oz|-Og|-Os|-Ofast)
            continue
            ;;
        -O*)
            echo "$var is not seen before"
            exit 1
            ;;
    esac
    CC_ARGS[${#CC_ARGS[@]}]="$var"
done

$REAL_GCC "${CC_ARGS[@]}"
EOF
        sed 's|/opt/gcc-latest/bin/gcc|/opt/gcc-latest/bin/g++|' gcc | sudo tee g++ > /dev/null
        sed 's|/opt/gcc-latest/bin/gcc|/opt/gcc-latest/bin/cpp|' gcc | sudo tee cpp > /dev/null
        sudo chmod +x gcc g++ cpp
        sudo ln -sf g++ g++-$NATIVE_GCC_VERSION
        sudo ln -sf gcc gcc-$NATIVE_GCC_VERSION
        sudo ln -sf cpp cpp-$NATIVE_GCC_VERSION
        ;;
    esac

    sbuild-hold $CHROOT_NAME cpp                                > /dev/null
    sbuild-hold $CHROOT_NAME cpp-$NATIVE_GCC_VERSION            > /dev/null
    sbuild-hold $CHROOT_NAME g++                                > /dev/null
    sbuild-hold $CHROOT_NAME g++-$NATIVE_GCC_VERSION            > /dev/null
    sbuild-hold $CHROOT_NAME gcc                                > /dev/null
    sbuild-hold $CHROOT_NAME gcc-$NATIVE_GCC_VERSION            > /dev/null
    sbuild-hold $CHROOT_NAME gcc-$NATIVE_GCC_VERSION-base:amd64 > /dev/null
    # Some packages might explicitly specify Clang/LLVM as build dependency.
    # E.g. doxygen [1]. The below is to prevent the Debian/Ubuntu's official
    # binaries from overriding our custom ones.
    # [1] https://salsa.debian.org/debian/doxygen/-/blob/master/debian/control
    sbuild-hold $CHROOT_NAME llvm                               > /dev/null
    sbuild-hold $CHROOT_NAME clang                              > /dev/null

    echo "Optional: to verify that the packages are indeed held, run"
    echo
    echo "  sudo sbuild-shell $CHROOT_NAME"
    echo "  # (Within the chroot)"
    echo "  dpkg --get-selections cpp                                &&\\"
    echo "  dpkg --get-selections cpp-$NATIVE_GCC_VERSION            &&\\"
    echo "  dpkg --get-selections g++                                &&\\"
    echo "  dpkg --get-selections g++-$NATIVE_GCC_VERSION            &&\\"
    echo "  dpkg --get-selections gcc                                &&\\"
    echo "  dpkg --get-selections gcc-$NATIVE_GCC_VERSION            &&\\"
    echo "  dpkg --get-selections gcc-$NATIVE_GCC_VERSION-base:amd64 &&\\"
    echo "  dpkg --get-selections llvm                               &&\\"
    echo "  dpkg --get-selections clang                              &&\\"
    echo "  true"

    case "${INSTR_OPTION}" in
    clang*) say "GCC executables replaced with LLVM wrapper scripts in the chroot for [$INSTR_OPTION]";;
    gcc*)   say "Original GCC executables replaced with custom GCC wrapper scripts in the chroot for [$INSTR_OPTION]";;
    esac

    sudo truncate -s 0 /srv/chroot/$CHROOT_NAME/etc/dpkg/buildflags.conf
    case "${INSTR_OPTION}" in
    clang-mcdc)
        CFLAGS="-O0 -fprofile-instr-generate -fcoverage-mapping -fcoverage-mcdc"
        LDFLAGS="-Wl,-z,relro -fprofile-instr-generate -fcoverage-mapping -fcoverage-mcdc"
        ;;
    clang-scc)
        CFLAGS="-O0 -fprofile-instr-generate -fcoverage-mapping"
        LDFLAGS="-Wl,-z,relro -fprofile-instr-generate -fcoverage-mapping"
        ;;
    clang-no-instr)
        CFLAGS="-O0"
        LDFLAGS="-Wl,-z,relro"
        ;;
    gcc-mcdc)
        CFLAGS="-O0 --coverage -fcondition-coverage"
        LDFLAGS="-Wl,-z,relro --coverage -fcondition-coverage"
        ;;
    gcc-gcov)
        CFLAGS="-O0 --coverage"
        LDFLAGS="-Wl,-z,relro --coverage"
        ;;
    gcc-no-instr)
        CFLAGS="-O0"
        LDFLAGS="-Wl,-z,relro"
        ;;
    esac
    sudo tee /srv/chroot/$CHROOT_NAME/etc/dpkg/buildflags.conf > /dev/null << EOF
SET CFLAGS $CFLAGS
SET CXXFLAGS $CFLAGS
SET LDFLAGS $LDFLAGS
EOF

    say "Compiler flags set up in the chroot for [$INSTR_OPTION]"

    echo "Optional: to verify that the compiler flag settings are recognized and honored, run"
    echo
    echo "  sudo sbuild-shell $CHROOT_NAME"
    echo "  # (Within the chroot)"
    echo "  dpkg-buildflags"

    # Generate unique profile filename for each invocation (LLVM-specific)

    say "install uuid-gen to the chroot for [$INSTR_OPTION]"
    sbuild-apt $CHROOT_NAME apt-get install uuid-runtime > /dev/null

    # Format generated JSON files for easier manual inspection

    say "install jq to the chroot for [$INSTR_OPTION]"
    sbuild-apt $CHROOT_NAME apt-get install jq > /dev/null

    # For development only

    say "install vim, fzf and strace to the chroot for [$INSTR_OPTION]"
    sbuild-apt $CHROOT_NAME apt-get install vim fzf strace > /dev/null

    say "configure Bash PS1 in the chroot for [$INSTR_OPTION]"
    printf "export PS1='\\[\\\e[34;1m\\]\${debian_chroot:+(\$debian_chroot)}\\\u@\\h:\\w\\[\\\e[0m\\]\\\n\\$ '\n" |\
        sudo tee -a /srv/chroot/$CHROOT_NAME/root/.bashrc > /dev/null

    # So that we can run "clear" in chroot
    say "configure Bash TERM in the chroot for [$INSTR_OPTION]"
    printf "export TERM=xterm-256color\n" |\
        sudo tee -a /srv/chroot/$CHROOT_NAME/root/.bashrc > /dev/null

    say "finish configuring the chroot for [$INSTR_OPTION]"
    sudo touch /srv/chroot/$CHROOT_NAME/etc/CONFIGURED
done
