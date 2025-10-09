checksum_failed() {
    cat << EOF
Unexpected program checksum. Examine program generation log and see if any
segmentation fault happened. Try regenerating them with:

    csmith -s <SEED> [--inline-function] [--lang-cpp] > <FILENAME>

Or completely rerun gen.py with a lower level of parallelism.
EOF
    exit 1
}

SUM=`(cd default-100k && find . -type f -exec md5sum {} + | LC_ALL=C sort | md5sum)`
if [[ $SUM != b065d1f68a4945dab0e23b63ba9b414e* ]]; then
    checksum_failed
fi
SUM=`(cd inline-100k && find . -type f -exec md5sum {} + | LC_ALL=C sort | md5sum)`
if [[ $SUM != fdfd268963e48bcaaf4566318b59463d* ]]; then
    checksum_failed
fi
SUM=`(cd cpp-100k && find . -type f -exec md5sum {} + | LC_ALL=C sort | md5sum)`
if [[ $SUM != cc8157e7a22c83799cc9c189ca42a392* ]]; then
    checksum_failed
fi

for d in default-100k inline-100k cpp-100k; do
    python check.py --nproc=40 --csmith-programs-dir $d |& tee $d.log
done

TMPDIR=`mktemp -d`
grep '/100000' default-100k.log | cut -d: -f1 > $TMPDIR/bug_id
grep '/100000' default-100k.log | cut -d: -f2 > $TMPDIR/default
grep '/100000' inline-100k.log  | cut -d: -f2 > $TMPDIR/inline
grep '/100000' cpp-100k.log     | cut -d: -f2 > $TMPDIR/cpp
paste $TMPDIR/{bug_id,default,inline,cpp} | column -t
rm -r $TMPDIR
