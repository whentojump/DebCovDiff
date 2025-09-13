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
    Analyzes a file for a narrow set of keywords that suggest multithreading.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    # A narrow set of keywords related to threading.
    # Using word boundaries for most to avoid matching substrings in other words,
    # but 'condition_' and 'pthread' are treated as root strings.
    threading_keywords_regex = re.compile(
        r'pthread|'                  # For pthread_*
        r'condition_|'               # For condition_variable or pthread_cond_
        r'\b(thread|mutex|atomic|future|async)\b' # For std::thread, std::mutex, etc.
    )

    found_patterns = []

    for i, line in enumerate(lines):
        match = threading_keywords_regex.search(line)
        if match:
            found_patterns.append({
                "file": filepath,
                "line": i + 1,
                "code": line.strip(),
                "reason": f"Found potential multithreading keyword: '{match.group(0)}'."
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
        print("No potential multithreading keywords found.")
        sys.exit(0)

    print(f"Found {len(all_findings)} potential instances of multithreading keywords.")
    print("This checker performs a narrow search for specific keywords that may indicate a multithreaded program.")
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

    print("\nDisclaimer:")
    print("This script provides a broad approximation and the presence of a keyword does not guarantee multithreading.")

    sys.exit(1)

if __name__ == "__main__":
    main()
