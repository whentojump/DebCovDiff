import os
import re
import sys
from typing import List, Dict, Any, Optional

def find_source_files(start_path: str) -> List[str]:
    """Finds all C/C++ source files in a directory."""
    source_files = []
    for root, _, files in os.walk(start_path):
        for file in files:
            if file.endswith(('.c', '.cpp', '.cc', '.h', '.hpp', '.cxx', '.hxx')):
                source_files.append(os.path.join(root, file))
    return source_files

def get_for_loop_parts(line: str) -> Optional[List[str]]:
    """
    Extracts the initializer, predicate, and increment parts from a for-loop statement.
    This is a heuristic and doesn't handle complex, multi-line loop headers.
    """
    match = re.search(r'for\s*\((.*)\)', line)
    if not match:
        return None

    content = match.group(1)
    parts = content.split(';')

    # A valid for-loop header should have exactly two semicolons.
    if len(parts) == 3:
        return [p.strip() for p in parts]

    return None

def analyze_file(filepath: str) -> List[Dict[str, Any]]:
    """Analyzes a file for patterns related to LLVM issue #116884."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    findings = []

    for i, line in enumerate(lines):
        if 'for' not in line:
            continue

        loop_parts = get_for_loop_parts(line)
        if not loop_parts:
            continue

        predicate = loop_parts[1]

        # Check for the two trigger conditions
        is_empty = predicate == ""
        # Use regex to robustly check for 'true', allowing for it to be a macro
        is_true = re.fullmatch(r'true', predicate)

        if is_empty or is_true:
            reason = "for-loop with an empty predicate."
            if is_true:
                reason = "for-loop with 'true' as the predicate."

            findings.append({
                "file": filepath,
                "line": i + 1,
                "code": line.strip(),
                "reason": reason
            })

    return findings

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
        print("No potential bug patterns found for LLVM issue #116884.")
        sys.exit(0)

    print(f"Found {len(all_findings)} potential instances of the pattern described in LLVM issue #116884.")
    print("These are for-loops with empty or 'true' predicates that can cause incorrect gcov counts.")
    print("-" * 60)

    for finding in all_findings:
        print(f"File: {finding['file']}:{finding['line']}")
        print(f"  Code: {finding['code']}")
        print(f"  Reason: {finding['reason']}")
        print("-" * 20)

    print("\nDisclaimer:")
    print("This script provides an approximation based on syntactic patterns and might have false positives.")

    sys.exit(1)

if __name__ == "__main__":
    main()
