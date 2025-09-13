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

serial = False

nproc = 30 # os.cpu_count() or 1

configs: list[tuple[str, str, int]] = [
    ("default", "", 100000),
    ("inline", "--inline-function", 100000),
    ("cpp", "--lang-cpp", 100000),
]

if len(sys.argv) == 3:
    start_seed = int(sys.argv[1])
    end_seed = int(sys.argv[2])
    program_range = range(start_seed, end_seed + 1)
elif len(sys.argv) > 1:
    print(f"Usage: {sys.argv[0]} [start_seed end_seed]", file=sys.stderr)
    sys.exit(1)
else:
    program_range = None

def generate_with_seed(seed, config_name, csmith_options):

    command_parts = ["csmith", "-s", str(seed)]
    if csmith_options:
        command_parts.extend(csmith_options.split())

    output_file_path = f"{config_name}/{seed}.c"

    with open(output_file_path, "w") as f_out:
        result = subprocess.run(command_parts, stdout=f_out)

    if result.returncode == -signal.SIGSEGV:
        return seed
    return None

for config in configs:
    config_name, csmith_options, program_num = config
    os.makedirs(config_name, exist_ok=False)

    seeds = program_range if program_range is not None else range(program_num)

    if serial:
        for seed in seeds:
            print("Generating with seed", seed)
            os.system(f"csmith -s {seed} {csmith_options} > {config_name}/{seed}.c")

    else:
        print(f"Generating {len(seeds)} programs using {nproc} processes for config '{config_name}'...")
        with multiprocessing.Pool(processes=nproc) as pool:
            worker = partial(generate_with_seed, config_name=config_name, csmith_options=csmith_options)
            results = pool.map(worker, seeds)

        segfaulting_seeds = sorted([seed for seed in results if seed is not None])

        if segfaulting_seeds:
            print("\n--- Csmith Segfault Report ---")
            print(f"Found {len(segfaulting_seeds)} seeds that caused segmentation faults:")
            print(", ".join(map(str, segfaulting_seeds)))
        else:
            print("\n--- No csmith segmentation faults detected. ---")
