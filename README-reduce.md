# Dataset for Program Reduction and Bug Deduplication

Both proudly and embarrassedly, all inspected inconsistencies in our
[ASE '25 work](https://mir.cs.illinois.edu/marinov/publications/ZhangETAL25DebCovDiff.pdf)
were manually done. We publish the dataset here for future research on
automating this process, particularly

1. How to obtain a standalone, reduced program that retains the same buggy
   symptom from the original large, multi-file, dependent Debian source code?
2. How to cluster bug triggering code (reduced or not) so that each cluster
   ideally represents a distinct bug? How to attribute newly seen bug triggering
   code to known bugs?
3. How are the unique challenges in reducing or deduplicating *coverage tool*
   bugs than general compiler bugs?

## Dataset Overview

The dataset can be found [./reduce/dataset/](./reduce/dataset/) with the
following structure[^1]:

```text
reduce/dataset/
├── ET-inconsistencies
│   ├── line_coverage.csv
│   ├── branch_coverage.csv
│   └── mcdc.csv
├── ET-inspection
│   ├── line_coverage.csv
│   ├── branch_coverage.csv
│   └── mcdc.csv
├── SC-inconsistencies
│   ├── line_coverage.csv
│   ├── branch_coverage.csv
│   └── mcdc.csv
└── SC-inspection
    ├── line_coverage.csv
    ├── branch_coverage.csv
    └── mcdc.csv
```

[^1]: This dataset is derived and cleaned from the version for the ASE '25 paper
      ([./tables-and-figures](./tables-and-figures)), with unified terminologies
      and labels, and slight changes. The conversion is reproduced and documented in
      [this script](./tables-and-figures/scripts/clean-for-reduce.py).

- "Inconsistencies": different coverage reported by Gcov and LLVM-cov

  Columns: `package`, `file name`, `line number`, `inconsistency type`, `gcov report`, `llvm-cov report`

  Examples:

  ```csv
  apache2,apache2-2.4.62/server/mpm_unix.c,901,line_val,4,2
  ```

  ```csv
  grep,grep-3.8/lib/stackvma.c,363,branch_val,"[0, 52, 52, 4038, 4038, 4090]","[0, 52, 52, 3962, 3962, 4014]"
  ```

- "Inspection": manually labeled cause

  Columns: `package`, `file name`, `line number`, `reason type`, `reason`

  Examples:

  ```csv
  bzip2,bzip2-1.0.8/blocksort.c,514,bug,GCC#121901
  ```

  ```csv
  less,less-590/main.c,145,bug,KNOWN BUG LLVM#UCF
  ```

- Small Commands ("SC") and Existing Tests ("ET"): please refer to
  [paper](https://mir.cs.illinois.edu/marinov/publications/ZhangETAL25DebCovDiff.pdf)
  III-C.

## How to Obtain the Full Debian Source Code

Given an entry such as `bzip2,bzip2-1.0.8/blocksort.c,514,bug,GCC#121901`,
how do I find and view this `blocksort.c`?

1. **If you've run sections 1, 2, and 3** in [README.md](./README.md), the
   source code is under `/var/lib/sbuild/build*` directories.
   In this particular example, `/var/lib/sbuild/build-ET/bzip2-gcc-1/bzip2-1.0.8/blocksort.c`.
   Please refer to ["4. Inspect Raw DebCovDiff Results"](./README.md#4-inspect-raw-debcovdiff-results)
   for details.

2. **Alternatively**, you can skip the end-to-end run and directly get the
   source code and source code only.

   ```shell
   git clone https://github.com/xlab-uiuc/DebCovDiff.git
   cd DebCovDiff/reduce
   bash download-source.sh
   ```

   The source code is now in `./source` directory.
   In this particular example, `source/bzip2-gcc-1/bzip2-1.0.8/blocksort.c`.

## How to Obtain Additional Information Such as Full Coverage Reports

For now please run DebCovDiff from end to end. We are working on a fast
path for you, potentially by providing you a tarball of the authors' own
run.
