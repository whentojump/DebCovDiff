checksum_failed() {
    cat << EOF
Unexpected program checksum. Examine program generation log and see if any
segmentation fault happened. Try regenerating them with:

    csmith -s <SEED> [--inline-function] [--lang-cpp] > <FILENAME>

Or completely rerun gen.py with a lower level of parallelism.
EOF
    exit 1
}

SUM=`(cd default-1k && find . -type f -exec md5sum {} + | LC_ALL=C sort | md5sum)`
if [[ $SUM != 06d3ea664413df70b65ca9fa3044620f* ]]; then
    checksum_failed
fi
SUM=`(cd inline-1k && find . -type f -exec md5sum {} + | LC_ALL=C sort | md5sum)`
if [[ $SUM != e1a82bdc99f7b0e367a25ae1483d1ab1* ]]; then
    checksum_failed
fi
SUM=`(cd cpp-1k && find . -type f -exec md5sum {} + | LC_ALL=C sort | md5sum)`
if [[ $SUM != 4ccca1b81e3e2732fd5fe769e85c8198* ]]; then
    checksum_failed
fi

for d in default-1k inline-1k cpp-1k; do
    python check.py --nproc=40 --csmith-programs-dir $d |& tee $d.log
done

TMPDIR=`mktemp -d`
grep '/1000' default-1k.log | cut -d: -f1 > $TMPDIR/bug_id
grep '/1000' default-1k.log | cut -d: -f2 > $TMPDIR/default
grep '/1000' inline-1k.log  | cut -d: -f2 > $TMPDIR/inline
grep '/1000' cpp-1k.log     | cut -d: -f2 > $TMPDIR/cpp
paste $TMPDIR/{bug_id,default,inline,cpp} | column -t
rm -r $TMPDIR
