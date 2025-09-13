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
    """Analyzes a file for macros containing 'return' or 'goto'."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    findings = []
    define_regex = re.compile(r'^\s*#\s*define\s+([_a-zA-Z]\w+)(.*)')

    i = 0
    while i < len(lines):
        line = lines[i]
        match = define_regex.match(line)
        if not match:
            i += 1
            continue

        macro_name = match.group(1)
        macro_body_start_line_idx = i

        # Handle multi-line macros by concatenating lines ending with '\'
        original_macro_lines = [line.rstrip()]
        macro_content = match.group(2).strip()

        while macro_content.endswith('\\'):
            macro_content = macro_content[:-1].strip()
            i += 1
            if i >= len(lines): break
            next_line_content = lines[i].rstrip()
            original_macro_lines.append(next_line_content)
            macro_content += " " + next_line_content.strip()

        # Check if the collected body contains the keywords
        if re.search(r'\b(return|goto)\b', macro_content):
            findings.append({
                "file": filepath,
                "line": macro_body_start_line_idx + 1,
                "code": "\n".join(original_macro_lines),
                "reason": f"Macro '{macro_name}' contains a 'return' or 'goto' statement."
            })

        i += 1

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
        print("No macros containing 'return' or 'goto' were found.")
        sys.exit(0)

    print(f"Found {len(all_findings)} macro definitions containing 'return' or 'goto'.")
    print("-" * 60)

    for finding in all_findings:
        print(f"File: {finding['file']}:{finding['line']}")
        print(f"  Macro Definition:\n---\n{finding['code']}\n---")
        print(f"  Reason: {finding['reason']}")
        print("-" * 20)

    print("\nDisclaimer:")
    print("This script provides an approximation based on syntactic patterns and might have false positives.")

    sys.exit(1)

if __name__ == "__main__":
    main()
