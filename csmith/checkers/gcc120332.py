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

def is_in_comment(line: str, in_multiline_comment: bool) -> tuple[bool, bool]:
    """
    Determines if a line is in a comment and updates multiline comment state.
    Returns: (is_in_comment, new_in_multiline_comment_state)
    """
    if in_multiline_comment:
        # Check if multiline comment ends on this line
        if '*/' in line:
            # Find the position of */ to see if there's code after it
            end_pos = line.find('*/')
            remaining = line[end_pos + 2:].strip()
            # If there's non-comment content after */, we're no longer in comment
            if remaining and not remaining.startswith('//'):
                return False, False
            return True, False
        return True, True
    
    # Check for single-line comment
    if '//' in line:
        comment_pos = line.find('//')
        # Check if there's a label before the comment
        before_comment = line[:comment_pos].strip()
        if before_comment and before_comment.endswith(':'):
            return False, False
        return True, False
    
    # Check for start of multiline comment
    if '/*' in line:
        start_pos = line.find('/*')
        # Check if there's a label before the comment starts
        before_comment = line[:start_pos].strip()
        if before_comment and before_comment.endswith(':'):
            return False, False
        
        # Check if multiline comment ends on same line
        if '*/' in line[start_pos:]:
            return True, False
        return True, True
    
    return False, False

def analyze_file(filepath: str) -> List[Dict[str, Any]]:
    """Analyzes a file for goto labels or case/default arms."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    findings = []

    label_regex = re.compile(r'^\s*([_a-zA-Z]\w*)\s*:')

    in_multiline_comment = False
    for i, line in enumerate(lines):
        # Check if this line is in a comment
        is_comment, in_multiline_comment = is_in_comment(line, in_multiline_comment)
        
        # Only check for labels if not in a comment
        if not is_comment and label_regex.search(line):
            findings.append({
                "file": filepath,
                "line": i + 1,
                "code": line.strip(),
                "reason": "A label or case or default arm was found."
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

    unique_findings = []
    seen = set()
    for f in all_findings:
        key = (f['file'], f['line'])
        if key not in seen:
            unique_findings.append(f)
            seen.add(key)

    if not unique_findings:
        print("No labels or case/default arms found.")
        sys.exit(0)

    print(f"Found {len(unique_findings)} potential instances of labels or cases or default arms.")
    print("This checker looks for goto labels and case/default arms in switch statements.")
    print("-" * 60)

    for finding in unique_findings:
        print(f"File: {finding['file']}:{finding['line']}")
        print(f"  Code: {finding['code']}")
        print(f"  Reason: {finding['reason']}")
        print("-" * 20)

    print("\nDisclaimer:")
    print("This script provides an approximation based on syntactic patterns and might have false positives.")

    sys.exit(1)

if __name__ == "__main__":
    main()
