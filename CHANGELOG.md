# Changelog

## 0.1.0 — 2026-10-14

- Freeze existing OMV 8 / Debian 13 / amd64 / BIOS Basic + ext4 support.
- Preserve the already tested fnos2 kernel and mdadm binary bytes.
- Package the 0.1.0 entry with installation, rollback and support documentation.
- Record the sample's fnOS version, upstream source, configuration and hashes.
- Complete unused-kernel removal/reinstallation, 15-minute bounded I/O, and one
  disposable-VM abrupt-stop/recovery test.
- No new runtime features or compatibility targets. 0.1.x is bugfix-only.

Prior rc3 fixed missing packaged Debian changelog information. No storage-code
defect requiring a new kernel or mdadm build was found in the additional tests.
