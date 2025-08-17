#!/usr/bin/env python3
#
# Credit: Roscoe A. Bartlett https://github.com/llvm/llvm-project/issues/135239
#
# Convert '<bin1> <bin2> ...' args from STDIN or cmnd-line to '<bin1> -object
# <bin2> ...' to pass into llv-cov commands.
#
import sys

# Get the list of binaries
if len(sys.argv) > 1:
  binariesList = sys.argv[1:]
else:
  binariesList = []
  for line in sys.stdin:
    binariesList.append(line.strip())

# Print the arguments
print(binariesList[0], end=" ")
if len(binariesList) > 1:
  for binary in binariesList[1:]:
    print("-object", end=" ")
    print(binary, end=" ")
