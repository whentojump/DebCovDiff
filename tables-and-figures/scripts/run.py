latex_macros = []

def canonicalize_triggering_conditions_latex(c, short=False):
    match c:
        case 'break':
            return '\\CodeIn{break}'
        case 'continue':
            return '\\CodeIn{continue}'
        case 'exit/longjmp/setjmp/exception':
            return '\\CodeIn{exit}/\\CodeIn{longjmp}/\\CodeIn{setjmp}/exception'
        case 'const keyword':
            return '\\CodeIn{const} keyword'
        case 'return':
            return '\\CodeIn{return}'
        case 'goto':
            return '\\CodeIn{goto}'
        case 'if':
            return '\\CodeIn{if}'
        case 'extern':
            return '\\CodeIn{extern "C"}'
        case 'switch-case':
            return '\\CodeIn{switch}-\\CodeIn{case}'
        case '#line':
            return '\\CodeIn{\\#line}'
    return c

def canonicalize_triggering_conditions_figure(c):
    match c:
        case 'break':
            return '\\texttt{break}'
        case 'continue':
            return '\\texttt{continue}'
        case 'exit/longjmp/setjmp/exception':
            return '\\texttt{exit}/\\texttt{longjmp}/\\texttt{setjmp}/exception'
        case 'const keyword':
            return '\\texttt{const} keyword'
        case 'return':
            return '\\texttt{return}'
        case 'goto':
            return '\\texttt{goto}'
        case 'if':
            return '\\texttt{if}'
        case 'extern':
            return '\\texttt{extern "C"}'
        case 'switch-case':
            return '\\texttt{switch}-\\texttt{case}'
        case '#line':
            return '\\texttt{\\#line}'
    return c

def canonicalize_inconsistencies(i):
    match i:
        case '': # FIXME remove this eventually
            return ''
        case 'line':
            return 'L'
        case 'branch_num':
            return 'BN'
        case 'branch_val':
            return 'BV'
        case 'mcdc_num':
            return 'MN'
        case 'mcdc_val':
            return 'MV'
    assert False, f"{i}"


cause_to_projects = {}
cause_to_occurrence = {}

import csv

description_to_id = {}
description_to_inconsistencies = {}
description_to_triggering_conditions = {}

latex_lines_to_print = []

with open('data/convs.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1
        assert len(row) in [ 4, 5 ] # Optionally "comment" field
        id = row[0]
        description_in_latex = row[1]
        inconsistencies = row[2]
        triggering_conditions = row[3]
        if len(row) == 5:
            comment = row[4]
        else:
            comment = ''
        # } // CSV schema

        if description_in_latex not in description_to_id:
            description_to_id[description_in_latex] = []
        description_to_id[description_in_latex].append(id)

        if description_in_latex not in description_to_inconsistencies:
            description_to_inconsistencies[description_in_latex] = []
        description_to_inconsistencies[description_in_latex].append(inconsistencies)

        if description_in_latex not in description_to_triggering_conditions:
            description_to_triggering_conditions[description_in_latex] = []
        description_to_triggering_conditions[description_in_latex].append(triggering_conditions)

id_to_projects = {}
id_to_occurrences = {}

with open('../tables/convs.tex', 'w') as out:
    with open('data/convs.csv', mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        row_idx = 0
        first_row = True
        for row in reader:
            # CSV schema {
            if first_row:
                first_row = False
                continue
            # row_idx += 1
            assert len(row) in [ 4, 5 ] # Optionally "comment" field
            id          = row[0]
            description_in_latex     = row[1]
            inconsistencies        = row[2]
            triggering_conditions = row[3]
            if len(row) == 5:
                comment = row[4]
            else:
                comment = ''
            # } // CSV schema

            # LaTeX table schema {

            # Multiple entries with distinct "id" fields may get merged in to
            # one entry with the same "description_in_latex" field
            if description_to_id[description_in_latex].index(id) != 0:
                continue

            row_idx += 1

            inconsistency_order = { 'line': 0, 'branch_num': 1, 'branch_val': 2,
                                    'mcdc_num': 3, 'mcdc_val': 4 }

            inconsistencies = set()
            for inconsistencies_one_entry in description_to_inconsistencies[description_in_latex]:
                for i in inconsistencies_one_entry.split(','):
                    inconsistencies.add(i)
            if len(inconsistencies) > 1:
                inconsistencies = sorted(inconsistencies, key=lambda x: inconsistency_order[x])

            triggering_conditions = set()
            for triggering_conditions_one_entry in description_to_triggering_conditions[description_in_latex]:
                for c in triggering_conditions_one_entry.split(','):
                    triggering_conditions.add(c)
            if len(triggering_conditions) > 1:
                triggering_conditions = sorted(triggering_conditions, key=lambda x: x)

            inconsistencies = [ canonicalize_inconsistencies(i) for i in inconsistencies ]
            inconsistencies = '/'.join(inconsistencies)

            triggering_conditions = [ canonicalize_triggering_conditions_latex(c) for c in triggering_conditions ]
            triggering_conditions = ','.join(triggering_conditions)

            affected_proj = {}
            occurrence = 0

            with open('data/line_coverage.csv', mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                first_row = True
                for row in reader:
                    # CSV schema {
                    if first_row:
                        first_row = False
                        continue
                    assert len(row) in [ 5, 6 ]
                    package = row[0]
                    reason = row[4]
                    # } // CSV schema
                    reason = reason.split(',')
                    for id in description_to_id[description_in_latex]:
                        if id in reason:
                            occurrence += 1
                            if package not in affected_proj:
                                affected_proj[package] = 1
                            else:
                                affected_proj[package] += 1
                            break

            with open('data/branch_coverage.csv', mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                first_row = True
                for row in reader:
                    # CSV schema {
                    if first_row:
                        first_row = False
                        continue
                    assert len(row) in [ 5, 6 ]
                    package = row[0]
                    reason = row[4]
                    # } // CSV schema
                    reason = reason.split(',')
                    for id in description_to_id[description_in_latex]:
                        if id in reason:
                            occurrence += 1
                            if package not in affected_proj:
                                affected_proj[package] = 1
                            else:
                                affected_proj[package] += 1
                            break

            with open('data/mcdc.csv', mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                first_row = True
                for row in reader:
                    # CSV schema {
                    if first_row:
                        first_row = False
                        continue
                    assert len(row) in [ 5, 6 ]
                    package = row[0]
                    reason = row[4]
                    # } // CSV schema
                    reason = reason.split(',')
                    for id in description_to_id[description_in_latex]:
                        if id in reason:
                            occurrence += 1
                            if package not in affected_proj:
                                affected_proj[package] = 1
                            else:
                                affected_proj[package] += 1
                            break

            if len(affected_proj):
                max_occurrence_per_project = max(affected_proj.values())
                max_occurring_project = { k for k, v in affected_proj.items() if v == max_occurrence_per_project }
                max_occurring_project = ','.join(sorted(list(max_occurring_project)))
                affected_proj_field_in_table = f"{len(affected_proj)} (\\package{{{max_occurring_project}}})"
            else:
                assert False

            id_to_projects[id] = affected_proj
            id_to_occurrences[id] = occurrence

            print(
                f"{row_idx} & {description_in_latex} & {inconsistencies} & {affected_proj_field_in_table} & {occurrence} & {triggering_conditions} \\\\ \\hline",
                file=out,
            )
            latex_lines_to_print.append((
                occurrence,
                inconsistencies,
                f"{description_in_latex} & {inconsistencies} & {affected_proj_field_in_table} & {occurrence} & {triggering_conditions} \\\\ \\hline",
                id,
            ))

m = f"\\newcommand{{\\numConventions}}{{{row_idx}\\xspace}}"
print(m)
latex_macros.append(m)


###

metrics_order = {
    'L': 0,
    'L/BN': 1,
    'L/BV': 2,
    'L/BN/BV': 3,
    'L/BV': 4,
    'BN': 5,
    'BV': 6,
    'BN/MN': 7,
    'BN/BV/MN': 8,
    'MN': 9,
    'MV': 10
}
latex_lines_to_print = sorted(latex_lines_to_print,
                              key=lambda x: (
                                  metrics_order.get(x[1], float('inf')), # metric, in a prescribed order
                                  -int(x[0]), # occur
                              ))

row_idx = 0
with open('../tables/convs.tex', 'w') as out:
    for l in latex_lines_to_print:
        row_idx += 1
        print(f'{row_idx} & ' + l[2], file=out)

        id = l[3]
        cause_name = 'Conv\\#' + str(row_idx)
        cause_to_occurrence[cause_name] = id_to_occurrences[id]
        cause_to_projects[cause_name] = id_to_projects[id]


import csv

num_bug_gcc = 0
num_bug_llvm = 0
num_bug_linecov = 0
num_bug_branchcov_or_mcdc = 0
num_proj_mostly_recurring = -1

package_to_bug_num: dict[str,int] = {}
package_to_unique_bug_num: dict[str,int] = {}

# FIXME
gcc_id_tbd = 0
llvm_id_tbd = 0

latex_lines_to_print = []

with open('../tables/diff_bugs.tex', 'w') as out:
    with open('data/bugs.csv', mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        row_idx = 0
        first_row = True
        for row in reader:
            # CSV schema {
            if first_row:
                first_row = False
                continue
            if len(row) >=3 and row[2] == 'dup':
                continue

            assert len(row) == 7, f"{row}"

            row_idx += 1

            id = row[0]
            comment = row[1]
            link = row[2]
            gcc_or_llvm = row[3]
            affected_metrics = row[4]
            inconsistencies = row[5]
            triggering_conditions = row[6]

            # } // CSV schema

            # Treat the known bug and duplicate multiline bugs specially
            if id == 'LineCoverageBug.MAWK_1' or link == 'dup':
                assert False
                # Deprecated
                increase_bug_cnt = 0
                row_idx -= 1
            else:
                increase_bug_cnt = 1

            if gcc_or_llvm == 'GCC':
                num_bug_gcc += increase_bug_cnt
            if gcc_or_llvm == 'LLVM':
                num_bug_llvm += increase_bug_cnt

            # LaTeX table schema {

            metric_order = { 'L': 0, 'B': 1, 'M': 2 }
            inconsistency_order = { 'line': 0, 'branch_num': 1, 'branch_val': 2,
                                    'mcdc_num': 3, 'mcdc_val': 4 }

            affected_metrics = affected_metrics.split(',')
            if 'L' in affected_metrics:
                num_bug_linecov += increase_bug_cnt
            if 'B' in affected_metrics or 'M' in affected_metrics:
                num_bug_branchcov_or_mcdc += increase_bug_cnt
            if len(affected_metrics) > 1:
                affected_metrics = sorted(affected_metrics, key=lambda x: metric_order[x])
            inconsistencies = inconsistencies.split(',')
            if len(inconsistencies) > 1:
                inconsistencies = sorted(inconsistencies, key=lambda x: inconsistency_order[x])
            triggering_conditions = triggering_conditions.split(',')
            if len(triggering_conditions) > 1:
                triggering_conditions = sorted(triggering_conditions, key=lambda x: x)

            affected_metrics = '/'.join(affected_metrics)

            inconsistencies = [ canonicalize_inconsistencies(i) for i in inconsistencies ]
            inconsistencies = '/'.join(inconsistencies)

            triggering_conditions = [ canonicalize_triggering_conditions_latex(c) for c in triggering_conditions ]
            triggering_conditions = ','.join(triggering_conditions)

            if link.startswith('https://github.com/llvm/llvm-project/'):
                assert gcc_or_llvm == 'LLVM'
                id_in_tracker = link.split('/')[-1]
                id_in_tracker_figure = id_in_tracker
                if id_in_tracker[-2:] == '41':
                    num_digits = 3
                else:
                    num_digits = 2
                id_in_tracker_latex = '\\blackout{' + id_in_tracker[:-num_digits] + '}' + id_in_tracker[-num_digits:]
            elif link.startswith('https://gcc.gnu.org/bugzilla/show_bug.cgi?id='):
                assert gcc_or_llvm == 'GCC'
                id_in_tracker = link.split('=')[-1]
                id_in_tracker_figure = id_in_tracker
                id_in_tracker_latex = '\\blackout{' + id_in_tracker[:-2] + '}' + id_in_tracker[-2:]
            else:
                assert False
                id_in_tracker = ''
                id_in_tracker_latex = ''
                id_in_tracker_figure = ''
            if gcc_or_llvm == 'GCC':
                tool = '\\gcov'
            else:
                tool = '\\llvmcov'

            affected_proj = {}
            occurrence = 0

            with open('data/line_coverage.csv', mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                first_row = True
                for row in reader:
                    # CSV schema {
                    if first_row:
                        first_row = False
                        continue
                    assert len(row) in [ 5, 6 ]
                    package = row[0]
                    reason = row[4]
                    # } // CSV schema
                    reason = reason.split(',')
                    if id in reason:
                        occurrence += 1
                        if package not in affected_proj:
                            affected_proj[package] = 1
                        else:
                            affected_proj[package] += 1

            with open('data/branch_coverage.csv', mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                first_row = True
                for row in reader:
                    # CSV schema {
                    if first_row:
                        first_row = False
                        continue
                    assert len(row) in [ 5, 6 ]
                    package = row[0]
                    reason = row[4]
                    # } // CSV schema
                    reason = reason.split(',')
                    if id in reason:
                        occurrence += 1
                        if package not in affected_proj:
                            affected_proj[package] = 1
                        else:
                            affected_proj[package] += 1

            with open('data/mcdc.csv', mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                first_row = True
                for row in reader:
                    # CSV schema {
                    if first_row:
                        first_row = False
                        continue
                    assert len(row) in [ 5, 6 ]
                    package = row[0]
                    reason = row[4]
                    # } // CSV schema
                    reason = reason.split(',')
                    if id in reason:
                        occurrence += 1
                        if package not in affected_proj:
                            affected_proj[package] = 1
                        else:
                            affected_proj[package] += 1

            if len(affected_proj):
                if len(affected_proj) == 1:
                    for proj in affected_proj.keys():
                        if proj in package_to_unique_bug_num:
                            package_to_unique_bug_num[proj] += increase_bug_cnt
                        else:
                            package_to_unique_bug_num[proj] = increase_bug_cnt

                for proj in affected_proj.keys():
                    if proj in package_to_bug_num:
                        package_to_bug_num[proj] += increase_bug_cnt
                    else:
                        package_to_bug_num[proj] = increase_bug_cnt

                max_occurrence_per_project = max(affected_proj.values())
                max_occurring_project = { k for k, v in affected_proj.items() if v == max_occurrence_per_project }
                max_occurring_project = ','.join(sorted(list(max_occurring_project)))
                affected_proj_field_in_table = f"{len(affected_proj)} (\\package{{{max_occurring_project}}})"
                if (len(affected_proj) > num_proj_mostly_recurring):
                    num_proj_mostly_recurring = len(affected_proj)

            if id_in_tracker_figure != '':
                cause_name = gcc_or_llvm + '\\#' + str(id_in_tracker_figure)
            elif id == 'LineCoverageBug.MAWK_1':
                cause_name = 'LLVM\\#UCF'
            else:
                if gcc_or_llvm == 'GCC':
                    cause_name = 'GCC\\#??' + str(gcc_id_tbd)
                    gcc_id_tbd += 1
                else:
                    cause_name = 'LLVM\\#??' + str(llvm_id_tbd)
                    llvm_id_tbd += 1
            cause_to_projects[cause_name] = affected_proj
            cause_to_occurrence[cause_name] = occurrence

            if id == 'LineCoverageBug.MAWK_1':
                # print(
                #     f"-- & \\llvmKnownBugInTable & {tool} & {inconsistencies} & {affected_proj_field_in_table} & {occurrence} & {triggering_conditions} \\\\ \\hline",
                #     file=out,
                # )
                pass
            else:
                latex_line = f"{row_idx} & {id_in_tracker_latex} & {tool} & {inconsistencies} & {affected_proj_field_in_table} & {occurrence} & {triggering_conditions} \\\\ \\hline"
                print(
                    latex_line,
                    file=out,
                )
                latex_line = f"{id_in_tracker_latex} & {tool} & {inconsistencies} & {affected_proj_field_in_table} & {occurrence} & {triggering_conditions} \\\\ \\hline"
                latex_lines_to_print.append((id_in_tracker,tool,inconsistencies,occurrence,latex_line))

print()

num_diff_bug = row_idx
m = f"\\newcommand{{\\numDiffBugs}}{{{num_diff_bug}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numGccDiffbugs}}{{{num_bug_gcc}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numLlvmDiffBugs}}{{{num_bug_llvm}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numDiffBugsLine}}{{{num_bug_linecov}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numDiffBugsBranchOrMcdc}}{{{num_bug_branchcov_or_mcdc}\\xspace}}"
print(m)
latex_macros.append(m)

# package_to_unique_bug_num = dict(sorted(package_to_unique_bug_num.items(), key=lambda item: item[1]))
# package_to_bug_num = dict(sorted(package_to_bug_num.items(), key=lambda item: item[1]))
# print(package_to_unique_bug_num)
# print(package_to_bug_num)

most_unique_bug = max(package_to_unique_bug_num.items(), key=lambda item: item[1])
most_bug = max(package_to_bug_num.items(), key=lambda item: item[1])

m = f"\\newcommand{{\\ProjExposingMostBugs}}{{\\package{{{most_bug[0]}}}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numExposingMostBugs}}{{{most_bug[1]}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\ProjExposingMostUniqueBugs}}{{\\package{{{most_unique_bug[0]}}}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numExposingMostUniqueBugs}}{{{most_unique_bug[1]}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numProjMostlyRecurringBug}}{{{num_proj_mostly_recurring}\\xspace}}"
print(m)
latex_macros.append(m)

###

metrics_order = {
    'L': 0,
    'L/BN': 1,
    'L/BV': 2,
    'L/BN/BV': 3,
    'L/BV': 4,
    'BN': 5,
    'BV': 6,
    'BN/MN': 7,
    'BN/BV/MN': 8,
    'MN': 9,
    'MV': 10
}
latex_lines_to_print = sorted(latex_lines_to_print,
                              key=lambda x: (
                                  x[1], # tool
                                  metrics_order.get(x[2], float('inf')), # metric, in a prescribed order
                                  -int(x[3]), # occur
                                  int(x[0]), # id
                              ))

row_idx = 0
with open('../tables/diff_bugs.tex', 'w') as out:
    for l in latex_lines_to_print:
        row_idx += 1
        print(f'{row_idx} & ' + l[4], file=out)


import csv

num_crash_occurrence = 0

with open('../tables/crash_bugs.tex', 'w') as out:
    with open('data/bugs_debian_crash.csv', mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        row_idx = 0
        first_row = True
        for row in reader:
            # CSV schema {
            if first_row:
                first_row = False
                continue
            row_idx += 1
            assert len(row) == 7, f"{row}"
            id          = row[0]
            comment     = row[1]
            link        = row[2]
            gcc_or_llvm = row[3]
            affected_metrics      = row[4]
            triggering_conditions = row[5]
            affected_proj         = row[6]
            # } // CSV schema

            # LaTeX table schema {

            metric_order = { 'L': 0, 'B': 1, 'M': 2 }

            affected_metrics = affected_metrics.split(',')
            if len(affected_metrics) > 1:
                affected_metrics = sorted(affected_metrics, key=lambda x: metric_order[x])
            triggering_conditions = triggering_conditions.split(',')
            if len(triggering_conditions) > 1:
                triggering_conditions = sorted(triggering_conditions, key=lambda x: x)
            affected_proj = affected_proj.split(',')
            if len(affected_proj) > 1:
                affected_proj = sorted(affected_proj, key=lambda x: x)

            affected_metrics = [ 'MC/DC' if m == 'M' else m for m in affected_metrics ]
            affected_metrics = '/'.join(affected_metrics)

            triggering_conditions = [ canonicalize_triggering_conditions_latex(c, short=False) for c in triggering_conditions ]
            triggering_conditions = ','.join(triggering_conditions)

            if link.startswith('https://github.com/llvm/llvm-project/'):
                assert gcc_or_llvm == 'LLVM'
                id_in_tracker = link.split('/')[-1]
                id_in_tracker_latex = '\\blackout{' + id_in_tracker[:-2] + '}' + id_in_tracker[-2:]
            elif link.startswith('https://gcc.gnu.org/bugzilla/show_bug.cgi?id='):
                assert gcc_or_llvm == 'GCC'
                id_in_tracker = link.split('=')[-1]
                id_in_tracker_latex = '\\blackout{' + id_in_tracker[:-2] + '}' + id_in_tracker[-2:]
            else:
                assert False
            if gcc_or_llvm == 'GCC':
                tool = '\\gcov'
            else:
                tool = '\\llvmcov'

            num_crash_occurrence += len(affected_proj)

            if len(affected_proj) > 1:
                project_1 = affected_proj[0]
                project_2 = affected_proj[1]
                affected_proj = f"{len(affected_proj)} (\\package{{{project_1}}}, ...)"
            elif len(affected_proj) == 1:
                project_1 = affected_proj[0]
                affected_proj = f"{len(affected_proj)} (\\package{{{project_1}}})"



            print(
                f"{row_idx} & {id_in_tracker_latex} & {tool} & {affected_metrics} & {affected_proj} & {triggering_conditions} \\\\ \\hline",
                file=out,
            )

num_crash_bug = row_idx
num_total_bug = num_crash_bug + num_diff_bug

print()

m = f"\\newcommand{{\\numCrashBugs}}{{{num_crash_bug}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numTotalBugs}}{{{num_total_bug}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numCrashOccurrence}}{{{num_crash_occurrence}\\xspace}}"
print(m)
latex_macros.append(m)


import csv
import numpy as np

all_package_line_coverage_total = []
all_package_line_coverage_failure = []
all_package_branch_coverage_total = []
all_package_branch_coverage_failure_val = []
all_package_branch_coverage_failure_num = []
all_package_mcdc_total = []
all_package_mcdc_failure_val = []
all_package_mcdc_failure_num = []

with open('data/per-package-failures.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1

        package = row[0]
        line_coverage_total = int(row[1])
        line_coverage_failure = int(row[2])
        branch_coverage_total = int(row[3])
        branch_coverage_failure_val = int(row[4])
        branch_coverage_failure_num = int(row[5])
        mcdc_total = int(row[6])
        mcdc_failure_val = int(row[7])
        mcdc_failure_num = int(row[8])
        # } // CSV schema

        all_package_line_coverage_total.append(line_coverage_total)
        all_package_line_coverage_failure.append(line_coverage_failure)
        all_package_branch_coverage_total.append(branch_coverage_total)
        all_package_branch_coverage_failure_val.append(branch_coverage_failure_val)
        all_package_branch_coverage_failure_num.append(branch_coverage_failure_num)
        all_package_mcdc_total.append(mcdc_total)
        all_package_mcdc_failure_val.append(mcdc_failure_val)
        all_package_mcdc_failure_num.append(mcdc_failure_num)

all_package_line_coverage_total = np.array(all_package_line_coverage_total)
all_package_line_coverage_failure = np.array(all_package_line_coverage_failure)
all_package_branch_coverage_total = np.array(all_package_branch_coverage_total)
all_package_branch_coverage_failure_val = np.array(all_package_branch_coverage_failure_val)
all_package_branch_coverage_failure_num = np.array(all_package_branch_coverage_failure_num)
all_package_branch_coverage_failure = all_package_branch_coverage_failure_num + all_package_branch_coverage_failure_val
all_package_mcdc_total = np.array(all_package_mcdc_total)
all_package_mcdc_failure_val = np.array(all_package_mcdc_failure_val)
all_package_mcdc_failure_num = np.array(all_package_mcdc_failure_num)
all_package_mcdc_failure = all_package_mcdc_failure_num + all_package_mcdc_failure_val

with open('../tables/inconsistencies.tex', 'w') as out:
    # LaTeX schema {
    my_format = lambda x : "{:,}".format(round(x))

    func = lambda x : my_format(np.sum(x))
    print(
        f"Total compared & "
        f"{func(all_package_line_coverage_total)} & "
        f"{func(all_package_branch_coverage_total)} & "
        f"{func(all_package_mcdc_total)} "
        "\\\\ \\hline", file=out
    )
    # func = lambda x : my_format(np.mean(x))
    # print(
    #     f"Mean compared & "
    #     f"{func(all_package_line_coverage_total)} & "
    #     f"{func(all_package_branch_coverage_total)} & "
    #     f"{func(all_package_mcdc_total)} "
    #     "\\\\ \\hline", file=out
    # )
    func = lambda x : my_format(np.median(x))
    print(
        f"Median compared & "
        f"{func(all_package_line_coverage_total)} & "
        f"{func(all_package_branch_coverage_total)} & "
        f"{func(all_package_mcdc_total)} "
        "\\\\ \\hhline{|=|=|=|=|}", file=out
    )

    func = lambda x : my_format(np.sum(x))
    print(
        f"\\makecell{{Total inconsistent\\\\(*\\_num + *\\_val)}} & "
        f"{func(all_package_line_coverage_failure)} & "
        f"\\makecell{{{func(all_package_branch_coverage_failure)}\\\\({func(all_package_branch_coverage_failure_num)} + {func(all_package_branch_coverage_failure_val)})}} & "
        f"\\makecell{{{func(all_package_mcdc_failure)}\\\\({func(all_package_mcdc_failure_num)} + {func(all_package_mcdc_failure_val)})}} "
        "\\\\ \\hline", file=out
    )
    # func = lambda x : my_format(np.mean(x))
    # print(
    #     f"Mean inconsistent & "
    #     f"{func(all_package_line_coverage_failure)} & "
    #     f"{func(all_package_branch_coverage_failure)} ({func(all_package_branch_coverage_failure_num)}+{func(all_package_branch_coverage_failure_val)}) & "
    #     f"{func(all_package_mcdc_failure)} ({func(all_package_mcdc_failure_num)}+{func(all_package_mcdc_failure_val)}) "
    #     "\\\\ \\hline", file=out
    # )
    func = lambda x : my_format(np.median(x))
    print(
        f"\\makecell{{Median inconsistent\\\\(*\\_num, *\\_val)}} & "
        f"{func(all_package_line_coverage_failure)} & "
        f"\\makecell{{{func(all_package_branch_coverage_failure)}\\\\({func(all_package_branch_coverage_failure_num)}, {func(all_package_branch_coverage_failure_val)})}} & "
        f"\\makecell{{{func(all_package_mcdc_failure)}\\\\({func(all_package_mcdc_failure_num)}, {func(all_package_mcdc_failure_val)})}} "
        "\\\\ \\hline", file=out
    )

    # my_format2 = lambda x : "{:.2f}".format(x)
    # func = lambda x, y : my_format2(np.sum(x)/np.sum(y)*1000)
    # print(
    #     f"Inconsistent rate & "
    #     f"{func(all_package_line_coverage_failure, all_package_line_coverage_total)}\\textperthousand & "
    #     f"\\makecell{{{func(all_package_branch_coverage_failure, all_package_branch_coverage_total)}\\textperthousand\\\\({func(all_package_branch_coverage_failure_num, all_package_branch_coverage_total)} + {func(all_package_branch_coverage_failure_val, all_package_branch_coverage_total)})\\textperthousand}} & "
    #     f"\\makecell{{{func(all_package_mcdc_failure, all_package_mcdc_total)}\\textperthousand\\\\({func(all_package_mcdc_failure_num, all_package_mcdc_total)} + {func(all_package_mcdc_failure_val, all_package_mcdc_total)})\\textperthousand}}"
    #     "\\\\ \\hline", file=out
    # )

    # } // LaTeX schema


num_package_at_least_one_inconsistency = sum(
    (all_package_line_coverage_failure > 0) |
    (all_package_branch_coverage_failure > 0) |
    (all_package_mcdc_failure > 0)
)

num_package_at_least_one_line_coverage_inconsistency = sum(
    (all_package_line_coverage_failure > 0)
)

num_package_at_least_one_branch_coverage_inconsistency = sum(
    (all_package_branch_coverage_failure > 0)
)
num_package_at_least_one_branch_coverage_num_inconsistency = sum(
    (all_package_branch_coverage_failure_num > 0)
)
num_package_at_least_one_branch_coverage_val_inconsistency = sum(
    (all_package_branch_coverage_failure_val > 0)
)

num_package_at_least_one_mcdc_inconsistency = sum(
    (all_package_mcdc_failure > 0)
)
num_package_at_least_one_mcdc_num_inconsistency = sum(
    (all_package_mcdc_failure_num > 0)
)
num_package_at_least_one_mcdc_val_inconsistency = sum(
    (all_package_mcdc_failure_val > 0)
)

print()
m = f"\\newcommand{{\\numPkgWithAtLeastOneInconsistency}}{{{num_package_at_least_one_inconsistency}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numPkgWithAtLeastOneLineCovInconsistency}}{{{num_package_at_least_one_line_coverage_inconsistency}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numPkgWithAtLeastOneBranchCovInconsistency}}{{{num_package_at_least_one_branch_coverage_inconsistency}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numPkgWithAtLeastOneBranchCovNumInconsistency}}{{{num_package_at_least_one_branch_coverage_num_inconsistency}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numPkgWithAtLeastOneBranchCovValInconsistency}}{{{num_package_at_least_one_branch_coverage_val_inconsistency}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numPkgWithAtLeastOneMcdcInconsistency}}{{{num_package_at_least_one_mcdc_inconsistency}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numPkgWithAtLeastOneMcdcNumInconsistency}}{{{num_package_at_least_one_mcdc_num_inconsistency}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numPkgWithAtLeastOneMcdcValInconsistency}}{{{num_package_at_least_one_mcdc_val_inconsistency}\\xspace}}"
print(m)
latex_macros.append(m)

metric_colors = [
    'cornflowerblue',
    'bisque',
    'limegreen',
]

metric_colors2 = [
    'tab:blue',
    'tab:orange',
    'tab:green',
]

bug_color = 'tab:red'
gcc_bug_color = bug_color
llvm_bug_color = 'peru'
conv_color = 'tab:purple'

metric_hatches = [
    '..',
    'xx',
    '--',
]

import matplotlib.colors as mcolors
from PIL import ImageColor

def matplotlib_color_name_to_RGB(name):
    return ImageColor.getcolor(mcolors.TABLEAU_COLORS[name], 'RGB')


print(matplotlib_color_name_to_RGB(bug_color))
print(matplotlib_color_name_to_RGB(conv_color))

import matplotlib.pyplot as plt
import numpy as np
import csv

data = []
package_names = []

with open('data/per-package-failures.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1

        package = row[0]
        line_coverage_total = int(row[1])
        line_coverage_failure = int(row[2])
        branch_coverage_total = int(row[3])
        branch_coverage_failure_val = int(row[4])
        branch_coverage_failure_num = int(row[5])
        mcdc_total = int(row[6])
        mcdc_failure_val = int(row[7])
        mcdc_failure_num = int(row[8])
        data.append([
            line_coverage_total,
            branch_coverage_total,
            mcdc_total,
        ])
        package_names.append(package)

data = np.array(data)
package_names = np.array(package_names)

sorted_indices = np.argsort(data[:, 0])

labels = [
    'Compared lines',
    'Compared branches',
    'Compared decisions'
]
data = data[sorted_indices]
package_names = package_names[sorted_indices]

num_package, num_bar = data.shape

x = np.arange(num_package)

bar_width = 0.25
offsets = np.linspace(-bar_width, bar_width, num_bar)

fig, ax = plt.subplots(figsize=(15, 5))

ax.set_yscale("log")

for bar_idx in range(num_bar):
    ax.bar(
        x + offsets[bar_idx], data[:, bar_idx],
        width=bar_width,
        label=labels[bar_idx],
        color=metric_colors[bar_idx],
    )

plt.xticks(x, package_names)
plt.ylabel('Number of instance(s)')
plt.legend()
plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')

plt.tight_layout()
plt.savefig('../figures/compared_num.pdf', metadata={'CreationDate': None})
plt.show()


import matplotlib.pyplot as plt
import numpy as np
import csv

data = []
package_names = []

with open('data/per-package-failures.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1

        package = row[0]
        line_coverage_total = int(row[1])
        line_coverage_failure = int(row[2])
        branch_coverage_total = int(row[3])
        branch_coverage_failure_val = int(row[4])
        branch_coverage_failure_num = int(row[5])
        mcdc_total = int(row[6])
        mcdc_failure_val = int(row[7])
        mcdc_failure_num = int(row[8])
        # } // CSV schema

        data.append([
            line_coverage_total, (line_coverage_failure),
            branch_coverage_total, (branch_coverage_failure_num + branch_coverage_failure_val),
            mcdc_total, (mcdc_failure_num + mcdc_failure_val)
        ])
        package_names.append(package)

data = np.array(data)
package_names = np.array(package_names)

sorted_indices = np.argsort(data[:, 0])

data = data[sorted_indices]
data = data[:, [1, 3, 5]]
labels = [
    'Inconsistent lines',
    'Inconsistent branches',
    'Inconsistent decisions'
]
package_names = package_names[sorted_indices]

num_package, num_bar = data.shape

x = np.arange(num_package)

bar_width = 0.25
offsets = np.linspace(-bar_width, bar_width, num_bar)

fig, ax = plt.subplots(figsize=(15, 5))

ax.set_yscale("log")

for bar_idx in range(num_bar):
    ax.bar(
        x + offsets[bar_idx], data[:, bar_idx],
        width=bar_width,
        label=labels[bar_idx],
        color=metric_colors[bar_idx],
    )

plt.xticks(x, package_names)
plt.ylabel('Number of instance(s)')
plt.legend()
plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')

plt.tight_layout()
plt.savefig('../figures/inconsistent_num.pdf', metadata={'CreationDate': None})
plt.show()

import matplotlib.pyplot as plt
import numpy as np
import csv

data = []
package_names = []

with open('data/per-package-failures.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1

        package = row[0]
        line_coverage_total = int(row[1])
        line_coverage_failure = int(row[2])
        branch_coverage_total = int(row[3])
        branch_coverage_failure_val = int(row[4])
        branch_coverage_failure_num = int(row[5])
        mcdc_total = int(row[6])
        mcdc_failure_val = int(row[7])
        mcdc_failure_num = int(row[8])
        def division(n, d):
            return n / d if d else 0
        data.append([
            line_coverage_total, division((line_coverage_failure), line_coverage_total),
            branch_coverage_total, division((branch_coverage_failure_num + branch_coverage_failure_val), branch_coverage_total),
            mcdc_total, division((mcdc_failure_num + mcdc_failure_val), mcdc_total)
        ])
        package_names.append(package)

data = np.array(data)
package_names = np.array(package_names)

sorted_indices = np.argsort(data[:, 0])

data = data[sorted_indices]
data = data[:, [1, 3, 5]]
labels = [
    'Inconsistent lines',
    'Inconsistent branches',
    'Inconsistent decisions'
]
package_names = package_names[sorted_indices]

num_package, num_bar = data.shape

x = np.arange(num_package)

bar_width = 0.25
offsets = np.linspace(-bar_width, bar_width, num_bar)

fig, ax = plt.subplots(figsize=(15, 5))

ax.set_yscale("log")

for bar_idx in range(num_bar):
    ax.bar(
        x + offsets[bar_idx], data[:, bar_idx],
        width=bar_width,
        label=labels[bar_idx],
        color=metric_colors[bar_idx],
    )

plt.xticks(x, package_names)
plt.ylabel('Percent')
plt.legend()
plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')

plt.tight_layout()
plt.savefig('../figures/inconsistent_percent.pdf', metadata={'CreationDate': None})
plt.show()

import matplotlib.pyplot as plt
import numpy as np
import csv

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Computer Modern Roman"
})

data = []
package_names = []

with open('data/per-package-failures.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1

        package = row[0]
        line_coverage_total = int(row[1])
        line_coverage_failure = int(row[2])
        branch_coverage_total = int(row[3])
        branch_coverage_failure_val = int(row[4])
        branch_coverage_failure_num = int(row[5])
        mcdc_total = int(row[6])
        mcdc_failure_val = int(row[7])
        mcdc_failure_num = int(row[8])
        data.append([
            line_coverage_total, line_coverage_failure,
            branch_coverage_total, (branch_coverage_failure_num+branch_coverage_failure_val),
            mcdc_total, (mcdc_failure_num+mcdc_failure_val)
        ])
        package_names.append('\\texttt{' + package + '}') # TODO sync with \package{} in LaTeX

data = np.array(data)
package_names = np.array(package_names)

sorted_indices = np.argsort(data[:, 0])

labels1 = [
    'Compared lines',
    'Compared branches',
    'Compared decisions',
]
labels2 = [
    'Inconsistent lines',
    'Inconsistent branches',
    'Inconsistent decisions',
]
data = data[sorted_indices]
data1 = data[:, [0,2,4]]
data2 = data[:, [1,3,5]]
package_names = package_names[sorted_indices]

num_package, num_bar = data1.shape

x = np.arange(num_package)

bar_width = 0.25
offsets = np.linspace(-bar_width, bar_width, num_bar)

fig, ax = plt.subplots(figsize=(15, 5))

ax.set_yscale("log")

for bar_idx in range(num_bar):
    ax.bar(
        x + offsets[bar_idx], data1[:, bar_idx],
        width=bar_width,
        label=labels1[bar_idx],
        color=metric_colors[bar_idx],
        hatch=None,
    )
    lower_bars = ax.bar(
        x + offsets[bar_idx], data2[:, bar_idx],
        width=bar_width,
        label=labels2[bar_idx],
        color=metric_colors2[bar_idx],
        # hatch=metric_hatches[bar_idx],
        alpha=0.99,
    )
    for bar in lower_bars:
        x0 = bar.get_x()
        width = bar.get_width()
        height = bar.get_height()
        shrink = 0.15 * width
        ax.plot([x0 + shrink, x0 + width - shrink], [height, height], color='red', linewidth=2)

min_x = (x[0] + offsets[0]) - bar_width / 2
max_x = (x[-1] + offsets[-1]) + bar_width / 2
padding = 0.02 * (max_x - min_x)
ax.set_xlim(min_x - padding, max_x + padding)

plt.xticks(x, package_names)
plt.ylabel('Number of instance(s)')
plt.legend()
plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')

plt.tight_layout()
plt.savefig('../figures/compared_and_inconsistent_num.pdf', metadata={'CreationDate': None})
plt.show()


import csv
import numpy as np

all_package_name = []

all_package_line_coverage_total = []
all_package_line_coverage_failure = []
all_package_branch_coverage_total = []
all_package_branch_coverage_failure_val = []
all_package_branch_coverage_failure_num = []
all_package_mcdc_total = []
all_package_mcdc_failure_val = []
all_package_mcdc_failure_num = []

with open('data/per-package-failures.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1

        package = row[0]
        line_coverage_total = int(row[1])
        line_coverage_failure = int(row[2])
        branch_coverage_total = int(row[3])
        branch_coverage_failure_val = int(row[4])
        branch_coverage_failure_num = int(row[5])
        mcdc_total = int(row[6])
        mcdc_failure_val = int(row[7])
        mcdc_failure_num = int(row[8])
        # } // CSV schema

        all_package_name.append(package)

        all_package_line_coverage_total.append(line_coverage_total)
        all_package_line_coverage_failure.append(line_coverage_failure)
        all_package_branch_coverage_total.append(branch_coverage_total)
        all_package_branch_coverage_failure_val.append(branch_coverage_failure_val)
        all_package_branch_coverage_failure_num.append(branch_coverage_failure_num)
        all_package_mcdc_total.append(mcdc_total)
        all_package_mcdc_failure_val.append(mcdc_failure_val)
        all_package_mcdc_failure_num.append(mcdc_failure_num)

all_package_name = np.array(all_package_name)

all_package_line_coverage_total = np.array(all_package_line_coverage_total)
all_package_line_coverage_failure = np.array(all_package_line_coverage_failure)
all_package_branch_coverage_total = np.array(all_package_branch_coverage_total)
all_package_branch_coverage_failure_val = np.array(all_package_branch_coverage_failure_val)
all_package_branch_coverage_failure_num = np.array(all_package_branch_coverage_failure_num)
all_package_branch_coverage_failure = all_package_branch_coverage_failure_num + all_package_branch_coverage_failure_val
all_package_mcdc_total = np.array(all_package_mcdc_total)
all_package_mcdc_failure_val = np.array(all_package_mcdc_failure_val)
all_package_mcdc_failure_num = np.array(all_package_mcdc_failure_num)
all_package_mcdc_failure = all_package_mcdc_failure_num + all_package_mcdc_failure_val

branch_inconsistent_percent = all_package_branch_coverage_failure / all_package_branch_coverage_total * 100
sorted_indices = np.argsort(branch_inconsistent_percent)
branch_inconsistent_percent = branch_inconsistent_percent[sorted_indices]
all_package_name = all_package_name[sorted_indices]

m = f"\\newcommand{{\\HighestBranchInconsistentPackage}}{{\\package{{{all_package_name[-1]}}}\\xspace}}"
print(m)
latex_macros.append(m)
val = "{:.2f}".format(branch_inconsistent_percent[-1])
m = f"\\newcommand{{\\HighestBranchInconsistentPercent}}{{{val}\\%\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\SecondHighestBranchInconsistentPackage}}{{\\package{{{all_package_name[-2]}}}\\xspace}}"
print(m)
latex_macros.append(m)
val = "{:.2f}".format(branch_inconsistent_percent[-2])
m = f"\\newcommand{{\\SecondHighestBranchInconsistentPercent}}{{{val}\\%\\xspace}}"
print(m)
latex_macros.append(m)


import csv

bug_triggering_condition_summary: dict[str,int] = {}
gcc_bug_triggering_condition_summary: dict[str,int] = {}
llvm_bug_triggering_condition_summary: dict[str,int] = {}
conv_triggering_condition_summary: dict[str,int] = {}

with open('data/bugs.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        if len(row) >=3 and row[2] == 'dup':
            continue

        assert len(row) == 7, f"{row}"

        row_idx += 1

        id = row[0]
        comment = row[1]
        link = row[2]
        gcc_or_llvm = row[3]
        affected_metrics = row[4]
        inconsistencies = row[5]
        triggering_conditions = row[6]

        # } // CSV schema

        triggering_conditions = triggering_conditions.split(',')
        if len(triggering_conditions) > 1:
            triggering_conditions = sorted(triggering_conditions, key=lambda x: x)

        triggering_conditions = [ canonicalize_triggering_conditions_figure(c) for c in triggering_conditions ]

        for c in triggering_conditions:
            if c not in bug_triggering_condition_summary:
                bug_triggering_condition_summary[c] = 0
            if c not in gcc_bug_triggering_condition_summary:
                gcc_bug_triggering_condition_summary[c] = 0
            if c not in llvm_bug_triggering_condition_summary:
                llvm_bug_triggering_condition_summary[c] = 0

            bug_triggering_condition_summary[c] += 1
            if gcc_or_llvm == 'GCC':
                gcc_bug_triggering_condition_summary[c] += 1
            elif gcc_or_llvm == 'LLVM':
                llvm_bug_triggering_condition_summary[c] += 1
            else:
                assert False

        # The below is counting the total occurrence of each triggering condition
        # which is not too meaningful
        continue

        with open('data/line_coverage.csv', mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_row = True
            for row in reader:
                # CSV schema {
                if first_row:
                    first_row = False
                    continue
                assert len(row) in [ 5, 6 ]
                package = row[0]
                reason = row[4]
                # } // CSV schema
                reason = reason.split(',')
                if id in reason:
                    for c in triggering_conditions:
                        if c not in bug_triggering_condition_summary:
                            bug_triggering_condition_summary[c] = 1
                        else:
                            bug_triggering_condition_summary[c] += 1

        with open('data/branch_coverage.csv', mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_row = True
            for row in reader:
                # CSV schema {
                if first_row:
                    first_row = False
                    continue
                assert len(row) in [ 5, 6 ]
                package = row[0]
                reason = row[4]
                # } // CSV schema
                reason = reason.split(',')
                if id in reason:
                    for c in triggering_conditions:
                        if c not in bug_triggering_condition_summary:
                            bug_triggering_condition_summary[c] = 1
                        else:
                            bug_triggering_condition_summary[c] += 1

        with open('data/mcdc.csv', mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_row = True
            for row in reader:
                # CSV schema {
                if first_row:
                    first_row = False
                    continue
                assert len(row) in [ 5, 6 ]
                package = row[0]
                reason = row[4]
                # } // CSV schema
                reason = reason.split(',')
                if id in reason:
                    for c in triggering_conditions:
                        if c not in bug_triggering_condition_summary:
                            bug_triggering_condition_summary[c] = 1
                        else:
                            bug_triggering_condition_summary[c] += 1

# print(bug_triggering_condition_summary)

description_to_id = {}
description_to_triggering_conditions = {}

with open('data/convs.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1
        assert len(row) in [ 4, 5 ], \
            f"{row}" # optionally "comment" field
        id = row[0]
        description_in_latex = row[1]
        inconsistencies = row[2]
        triggering_conditions = row[3]
        # } // CSV schema

        if description_in_latex not in description_to_id:
            description_to_id[description_in_latex] = []
        description_to_id[description_in_latex].append(id)

        if description_in_latex not in description_to_triggering_conditions:
            description_to_triggering_conditions[description_in_latex] = []
        description_to_triggering_conditions[description_in_latex].append(triggering_conditions)

with open('data/convs.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1
        assert len(row) in [ 4, 5 ], \
            f"{row}" # optionally "comment" field
        id = row[0]
        description_in_latex = row[1]
        inconsistencies = row[2]
        triggering_conditions = row[3]
        # } // CSV schema

        if description_to_id[description_in_latex].index(id) != 0:
            continue

        triggering_conditions = set()
        for triggering_conditions_one_entry in description_to_triggering_conditions[description_in_latex]:
            for c in triggering_conditions_one_entry.split(','):
                triggering_conditions.add(c)
        if len(triggering_conditions) > 1:
            triggering_conditions = sorted(triggering_conditions, key=lambda x: x)

        triggering_conditions = [ canonicalize_triggering_conditions_figure(c) for c in triggering_conditions ]

        for c in triggering_conditions:
            if c not in conv_triggering_condition_summary:
                conv_triggering_condition_summary[c] = 1
            else:
                conv_triggering_condition_summary[c] += 1

# print(conv_triggering_condition_summary)

all_triggering_conditions = list(bug_triggering_condition_summary.keys())

for c in conv_triggering_condition_summary:
    if c not in all_triggering_conditions:
        print(f"Triggering condition that's unique to conv: {c}")
        all_triggering_conditions.append(c)

bug_nums_by_this_condition = np.zeros(len(all_triggering_conditions))
gcc_bug_nums_by_this_condition = np.zeros(len(all_triggering_conditions))
llvm_bug_nums_by_this_condition = np.zeros(len(all_triggering_conditions))
conv_nums_by_this_condition = np.zeros(len(all_triggering_conditions))

for i, c in enumerate(all_triggering_conditions):
    if c in bug_triggering_condition_summary:
        bug_nums_by_this_condition[i] = bug_triggering_condition_summary[c]
    if c in gcc_bug_triggering_condition_summary:
        gcc_bug_nums_by_this_condition[i] = gcc_bug_triggering_condition_summary[c]
    if c in llvm_bug_triggering_condition_summary:
        llvm_bug_nums_by_this_condition[i] = llvm_bug_triggering_condition_summary[c]
    if c in conv_triggering_condition_summary:
        conv_nums_by_this_condition[i] = conv_triggering_condition_summary[c]

# Sort by (1) number of bugs + number of convention differences (2) number of
# bugs (3) number of convention differences
sorted_data = sorted(zip(
    all_triggering_conditions,
    bug_nums_by_this_condition,
    conv_nums_by_this_condition,
    bug_nums_by_this_condition+conv_nums_by_this_condition,
    gcc_bug_nums_by_this_condition,
    llvm_bug_nums_by_this_condition,
), key=lambda x: (x[3], x[1], x[2], x[0]), reverse=True)

all_triggering_conditions, bug_nums_by_this_condition, \
    conv_nums_by_this_condition, _, \
    gcc_bug_nums_by_this_condition, llvm_bug_nums_by_this_condition \
    = map(list, zip(*sorted_data))

all_triggering_conditions = np.array(all_triggering_conditions)
bug_nums_by_this_condition = np.array(bug_nums_by_this_condition)
conv_nums_by_this_condition = np.array(conv_nums_by_this_condition)
gcc_bug_nums_by_this_condition = np.array(gcc_bug_nums_by_this_condition)
llvm_bug_nums_by_this_condition = np.array(llvm_bug_nums_by_this_condition)

# TODO determine a proper threshold
more_than_one_index = (bug_nums_by_this_condition + conv_nums_by_this_condition > 1)
all_triggering_conditions = all_triggering_conditions[more_than_one_index]
bug_nums_by_this_condition = bug_nums_by_this_condition[more_than_one_index]
conv_nums_by_this_condition = conv_nums_by_this_condition[more_than_one_index]
gcc_bug_nums_by_this_condition = gcc_bug_nums_by_this_condition[more_than_one_index]
llvm_bug_nums_by_this_condition = llvm_bug_nums_by_this_condition[more_than_one_index]

# FIXME remove this eventually
idx = np.where(all_triggering_conditions == '')[0]
if idx.size > 0:
    idx = idx[0]
    all_triggering_conditions = np.delete(all_triggering_conditions, idx)
    bug_nums_by_this_condition = np.delete(bug_nums_by_this_condition, idx)
    conv_nums_by_this_condition = np.delete(conv_nums_by_this_condition, idx)
    gcc_bug_nums_by_this_condition = np.delete(gcc_bug_nums_by_this_condition, idx)
    llvm_bug_nums_by_this_condition = np.delete(llvm_bug_nums_by_this_condition, idx)

import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Computer Modern Roman"
})

fig, ax = plt.subplots()

bar_width = 0.8

ax.bar(all_triggering_conditions, bug_nums_by_this_condition, width=bar_width, facecolor=bug_color, bottom=0)
conv_bars = ax.bar(all_triggering_conditions, conv_nums_by_this_condition, width=bar_width, label='Convention differences', facecolor=conv_color, bottom=bug_nums_by_this_condition)
llvm_bars = ax.bar(all_triggering_conditions, llvm_bug_nums_by_this_condition, width=bar_width, label='LLVM Bugs', facecolor=llvm_bug_color, alpha=0.99, bottom=gcc_bug_nums_by_this_condition)
gcc_bars = ax.bar(all_triggering_conditions, gcc_bug_nums_by_this_condition, width=bar_width, label='GCC Bugs', facecolor=gcc_bug_color, alpha=0.99, bottom=0)

# for llvm_bar, gcc_bar in zip(llvm_bars, gcc_bars):
#     x0 = gcc_bar.get_x()
#     width = gcc_bar.get_width()
#     height = gcc_bar.get_height()
#     shrink = 0.02 * width
#     if llvm_bar.get_height() > 0:
#         ax.plot([x0 + shrink, x0 + width - shrink], [height, height], color='black', linewidth=1)

ax.legend(loc='upper right')

# ax.set_yscale("log") # TODO see if log scale is needed

# plt.xlabel("Triggering Condition")
plt.ylabel("Number of Bugs or Convention Differences")

plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')

plt.tight_layout()
plt.savefig('../figures/bug_conv_count_wrt_triggering_condition2.pdf', metadata={'CreationDate': None})
plt.show()

# def savepdfviasvg(fig, name, **kwargs):
#     import subprocess
#     fig.savefig(name+".svg", format="svg", **kwargs)
#     incmd = ["inkscape", name+".svg", "--export-pdf={}.pdf".format(name),
#              "--export-pdf-version=1.5"] #"--export-ignore-filters",
#     subprocess.check_output(incmd)

# savepdfviasvg(fig, "../figures/bug_conv_count_wrt_triggering_condition2")

import numpy as np

# print(cause_to_projects)
# print(cause_to_occurrence)

cause_to_project_num = {}
for cause, projects in cause_to_projects.items():
    cause_to_project_num[cause] = len(list(projects.keys()))

# print(cause_to_project_num)

causes = list(cause_to_projects.keys())
_causes = list(cause_to_occurrence.keys())
assert causes == _causes
_causes = list(cause_to_project_num.keys())
assert causes == _causes

occurrences = list(cause_to_occurrence.values())
project_nums = list(cause_to_project_num.values())

causes = np.array(causes)
occurrences = np.array(occurrences)
project_nums = np.array(project_nums)

# TODO determine a proper threshold
more_than_one_index = np.logical_or(project_nums > 1, occurrences > 1)

causes = causes[more_than_one_index]
occurrences = occurrences[more_than_one_index]
project_nums = project_nums[more_than_one_index]

sorted_data = sorted(zip(causes, occurrences, project_nums),
                     key=lambda x: (x[2], x[1], x[0]), reverse=True)
causes, occurrences, project_nums = map(list, zip(*sorted_data))

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

fig, ax = plt.subplots()
ax1 = ax
ax2 = ax1.twinx()

label1 = 'Occurrences'
label2 = 'Affected Packages'

p1, = ax1.plot(causes, occurrences, 'b--', label=label1)
p2, = ax2.plot(causes, project_nums, 'r+:', label=label2)

# ax.set_xlabel("Cause")

ax1.set_ylabel(f"Number of {label1}")
ax2.set_ylabel(f"Number of {label2}")

ax1.legend(handles=[p1, p2])

plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')

ax1.set_ylim(bottom=0)
ax2.set_ylim(bottom=0)

ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

ax1.yaxis.label.set_color(p1.get_color())
ax2.yaxis.label.set_color(p2.get_color())

plt.tight_layout()
plt.savefig('../figures/bug_conv_impact2.pdf', metadata={'CreationDate': None})
plt.show()

for a, b in zip(causes, occurrences):
    print(a, b)


with open('data/select/selection_1_priority.txt', 'r') as f:
    line_count = sum(1 for _ in f)
num_select_high_priority = line_count

with open('data/select/selection_2_unique_source_package.txt', 'r') as f:
    line_count = sum(1 for _ in f)
num_select_source_package = line_count

with open('data/select/selection_3_c_cxx.txt', 'r') as f:
    line_count = sum(1 for _ in f)
num_select_c_cxx = line_count

with open('data/select/selection_4_high_prio_success_coverage.txt', 'r') as f:
    line_count = sum(1 for _ in f)
num_select_high_prio_success_coverage = line_count

with open('data/select/selection_5_low_priority_random.txt', 'r') as f:
    line_count = sum(1 for _ in f)
num_select_random_from_low_priority_group = line_count

with open('data/select/selection_6_low_priority_success.txt', 'r') as f:
    line_count = sum(1 for _ in f)
num_select_success_from_low_priority_group = line_count

num_debian = num_select_success_from_low_priority_group + num_select_high_prio_success_coverage

num_crash_and_other_failure = num_select_c_cxx + num_select_random_from_low_priority_group - num_debian

m = f"\\newcommand{{\\numSelectHighPriority}}{{{num_select_high_priority}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numSelectUniqueSourcePkg}}{{{num_select_source_package}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numSelectCCpp}}{{{num_select_c_cxx}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numSelectSuccessfulCoverageFromHighPrioGroup}}{{{num_select_high_prio_success_coverage}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numSelectRandomFromLowPrioGroup}}{{{num_select_random_from_low_priority_group}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numSelectSuccessfulCoverageFromLowPrioGroup}}{{{num_select_success_from_low_priority_group}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numDebian}}{{{num_debian}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numCrashAndOtherFailure}}{{{num_crash_and_other_failure}\\xspace}}"
print(m)
latex_macros.append(m)
#
m = f"\\newcommand{{\\numAllAttemptedPkg}}{{{num_select_c_cxx+num_select_random_from_low_priority_group}\\xspace}}"
print(m)
latex_macros.append(m)

import csv

num_inspection = 0
num_inspection_line_coverage = 0
num_inspection_branch_coverage = 0
num_inspection_branch_coverage_num = 0
num_inspection_branch_coverage_val = 0
num_inspection_mcdc = 0

num_gcov_overwrite = 0
num_version_string = 0
num_proc_self_map = 0

num_inconsistency_caused_by_bug = 0
num_inconsistency_caused_by_conv = 0
num_inconsistency_caused_by_other = 0

with open('data/line_coverage.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        assert len(row) in [ 5, 6 ]
        package = row[0]
        reason_type = row[3]
        reason = row[4]
        # } // CSV schema
        num_inspection += 1
        num_inspection_line_coverage += 1
        if reason_type == 'bug':
            num_inconsistency_caused_by_bug += 1
        elif reason_type == 'conv':
            num_inconsistency_caused_by_conv += 1
        elif reason_type == 'other':
            num_inconsistency_caused_by_other += 1
        else:
            assert False
        if reason == 'gcov overwrite':
            num_gcov_overwrite += 1
        if reason == 'inherent compiler difference':
            comment = row[5]
            if comment == 'stackvma.c reading /proc/self/maps':
                num_proc_self_map += 1
            if comment == 'wget --version contains compiler name and flags':
                num_version_string += 1

with open('data/branch_coverage.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        assert len(row) in [ 5, 6 ]
        package = row[0]
        reason_type = row[3]
        reason = row[4]
        # } // CSV schema
        num_inspection += 1
        num_inspection_branch_coverage += 1
        if reason_type in [ 'conv num', 'bug num', 'other num' ]:
            num_inspection_branch_coverage_num += 1
        elif reason_type in [ 'conv val', 'bug val', 'other val' ]:
            num_inspection_branch_coverage_val += 1
        else:
            assert False
        if reason_type in [ 'bug num', 'bug val' ]:
            num_inconsistency_caused_by_bug += 1
        elif reason_type in [ 'conv num', 'conv val' ]:
            num_inconsistency_caused_by_conv += 1
        elif reason_type in [ 'other num', 'other val' ]:
            num_inconsistency_caused_by_other += 1
        else:
            assert False
        if reason == 'gcov overwrite':
            num_gcov_overwrite += 1
        if reason == 'inherent compiler difference':
            comment = row[5]
            if comment == 'stackvma.c reading /proc/self/maps':
                num_proc_self_map += 1
            if comment == 'wget --version contains compiler name and flags':
                num_version_string += 1

with open('data/mcdc.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        assert len(row) in [ 5, 6 ]
        package = row[0]
        reason_type = row[3]
        reason = row[4]
        # } // CSV schema
        num_inspection += 1
        num_inspection_mcdc += 1
        if reason_type in [ 'bug num', 'bug val' ]:
            num_inconsistency_caused_by_bug += 1
        elif reason_type in [ 'conv num', 'conv val' ]:
            num_inconsistency_caused_by_conv += 1
        elif reason_type in [ 'other num', 'other val' ]:
            num_inconsistency_caused_by_other += 1
        else:
            assert False
        if reason == 'gcov overwrite':
            num_gcov_overwrite += 1
        if reason == 'inherent compiler difference':
            comment = row[5]
            if comment == 'stackvma.c reading /proc/self/maps':
                num_proc_self_map += 1
            if comment == 'wget --version contains compiler name and flags':
                num_version_string += 1

m = f"\\newcommand{{\\numFpCompilerVersionString}}{{{num_version_string}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numFpReadProcMap}}{{{num_proc_self_map}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numFpGcovOverwrite}}{{{num_gcov_overwrite}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numInspectedLineCov}}{{{num_inspection_line_coverage}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numInspectedBranchCov}}{{{num_inspection_branch_coverage}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numInspectedBranchCovNum}}{{{num_inspection_branch_coverage_num}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numInspectedBranchCovVal}}{{{num_inspection_branch_coverage_val}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numInspectedMcdc}}{{{num_inspection_mcdc}\\xspace}}"
print(m)
latex_macros.append(m)
assert num_inspection == num_inspection_line_coverage \
                       + num_inspection_branch_coverage \
                       + num_inspection_mcdc
m = f"\\newcommand{{\\numInconsistencyCausedByBug}}{{{num_inconsistency_caused_by_bug}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numInconsistencyCausedByConv}}{{{num_inconsistency_caused_by_conv}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numInconsistencyCausedByOther}}{{{num_inconsistency_caused_by_other}\\xspace}}"
print(m)
latex_macros.append(m)
assert num_inspection == num_inconsistency_caused_by_bug \
                       + num_inconsistency_caused_by_conv \
                       + num_inconsistency_caused_by_other
m = f"\\newcommand{{\\numInspectedTotal}}{{{num_inspection}\\xspace}}"
print(m)
latex_macros.append(m)

triggering_condition_to_bug_num: dict[str,int] = {}

with open('data/bugs.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        if len(row) >=3 and row[2] == 'dup':
            continue

        assert len(row) == 7, f"{row}"

        row_idx += 1

        id = row[0]
        comment = row[1]
        link = row[2]
        gcc_or_llvm = row[3]
        affected_metrics = row[4]
        inconsistencies = row[5]
        triggering_conditions = row[6]

        # } // CSV schema

        for c in triggering_conditions.split(','):
            if c in triggering_condition_to_bug_num:
                triggering_condition_to_bug_num[c][gcc_or_llvm] += 1
            else:
                triggering_condition_to_bug_num[c] = { 'GCC': 0, 'LLVM': 0 }
                triggering_condition_to_bug_num[c][gcc_or_llvm] += 1

for c in triggering_condition_to_bug_num:
    gcc_num = triggering_condition_to_bug_num[c]['GCC']
    llvm_num = triggering_condition_to_bug_num[c]['LLVM']
    print(f"{c}, {gcc_num}, {llvm_num}")

with open('data/bugs_debian_crash.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    row_idx = 0
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        row_idx += 1
        assert len(row) == 7, f"{row}"
        id          = row[0]
        comment     = row[1]
        link        = row[2]
        gcc_or_llvm = row[3]
        affected_metrics      = row[4]
        triggering_conditions = row[5]
        affected_proj         = row[6]
        # } // CSV schema
        if link == 'https://github.com/llvm/llvm-project/issues/95739':
            x = len(affected_proj.split(','))
        elif link == 'https://github.com/llvm/llvm-project/issues/95831':
            y = len(affected_proj.split(','))

m = f"\\newcommand{{\\numOccurenceOfCrashBugsTriggeredByMcdc}}{{{x}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numOccurenceOfCrashBugsIncludeHeaderInFuncBody}}{{{y}\\xspace}}"
print(m)
latex_macros.append(m)
m = f"\\newcommand{{\\numOccurenceOfCrashBugsTotal}}{{{x+y}\\xspace}}"
print(m)
latex_macros.append(m)

import csv

# "Other failures" throughout means (1) not differential inconsistency
# (2) not crash
num_failure_other_than_crash = 0
num_gcov_failure_other_than_crash = 0
num_llvmcov_failure_other_than_crash = 0
num_both_tool_have_some_other_failure = 0

num_build_fail = 0
num_no_profile = 0
num_no_profile_custom_exit = 0
num_no_profile_cap = 0
num_no_profile_hardwire = 0
num_gcov_error = 0

with open('data/other_failures.csv', mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    first_row = True
    for row in reader:
        # CSV schema {
        if first_row:
            first_row = False
            continue
        assert len(row) == 8
        package = row[0]
        default_gcc = row[1]
        gcc_no_instr = row[2]
        clang_no_instr = row[3]
        gcc_gcov = row[4]
        clang_scc = row[5]
        gcc_mcdc = row[6]
        clang_mcdc = row[7]
        # } // CSV schema

        if 'cov:crash' not in clang_mcdc:
            num_failure_other_than_crash += 1
            if 'cov:pass' not in clang_mcdc:
                num_llvmcov_failure_other_than_crash += 1
            if 'cov:pass' not in gcc_mcdc:
                num_gcov_failure_other_than_crash += 1
            if 'cov:pass' not in clang_mcdc and 'cov:pass' not in gcc_mcdc:
                num_both_tool_have_some_other_failure += 1

            if 'build fail' in clang_mcdc or 'build fail' in gcc_mcdc:
                num_build_fail += 1
            if 'no gcda' in gcc_mcdc or 'empty profile' in clang_mcdc:
                num_no_profile += 1
            if 'exit' in gcc_mcdc or 'exit' in clang_mcdc:
                num_no_profile_custom_exit += 1
            if 'capability' in gcc_mcdc or 'capability' in clang_mcdc:
                num_no_profile_cap += 1
            if 'hardwire' in gcc_mcdc or 'hardwire' in clang_mcdc:
                num_no_profile_hardwire += 1
            if 'stamp mismatch with notes file' in gcc_mcdc or 'cannot open source file' in gcc_mcdc:
                num_gcov_error += 1

m = f"\\newcommand{{\\numFailureOtherThanCrash}}{{{num_failure_other_than_crash}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numGcovFailureOtherThanCrash}}{{{num_gcov_failure_other_than_crash}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numLlvmcovFailureOtherThanCrash}}{{{num_llvmcov_failure_other_than_crash}\\xspace}}"
print(m)
latex_macros.append(m)

assert num_both_tool_have_some_other_failure == \
       num_gcov_failure_other_than_crash \
     + num_llvmcov_failure_other_than_crash \
     - num_failure_other_than_crash

m = f"\\newcommand{{\\numBothToolsHaveSomeOtherFailure}}{{{num_both_tool_have_some_other_failure}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numOtherFailureBuildFail}}{{{num_build_fail}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numOtherFailureNoProfile}}{{{num_no_profile}\\xspace}}"
print(m)
latex_macros.append(m)

assert num_no_profile == num_no_profile_custom_exit \
                       + num_no_profile_cap\
                       + num_no_profile_hardwire

m = f"\\newcommand{{\\numOtherFailureNoProfileCustomExit}}{{{num_no_profile_custom_exit}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numOtherFailureNoProfileCap}}{{{num_no_profile_cap}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numOtherFailureNoProfileHardwire}}{{{num_no_profile_hardwire}\\xspace}}"
print(m)
latex_macros.append(m)

m = f"\\newcommand{{\\numOtherFailureGcovError}}{{{num_gcov_error}\\xspace}}"
print(m)
latex_macros.append(m)

with open('../numbers_auto.tex', 'w') as out:
    for m in latex_macros:
        print(m, file=out)
