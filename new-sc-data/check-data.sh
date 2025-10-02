THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd /var/lib/sbuild/build-SC-merged2

ls *-log/6.inconsistent.csv | wc -l
cat *-log/6.inconsistent.csv | wc -l

for f in *-log/6.inconsistent.csv; do
    grep LINE_COV_STEADY $f
done | sort > $THIS_DIR/line_coverage.csv

for f in *-log/6.inconsistent.csv; do
    grep BRANCH_COV $f
done | sort > $THIS_DIR/branch_coverage.csv

for f in *-log/6.inconsistent.csv; do
    grep MCDC $f
done | sort > $THIS_DIR/mcdc.csv

wc -l $THIS_DIR/*.csv

cd $THIS_DIR/../origin_inspection
rm -rf $THIS_DIR/../cleaned_inspection
mkdir $THIS_DIR/../cleaned_inspection

python $THIS_DIR/remove-not-appearing.py $THIS_DIR/../origin_inspection/line_coverage.csv $THIS_DIR/line_coverage.csv > $THIS_DIR/../cleaned_inspection/line_coverage.csv
python $THIS_DIR/remove-not-appearing.py $THIS_DIR/../origin_inspection/branch_coverage.csv $THIS_DIR/branch_coverage.csv > $THIS_DIR/../cleaned_inspection/branch_coverage.csv
python $THIS_DIR/remove-not-appearing.py $THIS_DIR/../origin_inspection/mcdc.csv $THIS_DIR/mcdc.csv > $THIS_DIR/../cleaned_inspection/mcdc.csv

wc -l $THIS_DIR/../origin_inspection/*
wc -l $THIS_DIR/../cleaned_inspection/*

cat $THIS_DIR/../cleaned_inspection/* > $THIS_DIR/../cleaned_inspection/all.csv

old_22_bug_labels=(
    "LineCoverageBug.LZMA_1"
    "LineCoverageBug.APACHE2_1"
    "LineCoverageBug.LZO2_1"
    "line coverage inline function superimpose direct or indirect invocations"
    "LineCoverageBug.LZ4_1"
    "LineCoverageBug.APACHE2_2"
    "cpp-extern-pass-pointer"
    "LineCoverageBug.CURL_1"
    "LineCoverageBug.LZ4_2"
    "LineCoverageBug.LZMA_6"
    "LineCoverageBug.LZMA_5"
    "LineCoverageBug.INETUTILS_1"
    "IdTbdCppSplitLine"
    "goto-label-after-if"
    "BranchCoverageBug.MAWK_1"
    "LineCoverageBug.LZMA_4"
    "LineCoverageBug.SL_1"
    "LineCoverageBug.GREP_3"
    "llvm105341"
    "bug-string-vector"
    "llvm101241"
    "McdcBug.HOSTNAME_1"
)

for label in "${old_22_bug_labels[@]}"; do
    grep "$label" $THIS_DIR/../cleaned_inspection/all.csv | wc -l
done
