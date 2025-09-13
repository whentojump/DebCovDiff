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
    """Analyzes a single file for infinite loops."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    # Regex to find common infinite loop constructs, allowing for whitespace.
    loop_regex = re.compile(r'\b(while\s*\(\s*(1|true)\s*\)|for\s*\(\s*;\s*;\s*\))')
    found_patterns = []

    for i, line in enumerate(lines):
        for match in loop_regex.finditer(line):
            report = {
                "file": filepath,
                "line": i + 1,
                "loop": match.group(0).strip(),
                "reason": "An infinite loop construct was found.",
            }
            found_patterns.append(report)

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
        print("No infinite loop patterns found.")
        sys.exit(0)

    print(f"Found {len(all_findings)} potential infinite loop instances.")
    print("This checker looks for common infinite loop constructs like 'while(1)', 'while(true)', and 'for(;;)'")
    print("-" * 60)

    for finding in all_findings:
        print(f"File: {finding['file']}:{finding['line']}")
        print(f"  Loop construct: {finding['loop']}")
        print(f"  Reason: {finding['reason']}")
        print("-" * 20)

    print("\nDisclaimer:")
    print("This script provides an approximation and might miss complex cases (e.g., macros).")

    sys.exit(1)

if __name__ == "__main__":
    main()
