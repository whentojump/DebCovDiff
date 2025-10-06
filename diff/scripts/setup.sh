#!/bin/bash

set -ex

if [[ $DEV == "1" ]]; then
    cat << 'EOF'

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

You are in development mode which is for the insiders only. If
you are not the authors please unset your DEV variable and rerun.

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

EOF

    read -n 1 -r -p "Press any key to continue..."

fi

#
# Script to set up everything for differential testing
#

### Set up variables

if ! grep '### DebCovDiff' ~/.bashrc >& /dev/null; then
    cat >> ~/.bashrc << 'EOF'

### DebCovDiff

export DIFF_WORKDIR="$HOME/DebCovDiff-workdir"

export PATH="$DIFF_WORKDIR/.build-gcc/install/bin:$PATH"
export PATH="$DIFF_WORKDIR/.build-llvm/install/bin:$PATH"

export SBUILD_WORKDIR="$HOME/.sbuild-artifacts"

export REPO_NAME="DebCovDiff"
export REPO_DIR="$DIFF_WORKDIR/$REPO_NAME"
EOF
fi

export DIFF_WORKDIR="$HOME/DebCovDiff-workdir"

export PATH="$DIFF_WORKDIR/.build-gcc/install/bin:$PATH"
export PATH="$DIFF_WORKDIR/.build-llvm/install/bin:$PATH"

export SBUILD_WORKDIR="$HOME/.sbuild-artifacts"

export REPO_NAME="DebCovDiff"
export REPO_DIR="$DIFF_WORKDIR/$REPO_NAME"

### Dependency

# apt

sudo apt -yq update
sudo apt -yq install flex cmake ninja-build mold git bc wget build-essential python3-pip bear unzip python-is-python3 jq libxml2-utils libmpc-dev sbuild csmith
# for figures
sudo apt -yq install texlive dvipng texlive-latex-extra texlive-fonts-recommended cm-super

# pip

if lsb_release -a | grep 'Distributor ID:	Debian' >& /dev/null; then
    PIP_OPTS="--break-system-packages $PIP_OPTS"
fi

pip install $PIP_OPTS pygments numpy
# for figures and tables
pip install $PIP_OPTS matplotlib==3.10.3 numpy==2.2.4

### Create workdir

mkdir -p $DIFF_WORKDIR

### Get LLVM and GCC (build both with stable GCC from the distro)

mkdir -p /tmp/DebCovDiff-toolchains/

# LLVM

if [[ ! -d $DIFF_WORKDIR/.build-llvm/install/ ]]; then

    rm -rf $DIFF_WORKDIR/.build-llvm/

    mkdir -p $DIFF_WORKDIR/.build-llvm/src/
    mkdir -p $DIFF_WORKDIR/.build-llvm/build/
    mkdir -p $DIFF_WORKDIR/.build-llvm/build-assertions/

    cd $DIFF_WORKDIR/.build-llvm/src/
    git init
    if [[ $DEV == "1" ]]; then
        git checkout -b DebCovDiff-next
    else
        git checkout -b DebCovDiff
    fi

    git remote add origin https://github.com/xlab-uiuc/llvm-project-DebCovDiff
    git pull origin DebCovDiff --depth=10


    cd $DIFF_WORKDIR/.build-llvm/build/

    # Or RelWithDebInfo
    # Always use GCC under /usr/bin/
    cmake -GNinja -DCMAKE_BUILD_TYPE="Release"                                 \
                  -DCMAKE_C_FLAGS="-pipe"                                      \
                  -DCMAKE_CXX_FLAGS="-pipe"                                    \
                  -DCMAKE_C_COMPILER="/usr/bin/gcc"                            \
                  -DCMAKE_CXX_COMPILER="/usr/bin/g++"                          \
                  -DLLVM_TARGETS_TO_BUILD="X86"                                \
                  -DLLVM_ENABLE_ASSERTIONS="OFF"                               \
                  -DLLVM_ENABLE_PROJECTS="clang;lld"                           \
                  -DLLVM_USE_LINKER="mold"                                     \
                  -DLLVM_ENABLE_RUNTIMES="compiler-rt"                         \
                  -DLLVM_PARALLEL_LINK_JOBS="2"                                \
                  -DCMAKE_EXPORT_COMPILE_COMMANDS="ON"                         \
                  -DCMAKE_INSTALL_PREFIX="$DIFF_WORKDIR/.build-llvm/install/"  \
                  $DIFF_WORKDIR/.build-llvm/src/llvm
    ninja -j$(nproc) install

    cd $DIFF_WORKDIR/.build-llvm/build-assertions/

    # Or RelWithDebInfo
    # Always use GCC under /usr/bin/
    cmake -GNinja -DCMAKE_BUILD_TYPE="Release"                                 \
                  -DCMAKE_C_FLAGS="-pipe"                                      \
                  -DCMAKE_CXX_FLAGS="-pipe"                                    \
                  -DCMAKE_C_COMPILER="/usr/bin/gcc"                            \
                  -DCMAKE_CXX_COMPILER="/usr/bin/g++"                          \
                  -DLLVM_TARGETS_TO_BUILD="X86"                                \
                  -DLLVM_ENABLE_ASSERTIONS="ON"                                \
                  -DLLVM_ENABLE_PROJECTS="clang;lld"                           \
                  -DLLVM_USE_LINKER="mold"                                     \
                  -DLLVM_ENABLE_RUNTIMES="compiler-rt"                         \
                  -DLLVM_PARALLEL_LINK_JOBS="2"                                \
                  -DCMAKE_EXPORT_COMPILE_COMMANDS="ON"                         \
                  -DCMAKE_INSTALL_PREFIX="$DIFF_WORKDIR/.build-llvm/install-assertions/" \
                  $DIFF_WORKDIR/.build-llvm/src/llvm
    ninja -j$(nproc) install

fi

# GCC

if [[ ! -d $DIFF_WORKDIR/.build-gcc/install/ ]]; then

    rm -rf $DIFF_WORKDIR/.build-gcc/

    mkdir -p $DIFF_WORKDIR/.build-gcc/src/
    mkdir -p $DIFF_WORKDIR/.build-gcc/build/

    cd $DIFF_WORKDIR/.build-gcc/src/
    git init
    git checkout -b DebCovDiff
    git remote add origin https://github.com/xlab-uiuc/gcc-DebCovDiff
    git pull origin DebCovDiff --depth=10
    cd $DIFF_WORKDIR/.build-gcc/build/
    # Always use GCC under /usr/bin/
    ../src/configure CC=/usr/bin/gcc CXX=/usr/bin/g++                          \
                     --prefix=$(realpath ../install)                           \
                     --enable-languages=c,c++                                  \
                     --enable-libstdcxx-debug                                  \
                     --enable-libstdcxx-backtrace                              \
                     --disable-bootstrap                                       \
                     --disable-multilib                                        \
                     --disable-libvtv                                          \
                     --with-system-zlib                                        \
                     --without-isl                                             \
                     --enable-multiarch
    make -j$(nproc)
    make install

fi

### Pull scripts

if [[ ! -d $REPO_DIR ]]; then
    if [[ $DEV == "1" ]]; then
        git clone git@github.com:xlab-uiuc/DebCovDiff.git $REPO_DIR
    else
        git clone https://github.com/xlab-uiuc/DebCovDiff.git $REPO_DIR
    fi
fi

### Debian

$REPO_DIR/debian/scripts/setup-all-init-chroot.sh
sudo sbuild-adduser $USER
newgrp sbuild <<< $REPO_DIR/debian/scripts/configure-all-chroot.sh

mkdir -p $SBUILD_WORKDIR

cat << EOF

===========================================================================

Setup has finished. Be sure to log out of the current shell and log back in
before starting your experiments, to make sure you are correctly in the
"sbuild" group.

===========================================================================

EOF

exit 0
