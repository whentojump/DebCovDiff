#!/usr/bin/env python3

from pathlib import Path
import argparse
from utils.logger import get_logger
logger = get_logger(__name__)

#
# Data structure for exchanging info within our scripts
#

SingleFileLcovFunctionCoverage = object         # TODO
SingleFileLcovLineCoverage     = dict[int, int]
SingleFileLcovBranchCoverage   = object         # TODO

# Key being one of {filename, function, line, branch}
SingleFileLcovData = dict[str, str                            |
                               SingleFileLcovFunctionCoverage |
                               SingleFileLcovLineCoverage     |
                               SingleFileLcovBranchCoverage]

LcovData = list[SingleFileLcovData]

def get_nth_file_name_from_lcov_data(lcov_data: LcovData, n: int) -> str:
    return str(lcov_data[n]['filename'])

def set_nth_file_name_from_lcov_data(lcov_data: LcovData, n: int,
                                     file_name: str):
    lcov_data[n]['filename'] = file_name

#
# Data structure that represent original text LCOV files
#

LcovRecord = list[str]

def get_lcov_data(lcov: str | Path, verbose=False) -> LcovData:
    lcov_data: LcovData = []

    records: list[LcovRecord] = []
    current_record: LcovRecord = []

    with open(lcov, 'r') as f:
        for line in f:
            if line.strip() == 'end_of_record':
                if current_record:
                    records.append(current_record)
                    current_record = []
            else:
                current_record.append(line.strip())
        assert (not current_record), \
               "LCOV file does not end with an \"end_of_record\""

    for r in records:
        single_file_lcov_data = process_record(r, verbose)
        lcov_data.append(single_file_lcov_data)

    return lcov_data

def process_record(record: LcovRecord, verbose: bool) -> SingleFileLcovData:
    single_file_lcov_data: SingleFileLcovData = {}

    # https://manpages.debian.org/bookworm/lcov/geninfo.1.en.html#FILES
    # https://github.com/linux-test-project/lcov/blob/master/man/geninfo.1

    # {line number} -> {counter} map
    line_results: dict[int, int] = {}

    source_file = ''

    for line in record:
        field_name, field_value = line.split(':', 1)
        match field_name:
            case 'SF':
                source_file = field_value
            case 'FN' | 'FNDA' | 'FNF' | 'FNH':
                pass
            case 'BRDA' | 'BRF' | 'BRH':
                pass
            case 'DA':
                line_number, counter = [ int(x) for x in field_value.split(',') ]
                line_results[line_number] = counter
            case 'LF':
                pass
            case 'LH':
                pass
            case _:
                assert False, f"LCOV field not seen before: {field_name}"

    assert (source_file), "Source file not found in LCOV record"

    if (verbose):
        print(source_file)
        print(line_results)

    single_file_lcov_data['filename'] = source_file
    single_file_lcov_data['line'] = line_results

    return single_file_lcov_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LCOV parser")
    parser.add_argument('lcov')
    args = parser.parse_args()
    get_lcov_data(args.lcov, verbose=True)
