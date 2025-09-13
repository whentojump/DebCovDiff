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
    Analyzes a single file for a multi-line assignment from a dereferenced function call.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    found_patterns = []

    # Regex for a line ending with an assignment from a dereferenced function call.
    # It looks for `*func(...) =` and tolerates whitespace and arguments.
    lhs_regex = re.compile(r"^\s*\*\s*([_a-zA-Z]\w*)\s*\(.*\)\s*=\s*$")

    for i in range(len(lines) - 1):
        line = lines[i]
        next_line = lines[i+1]

        # Check if the line matches the LHS of a multi-line assignment
        if lhs_regex.search(line.strip()):
            # The next line must have some content to be the RHS
            if next_line.strip():
                code_snippet = line.strip() + "\n" + next_line.strip()
                found_patterns.append({
                    "file": filepath,
                    "line": i + 1,
                    "code": code_snippet,
                    "reason": "A multi-line assignment where the LHS is a dereferenced function call."
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
        print("No potential bug patterns found for GCC bug 117415.")
        sys.exit(0)

    print(f"Found {len(all_findings)} potential instances of the pattern described in GCC bug 117415.")
    print("This simplified checker looks for multi-line assignments to a dereferenced function call.")
    print("-" * 60)

    for finding in all_findings:
        print(f"File: {finding['file']}:{finding['line']}")
        print(f"  Code Snippet:\n---\n{finding['code']}\n---")
        print(f"  Reason: {finding['reason']}")
        print("-" * 20)

    print("\nDisclaimer:")
    print("This script provides an approximation based on syntactic patterns and might have false positives.")

    sys.exit(1)

if __name__ == "__main__":
    main()
