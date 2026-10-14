#!/bin/sh
# Native package build only. Does not install software or access disks.
set -eu
test "$#" -eq 2 || { echo 'Usage: build-entry.sh REPO_ROOT NEW_OUTPUT_DIR' >&2; exit 2; }
repo=$(realpath "$1")
out=$(realpath -m "$2")
test ! -e "$out"
test -s "$repo/packaging/control"
mkdir -p "$out/entry-root/DEBIAN" "$out/entry-root/usr/share/doc/omv-fnos-support"
root=$out/entry-root
doc=$root/usr/share/doc/omv-fnos-support
cp "$repo/packaging/control" "$root/DEBIAN/control"
cp "$repo/packaging/README.md" "$doc/README.md"
cp "$repo/docs/INSTALL.md" "$doc/INSTALL.md"
cp "$repo/docs/SUPPORT.md" "$doc/SUPPORT.md"
cp "$repo/LICENSE" "$doc/copyright"
gzip -n -9 -c "$repo/packaging/changelog" > "$doc/changelog.Debian.gz"
(cd "$root" && find usr/share/doc -type f -print0 | LC_ALL=C sort -z | xargs -0 md5sum > DEBIAN/md5sums)
dpkg-deb --root-owner-group --build "$root" "$out/omv-fnos-support_0.1.0_amd64.deb"
dpkg-deb -f "$out/omv-fnos-support_0.1.0_amd64.deb" Package Version Depends
sha256sum "$out/omv-fnos-support_0.1.0_amd64.deb"
