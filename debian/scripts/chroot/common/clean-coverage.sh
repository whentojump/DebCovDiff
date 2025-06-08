#!/bin/bash

rm -vrf *.profraw *.profdata
rm -vrf html-coverage-report text-coverage-report text-coverage-report.txt
rm -vrf default.json default.lcov.txt

# for f in `find . -type f -name "*.gcno"`; do
#     rm -f $f
# done
for f in `find . -type f -name "*.gcda"`; do
    rm -vf $f
done
for f in `find . -type f -name "*.gcov"`; do
    rm -vf $f
done
for f in `find . -type f -name "*.gcov.json.gz"`; do
    rm -vf $f
done
for f in `find . -type f -name "*.gcov.json"`; do
    rm -vf $f
done
