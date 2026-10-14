# omv-fnos-support 0.1.0

Community dependency package for the tested OMV 8 / Debian 13 / amd64 / BIOS
fnOS Basic combination. Not affiliated with fnOS or OpenMediaVault.

Scope: single-member MD RAID1 metadata 1.2 / llbitmap, ordinary linear LVM,
ext4. No new compatibility or runtime functionality versus the fnos2 rc3
candidate. Multi-disk RAID, recovery, other platforms and Secure Boot are
not validated. Basic has no redundancy. Software rollback cannot undo writes.

Read INSTALL.md and SUPPORT.md before installing dependencies or accessing
data. This entry package has no maintainer scripts. Standard image/mdadm
hooks may regenerate initramfs/GRUB or trigger device discovery. No automatic
disk conversion, OMV apply, sharing, permission changes or reboot is supplied.

Use release checksums and release test evidence for the exact package set.
Preserve a working compatible kernel and data backups. A system-disk backup
is not a backup of the data disks. Do not downgrade existing mdadm 4.6-3.
