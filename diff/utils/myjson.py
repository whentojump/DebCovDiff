# gcov JSON
#
# .format_version
# .gcc_version
# .current_working_directory
# .data_file
# .files
#   [0]
#   [1]
#   [2]
#   [3]
#     .file
#     .functions ...
#     .lines
#       [0]
#       [1]
#       [2]
#       [3]
#         .line_number
#         .function_name
#         .count
#         .unexecuted_block
#         .block_ids
#         .branches
#         .calls
#         .conditions
#           [0]                                           +
#             .count                                      |
#             .covered                                   decision 0
#             .not_covered_true                           |
#             .not_covered_false                          +
#           [1]                                           +
#             .count                                      |
#             .covered                                   decision 1
#             .not_covered_true                           |
#             .not_covered_false                          +
#

# llvm-cov JSON
#
# .data
#   [0]
#     .files
#       [0]
#       [1]
#       [2]
#       [3]
#         .branches
#         .expansions
#         .filename
#         .mcdc_records
#         .segments
#         .summary
#     .functions ...
#     .totals ...
# .type
# .version
#

def get_file_list_from_gcc_json(gcc_json):
    return gcc_json['files']

def get_file_list_from_llvm_json(llvm_json):
    return llvm_json['data'][0]['files']

def get_nth_file_from_gcc_json(gcc_json, n):
    return gcc_json['files'][n]

def get_nth_file_from_llvm_json(llvm_json, n):
    return llvm_json['data'][0]['files'][n]

def get_nth_file_name_from_gcc_json(gcc_json, n) -> str:
    return gcc_json['files'][n]['file']

def get_nth_file_name_from_llvm_json(llvm_json, n) -> str:
    return llvm_json['data'][0]['files'][n]['filename']

def set_nth_file_name_from_gcc_json(gcc_json, n, file_name):
    gcc_json['files'][n]['file'] = file_name

def set_nth_file_name_from_llvm_json(llvm_json, n, file_name):
    llvm_json['data'][0]['files'][n]['filename'] = file_name

def merge_partial_gcc_file_json(gcc_file_json1, gcc_file_json2):
    if not gcc_file_json1:
        return gcc_file_json2
    if not gcc_file_json2:
        return gcc_file_json1

    assert gcc_file_json1['file'] == gcc_file_json2['file']
    output = {}
    output['file'] = gcc_file_json1['file']
    output_line_jsons = []

    def handle_some_crazy_shit(file_name, line_number, existing_json, new_json):
        if (
            file_name == 'coreutils-9.1/lib/gl_openssl.h' and
            # These locations are manually checked that the "branches" and
            # "conditions" fields are empty
            line_number in [ 78, 79, 93, 94, 97, 98, 101, 104, 105, 106 ]
        ):
            # https://sources.debian.org/src/coreutils/9.1-1/lib/sha256.h#L35
            # where the same header is included twice to define two sets of functions...
            # if HAVE_OPENSSL_SHA256
            #  define GL_OPENSSL_NAME 224
            #  include "gl_openssl.h"
            #  define GL_OPENSSL_NAME 256
            #  include "gl_openssl.h"
            # else
            return {
                'line_number': line_number,
                'count': existing_json['count'] + new_json['count'],
                'branches': [],
                'conditions': [],
            }
        else:
            print(existing_json)
            print(new_json)
            assert False, f"Duplicate line number {line_number} in a single JSON file {file_name}"

    lines1 = []
    gcc_line_jsons1 = {}
    for line_json in gcc_file_json1['lines']:
        line_number = int(line_json['line_number'])
        if line_number not in lines1:
            lines1.append(line_number)
            gcc_line_jsons1[line_number] = line_json
        else:
            merged_json = handle_some_crazy_shit(output['file'], line_number, gcc_line_jsons1[line_number], line_json)
            gcc_line_jsons1[line_number] = merged_json

    lines2 = []
    gcc_line_jsons2 = {}
    for line_json in gcc_file_json2['lines']:
        line_number = int(line_json['line_number'])
        if line_number not in lines2:
            lines2.append(line_number)
            gcc_line_jsons2[line_number] = line_json
        else:
            merged_json = handle_some_crazy_shit(output['file'], line_number, gcc_line_jsons2[line_number], line_json)
            gcc_line_jsons2[line_number] = merged_json

    lines_common = list(set(lines1) & set(lines2))
    lines_unique1 = list(set(lines1) - set(lines_common))
    lines_unique2 = list(set(lines2) - set(lines_common))

    def merge_branches(branches1, branches2):
        if not branches1:
            return branches2
        if not branches2:
            return branches1
        # This is not a valid assertion. E.g. in distro-info there are crazy
        # logical expressions with varying number of branches depending on
        # #ifdef's from its includer.
        # assert len(branches1) == len(branches2)

        # LLVM (with our patches) merges branches by treating them as different
        # ones at the same line.
        return branches1 + branches2

    def merge_conditions(conditions1, conditions2):
        if not conditions1:
            return conditions2
        if not conditions2:
            return conditions1
        return conditions1 + conditions2

    for line_number in lines_common:
        line_json = {
            'line_number': line_number,
            'count': gcc_line_jsons1[line_number]['count'] + gcc_line_jsons2[line_number]['count'],
            'branches': merge_branches(gcc_line_jsons1[line_number]['branches'], gcc_line_jsons2[line_number]['branches']),
            'conditions': merge_conditions(gcc_line_jsons1[line_number]['conditions'], gcc_line_jsons2[line_number]['conditions']),
        }
        output_line_jsons.append(line_json)
    for line_number in lines_unique1:
        output_line_jsons.append(gcc_line_jsons1[line_number])
    for line_number in lines_unique2:
        output_line_jsons.append(gcc_line_jsons2[line_number])

    output['lines'] = output_line_jsons

    return output
