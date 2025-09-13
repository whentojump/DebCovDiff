import os
import re
import sys
from typing import List, Dict, Any, Optional, Tuple

def find_source_files(start_path: str) -> List[str]:
    """Finds all C/C++ source files in a directory."""
    source_files = []
    for root, _, files in os.walk(start_path):
        for file in files:
            if file.endswith(('.c', '.cpp', '.cc', '.h', '.hpp', '.cxx', '.hxx')):
                source_files.append(os.path.join(root, file))
    return source_files

def find_block_body(lines: List[str], start_index: int) -> Optional[Tuple[int, int]]:
    """
    Finds the start and end line indices of a block enclosed in {}.
    Returns a tuple of (start_line_of_block, end_line_of_block), or None.
    """
    open_brace_line = -1
    open_brace_col = -1

    # Find the first opening brace on or after the start_index.
    for i in range(start_index, len(lines)):
        pos = lines[i].find('{')
        if pos != -1:
            open_brace_line = i
            open_brace_col = pos
            break

    if open_brace_line == -1:
        return None

    brace_level = 1
    for i in range(open_brace_line, len(lines)):
        line_to_scan = lines[i]
        start_col = open_brace_col + 1 if i == open_brace_line else 0

        for char in line_to_scan[start_col:]:
            if char == '{': brace_level += 1
            elif char == '}': brace_level -= 1

        if brace_level == 0:
            return (open_brace_line, i)

    return None

def analyze_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Analyzes a single file for if statements with variable declarations in the body.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    found_patterns = []

    # Find if statements
    if_regex = re.compile(r'if\s*\(')
    decl_regex = re.compile(r'\b(int|char|long|float|double|struct|enum|union|auto|const)\s+[_a-zA-Z]\w*\s*[=;\[]')

    for i, line in enumerate(lines):
        if not if_regex.search(line):
            continue

        # Found a potential `if`. Now check for variable declaration in the body.
        if_body = find_block_body(lines, i)
        if not if_body:
            continue

        # Check for variable declaration inside the if-body.
        has_var_decl = False
        start_if_body, end_if_body = if_body
        for j in range(start_if_body, end_if_body + 1):
            body_line = lines[j]
            if decl_regex.search(body_line): 
                has_var_decl = True
                break

        if not has_var_decl:
            continue

        # All conditions met - if statement with variable declaration in body.
        found_patterns.append({
            "file": filepath,
            "line": i + 1,
            "code": line.strip(),
            "reason": "if-statement with variable declaration in the body."
        })

    return found_patterns

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path_to_source_code_directory_or_file>", file=sys.stderr)
        print("This script searches for if statements that contain variable declarations in their body.", file=sys.stderr)
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
        print("No if statements with variable declarations in the body found.")
        sys.exit(0)

    print(f"Found {len(all_findings)} if statements with variable declarations in the body.")
    print("These are if statements that contain variable declarations within their block.")
    print("-" * 60)

    for finding in all_findings:
        print(f"File: {finding['file']}:{finding['line']}")
        print(f"  Code: {finding['code']}")
        print(f"  Reason: {finding['reason']}")
        print("-" * 20)

    print("\nNote:")
    print("This script identifies if statements that contain variable declarations in their body.")

    sys.exit(1)

if __name__ == "__main__":
    main()
