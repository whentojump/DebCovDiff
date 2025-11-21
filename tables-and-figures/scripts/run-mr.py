#!/usr/bin/env python3

import csv
from pathlib import Path
import sys

submitted_bugs = set([
    'llvm101241',
    'llvm105341',
    'LineCoverageBug.SL_1',
    'LineCoverageBug.APACHE2_1',
    'LineCoverageBug.APACHE2_2',
    'IdTbdCppSplitLine',
    'LineCoverageBug.LZMA_1',
    'LineCoverageBug.LZMA_4',
    'LineCoverageBug.LZMA_5',
    'LineCoverageBug.LZMA_6',
    'LineCoverageBug.LZ4_1',
    'LineCoverageBug.LZ4_2',
    'LineCoverageBug.CURL_1',
    'LineCoverageBug.GREP_3',
    'BranchCoverageBug.MAWK_1',
    'McdcBug.HOSTNAME_1',
    'LineCoverageBug.INETUTILS_1',
    'LineCoverageBug.LZO2_1',
    'line coverage inline function superimpose direct or indirect invocations',
    'bug-string-vector',
    'goto-label-after-if',
    'cpp-extern-pass-pointer',
])

duplicate_bugs = set([
    'LineCoverageBug.DISTRO_INFO_1(bug)',
    'LineCoverageBug.MAWK_1',
])

should_not_be_rediscovered = set([
    'LineCoverageBug.GREP_1',
    'LineCoverageBug.LZMA_2',
])

new_bugs = set([
    "crazy macro wrapping case labels",
    "gcc coverage of while statement added by coverage of line after while loop",
    "gcc if statement in one line with multiconditions",
    "gcc line coverage for if's then clause is somehow reflecting the whole if statement",
    "gcc missing coverage at return of inline function",
    "gcc return at the end of if statement",
    "llvm case label line coverage reflecting the previous case",
    "llvm for loop",
    "llvm merge coverage for the same function with different body due to ifdef's",
    "variant llvm case label line coverage reflecting the previous case",
])

def read_packages(package_file):
    """Read package names from big-tests-packages.txt"""
    with open(package_file, 'r') as f:
        return [line.strip() for line in f]

# For failures, the key is package,filename,line_number,failure_type
def read_failures(csv_file, packages=None, columns=4):
    """Read failures from CSV file, optionally filtering by package names"""
    results = set()
    with open(csv_file, 'r') as f:
        reader = csv.reader(f, quotechar='"', escapechar='\\')
        for row in reader:
            assert len(row) >= columns
            # Take first 'columns' fields and rejoin with commas
            key = ','.join(row[:columns])
            if packages is None or any(key.startswith(f"{pkg},") for pkg in packages):
                results.add(key)
    return results

# For inspection, the key is package,filename,line_number
def read_inspection(csv_file, packages=None, columns=3):
    """Read failures from CSV file, optionally filtering by package names"""
    results = {}
    with open(csv_file, 'r') as f:
        reader = csv.reader(f, quotechar='"', escapechar='\\')
        for row in reader:
            assert len(row) >= columns
            # Take first 'columns' fields and rejoin with commas
            key = ','.join(row[:columns])
            if not any(key.startswith(f"{pkg},") for pkg in packages):
                assert False, f"Unexpected inspection with key {key}"
            results[key] = row
    return results

def main():
    data_dir = Path(__file__).parent / 'data-mr'
    small_tests_failures_file = data_dir / "small-tests-failures.csv"
    big_tests_failures_file = data_dir / "big-tests-failures.csv"
    big_tests_packages_file = data_dir / "big-tests-packages.txt"

    big_tests_inspections_file_line = data_dir / 'big-tests-inspection-ex-small' / 'line_coverage.csv'
    big_tests_inspections_file_branch = data_dir / 'big-tests-inspection-ex-small' / 'branch_coverage.csv'
    big_tests_inspections_file_mcdc = data_dir / 'big-tests-inspection-ex-small' / 'mcdc.csv'

    # Read package names
    big_tests_packages = read_packages(big_tests_packages_file)

    # Read failures from both files
    small_tests_failures = read_failures(small_tests_failures_file, packages=big_tests_packages)
    big_tests_failures = read_failures(big_tests_failures_file)

    # Read inspections from files
    big_tests_inspections_line = read_inspection(big_tests_inspections_file_line, packages=big_tests_packages)
    big_tests_inspections_branch = read_inspection(big_tests_inspections_file_branch, packages=big_tests_packages)
    big_tests_inspections_mcdc = read_inspection(big_tests_inspections_file_mcdc, packages=big_tests_packages)

    num_big_tests_all_failures = len(big_tests_failures)

    # Calculate unique and common failures
    num_small_tests_unique_failures = len(small_tests_failures - big_tests_failures)
    num_common_failures = len(small_tests_failures & big_tests_failures)
    num_big_tests_unique_failures = len(big_tests_failures - small_tests_failures)

    print(f"\\newcommand{{\\numAllFailuresUsingBigTests}}{{{num_big_tests_all_failures}\\xspace}}")

    # assert num_small_tests_unique_failures == 23
    # assert num_common_failures == 240
    # assert num_big_tests_unique_failures == 553

    print(f"\\newcommand{{\\numUniqFailuresUsingSmallTests}}{{{num_small_tests_unique_failures}\\xspace}}")
    print(f"\\newcommand{{\\numCommFailuresUsingBigAndSmallTests}}{{{num_common_failures}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTests}}{{{num_big_tests_unique_failures}\\xspace}}")

    res = num_common_failures * 100.0/ (num_common_failures + num_small_tests_unique_failures)
    print(f"\\newcommand{{\\percentCommonFailuresOverAllSmallTestsFailures}}{{{res:.2f}\%\\xspace}}")
    res = num_big_tests_unique_failures * 100.0/ (num_big_tests_unique_failures + num_common_failures)
    print(f"\\newcommand{{\\percentBigUniqFailuresOverAllBigTestsFailures}}{{{res:.2f}\%\\xspace}}")

    num_small_tests_unique_failures__line = 0
    num_small_tests_unique_failures__branch = 0
    num_small_tests_unique_failures__mcdc = 0
    for f in (small_tests_failures - big_tests_failures):
        f_type = f.strip().split(',')[3].strip()
        if f_type == 'Inconsistency.LINE_COV_STEADY':
            num_small_tests_unique_failures__line += 1
        elif f_type in [ 'Inconsistency.BRANCH_COV_NUM_OUTCOME', 'Inconsistency.BRANCH_COV_COUNT_STEADY' ]:
            num_small_tests_unique_failures__branch += 1
        elif f_type in [ 'Inconsistency.MCDC_NUM_CONDITION', 'Inconsistency.MCDC_GCC_OVER_REPORT' ]:
            num_small_tests_unique_failures__mcdc += 1
        else:
            assert False, f"Unknown failure type: {f_type}"

    print(f"\\newcommand{{\\numUniqFailuresUsingSmallTestsLine}}{{{num_small_tests_unique_failures__line}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingSmallTestsBranch}}{{{num_small_tests_unique_failures__branch}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingSmallTestsMcdc}}{{{num_small_tests_unique_failures__mcdc}\\xspace}}")

    num_big_tests_unique_failures__line = 0
    num_big_tests_unique_failures__branch = 0
    num_big_tests_unique_failures__mcdc = 0

    for f in (big_tests_failures - small_tests_failures):
        f_type = f.strip().split(',')[3].strip()
        if f_type == 'Inconsistency.LINE_COV_STEADY':
            num_big_tests_unique_failures__line += 1
        elif f_type in [ 'Inconsistency.BRANCH_COV_NUM_OUTCOME', 'Inconsistency.BRANCH_COV_COUNT_STEADY' ]:
            num_big_tests_unique_failures__branch += 1
        elif f_type in [ 'Inconsistency.MCDC_NUM_CONDITION', 'Inconsistency.MCDC_GCC_OVER_REPORT' ]:
            num_big_tests_unique_failures__mcdc += 1
        else:
            assert False, f"Unknown failure type: {f_type}"

    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsLine}}{{{num_big_tests_unique_failures__line}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsBranch}}{{{num_big_tests_unique_failures__branch}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsMcdc}}{{{num_big_tests_unique_failures__mcdc}\\xspace}}")

    num_big_small_common_failures__line = 0
    num_big_small_common_failures__branch = 0
    num_big_small_common_failures__mcdc = 0

    for f in (big_tests_failures & small_tests_failures):
        f_type = f.strip().split(',')[3].strip()
        if f_type == 'Inconsistency.LINE_COV_STEADY':
            num_big_small_common_failures__line += 1
        elif f_type in [ 'Inconsistency.BRANCH_COV_NUM_OUTCOME', 'Inconsistency.BRANCH_COV_COUNT_STEADY' ]:
            num_big_small_common_failures__branch += 1
        elif f_type in [ 'Inconsistency.MCDC_NUM_CONDITION', 'Inconsistency.MCDC_GCC_OVER_REPORT' ]:
            num_big_small_common_failures__mcdc += 1
        else:
            assert False, f"Unknown failure type: {f_type}"

    print(f"\\newcommand{{\\numBigSmallCommonFailuresLine}}{{{num_big_small_common_failures__line}\\xspace}}")
    print(f"\\newcommand{{\\numBigSmallCommonFailuresBranch}}{{{num_big_small_common_failures__branch}\\xspace}}")
    print(f"\\newcommand{{\\numBigSmallCommonFailuresMcdc}}{{{num_big_small_common_failures__mcdc}\\xspace}}")

    num_big_tests_unique_failures__conv = 0
    num_big_tests_unique_failures__bug = 0
    num_big_tests_unique_failures__submission_bug = 0
    num_big_tests_unique_failures__duplicate_bug = 0
    num_big_tests_unique_failures__duplicate_bug__ucf = 0
    num_big_tests_unique_failures__duplicate_bug__multiline = 0
    num_big_tests_unique_failures__new_bug = 0
    num_big_tests_unique_failures__false_positive = 0
    num_big_tests_unique_failures__not_fully_inspected = 0

    rediscovered_submission_bugs = set()
    rediscovered_duplicate_bugs = set()
    discovered_new_bugs = set()
    bugs_manifesting_in_big_tests = set()

    for f in (big_tests_failures - small_tests_failures):
        key = ','.join(f.strip().split(',')[:3])
        f_type = f.strip().split(',')[3].strip()

        match f_type:
            case 'Inconsistency.LINE_COV_STEADY':
                inspections = big_tests_inspections_line
            case 'Inconsistency.BRANCH_COV_NUM_OUTCOME' | 'Inconsistency.BRANCH_COV_COUNT_STEADY':
                inspections = big_tests_inspections_branch
            case 'Inconsistency.MCDC_NUM_CONDITION' | 'Inconsistency.MCDC_GCC_OVER_REPORT':
                inspections = big_tests_inspections_mcdc
            case _:
                assert False, f"Unknown failure type: {f_type}"

        if key not in inspections:
            assert False, f"Not even coarse-grained inspected: {f}"

        inspection = inspections[key]

        reason_type = inspection[3].strip()
        reason = inspection[4].strip()

        match reason_type:
            case 'conv' | 'conv num' | 'conv val':
                num_big_tests_unique_failures__conv += 1
            case 'bug' | 'bug val' | 'bug num':
                if reason != 'NOT INSPECTED YET':
                    num_big_tests_unique_failures__bug += 1
            case 'false positive':
                num_big_tests_unique_failures__false_positive += 1
            case 'not fully inspected':
                assert False
            case _:
                assert False, f"Unknown reason type: {reason_type}"

        if reason_type in ['bug', 'bug num', 'bug val']:
            # We have given multiple reasons for some inconsistencies,
            # let's just count the first to ease processing.

            # FIXME the current version does produce the version of MR
            # submission but it has its own problems. E.g. it emits
            # \newcommand{\numUniqFailuresUsingBigTestsSubmissionBug}{51\xspace}
            # which does not match the sum of blue columns in the top
            # half of the table.
            # The following numbers are affected by difference choices below 
            # but none is referenced in the paper.
            #   numUniqFailuresUsingBigTestsSubmissionBug
            #   numUniqFailuresUsingBigTestsDuplicateBug
            #   numUniqFailuresUsingBigTestsDuplicateBugUcf

            # Version 1
            if True:
                if len(reason.split(',')) > 1:
                    print(reason, file=sys.stderr)
                sub_reason = reason.split(',')[0].strip()

            # Version 2
            # if True:
            #     if len(reason.split(',')) > 1:
            #         print(reason, file=sys.stderr)
            #     sub_reason = reason.split(',')[-1].strip()

            # Version 3
            # for sub_reason in reason.split(','):

                if sub_reason in submitted_bugs:
                    num_big_tests_unique_failures__submission_bug += 1
                    rediscovered_submission_bugs.add(sub_reason)
                elif sub_reason in duplicate_bugs:
                    num_big_tests_unique_failures__duplicate_bug += 1
                    rediscovered_duplicate_bugs.add(sub_reason)
                    if sub_reason == 'LineCoverageBug.DISTRO_INFO_1(bug)':
                        num_big_tests_unique_failures__duplicate_bug__multiline += 1
                    elif sub_reason == 'LineCoverageBug.MAWK_1':
                        num_big_tests_unique_failures__duplicate_bug__ucf += 1
                elif sub_reason in new_bugs:
                    num_big_tests_unique_failures__new_bug += 1
                    discovered_new_bugs.add(sub_reason)
                elif sub_reason == 'NOT INSPECTED YET':
                    num_big_tests_unique_failures__not_fully_inspected += 1
                else:
                    assert False, f"Unknown bug: |{sub_reason}|"

                if sub_reason != 'NOT INSPECTED YET':
                    bugs_manifesting_in_big_tests.add(sub_reason)

    # assert len((big_tests_failures - small_tests_failures)) == \
    #     num_big_tests_unique_failures__conv + \
    #     num_big_tests_unique_failures__bug + \
    #     num_big_tests_unique_failures__false_positive + \
    #     num_big_tests_unique_failures__not_fully_inspected

    # assert num_big_tests_unique_failures__bug == \
    #     num_big_tests_unique_failures__submission_bug + \
    #     num_big_tests_unique_failures__duplicate_bug + \
    #     num_big_tests_unique_failures__new_bug

    # assert num_big_tests_unique_failures__duplicate_bug == \
    #     num_big_tests_unique_failures__duplicate_bug__ucf + \
    #     num_big_tests_unique_failures__duplicate_bug__multiline

    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsConv}}{{{num_big_tests_unique_failures__conv}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsBug}}{{{num_big_tests_unique_failures__bug}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsFalsePositive}}{{{num_big_tests_unique_failures__false_positive}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsNotFullyInspected}}{{{num_big_tests_unique_failures__not_fully_inspected}\\xspace}}")

    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsSubmissionBug}}{{{num_big_tests_unique_failures__submission_bug}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsNewBug}}{{{num_big_tests_unique_failures__new_bug}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsDuplicateBug}}{{{num_big_tests_unique_failures__duplicate_bug}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsDuplicateBugMultiline}}{{{num_big_tests_unique_failures__duplicate_bug__multiline}\\xspace}}")
    print(f"\\newcommand{{\\numUniqFailuresUsingBigTestsDuplicateBugUcf}}{{{num_big_tests_unique_failures__duplicate_bug__ucf}\\xspace}}")

    print(f"\\newcommand{{\\numRediscoveredSubmissionBug}}{{{len(rediscovered_submission_bugs)}\\xspace}}")
    print(f"\\newcommand{{\\numRediscoveredDuplicateBug}}{{{len(rediscovered_duplicate_bugs)}\\xspace}}")
    print(f"\\newcommand{{\\numDiscoveredNewBug}}{{{len(discovered_new_bugs)}\\xspace}}")
    print(f"\\newcommand{{\\numBugsManifestingInBigTests}}{{{len(bugs_manifesting_in_big_tests)}\\xspace}}")

if __name__ == "__main__":
    main()
