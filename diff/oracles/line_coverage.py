from utils.lcov import SingleFileLcovData
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
from oracles.history import LineCoverageHistory

def compare_gcc_llvm(
    source_dir,
    file_name,
    gcc_file_json,
    llvm_file_json,
    llvm_file_lcov_data: SingleFileLcovData,
    repeat=1,
    line_coverage_history: LineCoverageHistory = {},
    show_source=False,
) -> int:
    """
    Compare line coverage of the same source file.

    Parameters
    ----------
    gcc_file_json : dict

      The JSON object corresponding to this file in GCC output.

    llvm_file_json : dict

      The JSON object corresponding to this file in LLVM output.

    llvm_file_lcov_data : SingleFileLcovData

      Coverage information of this file obtained from LLVM's LCOV output.

    """

    info_section(logger, "Compare line coverage measure", divider='-')

    #
    # {line number} -> {counter} maps
    #

    gcc_line_results: dict[int, int] = {}
    llvm_line_results: dict[int, int] = {}

    #
    # Gather information into the map -- GCC
    #

    assert file_name == gcc_file_json['file'], \
           "Inconsistent filename contained in GCC's JSON output"
    file_json = gcc_file_json

    for line_json in file_json['lines']:
        line_number = line_json['line_number']
        counter = line_json['count']
        gcc_line_results[line_number] = counter

    #
    # Gather information into the map -- LLVM
    #

    assert file_name == llvm_file_lcov_data['filename'], \
           "Inconsistent filename contained in LLVM's JSON output"
    llvm_line_results = llvm_file_lcov_data['line']

    #
    # Oracles
    #

    gcc_total = len(gcc_line_results)
    llvm_total = len(llvm_line_results)
    total = utils.count_lines(source_dir, file_name)
    line_number_intersection = set(gcc_line_results).intersection(set(llvm_line_results))
    comparable_cnt = len(line_number_intersection)

    # Find common lines and compare

    for line_number in line_number_intersection:
        gcc_line_result = gcc_line_results[line_number]
        llvm_line_result = llvm_line_results[line_number]
        if (
            gcc_line_result and
            llvm_line_result and
            gcc_line_result != llvm_line_result
        ):
            inconsistency_type = Inconsistency.LINE_COV
            if (
                file_name in line_coverage_history and
                # This JSON is going to be written to and read back from disk by
                # json.dump(), so strictly use string as keys. (Elsewhere in
                # this script, we have been using int as JSON keys which in fact
                # does not conform to standards)
                str(line_number) in line_coverage_history[file_name]
            ):
                site_history = line_coverage_history[file_name][str(line_number)]
                if len(site_history) + 1 >= repeat and min(site_history) == max(site_history):
                    inconsistency_type = Inconsistency.LINE_COV_STEADY
            inconsistency_count[inconsistency_type] += 1
            if inconsistency_type == Inconsistency.LINE_COV_STEADY:
                inconsistency_list.append((
                    inconsistency_type,
                    file_name,
                    line_number,
                    gcc_line_result,
                    llvm_line_result
                ))
            actions = policies[inconsistency_type]
            if (Action.SILENT not in actions):
                if inconsistency_type == Inconsistency.LINE_COV:
                    logger.warning(f"Line coverage: inconsistency at {file_name}:{line_number}")
                if  inconsistency_type == Inconsistency.LINE_COV_STEADY:
                    logger.warning(f"Line coverage: (steady) inconsistency at {file_name}:{line_number}")
                logger.warning(f"  counter reported by GCC is {gcc_line_result}")
                logger.warning(f"  counter reported by LLVM is {llvm_line_result}")
                if (show_source and source_dir):
                    utils.show_source(logger, source_dir, file_name, line_number)
            # Strictly use string as JSON keys
            line_number = str(line_number)
            if (Action.LEARN in actions):
                if file_name in line_coverage_history:
                    if line_number in line_coverage_history[file_name]:
                        line_coverage_history[file_name][line_number].append(gcc_line_result)
                    else:
                        line_coverage_history[file_name][line_number] = [ gcc_line_result ]
                else:
                    line_coverage_history[file_name] = { line_number : [ gcc_line_result ] }
            if (Action.ABORT in actions):
                exit()
            if (Action.CONTINUE in actions):
                continue
        else:
            logger.debug(f"Match at {file_name}:{line_number}")

    logger.info("")
    logger.info(f"{file_name}:")
    logger.info(f"  File:     {total} line(s)")
    logger.info(f"  GCC:      {gcc_total} line(s) instrumented")
    logger.info(f"  LLVM:     {llvm_total} line(s) instrumented")
    logger.info(f"  Compared: {comparable_cnt} line(s)")
    return comparable_cnt
