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
    Analyzes a file for multi-line logical expressions using a combined heuristic.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    findings = []
    processed_lines = set()

    for i, line in enumerate(lines):
        if i in processed_lines:
            continue

        line_no_comments = re.sub(r'//.*', '', line).strip()

        start_line_idx = -1

        # Heuristic 1: Find a line that ends with a logical operator.
        if line_no_comments.endswith('&&') or line_no_comments.endswith('||'):
            start_line_idx = i

        # Heuristic 2: Find a line that starts with a logical operator.
        elif i > 0 and (line_no_comments.startswith('&&') or line_no_comments.startswith('||')):
            # The expression started on a previous line.
            start_line_idx = i - 1

        if start_line_idx != -1:
            # We found a potential start. Now find the end of the statement for the snippet.
            end_line_idx = i
            for j in range(i, len(lines)):
                if ';' in lines[j] or ')' in re.sub(r'".*?"', '', lines[j]):
                    end_line_idx = j
                    break

            # If no clear end is found, the statement might be a single line after all.
            # This check ensures we only report genuinely multi-line statements.
            if end_line_idx <= start_line_idx:
                continue

            # Ensure we haven't already processed this block
            if start_line_idx in processed_lines:
                continue

            code_snippet = "".join(lines[start_line_idx : end_line_idx+1]).strip()

            findings.append({
                "file": filepath,
                "line": start_line_idx + 1,
                "code": code_snippet,
                "reason": "A logical expression appears to be split across multiple lines."
            })

            # Mark all lines in this snippet as processed to avoid double-counting
            for k in range(start_line_idx, end_line_idx + 1):
                processed_lines.add(k)

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
        print("No potential bug patterns found.")
        sys.exit(0)

    print(f"Found {len(all_findings)} potential instances of the pattern.")
    print("This checker looks for multi-line logical expressions.")
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
