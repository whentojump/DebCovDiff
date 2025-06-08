from utils import utils
from oracles.inconsistency import (
    Inconsistency,
    Action,
    policies,
    inconsistency_count,
    inconsistency_list,
)
from utils.logger import get_logger
logger = get_logger(__name__)
from utils.utils import info_section
from oracles.history import BranchCoverageHistory
import numpy as np

def compare_gcc_llvm(
    source_dir,
    file_name,
    gcc_file_json,
    llvm_file_json={},
    llvm_branches_json={},
    repeat=1,
    branch_coverage_history: BranchCoverageHistory = {},
    show_source=False,
) -> int:
    """
    Compare branch coverage of the same source file.

    Parameters
    ----------
    gcc_file_json : dict

      The JSON object corresponding to this file in GCC output.

    llvm_file_json : dict

      The JSON object corresponding to this file in LLVM output. For LLVM,
      provide either `llvm_file_json` or `llvm_branches_json` as parameter.

    llvm_branches_json : dict

      The `"branches"` JSON object of this file in LLVM output. For LLVM,
      provide either `llvm_file_json` or `llvm_branches_json` as parameter.

    """

    if not llvm_file_json and not llvm_branches_json:
        print("Pass either .data[0].files[n].branches or .data[0].files[n]")
        exit()
    if llvm_file_json and llvm_branches_json:
        print("Pass either .data[0].files[n].branches or .data[0].files[n]")
        exit()
    if llvm_file_json:
        llvm_branches_json = llvm_file_json['branches']

    info_section(logger, "Compare branch coverage measure", divider='-')

    #
    # {line number} -> {branch coverage statistics} maps
    #

    gcc_branch_results: dict[int, list[int]] = {}
    llvm_branch_results: dict[int, list[int]] = {}

    func_name_map: dict[int, str] = {}

    #
    # Gather information into the map -- GCC
    #

    assert file_name == gcc_file_json['file'], \
           "Inconsistent filename contained in GCC's JSON output"
    file_json = gcc_file_json

    for line_json in file_json['lines']:
        if line_json['branches']:

            try:
                func_name = line_json['function_name']
            except KeyError:
                func_name = 'UNKNOWN'

            line_number = int(line_json['line_number'])
            decision_json_array = line_json['branches']

            gcc_branch_results[line_number] = [ int(outcome["count"]) for outcome in decision_json_array ]

            func_name_map[line_number] = func_name

    #
    # Gather information into the map -- LLVM
    #

    if llvm_file_json:
        assert file_name == llvm_file_json['filename'], \
               "Inconsistent filename contained in LLVM's JSON output"

    for decision_json in llvm_branches_json:
        # https://github.com/llvm/llvm-project/blob/llvmorg-20-init/llvm/tools/llvm-cov/CoverageExporterJson.cpp#L96-L102
        LineStart           = int(decision_json[0])
        ColumnStart         =     decision_json[1]
        LineEnd             =     decision_json[2]
        ColumnEnd           =     decision_json[3]
        ExecutionCount      = int(decision_json[4])
        FalseExecutionCount = int(decision_json[5])
        FileID              =     decision_json[6]
        ExpandedFileID      =     decision_json[7]
        if FileID != 0 or ExpandedFileID != 0:
            print(decision_json)
            assert 0
        Kind                =     decision_json[8]
        # https://github.com/llvm/llvm-project/blob/llvmorg-20-init/llvm/include/llvm/ProfileData/Coverage/CoverageMapping.h#L242
        assert Kind in [ 4, 6 ], \
               "Branches in LLVM's JSON output should be of either `BranchRegion` or `MCDCBranchRegion` kind"

        if LineStart in llvm_branch_results:
            llvm_branch_results[LineStart].append(ExecutionCount)
            llvm_branch_results[LineStart].append(FalseExecutionCount)
        else:
            llvm_branch_results[LineStart] = [ExecutionCount, FalseExecutionCount]

    #
    # Oracles
    #

    total = utils.count_lines(source_dir, file_name)
    gcc_total = len(gcc_branch_results)
    llvm_total = len(llvm_branch_results)
    line_number_intersection = set(gcc_branch_results).intersection(set(llvm_branch_results))
    comparable_cnt = len(line_number_intersection)

    for line_number in line_number_intersection:

        gcc_branch_result = gcc_branch_results[line_number]
        llvm_branch_result = llvm_branch_results[line_number]

        func_name = func_name_map[line_number]

        gcc_num_outcome = len(gcc_branch_result)
        llvm_num_outcome = len(llvm_branch_result)

        if gcc_num_outcome != llvm_num_outcome:

            inconsistency_type = Inconsistency.BRANCH_COV_NUM_OUTCOME
            inconsistency_count[inconsistency_type] += 1
            inconsistency_list.append((
                inconsistency_type,
                file_name,
                line_number,
                gcc_num_outcome,
                llvm_num_outcome
            ))
            actions = policies[inconsistency_type]
            if (Action.SILENT not in actions):
                logger.warning(f"Branch coverage: inconsistency at {func_name}:{file_name}:{line_number}")
                logger.warning(f"  number of outcome(s) reported by GCC is {gcc_num_outcome}")
                logger.warning(f"  number of outcome(s) reported by LLVM is {llvm_num_outcome}")
                if (show_source and source_dir):
                    utils.show_source(logger, source_dir, file_name, line_number)
                logger.warning("")
            if (Action.ABORT in actions):
                exit()
            if (Action.CONTINUE in actions):
                continue

        if gcc_branch_result != llvm_branch_result:

            # Be optimistic if the only difference is the order. We do know that
            # in LLVM results, the "true" outcome and "false" outcome for the
            # same condition are put next to each other; but we know nothing
            # about GCC.

            sorted_gcc_branch_result = sorted(gcc_branch_result)
            sorted_llvm_branch_result = sorted(llvm_branch_result)

            if sorted_gcc_branch_result != sorted_llvm_branch_result:
                inconsistency_type = Inconsistency.BRANCH_COV_COUNT
                if (
                    file_name in branch_coverage_history and
                    str(line_number) in branch_coverage_history[file_name]
                ):
                    site_history = branch_coverage_history[file_name][str(line_number)]
                    lo = np.min(site_history, axis=0)
                    hi = np.max(site_history, axis=0)

                    if len(site_history) + 1 >= repeat and all(lo == hi):
                        inconsistency_type = Inconsistency.BRANCH_COV_COUNT_STEADY
                inconsistency_count[inconsistency_type] += 1
                if inconsistency_type == Inconsistency.BRANCH_COV_COUNT_STEADY:
                    inconsistency_list.append((
                        inconsistency_type,
                        file_name,
                        line_number,
                        sorted_gcc_branch_result,
                        sorted_llvm_branch_result
                    ))
                actions = policies[inconsistency_type]
                if (Action.SILENT not in actions):
                    if inconsistency_type == Inconsistency.BRANCH_COV_COUNT:
                        logger.warning(f"Branch coverage: inconsistency at {file_name}:{line_number}")
                    if  inconsistency_type == Inconsistency.BRANCH_COV_COUNT_STEADY:
                        logger.warning(f"Branch coverage: (steady) inconsistency at {file_name}:{line_number}")
                    logger.warning(f"  GCC:  {sorted_gcc_branch_result}")
                    logger.warning(f"  LLVM: {sorted_llvm_branch_result}")
                    if (show_source and source_dir):
                        utils.show_source(logger, source_dir, file_name, line_number)
                    logger.warning("")
                line_number = str(line_number)
                if (Action.LEARN in actions):
                    if file_name in branch_coverage_history:
                        if line_number in branch_coverage_history[file_name]:
                            branch_coverage_history[file_name][line_number].append(gcc_branch_result)
                        else:
                            branch_coverage_history[file_name][line_number] = [ gcc_branch_result ]
                    else:
                        branch_coverage_history[file_name] = { line_number : [ gcc_branch_result ] }
                if (Action.ABORT in actions):
                    exit()
                if (Action.CONTINUE in actions):
                    continue

        logger.debug(f"Match at {file_name}:{line_number}")

    logger.info("")
    logger.info(f"{file_name}:")
    logger.info(f"  File:     {total} line(s)")
    logger.info(f"  GCC:      {gcc_total} line(s) having branches")
    logger.info(f"  LLVM:     {llvm_total} line(s) having branches")
    logger.info(f"  Compared: {comparable_cnt} line(s)")
    return comparable_cnt
