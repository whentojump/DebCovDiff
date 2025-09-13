import os
import sys
import subprocess
from multiprocessing import Pool, cpu_count
from typing import List, Tuple
import argparse

# Configuration
BUG_IDS = [
    "gcc120321", "gcc117412", "gcc120478", "gcc120482", "gcc120490",
    "gcc117415", "gcc120348", "gcc120484", "gcc120489", "gcc120491",
    "gcc120492", "gcc120486", "gcc120319", "gcc120332", "llvm140427",
    "llvm114622", "llvm116884", "llvm105341"
]

def get_csmith_programs(directory: str) -> List[str]:
    """Get a list of all program files in the specified directory."""
    if not os.path.isdir(directory):
        print(f"Error: Csmith programs directory '{directory}' not found.")
        sys.exit(1)
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def run_checker_on_program(bug_id: str, program_path: str) -> bool:
    """
    Runs a single checker on a single program and returns True if it triggers (exit code 1).
    """
    checker_script = os.path.join("checkers", f"{bug_id}.py")
    if not os.path.isfile(checker_script):
        return False # Checker not found

    try:
        # We redirect stdout and stderr to DEVNULL to keep the output clean,
        # as we only care about the exit code.
        result = subprocess.run(
            ["python3", checker_script, program_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        return result.returncode == 1
    except Exception:
        return False

def check_bug_id(bug_id: str, programs: List[str]) -> Tuple[str, int, int]:
    """
    Checks all Csmith programs for a single bug ID and returns the results.
    """
    total = len(programs)
    positive = 0
    print(f"Starting checks for {bug_id}...")

    for program in programs:
        if run_checker_on_program(bug_id, program):
            print(f"  -> {program} may trigger {bug_id}")
            positive += 1

    print(f"Finished checks for {bug_id}.")
    return (bug_id, positive, total)

def main():
    """
    Main function to orchestrate the parallel checking.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--csmith-programs-dir", type=str, default='inline')
    args = parser.parse_args()

    csmith_programs_dir = args.csmith_programs_dir

    csmith_programs = get_csmith_programs(csmith_programs_dir)
    if not csmith_programs:
        print(f"No programs found in '{csmith_programs_dir}'. Exiting.")
        sys.exit(0)

    # Use a pool of workers to run checks in parallel.
    # The number of workers will be the number of CPU cores available.
    num_workers = cpu_count()
    print(f"Running checks in parallel with {num_workers} workers...")

    # Prepare arguments for the pool
    pool_args = [(bug_id, csmith_programs) for bug_id in BUG_IDS]

    with Pool(processes=num_workers) as pool:
        # Use starmap to pass multiple arguments to the worker function
        results = pool.starmap(check_bug_id, pool_args)

    print("\n--- Summary ---")
    for bug_id, positive, total in sorted(results):
        print(f"{bug_id}: {positive}/{total}")

    try:
        script_version = subprocess.check_output(
            ["git", "log", "--pretty=format:%h \"%s\"", "-n", "1"],
            cwd=os.path.dirname(__file__) or ".",
            text=True
        ).strip()
        print(f"\nScript version: {script_version}")
    except Exception as e:
        print(f"\nCould not get script version: {e}")

if __name__ == "__main__":
    main()
