# Statistics: (Intel Core i9-14900K)
# Serial, default, 1000x: 11min22s
# Parallel (nproc=10/32), default, 1000x: 1min24s

# (CloudLab c6320)
# Serial, default, 1000x, 46min08s
# Parallel (nproc=20/56), default, 1000x: 2min50s
# Parallel (nproc=40/56), default, 1000x: 2min20s
# Parallel (nproc=50/56), default, 1000x: 2min32s

# (CloudLab c6525-25g)
# Serial, default, 1000x, 28min50s
# Parallel (nproc=30/32), default, 1000x: 1min56s
# Parallel (nproc=30/32), default, 100000x: 2h16min

import os
import multiprocessing
from functools import partial
import signal
import subprocess
import sys
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--nproc", type=int, default=10)
argparser.add_argument("--first-1k", action="store_true")
argparser.add_argument("--start-seed", type=int)
argparser.add_argument("--end-seed", type=int)

args = argparser.parse_args()

nproc = args.nproc

if args.first_1k and (args.start_seed is not None or args.end_seed is not None):
    print("Error: --first-1k cannot be used with --start-seed or --end-seed")
    sys.exit(1)

if args.start_seed is not None and args.end_seed is None:
    print("Error: --end-seed is required when --start-seed is provided")
    sys.exit(1)
elif args.start_seed is None and args.end_seed is not None:
    print("Error: --start-seed is required when --end-seed is provided")
    sys.exit(1)

if args.start_seed is not None and args.end_seed is not None:
    dir_suffix = f"{args.start_seed}-{args.end_seed}"
    program_range = range(args.start_seed, args.end_seed + 1)
else:
    dir_suffix = "1k" if args.first_1k else "100k"
    program_range = range(1_000) if args.first_1k else range(100_000)

def generate_with_seed(seed, dir_name, csmith_options):

    command_parts = ["csmith", "-s", str(seed)]
    if csmith_options:
        command_parts.extend(csmith_options.split())

    output_file_path = f"{dir_name}/{seed}.c"

    with open(output_file_path, "w") as f_out:
        result = subprocess.run(command_parts, stdout=f_out)

    if result.returncode == -signal.SIGSEGV:
        return seed
    return None

for csmith_options in [ "", "--inline-function", "--lang-cpp" ]:

    match csmith_options:
        case "":
            dir_name = "default"
        case "--inline-function":
            dir_name = "inline"
        case "--lang-cpp":
            dir_name = "cpp"

    dir_name += f"-{dir_suffix}"

    os.makedirs(dir_name, exist_ok=False)

    if nproc == 1:
        results = []
        for seed in program_range:
            print("Generating with seed", seed)
            results.append(generate_with_seed(seed, dir_name, csmith_options))

    else:
        print(f"Generating {len(program_range)} programs using {nproc} processes for config '{dir_name}'...")
        with multiprocessing.Pool(processes=nproc) as pool:
            worker = partial(generate_with_seed, dir_name=dir_name, csmith_options=csmith_options)
            results = pool.map(worker, program_range)

    segfaulting_seeds = sorted([seed for seed in results if seed is not None])

    if segfaulting_seeds:
        print("\n--- Csmith Segfault Report ---")
        print(f"Found {len(segfaulting_seeds)} seeds that caused segmentation faults:")
        print(", ".join(map(str, segfaulting_seeds)))
    else:
        print("\n--- No csmith segmentation faults detected. ---")
