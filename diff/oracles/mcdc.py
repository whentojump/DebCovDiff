import pprint
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

def compare_gcc_llvm(
    source_dir,
    file_name,
    gcc_file_json,
    llvm_file_json={},
    llvm_mcdc_records_json={},
    repeat=1,
    mcdc_history={},
    show_source=False,
) -> int:
    """
    Compare MC/DC of the same source file.

    Parameters
    ----------
    gcc_file_json : dict

      The JSON object corresponding to this file in GCC output.

    llvm_file_json : dict

      The JSON object corresponding to this file in LLVM output. For LLVM,
      provide either `llvm_file_json` or `llvm_mcdc_records_json` as parameter.

    llvm_mcdc_records_json : dict

      The `"mcdc_records"` JSON object of this file in LLVM output. For LLVM,
      provide either `llvm_file_json` or `llvm_mcdc_records_json` as parameter.

    """

    if not llvm_file_json and not llvm_mcdc_records_json:
        print("Pass either .data[0].files[n].mcdc_records or .data[0].files[n]")
        exit()
    if llvm_file_json and llvm_mcdc_records_json:
        print("Pass either .data[0].files[n].mcdc_records or .data[0].files[n]")
        exit()
    if llvm_file_json:
        llvm_mcdc_records_json = llvm_file_json['mcdc_records']

    info_section(logger, "Compare MC/DC measure", divider='-')

    #
    # {line number} -> {MC/DC statistics} maps
    #

    gcc_mcdc_results: dict[int, list[int]] = {}
    llvm_mcdc_results: dict[int, list[int]] = {}

    #
    # Gather information into the map -- GCC
    #

    assert file_name == gcc_file_json['file'], \
           "Inconsistent filename contained in GCC's JSON output"
    file_json = gcc_file_json

    for line_json in file_json['lines']:
        if line_json['conditions']:

            line_number = line_json['line_number']
            decision_json_array = line_json['conditions']

            if len(decision_json_array) != 1:
                inconsistency_type = Inconsistency.MCDC_GCC_PLURAL_DECISION_A_LINE
                inconsistency_count[inconsistency_type] += 1
                actions = policies[inconsistency_type]
                if (Action.SILENT not in actions):
                    logger.warning(f"MC/DC: GCC reports more than one decisions per line at {file_name}:{line_number}")
                    logger.debug("  JSON for this line:\n%s", pprint.pformat(line_json, compact=True))
                    logger.warning("")
                if (Action.ABORT in actions):
                    exit()
                if (Action.CONTINUE in actions):
                    continue

            decision_json = decision_json_array[0]

            count             = decision_json['count']
            covered           = decision_json['covered']
            not_covered_true  = decision_json['not_covered_true']
            not_covered_false = decision_json['not_covered_false']

            gcc_mcdc_results[line_number] = [count, covered, not_covered_true, not_covered_false]

    #
    # Gather information into the map -- LLVM
    #

    if llvm_file_json:
        assert file_name == llvm_file_json['filename'], \
               "Inconsistent filename contained in LLVM's JSON output"

    multiple_decision_lines: list[int] = []

    for decision_json in llvm_mcdc_records_json:
        # https://github.com/llvm/llvm-project/blob/llvmorg-20-init/llvm/tools/llvm-cov/CoverageExporterJson.cpp#L111-L116
        LineStart      = int(decision_json[0])
        ColumnStart    = decision_json[1]
        LineEnd        = decision_json[2]
        ColumnEnd      = decision_json[3]
        ExpandedFileID = decision_json[4]
        Kind           = decision_json[5]
        # https://github.com/llvm/llvm-project/blob/llvmorg-20-init/llvm/include/llvm/ProfileData/Coverage/CoverageMapping.h#L246
        assert Kind == 5, \
               "MC/DC records in LLVM's JSON output should always be of `MCDCDecisionRegion` kind"
        Conditions     = list(decision_json[6])

        if (LineStart in llvm_mcdc_results):
            inconsistency_type = Inconsistency.MCDC_LLVM_PLURAL_DECISION_A_LINE
            inconsistency_count[inconsistency_type] += 1
            actions = policies[inconsistency_type]
            if (Action.SILENT not in actions):
                logger.warning(f"MC/DC: LLVM reports more than one decisions per line at {file_name}:{LineStart}")
                logger.debug("  Previously we've had: %s", pprint.pformat(llvm_mcdc_results[LineStart], compact=True))
                logger.debug("  Attempting to add: %s", pprint.pformat(Conditions, compact=True))
                logger.warning("")
            if (Action.ABORT in actions):
                exit()
            if (Action.CONTINUE in actions):
                if LineStart not in multiple_decision_lines:
                    multiple_decision_lines.append(LineStart)
                continue

        llvm_mcdc_results[LineStart] = Conditions

    for line_number in multiple_decision_lines:
        del llvm_mcdc_results[line_number]

    #
    # Oracles
    #

    total = utils.count_lines(source_dir, file_name)
    gcc_total = len(gcc_mcdc_results)
    llvm_total = len(llvm_mcdc_results)
    comparable_cnt = 0

    for line_number, gcc_mcdc_result in gcc_mcdc_results.items():
        if line_number in llvm_mcdc_results:

            comparable_cnt += 1

            llvm_mcdc_result = llvm_mcdc_results[line_number]

            num_outcome                  = gcc_mcdc_result[0]
            num_covered_outcome          = gcc_mcdc_result[1]
            true_not_covered_conditions  = gcc_mcdc_result[2]
            false_not_covered_conditions = gcc_mcdc_result[3]

            condition_coverage = llvm_mcdc_result

            # LLVM by default doesn't tell whether a condition is "const folded"
            # or not in its JSON output. GCC doesn't count "const folded" ones
            # as conditions at all.
            #
            # If LLVM is locally patched, we let the "Conditions" field be an
            # array of {0,1,2}, where 0 means False before; 1 means True before;
            # 2 which is newly added means "const folded".

            contains_constant_fold = any([ c == 2 for c in condition_coverage ])

            # Convert 0 and 1 back to boolean again
            condition_coverage = [ True if c == 1 else False if c == 0 else c for c in condition_coverage ]
            # Remove "const folded" conditions in the result vector
            condition_coverage = [ c for c in condition_coverage if c in [ True, False ] ]

            num_condition = len(condition_coverage)

            gcc_num_outcome = num_outcome
            llvm_num_outcome = num_condition*2

            if gcc_num_outcome != llvm_num_outcome:
                if contains_constant_fold:
                    continue

                inconsistency_type = Inconsistency.MCDC_NUM_CONDITION
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
                    logger.warning(f"MC/DC: inconsistency at {file_name}:{line_number}")
                    logger.warning(f"  number of outcome(s) reported by GCC is {num_outcome}")
                    logger.warning(f"  number of condition(s) reported by LLVM is {num_condition}")
                    if (show_source and source_dir):
                        utils.show_source(logger, source_dir, file_name, line_number)
                if (Action.ABORT in actions):
                    exit()
                if (Action.CONTINUE in actions):
                    continue

            if num_outcome != num_covered_outcome              + \
                              len(true_not_covered_conditions) + \
                              len(false_not_covered_conditions):
                if contains_constant_fold:
                    continue
                inconsistency_type = Inconsistency.MCDC_GCC_INTERNAL_INCONSISTENCY
                inconsistency_count[inconsistency_type] += 1
                inconsistency_list.append((
                    inconsistency_type,
                    file_name,
                    line_number
                ))
                actions = policies[inconsistency_type]
                if (Action.SILENT not in actions):
                    logger.warning(f"MC/DC: GCC internal inconsistency at {file_name}:{line_number}")
                    logger.warning(f"  number of outcome(s) is {num_outcome}")
                    logger.warning(f"  number of covered outcome(s) is {num_covered_outcome}")
                    logger.warning(f"  condition(s) whose true outcome is not covered: {true_not_covered_conditions}")
                    logger.warning(f"  condition(s) whose false outcome is not covered: {false_not_covered_conditions}")
                    if (show_source and source_dir):
                        utils.show_source(logger, source_dir, file_name, line_number)
                if (Action.ABORT in actions):
                    exit()
                if (Action.CONTINUE in actions):
                    continue

            for i in range(num_condition):
                if i in true_not_covered_conditions or i in false_not_covered_conditions:
                    if condition_coverage[i] == True:
                        if contains_constant_fold:
                            continue
                        inconsistency_type = Inconsistency.MCDC_LLVM_OVER_REPORT
                        inconsistency_count[inconsistency_type] += 1
                        inconsistency_list.append((
                            inconsistency_type,
                            file_name,
                            line_number
                        ))
                        actions = policies[inconsistency_type]
                        if (Action.SILENT not in actions):
                            logger.warning(f"MC/DC: inconsistency at {file_name}:{line_number} condition #{i}")
                            msg = "GCC report: "
                            if i in true_not_covered_conditions:
                                msg += "true outcome is not covered; "
                            if i in false_not_covered_conditions:
                                msg += "false outcome is not covered; "
                            logger.warning(f"  {msg}")
                            logger.warning(f"  LLVM report: covered")
                            if (show_source and source_dir):
                                utils.show_source(logger, source_dir, file_name, line_number)
                        if (Action.ABORT in actions):
                            exit()
                        if (Action.CONTINUE in actions):
                            continue
                else:
                    if condition_coverage[i] == False:
                        if contains_constant_fold:
                            continue
                        inconsistency_type = Inconsistency.MCDC_GCC_OVER_REPORT
                        inconsistency_count[inconsistency_type] += 1
                        inconsistency_list.append((
                            inconsistency_type,
                            file_name,
                            line_number
                        ))
                        actions = policies[inconsistency_type]
                        if (Action.SILENT not in actions):
                            logger.warning(f"MC/DC: inconsistency at {file_name}:{line_number} condition #{i}")
                            logger.warning(f"  GCC report: covered")
                            logger.warning(f"  LLVM report: not covered")
                            if (show_source and source_dir):
                                utils.show_source(logger, source_dir, file_name, line_number)
                        if (Action.ABORT in actions):
                            exit()
                        if (Action.CONTINUE in actions):
                            continue

            logger.debug(f"Match at {file_name}:{line_number}")

    logger.info("")
    logger.info(f"{file_name}:")
    logger.info(f"  File:     {total} line(s)")
    logger.info(f"  GCC:      {gcc_total} line(s) having one decision")
    logger.info(f"  LLVM:     {llvm_total} line(s) having one decision")
    logger.info(f"  Compared: {comparable_cnt} line(s), i.e. {comparable_cnt} decisions(s)")
    return comparable_cnt
