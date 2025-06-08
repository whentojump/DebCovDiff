#!/usr/bin/env python3

import argparse
from oracles.inconsistency import (
    Inconsistency,
    Action,
    inconsistency_summary,
    dump_csv,
    policies,
    compared_sites,
)
from input import (
    debian_package,
)

from utils.logger import get_logger, config_logger
logger = get_logger(__name__)
import logging

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Coverage tools differential testing")

    parser.add_argument('--log-level', help='One of {critical,error,warning,info,debug}')
    parser.add_argument('--all-inconsistency-csv', help='Path of CSV for all inconsistencies')
    parser.add_argument('--total-num-csv', help='Path of CSV for all compared sites')
    parser.add_argument('--show-source', action='store_true',
                                         help='Print source code around the line of inconsistency')
    parser.add_argument('--all-metrics', action='store_true',
                                         help="Warn of all metrics despite `Action.SILENT'")

    subparsers = parser.add_subparsers(help='Subcommands', dest='subcommand')

    parser_deb = subparsers.add_parser('deb', help='Process results from a Debian package')
    parser_deb.add_argument('package_name')

    args = parser.parse_args()

    show_source = False

    if args.show_source:
        show_source = True

    level = None

    if args.log_level:
        match args.log_level.lower():
            case 'critical':
                level = logging.CRITICAL
            case 'error':
                level = logging.ERROR
            case 'warning':
                level = logging.WARNING
            case 'info':
                level = logging.INFO
            case 'debug':
                level = logging.DEBUG
            case _:
                parser.print_help()
                exit()

    if level:
        config_logger(level)
    else:
        config_logger()

    if args.all_metrics:

        def do_not_be_silent(inconsistency):
            if Action.SILENT in policies[inconsistency]:
                policies[inconsistency].remove(Action.SILENT)

        do_not_be_silent(Inconsistency.MCDC_NUM_CONDITION)
        do_not_be_silent(Inconsistency.MCDC_GCC_INTERNAL_INCONSISTENCY)
        do_not_be_silent(Inconsistency.MCDC_LLVM_OVER_REPORT)
        do_not_be_silent(Inconsistency.MCDC_GCC_OVER_REPORT)

        do_not_be_silent(Inconsistency.LINE_COV)
        do_not_be_silent(Inconsistency.LINE_COV_STEADY)

        do_not_be_silent(Inconsistency.BRANCH_COV_NUM_OUTCOME)
        do_not_be_silent(Inconsistency.BRANCH_COV_COUNT)
        do_not_be_silent(Inconsistency.BRANCH_COV_COUNT_STEADY)

    if args.all_inconsistency_csv:
        all_inconsistency_csv = args.all_inconsistency_csv
    else:
        all_inconsistency_csv = ''

    if args.total_num_csv:
        total_num_csv = args.total_num_csv
    else:
        total_num_csv = ''

    if not args.subcommand:
        parser.print_help()
        exit()

    if args.subcommand == 'deb':
        line_coverage_total, branch_coverage_total, mcdc_total = \
            debian_package.run(args.package_name, show_source)
        compared_sites['line'] += line_coverage_total
        compared_sites['branch'] += branch_coverage_total
        compared_sites['decision'] += mcdc_total

    if all_inconsistency_csv and total_num_csv:
        dump_csv(all_inconsistency_csv, total_num_csv)

    exit(inconsistency_summary())
