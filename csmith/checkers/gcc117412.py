import os
import re
import sys
from typing import List, Dict, Any

def find_source_files(start_path: str) -> List[str]:
    """Finds all C/C++ source files in a directory."""
    source_files = []
    for root, _, files in os.walk(start_path):
        for file in files:
            if file.endswith(('.c', '.cpp', '.cc', '.h', '.hpp', '.cxx', '.hxx')):
                source_files.append(os.path.join(root, file))
    return source_files

def analyze_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Analyzes a single file for patterns matching GCC bug 117412.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    # Regex for a "complex" lvalue (pointer, array, member access)
    lhs_pattern = r"(\*\s*\w+|\w+\s*\[[^\]]*\]|\w+\s*\.\s*\w+|\w+\s*->\s*\w+)"
    # Regex for the start of a function call assignment (allowing expressions after the opening parenthesis)
    start_regex = re.compile(rf"^\s*{lhs_pattern}\s*=\s*\w+\s*\([^)]*$")
    # Regex for operators in the arguments on the next line
    operator_regex = re.compile(r"[\+\-\*\/%&\|\^]|<<|>>")

    found_patterns = []

    for i in range(len(lines) - 1):
        line = lines[i].strip()
        next_line = lines[i+1].strip()

        # Check for the key syntactic triggers from the bug report:
        # 1. An assignment to a complex lvalue with an opening function call.
        # 2. The function call is not closed on the same line.
        # 3. The next line contains an operator, indicating a complex argument.
        if start_regex.search(line) and line.count('(') > line.count(')') and operator_regex.search(next_line):
            found_patterns.append({
                "file": filepath,
                "line": i + 1,
                "code": lines[i].strip() + "\n" + lines[i+1].strip()
            })

    return found_patterns

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path_to_source_code_directory_or_file>", file=sys.stderr)
        sys.exit(2)

    source_path = sys.argv[1]
    files_to_scan = []
    if os.path.isdir(source_path):
        files_to_scan = find_source_files(source_path)
    elif os.path.isfile(source_path):
        files_to_scan.append(source_path)
    else:
        print(f"Error: '{source_path}' is not a valid file or directory.", file=sys.stderr)
        sys.exit(2)

    all_findings = []
    for f in files_to_scan:
        findings = analyze_file(f)
        if findings:
            all_findings.extend(findings)

    if not all_findings:
        print("No potential bug patterns found for GCC bug 117412.")
        sys.exit(0)

    print(f"Found {len(all_findings)} potential instances of the pattern described in GCC bug 117412.")
    print("These are multi-line assignments with function calls where gcov might report bogus execution counts.")
    print("-" * 60)

    for finding in all_findings:
        print(f"File: {finding['file']}:{finding['line']}")
        print(f"  Code Snippet:\n---\n{finding['code']}\n---")

    print("\nDisclaimer:")
    print("This script provides an approximation based on syntactic patterns and might have false positives.")
    print("It does not check for type differences between function arguments and parameters, which is another condition for the bug.")

    sys.exit(1)

if __name__ == "__main__":
    main()
