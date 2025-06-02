# DebCovDiff

## Setup

```shell
wget 'https://github.com/shock-hamburger/ase25/blob/master/diff/scripts/setup.sh?raw=true' -O /tmp/setup.sh
chmod +x /tmp/setup.sh
/tmp/setup.sh
```

As prompted, log out the current shell and log back in again.

## Test with Debian packages

```shell
ALL_METRICS=1 \
LOG_LEVEL=warning \
SHOW_SOURCE=1 \
START_WITH="download_source" \
$DIFF_WORKDIR/ase25/diff/scripts/debian-diff.sh distro-info
```

Options:

- `distro-info`: Debian package name
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
$DIFF_WORKDIR/enhanced-gcov/diff/scripts/debian-batch.sh
$DIFF_WORKDIR/enhanced-gcov/diff/scripts/debian-post-batchrun.sh
```
