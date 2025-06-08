#!/bin/bash

set -e

echo "DEB_BUILD_PROFILES $DEB_BUILD_PROFILES"
echo "DEB_BUILD_OPTIONS $DEB_BUILD_OPTIONS"

dpkg-buildpackage --sanitize-env -Pnocheck,nostrip -us -uc -b -rfakeroot
