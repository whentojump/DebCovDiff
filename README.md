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

## 1. Setup

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

## 2. Test with One Debian Package

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
  <sup>(not [binary package](https://www.debian.org/doc/debian-policy/ch-binary.html))</sup> name
- `LOG_LEVEL=<level>`: one of `error`, `warning`, `info`, `debug`
- `SHOW_SOURCE=1`: show the inconsistent source code snippet
- `ALL_METRICS=1`: warn of inconsistencies for all metrics. Otherwise this is
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
  if available. Otherwise invoke simple commands as specified in
  [`./debian/scripts/chroot/`](./debian/scripts/chroot/).

Back up and clean build directory before moving on to next sections

```shell
cp -r /var/lib/sbuild/build/ /var/lib/sbuild/build-individual-packages
rm -rf /var/lib/sbuild/build/*
```

## 3. Test with All Debian Packages

### Run with Existing Tests (ET) and 9 Debian Packages

```shell
export AUTO_TESTS=1
$REPO_DIR/diff/scripts/debian-batch.sh
```

Back up and clean build directory

```shell
mv $(ls -dt /var/lib/sbuild/build-* | head -2 | tail -1) /var/lib/sbuild/build-ET
rm -rf /var/lib/sbuild/build/*
```

### Run with Simple Commands (SC) and 41 Debian Packages

```shell
export AUTO_TESTS=0
$REPO_DIR/diff/scripts/debian-batch.sh
```

Back up and clean build directory

```shell
mv $(ls -dt /var/lib/sbuild/build-* | head -2 | tail -1) /var/lib/sbuild/build-SC
rm -rf /var/lib/sbuild/build/*
```

## 4. Inspect Raw DebCovDiff Results

The results (with one package or all packages) are generated under
`/var/lib/sbuild/build*` directories:

- `build`: the most recent run, where all actual builds happen
- `build-<date>-<random>`: a copy of `build` after batch run
- `build-{individual-packages,ET,SC}`: renamed to more recognizable names
  in previous sections.

These directories have the following structure:

For each package there are two or four directories

```text
<package>-gcc-1   // build and measure coverage using GCC
<package>-clang-1 // build and measure coverage using Clang/LLVM
                  // (The below two only exist for batch runs)
<package>-log     // various logs
<package>         // historic inconsistencies
```

Take package `grep` for example

(`+` means files created by our tool in addition to a regular Debian package build)

```text
/var/lib/sbuild/build-SC/grep-clang-1/
├── grep-3.8/
│   ├── Makefile, configure, ... // The upstream source code, e.g. by GNU developers
│   ├── debian/                  // Configuration, patches etc by downstream Debian developers
│   ├── dh_auto_test.log         // + Log of running dh_auto_test
│   └── llvm-cov-profraw/        // + *.profraw files generated during test
│
├── llvm-cov-executables.txt // + List of instrumented executables and libraries,
│                            //   which is passed as argument to llvm-cov
├── default.profdata         // + Merged and indexed result of all *.profraw files
├── default.json             // + JSON coverage report
├── default.lcov.txt         // + LCOV coverage report
├── text-coverage-report/    // + Text coverage report organized by source structure
├── text-coverage-report.txt // + Text coverage report concatenated in one file
│
├── // Various Debian build artifacts
├── grep_3.8-5.debian.tar.xz
├── grep_3.8-5.disc
├── grep_3.8-5_amd64.buildinfo
├── grep_3.8-5_amd64.changes
├── grep_3.8-5_amd64.deb
└── ...
```

Due to the tools' nature, coverage related files are found at different places
for GCC.

```text
/var/lib/sbuild/build-SC/grep-gcc-1/
├── grep-3.8/
│   ├── Makefile, configure, ... // The upstream source code, e.g. by GNU developers
│   ├── src/                     // The upstream source code, e.g. by GNU developers
│   │   ├── grep.c               // The upstream source code, e.g. by GNU developers
│   │   ├── grep.o               // Build files
│   │   ├── grep.{gcda,gcno}     // + gcov note and data files that spread across the
│   │   │                        //   whole build directory, usually found next to
│   │   │                        //   the corresponding *.o file
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
├── // Various Debian build artifacts
├── grep_3.8-5.debian.tar.xz
├── grep_3.8-5.disc
├── grep_3.8-5_amd64.buildinfo
├── grep_3.8-5_amd64.changes
├── grep_3.8-5_amd64.deb
└── ...
```

```text
/var/lib/sbuild/build-SC/grep-log/
├── 1.clang_build_log.txt
├── 1.gcc_build_log.txt
├── 1.compared.csv        // Total compared lines, branches and MC/DC decisions
├── 1.inconsistent.csv    // Inconsistent lines, branches and MC/DC decisions
├── 1.diff_log.txt        // Verbose log of inconsistencies
├── ...
├── T.clang_build_log.txt // T means repeated runs
├── T.gcc_build_log.txt
├── T.compared.csv
├── T.inconsistent.csv
└── T.diff_log.txt
```

$T$ is configurable via [`config.json`](./diff/config.json).

## 5. Bug Reproduction

### GCC#120321

Bug report: https://gcc.gnu.org/bugzilla/show_bug.cgi?id=120321

Example occurrence in Debian packages:

- Code location: `/var/lib/sbuild/build-SC/gzip-gcc-1/gzip-1.12/gzip.c:467`
- Coverage report location: `/var/lib/sbuild/build-SC/gzip-gcc-1/gzip-1.12/builddir/gzip.c.gcov:507`

    ```c
           10:  464:    z_suffix = Z_SUFFIX;
           10:  465:    z_len = strlen(z_suffix);
            -:  466:
            6:  467:    while (true) {
            -:  468:        int optc;
           16:  469:        int longind = -1;
            -:  470:
           16:  471:        if (env_argv)
    ```

### LLVM#131505 (Listing 1)

Bug report: https://github.com/llvm/llvm-project/issues/131505

Example occurrence in Debian packages:

- Code location: `/var/lib/sbuild/build-SC/hostname-clang-1/hostname-3.23+nmu1/hostname.c:312`
- Coverage report location: `/var/lib/sbuild/build-SC/hostname-clang-1/text-coverage-report/coverage/build/hostname-clang-1/hostname-3.23+nmu1/hostname.c.txt:611`

    ```c
      311|                   0|					sin6 = (struct sockaddr_in6 *)ifap->ifa_addr;
      312|                   0|					if (IN6_IS_ADDR_LINKLOCAL(&sin6->sin6_addr) ||
      -------------------------------
      |  Branch (312:10): [True: 0, False: 0]
      -------------------------------
      313|                   0|							IN6_IS_ADDR_MC_LINKLOCAL(&sin6->sin6_addr))
      -------------------------------
      |  Branch (313:8): [True: 18446744073709551615, False: 1]
      -------------------------------
      |---> MC/DC Decision Region (312:10) to (313:32)
      |
      |  Number of Conditions: 2
      |     Condition C1 --> (312:10)
      |     Condition C2 --> (313:8)
      |
      |  Executed MC/DC Test Vectors:
      |
      |     None.
      |
      |  C1-Pair: not covered
      |  C2-Pair: not covered
      |  MC/DC Coverage for Decision: 0.00%
      |
      -------------------------------
      314|                   0|						continue;
      315|                   0|				}
    ```

    (We [patched LLVM](https://github.com/xlab-uiuc/llvm-project-DebCovDiff/commit/201222abab7d4d1eed1125520699d8bcce8d18a2)
    in our experiments for debugging purposes, so that it expands "18.4E" into full digits)

### More bugs WIP...

## 6. Csmith Experiments

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

## 7. Bug Age Study

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

## 8. Generate Figure 4, 7, and 8 and Table 1, 2, and 3

```shell
cd $REPO_DIR/tables-and-figures/scripts
python run.py
```
