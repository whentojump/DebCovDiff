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

def find_block_body(lines: List[str], start_index: int) -> tuple[int, int] | None:
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
    Analyzes a file for goto statements that meet any of three conditions:
    1. 'if' on the same line as goto
    2. 'if' on the previous line
    3. '}' right before this goto
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
        
        # Search for 'goto' in this line
        if 'goto' not in line_stripped:
            continue
            
        # Find goto position and check what's before it
        goto_pos = line_stripped.find('goto')
        before_goto = line_stripped[:goto_pos].strip() if goto_pos > 0 else ""
        
        # Check if there's a word right before goto in the same line
        has_word_before_goto = len(before_goto) > 0
        
        condition_met = False
        reason = ""
        
        if has_word_before_goto:
            # Check if word before goto is ';' or '}'
            if before_goto.endswith(';'):
                # Check if there's 'if' in same line or previous line
                if 'if' in line_stripped:
                    condition_met = True
                    reason = "Found 'if' on same line with semicolon before goto"
                elif i > 0 and 'if' in lines[i-1]:
                    condition_met = True
                    reason = "Found 'if' on previous line with semicolon before goto"
            elif before_goto.endswith('}'):
                # Report if there's '}' before goto
                condition_met = True
                reason = "Found '}' right before goto"
        else:
            # No word before goto in same line, check if previous line ends with ';' or '}'
            if i > 0:
                prev_line = lines[i-1].strip()
                if prev_line.endswith(';'):
                    # Check if there's 'if' in same line or previous line
                    if 'if' in line_stripped:
                        condition_met = True
                        reason = "Found 'if' on same line with semicolon on previous line"
                    elif 'if' in lines[i-1]:
                        condition_met = True
                        reason = "Found 'if' on previous line with semicolon on previous line"
                elif prev_line.endswith('}'):
                    # Report if previous line ends with '}'
                    condition_met = True
                    reason = "Found '}' on previous line before goto"
        
        if condition_met:
            found_patterns.append({
                "file": filepath,
                "line": i + 1,
                "code": line_stripped,
                "reason": reason
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
        print("No goto statements meeting the conditions found.")
        sys.exit(0)

    print(f"Found {len(all_findings)} goto statements meeting the conditions.")
    print("This checker looks for goto statements with '}' before goto, or 'if' with semicolon before goto.")
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
    print("This script identifies goto statements that meet any of three simple conditions.")

    sys.exit(1)

if __name__ == "__main__":
    main()
