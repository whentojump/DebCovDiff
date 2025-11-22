import csv

unify_inconsistency_type = {
    'Inconsistency.LINE_COV_STEADY': 'line_val',
    'Inconsistency.BRANCH_COV_COUNT_STEADY': 'branch_val',
    'Inconsistency.BRANCH_COV_NUM_OUTCOME': 'branch_num',
    'Inconsistency.MCDC_NUM_CONDITION': 'mcdc_num',
    'Inconsistency.MCDC_GCC_OVER_REPORT': 'mcdc_val',
}

unify_bug_label = {
    # Table II upper
    "LineCoverageBug.LZMA_1": "GCC#120321",
    "LineCoverageBug.LZO2_1": "GCC#120478",
    "LineCoverageBug.APACHE2_1": "GCC#117412",
    "line coverage inline function superimpose direct or indirect invocations": "GCC#120482",
    "LineCoverageBug.LZ4_1": "GCC#120490",
    "LineCoverageBug.APACHE2_2": "GCC#117415",
    "cpp-extern-pass-pointer": "GCC#120348",
    "LineCoverageBug.CURL_1": "GCC#120484",
    "LineCoverageBug.LZ4_2": "GCC#120489",
    "LineCoverageBug.LZMA_6": "GCC#120491",
    "LineCoverageBug.LZMA_5": "GCC#120492",
    "LineCoverageBug.INETUTILS_1": "GCC#120486",
    "IdTbdCppSplitLine": "GCC#120319",
    "goto-label-after-if": "GCC#120332",
    "BranchCoverageBug.MAWK_1": "GCC#120485",
    "LineCoverageBug.LZMA_4": "LLVM#140427",
    "LineCoverageBug.SL_1": "LLVM#114622",
    "LineCoverageBug.GREP_3": "LLVM#116884",
    "llvm105341": "LLVM#105341",
    "bug-string-vector": "LLVM#116902",
    "llvm101241": "LLVM#101241",
    "McdcBug.HOSTNAME_1": "LLVM#131505",
    # Table II lower
    "gcc missing coverage at return of inline function": "GCC#121914",
    "gcc if statement in one line with multiconditions": "GCC#121897",
    "gcc coverage of while statement added by coverage of line after while loop": "GCC#121901",
    "gcc line coverage for if's then clause is somehow reflecting the whole if statement": "GCC#121896",
    "gcc return at the end of if statement": "GCC#121902",
    "crazy macro wrapping case labels": "LLVM#158003",
    "llvm case label line coverage reflecting the previous case": "LLVM#158080",
    "variant llvm case label line coverage reflecting the previous case": "LLVM#157959",
    "llvm merge coverage for the same function with different body due to ifdef's": "LLVM#157946",
    "llvm for loop": "LLVM#157981",
    # Section IV-B
    "LineCoverageBug.DISTRO_INFO_1(bug)": "KNOWN BUG GCC#97923",
    "LineCoverageBug.GREP_1": "KNOWN BUG GCC#97923",
    "LineCoverageBug.LZMA_2": "KNOWN BUG GCC#97923",
    "LineCoverageBug.MAWK_1": "KNOWN BUG LLVM#UCF",
}

def clean_inconsistencies_csv(input_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file:
        with open(output_file_path, 'w') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)
            for row in reader:
                inconsistency_type = row[3]
                assert inconsistency_type in unify_inconsistency_type
                inconsistency_type = unify_inconsistency_type[inconsistency_type]
                row[3] = inconsistency_type
                writer.writerow(row)

clean_inconsistencies_csv('data-mr/big-tests-failures/line_coverage.csv', '../../reduce/dataset/ET-inconsistencies/line_coverage.csv')
clean_inconsistencies_csv('data-mr/big-tests-failures/branch_coverage.csv', '../../reduce/dataset/ET-inconsistencies/branch_coverage.csv')
clean_inconsistencies_csv('data-mr/big-tests-failures/mcdc.csv', '../../reduce/dataset/ET-inconsistencies/mcdc.csv')

clean_inconsistencies_csv('data-mr/small-tests-failures/line_coverage.csv', '../../reduce/dataset/SC-inconsistencies/line_coverage.csv')
clean_inconsistencies_csv('data-mr/small-tests-failures/branch_coverage.csv', '../../reduce/dataset/SC-inconsistencies/branch_coverage.csv')
clean_inconsistencies_csv('data-mr/small-tests-failures/mcdc.csv', '../../reduce/dataset/SC-inconsistencies/mcdc.csv')

def clean_inspection_csv(input_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file:
        with open(output_file_path, 'w') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)
            for row in reader:
                reason_type = row[3]
                # Unify these three reason types to 'conv'
                if reason_type in ['conv', 'conv num', 'conv val']:
                    # We didn't give complete and mutually exclusive reasons
                    # for convention differences. Discard existing data...
                    writer.writerow([row[0], row[1], row[2], 'conv', ''])
                    continue
                # Unify these three reason types to 'bug'
                if reason_type in ['bug', 'bug num', 'bug val']:
                    reason = row[4]
                    # Sorry the organization of raw CSV was a hell...
                    # This should be correctly handled in run-mr.py
                    # so any LaTeX should not be affected.
                    # Drop such entries entirely.
                    if reason == 'NOT INSPECTED YET':
                        continue
                    # We forgot this particular label and did not report the bug...
                    if reason == 'GCC-bug-string-vector':
                        continue
                    sub_reasons = []
                    # There are cases we labeled multiple bugs and/or conventions
                    for sub_reason in reason.split(','):
                        if sub_reason in unify_bug_label:
                            sub_reasons.append(unify_bug_label[sub_reason])
                    reason = ','.join(sorted(sub_reasons))
                    writer.writerow([row[0], row[1], row[2], 'bug', reason])
                    continue

                # Unify these reason types ('false positive', 'other', 'other val')
                # to 'other'.
                # Some of them put the actual reason in the 'comment' column --
                # move all back to the 'reason' column.
                if 'reading environment variables during program execution' in row:
                    reason = 'reading environment variables during program execution'
                elif 'main function looping over argv[0]' in row:
                    reason = 'main function looping over argv[0]'
                elif 'stackvma.c reading /proc/self/maps' in row:
                    reason = 'stackvma.c reading /proc/self/maps'
                elif 'wget --version contains compiler name and flags' in row:
                    reason = 'wget --version contains compiler name and flags'
                elif 'gcov overwrite' in row:
                    reason = 'gcov subtlety of passing gcda or gcno as arguments'
                elif 'gcc missing never taken branch' in row:
                    # For internal reference, see [1]
                    reason = 'gcov subtlety of passing gcda or gcno as arguments'
                elif 'llvm extra branch reports in macro' in row:
                    # For internal reference, see [1]
                    # [1] https://github.com/xlab-uiuc-prep/cov-study-prep/commit/e9377bc18ea8719eb1bac5e50cabf3c2f39e5198
                    reason = 'gcov subtlety of passing gcda or gcno as arguments'
                else:
                    assert False

                writer.writerow([row[0], row[1], row[2], 'other', reason])

clean_inspection_csv('data-mr/big-tests-inspection/line_coverage.csv', '../../reduce/dataset/ET-inspection/line_coverage.csv')
clean_inspection_csv('data-mr/big-tests-inspection/branch_coverage.csv', '../../reduce/dataset/ET-inspection/branch_coverage.csv')
clean_inspection_csv('data-mr/big-tests-inspection/mcdc.csv', '../../reduce/dataset/ET-inspection/mcdc.csv')

clean_inspection_csv('data-mr/small-tests-inspection/line_coverage.csv', '../../reduce/dataset/SC-inspection/line_coverage.csv')
clean_inspection_csv('data-mr/small-tests-inspection/branch_coverage.csv', '../../reduce/dataset/SC-inspection/branch_coverage.csv')
clean_inspection_csv('data-mr/small-tests-inspection/mcdc.csv', '../../reduce/dataset/SC-inspection/mcdc.csv')
