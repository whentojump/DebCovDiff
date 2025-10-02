THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

packages=(
    "sl"
    "distro-info"
    "grep"
    "util-linux"
    "mawk"
    "net-tools"
    "coreutils"
    "iproute2"
    "bzip2"
    "gzip"
    "curl"
    "lz4"
    "xz-utils"
    "lzma"
    "lzo2"
    "apache2"
    "base-passwd"
    "cron"
    "e2fsprogs"
    "file"
    "hostname"
    "ifupdown"
    "less"
    "shadow"
    "sysvinit"
    "wget"
    "traceroute"
    "psmisc"
    "pciutils"
    "pam"
    "newt"
    "nano"
    "man-db"
    "lsof"
    "liblockfile"
    "krb5"
    "inetutils"
    "dmidecode"
    "debianutils"
    "dbus"
    "procps"
)

echo "package,line coverage total,line coverage failure,branch coverage total,branch coverage failure val,branch coverage failure num,mcdc total,mcdc failure val,mcdc failure num"

for p in "${packages[@]}"; do
    line_total=`cut -d, -f1 /var/lib/sbuild/build-SC-merged2/$p-log/6.compared.csv`
    branch_total=`cut -d, -f2 /var/lib/sbuild/build-SC-merged2/$p-log/6.compared.csv`
    mcdc_total=`cut -d, -f3 /var/lib/sbuild/build-SC-merged2/$p-log/6.compared.csv | tr -d '\r'`

    line_fail=`grep ^$p, $THIS_DIR/../new-sc-data/line_coverage.csv | wc -l`
    branch_fail_val=`grep ^$p, $THIS_DIR/../new-sc-data/branch_coverage.csv | grep BRANCH_COV_COUNT | wc -l`
    branch_fail_num=`grep ^$p, $THIS_DIR/../new-sc-data/branch_coverage.csv | grep BRANCH_COV_NUM | wc -l`
    mcdc_fail_val=`grep ^$p, $THIS_DIR/../new-sc-data/mcdc.csv | grep -v MCDC_NUM | wc -l`
    mcdc_fail_num=`grep ^$p, $THIS_DIR/../new-sc-data/mcdc.csv | grep MCDC_NUM | wc -l`
    echo "$p,$line_total,$line_fail,$branch_total,$branch_fail_val,$branch_fail_num,$mcdc_total,$mcdc_fail_val,$mcdc_fail_num,"
done
