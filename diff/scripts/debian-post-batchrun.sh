#!/bin/bash

# After running debian-batch.sh, aggregate the results
#
# - Copy the log for each package's latest run to /var/lib/sbuild/build-latest/log/PACKAGE.txt
# - Copy the CSV for each package's latest run to /var/lib/sbuild/build-latest/log/PACKAGE.csv
# - Generate per-package summary to /var/lib/sbuild/build-latest/log/per-package-failures.txt
# - Generate the CSV of all failures to /var/lib/sbuild/build-latest/log/all-failures.csv

mapfile -t PACKAGE_LIST < $REPO_DIR/tables-and-figures/scripts/data/select/selection_7_success.txt

REPEAT=$(jq -r .repeat config.json)

# For developing and testing this script itself
if [[ $DEV == "1" ]]; then
    packages=( "hostname" )
fi

mkdir -p /var/lib/sbuild/build-latest/log

touch /var/lib/sbuild/build-latest/log/{all-failures,per-package-failures}.csv
truncate -s 0 /var/lib/sbuild/build-latest/log/{all-failures,per-package-failures}.csv

# Schema
echo "package,filename,line number,failure type,gcc result,llvm result" \
    > /var/lib/sbuild/build-latest/log/all-failures.csv
echo "package,line coverage total,line coverage failure,branch coverage total,branch coverage failure val,branch coverage failure num,mcdc total,mcdc failure val,mcdc failure num" \
    > /var/lib/sbuild/build-latest/log/per-package-failures.csv

for p in ${packages[@]}; do
    log=/var/lib/sbuild/build-latest/$p-log/$REPEAT.txt
    csv=/var/lib/sbuild/build-latest/$p-log/$REPEAT.csv
    nocolor=$( mktemp /tmp/debian-package-log-nocolor-XXXX )
    totals=$( mktemp /tmp/debian-package-log-totals-XXXX )
    failures=$( mktemp /tmp/debian-package-log-failures-XXXX )

    sed -e 's/\x1b\[[0-9;]*m//g' $log > $nocolor
    cp $nocolor /var/lib/sbuild/build-latest/log/$p.txt
    cp $csv /var/lib/sbuild/build-latest/log/$p.csv
    grep 'input.debian_package      - ERROR    - Totals,' $nocolor > $totals
    grep 'oracles.inconsistency     - ERROR    - Failures,' $nocolor > $failures

    line_total=$( cut -d , -f 2  $totals )
    branch_total=$( cut -d , -f 3  $totals )
    mcdc_total=$( cut -d , -f 4  $totals )

    num1=$( cut -d , -f 2 $failures )
    num2=$( cut -d , -f 3 $failures )
    num3=$( cut -d , -f 4 $failures )
    num4=$( cut -d , -f 5 $failures )
    num5=$( cut -d , -f 6 $failures )

    # Schema
    echo "$p,$line_total,$num1,$branch_total,$num2,$num3,$mcdc_total,$num4,$num5," \
        >> /var/lib/sbuild/build-latest/log/per-package-failures.csv
    cat /var/lib/sbuild/build-latest/log/$p.csv >> /var/lib/sbuild/build-latest/log/all-failures.csv

    rm -f $nocolor $totals $failures
done
