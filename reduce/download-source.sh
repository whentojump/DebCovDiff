#!/bin/bash

set -ex

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_DIR=$(realpath $THIS_DIR/../)

OUTPUT_DIR=$REPO_DIR/reduce/source

DEBIAN_ARCHIVE=$(jq -r .debian_archive $REPO_DIR/diff/config.json)

if [[ -d $OUTPUT_DIR ]]; then
    echo "Output directory $OUTPUT_DIR already exists"
    exit 1
fi

mkdir $OUTPUT_DIR

PACKAGE_LIST_FILE=$(mktemp)
cp $REPO_DIR/tables-and-figures/scripts/data/select/selection_7_success.txt $PACKAGE_LIST_FILE

docker run --rm \
           --name debian-source-downloader \
           -v $OUTPUT_DIR:/output \
           -v $PACKAGE_LIST_FILE:/package_list.txt \
           -e DEBIAN_ARCHIVE="$DEBIAN_ARCHIVE" \
           -e HOST_UID=$(id -u) \
           -e HOST_GID=$(id -g) \
           debian:12-slim bash -c '
    set -ex

    apt update && apt install -y wget gnupg apt-utils dpkg-dev

    rm -f /etc/apt/sources.list.d/debian.sources

    echo "deb $DEBIAN_ARCHIVE bookworm main" > /etc/apt/sources.list
    echo "deb-src $DEBIAN_ARCHIVE bookworm main" >> /etc/apt/sources.list

    apt update

    while read -r package; do
        # Create a similar directory structure as an actual build
        mkdir -p /output/$package-gcc-1/
        cd /output/$package-gcc-1/
        apt source $package
    done < /package_list.txt

    chown -R $HOST_UID:$HOST_GID /output
'

rm -f $PACKAGE_LIST_FILE

cat << EOF

===========================================================================

Source download completed. Sources saved to $OUTPUT_DIR

===========================================================================

EOF
