import sys
from pathlib import Path
from pygments import highlight
from pygments.lexers import CLexer
from pygments.formatters import TerminalFormatter

def warning_section(logger, msg, divider='='):
    logger.warning("")
    logger.warning(msg)
    dividers = divider * len(msg)
    logger.warning(dividers)
    logger.warning("")

def info_section(logger, msg, divider='='):
    logger.info("")
    logger.info(msg)
    dividers = divider * len(msg)
    logger.info(dividers)
    logger.info("")

def debug_section(logger, msg, divider='='):
    logger.debug("")
    logger.debug(msg)
    dividers = divider * len(msg)
    logger.debug(dividers)
    logger.debug("")

def count_lines(source_dir, file_name) -> int:
    try:
        with open(Path(source_dir)/Path(file_name), 'r') as f:
            total = len(f.readlines())
    except UnicodeDecodeError:
        # In apache2-2.4.62/modules/metadata/mod_version.c:L21 "André Malo"
        with open(Path(source_dir)/Path(file_name), 'r', encoding='cp1252') as f:
            total = len(f.readlines())
    return total

def show_source(logger, source_dir, file_name, line_number, context_lines=8):
    try:
        with open(Path(source_dir) / file_name, 'r') as f:
            lines = f.readlines()

        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)

        logger.warning("")

        green = "\033[42m"
        yellow = "\033[43m"
        reset = "\033[0m"

        for i in range(start, end):
            line = lines[i].rstrip()
            line = highlight(line, CLexer(), TerminalFormatter())
            line = line.rstrip()

            line = line.replace('&&', f"{green}&&{reset}")
            line = line.replace('||', f"{yellow}||{reset}")

            if i+1 == line_number:
                logger.warning(f"{i+1:<4}*|{line}")
            else:
                logger.warning(f"{i+1:<5}|{line}")
        logger.warning("")

    except FileNotFoundError:
        print(f"{Path(source_dir) / file_name} not found.", file=sys.stderr)

    except Exception as e:
        print(f"show_source: {e}", file=sys.stderr)

def project_root_dir_to_project_name(root_dir: str) -> str:
    return root_dir.rsplit('-', 1)[0]

def file_name_to_project_name(file_name: str) -> str:
    root_dir = file_name.split('/')[0]
    return project_root_dir_to_project_name(root_dir)
