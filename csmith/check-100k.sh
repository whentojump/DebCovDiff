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
