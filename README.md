# DebCovDiff

The experiments are mainly run on a CloudLab c6420 physical server (amd64, see
detailed specs in [CloudLab documentation](https://docs.cloudlab.us/hardware.html)),
with an Ubuntu 22.04 image.

Other Debian-based distributions and virtual machines should also work but less
tested.
Containers, other Linux distributions or operating systems or other architectures
are never guaranteed to work.

> [!WARNING]
> `sudo` is used in setup and test scripts. It is recommended to use
> one-off machines like CloudLab or virtual machines.

## Setup

```shell
wget 'https://github.com/xlab-uiuc/DebCovDiff/blob/main/diff/scripts/setup.sh?raw=true' -O- | bash
```

As prompted, log out the current shell and log back in again, to make sure
you are correctly in `sbuild` group (check via `id -nG | grep sbuild`).

[This script](./diff/scripts/setup.sh) notably does the following:

1. Build GCC (`c1fb78fb` + [changes](https://github.com/xlab-uiuc/gcc-DebCovDiff/compare/base...xlab-uiuc:gcc-DebCovDiff:DebCovDiff))
   and LLVM (`ce9a2c65` + [changes](https://github.com/xlab-uiuc/llvm-project-DebCovDiff/compare/base...xlab-uiuc:llvm-project-DebCovDiff:DebCovDiff))
2. Run [`sbuild-createchroot`](https://manpages.debian.org/bookworm/sbuild/sbuild-createchroot.8.en.html)
   for each toolchain which (1) sets up an isolated `chroot` and (2) runs
   [`debootstrap`](https://manpages.debian.org/bookworm/debootstrap/debootstrap.8.en.html)
   in it. This step creates the environment for general Debian package build.

   For reproducibility, all Debian binaries and source files are [pinned](./diff/config.json)
   to snapshots in December 2024 (Debian 12.8) via `https://snapshot.debian.org/`
   instead of the regular `http://deb.debian.org/debian`.

3. Copy custom toolchains (step 1) into the `chroot`s and rewire GCC invocations
   to the desired toolchain with appropriate flags, via hook scripts embedded in
   [`configure-all-chroot.sh`](debian/scripts/configure-all-chroot.sh).

## Test with Debian packages

```shell
AUTO_TESTS=1 \
ALL_METRICS=1 \
LOG_LEVEL=warning \
SHOW_SOURCE=1 \
START_WITH="download_source" \
$REPO_DIR/diff/scripts/debian-diff.sh procps
```

Options:

- `procps`: Debian [source package](https://www.debian.org/doc/debian-policy/ch-source.html)
  <sup>not [binary package](https://www.debian.org/doc/debian-policy/ch-binary.html)</sup> name
- `LOG_LEVEL=<level>`: one of `error`, `warning`, `info`, `debug`
- `SHOW_SOURCE=1`: show problematic source code snippet
- `ALL_METRICS=1`: warn of inconsistency for all metrics. Otherwise this is
  configurable in [`inconsistency.py`](./diff/oracles/inconsistency.py).
- `START_WITH=<mode>`
    - `"download_source"`: run everything (starting with pulling the source from
      Debian) at a new directory `/var/lib/sbuild/build/<package>-<toolchain>-<new_id>`
    - `"test"`: if the package has been run before, skip downloading the source
      and build, but directly run tests, generate coverage reports and perform
      differential testing. Everything happens in the old directory
      `/var/lib/sbuild/build/<package>-<toolchain>-<old_id>`
    - `"diff"`: if the package has been run before, skip everything but the
      final differential testing step, based on the existing coverage reports
      under `/var/lib/sbuild/build/<package>-<toolchain>-<old_id>`
- `AUTO_TESTS=1`: measure coverage of
  [`dh_auto_test`](https://manpages.debian.org/bookworm/debhelper/dh_auto_test.1.en.html)
  if available. Otherwise invoke simple commands as specified in [`./debian/scripts/chroot/`](./debian/scripts/chroot/).

Run all packages

```shell
# Optionally: export AUTO_TESTS=1
$REPO_DIR/diff/scripts/debian-batch.sh
```

The results are generated under `/var/lib/sbuild/build` with the following structure:

For each package there are four directories

```text
<package>-gcc-1   // build and measure coverage using GCC
<package>-clang-1 // build and measure coverage using Clang/LLVM
<package>-log     // various logs
<package>         // historic inconsistencies
```

Take package `grep` for example

(`+` means stuffs created by our tool in addition to a regular Debian package build)

```text
grep-clang-1
├── grep-3.8/
│   ├── Makefile, configure, ... // The upstream source code, e.g. by GNU developers
│   ├── debian/                  // Configuration, patches etc by downstream Debian developers
│   ├── dh_auto_test.log         // + Log of running dh_auto_test
│   └── llvm-cov-profraw/        // + *.profraw files generated during test
│
├── // Various Debian build artifacts
├── grep_3.8-5.debian.tar.xz
├── grep_3.8-5.disc
├── grep_3.8-5_amd64.buildinfo
├── grep_3.8-5_amd64.changes
├── grep_3.8-5_amd64.deb
├── ...
│
├── llvm-cov-executables.txt // + List of instrumented executables and libraries,
│                            //   which is passed as argument to llvm-cov
├── default.profdata         // + Merged and indexed result of all *.profraw files
├── default.json             // + JSON coverage report
├── default.lcov.txt         // + LCOV coverage report
├── text-coverage-report/    // + Text coverage report organized by source structure
└── text-coverage-report.txt // + Text coverage report concatenated in one file
```

Due to the tools' nature, coverage related files are found at different places
for GCC.

```text
grep-gcc-1
├── grep-3.8/
│   ├── Makefile, configure, ... // The upstream source code, e.g. by GNU developers
│   ├── src/                     // The upstream source code, e.g. by GNU developers
│   │   ├── grep.c               // The upstream source code, e.g. by GNU developers
│   │   ├── grep.o               // Build files
│   │   ├── grep.{gcda,gcno}     // + gcov note and data file that spread across the
│   │   │                        //   whole build directory, usually found next to
│   │   │                        //   the corresponding .o file
│   │   ├── lib/                                 // The upstream source code, e.g. by GNU developers
│   │   │   ├── fcntl.c                          // The upstream source code, e.g. by GNU developers
│   │   │   ├── libgreputils_a-fcntl.o           // Build files
│   │   │   └── libgreputils_a-fcntl.{gcda,gcno} // + Another example of gcov note and data files
│   │   └── ...
│   ├── debian/                  // Configuration, patches etc by downstream Debian developers
│   ├── dh_auto_test.log         // + Log of running dh_auto_test
│   │
│   ├── grep.c.gcov              // + Text coverage report
│   ├── grep.c.gcov.json         // + JSON coverage report
│   │
│   ├── fcntl.c.gcov                    // + Another example of coverage reports.
│   ├── libgreputils_a-fcntl.gcov.json  //   Note they are no longer reflecting
│   │                                   //   the source structure
│   └── ...
│
├── // Various Debian build artifacts, not important for our purposes
├── grep_3.8-5.debian.tar.xz
├── grep_3.8-5.disc
├── grep_3.8-5_amd64.buildinfo
├── grep_3.8-5_amd64.changes
├── grep_3.8-5_amd64.deb
└── ...
```

```text
grep-log/
├── 1.clang_build_log.txt
├── 1.gcc_build_log.txt
├── 1.compared.csv        // Total compared lines, branches and MC/DC decisions
├── 1.inconsistent.csv    // Inconsistent lines, branches and MC/DC decisions
├── 1.diff_log.txt        // Verbose log of inconsistencies
├── ...
├── T.clang_build_log.txt // T means repeated runs. Let's focus on the last one
├── T.gcc_build_log.txt
├── T.compared.csv
├── T.inconsistent.csv
└── T.diff_log.txt
```

## Csmith experiments

```shell
pushd /tmp/
git clone https://github.com/csmith-project/csmith.git
cd csmith
git checkout 0ec6f1bad2df865beadf13c6e97ec6505887b0a5
cmake -D CMAKE_C_COMPILER=/usr/bin/gcc -D CMAKE_CXX_COMPILER=/usr/bin/g++ .
make -j10
sudo make -j10 install
popd
```

```shell
cd $REPO_DIR/csmith

python gen.py

python run-csmith-parallel.py --csmith-programs-dir default |& tee default.log
python run-csmith-parallel.py --csmith-programs-dir inline |& tee inline.log
python run-csmith-parallel.py --csmith-programs-dir cpp |& tee cpp.log
```

## Bug age study

```shell
cd $REPO_DIR/bug-ages
docker build -t old-compilers-env .
docker run -it --rm -v $PWD:/usr/src/app old-compilers-env
```

Inside the container

```shell
bash bugs/setup-links.sh
gcc --version
clang --version
```

```shell
bash bugs/run.sh |& tee log.txt
grep 'NOT REPRODUCING' log.txt
grep ' OK' log.txt
```

## Generate Figure 4, 7, and 8 and Table 1, 2, and 3

```shell
cd $REPO_DIR/tables-and-figures/scripts
python run.py
```
