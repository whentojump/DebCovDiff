#!/bin/bash

echo "Remove .gcda files generated during build or dh_auto_test"

mkdir -p /tmp/gcov

find . -type f -name "*.gcda" | sort | uniq | sed 's|.gcda$||' | sort | uniq > /tmp/gcov/gcda_files.txt
find . -type f -name "*.gcno" | sort | uniq | sed 's|.gcno$||' | sort | uniq > /tmp/gcov/gcno_files.txt

echo
echo Unique .gcda files
echo
comm -23 /tmp/gcov/gcda_files.txt /tmp/gcov/gcno_files.txt | wc -l
echo
echo Unique .gcno files
echo
comm -13 /tmp/gcov/gcda_files.txt /tmp/gcov/gcno_files.txt | wc -l
echo
echo Overlapping .gcda and .gcno files
echo
comm -12 /tmp/gcov/gcda_files.txt /tmp/gcov/gcno_files.txt | wc -l
echo

for f in `cat /tmp/gcov/gcda_files.txt`; do
    rm -v $f.gcda
done

rm -rf /tmp/gcov
