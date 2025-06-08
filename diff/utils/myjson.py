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
