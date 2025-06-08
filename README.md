# DebCovDiff

The experiments are mainly run on a CloudLab c6420 physical server (amd64, see
detailed specs in [CloudLab documentation](https://docs.cloudlab.us/hardware.html)),
with an Ubuntu 22.04 image.

Other Debian-based distributions and virtual machines should also work but less
tested.
Containers, other Linux distributions or operating systems or other architectures
are never guaranteed to work.

Caution: `sudo` are used in setup and test scripts. It is recommended to use
one-off machines like CloudLab or virtual machines.

## Setup

```shell
wget 'https://github.com/shock-hamburger/ase25/blob/main/diff/scripts/setup.sh?raw=true' -O- | bash
```

As prompted, log out the current shell and log back in again, to make sure
you are correctly in `sbuild` group.

## Test with Debian packages

```shell
ALL_METRICS=1 \
LOG_LEVEL=warning \
SHOW_SOURCE=1 \
START_WITH="download_source" \
$DIFF_WORKDIR/ase25/diff/scripts/debian-diff.sh grep
```

Options:

- `grep`: Debian package name
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

Run all packages

```shell
$DIFF_WORKDIR/ase25/diff/scripts/debian-batch.sh
$DIFF_WORKDIR/ase25/diff/scripts/debian-post-batchrun.sh
```

## Generate figures and tables in the paper

```shell
cd $DIFF_WORKDIR/ase25/tables-and-figures/scripts
python run.py
```
