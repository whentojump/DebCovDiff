import csv
from enum import Enum
from utils.logger import get_logger
from utils.utils import file_name_to_project_name
logger = get_logger(__name__)

# Inconsistency types

class Inconsistency(Enum):
    MCDC_NUM_CONDITION               = 0
    MCDC_GCC_INTERNAL_INCONSISTENCY  = 1
    MCDC_LLVM_OVER_REPORT            = 2
    MCDC_GCC_OVER_REPORT             = 3
    MCDC_GCC_PLURAL_DECISION_A_LINE  = 4
    MCDC_LLVM_PLURAL_DECISION_A_LINE = 5

    LINE_COV                         = 10
    LINE_COV_STEADY                  = 11

    BRANCH_COV_NUM_OUTCOME           = 20
    BRANCH_COV_COUNT                 = 21
    BRANCH_COV_COUNT_STEADY          = 22

# What to do upon inconsistency

class Action(Enum):
    SILENT   = 0
    CONTINUE = 1
    ABORT    = 2
    LEARN    = 3

policies: dict[Inconsistency, list[Action]] = {
    Inconsistency.MCDC_NUM_CONDITION:               [ Action.SILENT, Action.CONTINUE ],
    Inconsistency.MCDC_GCC_INTERNAL_INCONSISTENCY:  [ Action.SILENT, Action.CONTINUE ],
    Inconsistency.MCDC_LLVM_OVER_REPORT:            [ Action.SILENT, Action.CONTINUE ],
    Inconsistency.MCDC_GCC_OVER_REPORT:             [ Action.SILENT, Action.CONTINUE ],
    Inconsistency.MCDC_GCC_PLURAL_DECISION_A_LINE:  [ Action.SILENT, Action.CONTINUE ],
    Inconsistency.MCDC_LLVM_PLURAL_DECISION_A_LINE: [ Action.SILENT, Action.CONTINUE ],

    Inconsistency.LINE_COV:                         [ Action.LEARN, Action.CONTINUE, Action.SILENT ],
    Inconsistency.LINE_COV_STEADY:                  [ Action.LEARN, Action.CONTINUE, Action.SILENT ],

    Inconsistency.BRANCH_COV_NUM_OUTCOME:           [ Action.CONTINUE ],
    Inconsistency.BRANCH_COV_COUNT:                 [ Action.LEARN, Action.CONTINUE, Action.SILENT ],
    Inconsistency.BRANCH_COV_COUNT_STEADY:          [ Action.LEARN, Action.CONTINUE, Action.SILENT ],
}

# Count inconsistency by type

inconsistency_count: dict[Inconsistency, int] = {}

inconsistency_count[Inconsistency.MCDC_NUM_CONDITION]               = 0
inconsistency_count[Inconsistency.MCDC_GCC_INTERNAL_INCONSISTENCY]  = 0
inconsistency_count[Inconsistency.MCDC_LLVM_OVER_REPORT]            = 0
inconsistency_count[Inconsistency.MCDC_GCC_OVER_REPORT]             = 0
inconsistency_count[Inconsistency.MCDC_GCC_PLURAL_DECISION_A_LINE]  = 0
inconsistency_count[Inconsistency.MCDC_LLVM_PLURAL_DECISION_A_LINE] = 0
inconsistency_count[Inconsistency.LINE_COV]                         = 0
inconsistency_count[Inconsistency.LINE_COV_STEADY]                  = 0
inconsistency_count[Inconsistency.BRANCH_COV_NUM_OUTCOME]           = 0
inconsistency_count[Inconsistency.BRANCH_COV_COUNT]                 = 0
inconsistency_count[Inconsistency.BRANCH_COV_COUNT_STEADY]          = 0

inconsistency_list: list = []

compared_sites = {
    'line': 0,
    'branch': 0,
    'decision': 0,
}

def dump_csv(inconsistency_csv_path, total_num_csv_path):

    with open(inconsistency_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        sorted_inconsistency_list = sorted(inconsistency_list, key=lambda elem: (elem[0].name, elem[1], elem[2]))

        for f in sorted_inconsistency_list:
            failure_type = f[0]
            file_name = f[1]
            project_name = file_name_to_project_name(file_name)
            line_number = f[2]

            # Schema
            if failure_type == Inconsistency.LINE_COV_STEADY:
                gcc_line_result = f[3]
                llvm_line_result = f[4]
                writer.writerow([project_name,file_name,line_number,failure_type,gcc_line_result,llvm_line_result])
            elif failure_type == Inconsistency.BRANCH_COV_COUNT_STEADY:
                gcc_branch_result = f[3]
                llvm_branch_result = f[4]
                writer.writerow([project_name,file_name,line_number,failure_type,gcc_branch_result,llvm_branch_result])
            elif failure_type == Inconsistency.BRANCH_COV_NUM_OUTCOME:
                gcc_num_outcome = f[3]
                llvm_num_outcome = f[4]
                writer.writerow([project_name,file_name,line_number,failure_type,gcc_num_outcome,llvm_num_outcome])
            elif failure_type == Inconsistency.MCDC_NUM_CONDITION:
                gcc_num_outcome = f[3]
                llvm_num_outcome = f[4]
                writer.writerow([project_name,file_name,line_number,failure_type,gcc_num_outcome,llvm_num_outcome])
            elif failure_type == Inconsistency.MCDC_GCC_OVER_REPORT:
                writer.writerow([project_name,file_name,line_number,failure_type,True,False])
            elif failure_type == Inconsistency.MCDC_LLVM_OVER_REPORT:
                writer.writerow([project_name,file_name,line_number,failure_type,False,True])

    with open(total_num_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([compared_sites['line'], compared_sites['branch'], compared_sites['decision']])

# Print inconsistency summary

class Result(Enum):
    CONSISTENT   = 0
    INCONSISTENT = 10

def inconsistency_summary() -> int:
    """
    1. Print summary regardless of `Action.SILENT`
    2. Return nonzero if there's any inconsistency, but honoring `Action.SILENT`
    """
    ret = Result.CONSISTENT
    if any(list(inconsistency_count.values())):
        logger.warning("")
        logger.warning("----------------------------------------------")
        logger.warning("Inconsistency type                       Count")
        logger.warning("----------------------------------------------")
        inconsistency_type: Inconsistency
        for inconsistency_type in inconsistency_count:
            count = inconsistency_count[inconsistency_type]
            if count:
                logger.warning(f"{inconsistency_type.name:<40} {count}")
                if Action.SILENT not in policies[inconsistency_type]:
                    ret = Result.INCONSISTENT
        logger.warning("----------------------------------------------")

    return ret.value
