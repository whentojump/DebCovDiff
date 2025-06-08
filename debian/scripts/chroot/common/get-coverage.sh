#!/bin/bash

if [[ $INSTR_OPTION == clang* ]]; then

    echo "=========================== llvm-profdata ==========================="

    if [[ ! -s $(ls *.profraw | head -n 1) ]]; then
        echo "Raw profiles should not be empty"
        exit 1
    fi

    llvm-profdata merge *.profraw -o default.profdata

    echo OK

    echo "========================== llvm-cov (text) =========================="

    llvm-cov show $LLVM_COV_FLAGS                                              \
                  -use-color=false                                             \
                  -instr-profile default.profdata                              \
                  ./$BINARY                                                    \
                  > text-coverage-report.txt

    head -n 50 text-coverage-report.txt
    printf '     .\n     .\n     .\n'
    tail -n 50 text-coverage-report.txt

    llvm-cov show $LLVM_COV_FLAGS                                              \
                  --show-region-summary=false                                  \
                  -use-color=false                                             \
                  -output-dir=text-coverage-report                             \
                  -instr-profile default.profdata                              \
                  ./$BINARY

    # # Only print function coverage to terminal otherwise the table is too wide
    # col=$(head text-coverage-report/index.txt -n1 | awk -v s="Lines" '{print index($0, s)}')
    # cut -c-$((col-1)) text-coverage-report/index.txt
    cat text-coverage-report/index.txt

    # In this version of LLVM there's no final new line in the generated text
    # index file
    echo

    # echo "========================== llvm-cov (HTML) =========================="
    #
    # llvm-cov show $LLVM_COV_FLAGS                                              \
    #               --format=html                                                \
    #               -output-dir=html-coverage-report                             \
    #               -instr-profile default.profdata                              \
    #               ./$BINARY
    #
    # echo OK

    echo "========================== llvm-cov (JSON) =========================="

    llvm-cov export -instr-profile default.profdata ./$BINARY | jq > default.json

    echo OK

    echo "========================== llvm-cov (LCOV) =========================="

    llvm-cov export -instr-profile default.profdata ./$BINARY -format=lcov > default.lcov.txt

    echo OK

elif [[ $INSTR_OPTION == gcc* ]]; then

    PROJECT_ROOT=$(realpath $PROJECT_ROOT)
    cd $PROJECT_ROOT

    NUM_GCOV_RESULTS=$(find . -type f -name "*.gcov" | wc -l)
    if [[ "$NUM_GCOV_RESULTS" -gt 0 ]]; then
        echo "$NUM_GCOV_RESULTS .gcov file(s) already exist(s)"
        exit 1
    fi

    mkdir -p /tmp/gcov

    find . -type f -name "*.gcda" | sort | uniq | sed 's|.gcda$||' | sort | uniq > /tmp/gcov/gcda_files.txt
    find . -type f -name "*.gcno" | sort | uniq | sed 's|.gcno$||' | sort | uniq > /tmp/gcov/gcno_files.txt

    echo "==================== Count .gcda and .gcno files ===================="

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
    comm -12 /tmp/gcov/gcda_files.txt /tmp/gcov/gcno_files.txt > /tmp/gcov/common_gcda_and_gcno_files.txt

    echo "================================ gcov ==============================="

    truncate -s 0 /tmp/gcov/gcov_log.txt

    for f in `cat /tmp/gcov/common_gcda_and_gcno_files.txt`; do

        DIRNAME=$(dirname $f)
        BASENAME=$(basename $f)

        cd $DIRNAME

        /opt/gcc-latest/bin/gcov $GCOV_FLAGS $BASENAME                         \
                                  > /tmp/gcov/gcov_stdout.txt                  \
                                 2> /tmp/gcov/gcov_stderr.txt
        RET1=$?

        cat /tmp/gcov/gcov_stderr.txt
        grep "Cannot open source file" /tmp/gcov/gcov_stderr.txt > /dev/null
        RET2=$?

        if [[ $RET1 -ne 0 ]]; then

            cat /tmp/gcov/gcov_stdout.txt >> /tmp/gcov/gcov_log.txt

            echo "gcov error when processing $f"
            echo
            echo "The command is"
            echo
            echo "cd $DIRNAME"
            echo "/opt/gcc-latest/bin/gcov $GCOV_FLAGS $BASENAME"
            echo
            head -n 50 /tmp/gcov/gcov_log.txt
            printf ' .\n .\n .\n'
            tail -n 50 /tmp/gcov/gcov_log.txt
            rm -rf /tmp/gcov
            exit 1
        fi

        if [[ $RET2 -eq 0 ]]; then

            # Find source files that are not at the same location as *.gcda
            # files. This is e.g. observed in "gawk" package. It would cd to
            # its ./support and then compile ./malloc/*.
            #
            # Our first attempt will first cd to ./support/malloc and run gcov,
            # which will result in:
            #
            #   Cannot open source file malloc/dynarray_finalize.c
            #   Cannot open source file malloc/dynarray.h
            #   File 'malloc/dynarray_finalize.c'
            #   Lines executed:0.00% of 19
            #   Condition outcomes covered:0.00% of 12
            #   Creating 'dynarray_finalize.c.gcov'
            #
            #   File 'malloc/dynarray.h'
            #   Lines executed:0.00% of 4
            #   No conditions
            #   Creating 'dynarray.h.gcov'
            #
            #   Lines executed:0.00% of 23
            #
            # because relative paths malloc/* were written in those *.gcda or
            # *.gcno files at compile time. Such cases won't return nonzero and
            # still produce some partial *.gcov results.
            #
            # After we detects "Cannot open source file" in stderr, the
            # following script deletes those partial *.gcov results and try
            # finding the right location to run gcov again.

            FILE_TO_FIND=$(cat /tmp/gcov/gcov_stdout.txt | grep "^File" | head -n 1 | grep -o "'[^']*'" | sed "s/'//g")
            INCOMPLETE_RESULTS_CREATED=$(cat /tmp/gcov/gcov_stdout.txt | grep "^Creating" | grep -o "'[^']*'" | sed "s/'//g")

            echo
            echo "The path stored in the *.gcda or *.gcno file is $FILE_TO_FIND."
            echo "Deleting incomplete *.gcov file(s) just generated."
            echo
            rm $INCOMPLETE_RESULTS_CREATED
            echo

            cd $PROJECT_ROOT

            RELPATH_TO_PROJECT_ROOT=$(find . -type f -wholename "*$FILE_TO_FIND")
            NUM_OF_FOUND_FILES=$(find . -type f -wholename "*$FILE_TO_FIND" | wc -l)
            if [[ "$NUM_OF_FOUND_FILES" -gt 1 ]]; then
                echo '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
                find . -type f -wholename "*$FILE_TO_FIND"
                echo '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
            fi
            echo "The file in question is $RELPATH_TO_PROJECT_ROOT relative to project root."
            REVISED_DIRNAME=$(echo $RELPATH_TO_PROJECT_ROOT | sed "s|$FILE_TO_FIND\$||")
            echo "Change directory to $REVISED_DIRNAME and try again."
            cd $REVISED_DIRNAME
            echo
            echo

            if ! [[ -f $FILE_TO_FIND ]]; then
                echo "Still cannot find the file. Abort."
                echo
                echo "gcov error when processing $f"
                echo
                echo "The command is"
                echo
                echo "cd $DIRNAME"
                echo "/opt/gcc-latest/bin/gcov $GCOV_FLAGS $BASENAME"
                echo
                head -n 50 /tmp/gcov/gcov_log.txt
                printf ' .\n .\n .\n'
                tail -n 50 /tmp/gcov/gcov_log.txt
                rm -rf /tmp/gcov
                exit 1
            else
                echo "------------- Second attempt of running gcov ------------"
                echo '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'

                /opt/gcc-latest/bin/gcov $GCOV_FLAGS $PROJECT_ROOT/$f          \
                                          > /tmp/gcov/gcov_stdout.txt          \
                                         2> /tmp/gcov/gcov_stderr.txt
                RET1=$?

                cat /tmp/gcov/gcov_stderr.txt
                grep "Cannot open source file" /tmp/gcov/gcov_stderr.txt > /dev/null
                RET2=$?

                if [[ $RET1 -ne 0 || $RET2 -eq 0 ]]; then
                    echo "Second attempt failed. Abort."
                    echo '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
                    rm -rf /tmp/gcov
                    exit 1
                fi

                /opt/gcc-latest/bin/gcov --json-format                         \
                                         $GCOV_FLAGS $PROJECT_ROOT/$f          \
                                         > /dev/null

                cat /tmp/gcov/gcov_stdout.txt >> /tmp/gcov/gcov_log.txt

                echo '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
                echo "---------------------------------------------------------"
            fi
        else
            # If everything is good in the first attempt, produce JSON as well
            /opt/gcc-latest/bin/gcov --json-format $GCOV_FLAGS $BASENAME > /dev/null
        fi

        cat /tmp/gcov/gcov_stdout.txt >> /tmp/gcov/gcov_log.txt
        cd $PROJECT_ROOT
    done

    # Display part of gcov commands' stdout

    head -n 50 /tmp/gcov/gcov_log.txt
    printf ' .\n .\n .\n'
    tail -n 50 /tmp/gcov/gcov_log.txt

    # Display part of generated *.gcov files

    truncate -s 0 /tmp/gcov/gcov_reports.txt
    for f in `find . -type f -name "*.gcov"`; do
        cat $f > /tmp/gcov/gcov_reports.txt
    done

    head -n 50 /tmp/gcov/gcov_reports.txt
    printf '         .\n         .\n         .\n'
    tail -n 50 /tmp/gcov/gcov_reports.txt

    echo
    echo JSON files
    echo
    for gcov_json_gz in `find . -type f -name "*.gcov.json.gz"`; do
        zcat $gcov_json_gz | jq > $(dirname $gcov_json_gz)/$(basename $gcov_json_gz .gcov.json.gz).gcov.json
    done
    find . -type f -name "*.gcov.json"

    rm -rf /tmp/gcov

fi
