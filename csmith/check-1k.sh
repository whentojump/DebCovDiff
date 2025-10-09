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
