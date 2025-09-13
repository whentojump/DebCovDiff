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
    Analyzes a file for for loops where parentheses are split across multiple lines.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    found_patterns = []

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Check if line starts with "for" and contains parentheses
        if line_stripped.startswith('for ') and '(' in line_stripped:
            # Count opening and closing parentheses in this line
            open_count = line_stripped.count('(')
            close_count = line_stripped.count(')')
            
            # If parentheses don't match (more opens than closes), it's split across lines
            if open_count > close_count:
                found_patterns.append({
                    "file": filepath,
                    "line": i + 1,
                    "code": line_stripped,
                    "reason": "For loop with parentheses split across multiple lines."
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
        print("No for loops with parentheses split across multiple lines found.")
        sys.exit(0)

    print(f"Found {len(all_findings)} for loops with parentheses split across multiple lines.")
    print("This checker looks for for loops where the opening and closing parentheses are on different lines.")
    print("-" * 60)

    unique_findings = []
    seen = set()
    for f in all_findings:
        key = (f['file'], f['line'])
        if key not in seen:
            unique_findings.append(f)
            seen.add(key)

    for finding in unique_findings:
        print(f"File: {finding['file']}:{finding['line']}")
        print(f"  Code: {finding['code']}")
        print(f"  Reason: {finding['reason']}")
        print("-" * 20)

    print("\nNote:")
    print("This script identifies for loops where parentheses span across multiple lines.")

    sys.exit(1)

if __name__ == "__main__":
    main()
