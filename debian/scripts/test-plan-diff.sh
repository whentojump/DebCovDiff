case "$1" in
apache2)
    EXECUTABLE="$PROJECT_ROOT/apache2"
    ARGS="-f $PROJECT_ROOT/debian/config-dir/apache2.conf -d ."
    ;;
base-passwd)
    # Skip some flaky doc build problems.
    STARTING_BUILD_HOOK="
        $STARTING_BUILD_HOOK
        sed -i 's|SUBDIRS = doc man|SUBDIRS = ""|' $PROJECT_ROOT/Makefile.am
    "
    EXECUTABLE="$PROJECT_ROOT/update-passwd"
    ARGS="--version"
    ;;
bzip2)
    EXECUTABLE="$PROJECT_ROOT/debian/bzip2/bin/bzip2"
    EXECUTABLE2="$PROJECT_ROOT/debian/bzip2/bin/bzcat"
    ;;
coreutils)
    EXECUTABLE="$PROJECT_ROOT/src/seq"
    ARGS="100 200"
    ;;
cron)
    EXECUTABLE="$PROJECT_ROOT/cron"
    ARGS="--version"
    ;;
curl)
    STARTING_BUILD_HOOK="
        $STARTING_BUILD_HOOK
        apt install libcurl4
    "
    EXECUTABLE="$PROJECT_ROOT/debian/build/src/.libs/curl"
    ARGS="ifconfig.me"
    ;;
dbus)
    STARTING_BUILD_HOOK="
        $STARTING_BUILD_HOOK
        apt install libdbus-1-3
    "
    EXECUTABLE="$PROJECT_ROOT/debian/dbus-bin/usr/bin/dbus-uuidgen"
    ;;
debianutils)
    EXECUTABLE="$PROJECT_ROOT/ischroot"
    ;;
distro-info)
    STARTING_BUILD_HOOK="
        $STARTING_BUILD_HOOK
        # This is not needed without "nocheck"
        apt install distro-info-data
    "
    EXECUTABLE="$PROJECT_ROOT/debian-distro-info"
    # We don't really change the Makefile but for experiment purpose
    MAKEFILE="$PROJECT_ROOT/debian/rules"
    ;;
dmidecode)
    EXECUTABLE="$PROJECT_ROOT/dmidecode"
    ARGS="--version"
    ;;
e2fsprogs)
    EXECUTABLE="$PROJECT_ROOT/debian/e2fsprogs/sbin/e2fsck"
    ARGS="-n"
    ;;
file)
    EXECUTABLE="$PROJECT_ROOT/src/.libs/file"
    ARGS="--version"
    ;;
grep)
    EXECUTABLE="$PROJECT_ROOT/src/grep"
    ;;
gzip)
    EXECUTABLE="$PROJECT_ROOT/builddir/gzip"
    ;;
hostname)
    EXECUTABLE="$PROJECT_ROOT/hostname"
    ;;
ifupdown)
    EXECUTABLE="$PROJECT_ROOT/ifup"
    ARGS="--version"
    ;;
inetutils)
    EXECUTABLE="$PROJECT_ROOT/debian/inetutils-telnet/usr/bin/inetutils-telnet"
    ARGS="--version"
    ;;
iproute2)
    EXECUTABLE="$PROJECT_ROOT/ip/ip"
    ARGS="a"
    ;;
krb5)
    EXECUTABLE="$PROJECT_ROOT/build/clients/klist/klist"
    ;;
less)
    EXECUTABLE="$PROJECT_ROOT/less"
    ARGS="--version"
    ;;
liblockfile)
    EXECUTABLE="$PROJECT_ROOT/dotlockfile"
    ;;
lsof)
    EXECUTABLE="$PROJECT_ROOT/lsof"
    ARGS="--version"
    ;;
lz4)
    EXECUTABLE="$PROJECT_ROOT/lz4"
    ;;
lzma)
    # (1) Without setting "campat", CFLAGS is not visible in "debian/rules"
    # (2) By just setting "compat", CFLAGS is overwritten in "makefile.gcc"
    #     files. Previously we circumvent this by "make CFLAGS=..." which has
    #     higher-precedence than whatever in "makefile.gcc" but the old approach
    #     was not flexible and hardwired to one CFLAGS list, while each
    #     "makefile.gcc" may have different CFLAGS.
    STARTING_BUILD_HOOK="
        echo 13 > $PROJECT_ROOT/debian/compat
        sed -i 's|CFLAGS =|CFLAGS +=|' $PROJECT_ROOT/C/Util/7z/makefile.gcc
        sed -i 's|CFLAGS =|CFLAGS +=|' $PROJECT_ROOT/C/Util/Lzma/makefile.gcc
        sed -i 's|CFLAGS =|CFLAGS +=|' $PROJECT_ROOT/CPP/7zip/Bundles/LzmaCon/makefile.gcc
    "
    EXECUTABLE="$PROJECT_ROOT/CPP/7zip/Bundles/LzmaCon/lzmp"
    ;;
lzo2)
    LIBRARY="$PROJECT_ROOT/debian/liblzo2-2/lib/x86_64-linux-gnu/liblzo2.so.2"
    ;;
man-db)
    EXECUTABLE="$PROJECT_ROOT/debian/build/src/.libs/man"
    ;;
mawk)
    EXECUTABLE="$PROJECT_ROOT/mawk"
    ;;
nano)
    EXECUTABLE="$PROJECT_ROOT/build-nano/src/nano"
    ARGS="--version"
    ;;
net-tools)
    EXECUTABLE="$PROJECT_ROOT/netstat"
    ARGS="--route"
    ;;
newt)
    LD_LIBRARY_PATH="$PROJECT_ROOT"
    EXECUTABLE="$PROJECT_ROOT/whiptail"
    ;;
pam)
    EXECUTABLE="$PROJECT_ROOT/modules/pam_unix/unix_chkpwd"
    ;;
pciutils)
    EXECUTABLE="$PROJECT_ROOT/lspci"
    ARGS="--version"
    LD_LIBRARY_PATH="$PROJECT_ROOT/debian/libpci3/usr/lib/x86_64-linux-gnu"
    ;;
procps)
    EXECUTABLE="$PROJECT_ROOT/debian/procps/bin/ps"
    ARGS="--version"
    LD_LIBRARY_PATH="$PROJECT_ROOT/debian/libproc2-0/lib/x86_64-linux-gnu/"
    ;;
psmisc)
    EXECUTABLE="$PROJECT_ROOT/src/pstree"
    ARGS="--version"
    ;;
shadow)
    EXECUTABLE="$PROJECT_ROOT/src/id"
    ARGS="-a"
    ;;
sl)
    EXECUTABLE="$PROJECT_ROOT/sl"
    ;;
sysvinit)
    EXECUTABLE="$PROJECT_ROOT/src/last"
    ARGS="--version"
    ;;
traceroute)
    EXECUTABLE="$PROJECT_ROOT/traceroute/traceroute"
    ARGS="--version"
    ;;
util-linux)
    EXECUTABLE="$PROJECT_ROOT/last"
    ;;
wget)
    EXECUTABLE="$PROJECT_ROOT/build/src/wget"
    ARGS="--version"
    ;;
xz-utils)
    EXECUTABLE="$PROJECT_ROOT/debian/xz-utils/usr/bin/xz"
    EXECUTABLE2="$PROJECT_ROOT/debian/xz-utils/usr/bin/xzcat" # A symbolic link to the above
    ;;
esac
