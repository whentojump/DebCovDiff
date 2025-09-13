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
    Analyzes a single file for multi-line ternary expressions by looking at
    statements ending in a semicolon.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []

    found_patterns = []

    # Strip comments from the entire file content first
    content_no_comments = re.sub(r'//.*|/\*.*?\*/', '', content, flags=re.DOTALL)

    # Heuristically split the content into statements ending with a semicolon.
    # The regex is non-greedy to handle multiple statements correctly.
    statements = re.findall(r'.*?;', content_no_comments, re.DOTALL)

    original_lines = content.splitlines()
    char_offset = 0

    for stmt in statements:
        # Check if the statement is multi-line and contains a ternary operator
        if '?' in stmt and ':' in stmt and '\n' in stmt.strip():
            # Find the position of this statement in the original content to get line numbers
            try:
                stmt_start_pos = content.find(stmt.strip().split('\n')[0], char_offset)
                if stmt_start_pos == -1:
                    continue

                start_line = content.count('\n', 0, stmt_start_pos) + 1
                end_line = content.count('\n', 0, stmt_start_pos + len(stmt)) + 1

                # Ensure we have a valid line range
                if end_line >= start_line:
                    code_snippet = "\n".join(original_lines[start_line-1:end_line])
                    found_patterns.append({
                        "file": filepath,
                        "line": start_line,
                        "code": code_snippet,
                        "reason": "A multi-line ternary expression was found."
                    })

                char_offset = stmt_start_pos + len(stmt)
            except Exception:
                continue # Ignore statements we can't process

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
        print("No multi-line ternary expressions found.")
        sys.exit(0)

    print(f"Found {len(all_findings)} multi-line ternary expressions.")
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
