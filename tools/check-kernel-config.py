#!/usr/bin/env python3
"""Read-only config gate, not a disk/boot/package safety certification."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


REQUIRED = """
BLK_DEV_MD MD_RAID1 BLK_DEV_DM EXT4_FS EXT4_FS_POSIX_ACL EXT4_FS_SECURITY
QUOTA QFMT_V2 QUOTA_TREE NFSD NFSD_V4 NFS_FS NFS_V3 NFS_V4
SUNRPC RPCSEC_GSS_KRB5 NETFILTER NF_TABLES NF_CONNTRACK
DEBUG_INFO_BTF DEBUG_INFO_BTF_MODULES BPF_SYSCALL
SCSI_VIRTIO BLK_DEV_SD VIRTIO_PCI VIRTIO_BLK VIRTIO_NET VIRTIO_CONSOLE
DEVTMPFS MODULES BLK_DEV_INITRD SECURITY_APPARMOR MODULE_SIG
""".split()


def parse_config(text):
    result = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        match = re.fullmatch(r"CONFIG_([A-Za-z0-9_]+)=(.+)", line)
        unset = re.fullmatch(r"# CONFIG_([A-Za-z0-9_]+) is not set", line)
        if match:
            key, value = match.groups()
        elif unset:
            key, value = unset.group(1), "n"
        elif line.startswith("#"):
            continue
        else:
            raise ValueError(f"malformed config line {number}")
        if key in result:
            raise ValueError(f"duplicate CONFIG_{key} at line {number}")
        result[key] = value
    if not result:
        raise ValueError("empty config")
    return result


def compare(base, candidate, localversion):
    errors = []
    for key in REQUIRED:
        if candidate.get(key) not in ("y", "m"):
            errors.append(f"required CONFIG_{key} is not enabled")
    expected = {
        "MD_LLBITMAP": "y",
        "MD_BITMAP": "y",
        "LOCALVERSION": json.dumps(localversion),
        "LOCALVERSION_AUTO": "n",
    }
    for key, value in expected.items():
        if candidate.get(key) != value:
            errors.append(f"CONFIG_{key} must equal {value}")

    # Fail closed on every unreviewed delta, including security strings and
    # dependencies introduced by olddefconfig. Do not hide m/y transitions.
    permitted = {"MD_LLBITMAP", "LOCALVERSION"}
    # Debian's shipped config omits these packaging/signing inputs. The local
    # BIOS test build adds its own signing identity, not Debian's private key.
    # Only absent -> exact reviewed value is accepted; existing values cannot
    # be cleared/changed by this exception. Never ship the generated PEM key.
    additions = {
        "BUILD_SALT": json.dumps("7.2.6" + localversion),
        "MODULE_SIG_ALL": "y",
        "MODULE_SIG_KEY": '"certs/signing_key.pem"',
        "SYSTEM_TRUSTED_KEYS": '""',
    }
    delta = []
    for key in sorted(base.keys() | candidate.keys()):
        before, after = base.get(key), candidate.get(key)
        if before != after:
            delta.append({"symbol": key, "before": before, "after": after})
            reviewed_addition = before is None and key in additions and after == additions[key]
            if key not in permitted and not reviewed_addition:
                errors.append(f"unreviewed CONFIG_{key}: {before!r} -> {after!r}")
    return delta, errors


def inspect(baseline, candidate, plan):
    base = parse_config(baseline.decode("utf-8"))
    new = parse_config(candidate.decode("utf-8"))
    delta, errors = compare(base, new, plan["candidate_localversion"])
    base_hash = hashlib.sha256(baseline).hexdigest()
    if base_hash != plan["baseline_config_sha256"]:
        errors.insert(0, "baseline SHA256 does not match the pinned official config")
    return {
        "baseline_sha256": base_hash,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "baseline_y": list(base.values()).count("y"),
        "baseline_m": list(base.values()).count("m"),
        "candidate_y": list(new.values()).count("y"),
        "candidate_m": list(new.values()).count("m"),
        "delta": delta,
        "errors": errors,
        "configuration_gate_passed": not errors,
        "scope": "Config only; no proof of source features, module build, boot, disk integrity or runtime safety.",
    }


def self_test():
    base = {key: "m" for key in REQUIRED}
    base.update(MD_BITMAP="y", MD_LLBITMAP="n", LOCALVERSION='""', LOCALVERSION_AUTO="n")
    candidate = dict(base, MD_LLBITMAP="y", LOCALVERSION='"-fnos1-amd64"')
    assert not compare(base, candidate, "-fnos1-amd64")[1]
    for key in ("NFSD", "DEBUG_INFO_BTF", "QFMT_V2", "NF_TABLES"):
        broken = dict(candidate, **{key: "n"})
        assert compare(base, broken, "-fnos1-amd64")[1]
    assert compare(base, dict(candidate, UNREVIEWED="y"), "-fnos1-amd64")[1]
    assert compare(base, dict(candidate, LOCALVERSION='"-old"'), "-fnos1-amd64")[1]
    assert compare(base, dict(candidate, LOCALVERSION_AUTO="y"), "-fnos1-amd64")[1]
    signed = dict(candidate, BUILD_SALT='"7.2.6-fnos1-amd64"', MODULE_SIG_ALL="y",
                  MODULE_SIG_KEY='"certs/signing_key.pem"', SYSTEM_TRUSTED_KEYS='""')
    assert not compare(base, signed, "-fnos1-amd64")[1]
    next_release = dict(signed, LOCALVERSION='"-fnos2-amd64"', BUILD_SALT='"7.2.6-fnos2-amd64"')
    assert not compare(base, next_release, "-fnos2-amd64")[1]
    assert compare(base, next_release, "-fnos1-amd64")[1]
    assert compare(base, dict(signed, MODULE_SIG_ALL="n"), "-fnos1-amd64")[1]
    assert compare(base, dict(signed, MODULE_SIG_KEY='"elsewhere.pem"'), "-fnos1-amd64")[1]
    trusted_base = dict(base, SYSTEM_TRUSTED_KEYS='"vendor.pem"')
    assert compare(trusted_base, signed, "-fnos1-amd64")[1]
    missing = dict(candidate)
    del missing["NFS_V4"]
    assert compare(base, missing, "-fnos1-amd64")[1]
    for bad in ("", "CONFIG_X=y\nCONFIG_X=m", "CONFIG_X=", "oops"):
        try:
            parse_config(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"parser accepted {bad!r}")
    assert parse_config('# comment\nCONFIG_X=y\n# CONFIG_Y is not set\nCONFIG_S="a,b"') == {
        "X": "y", "Y": "n", "S": '"a,b"'
    }
    def encode(config):
        return "\n".join(f"CONFIG_{key}={value}" for key, value in config.items()).encode()
    raw = encode(base)
    plan = {"candidate_localversion": "-fnos1-amd64", "baseline_config_sha256": hashlib.sha256(raw).hexdigest()}
    assert inspect(raw, encode(candidate), plan)["configuration_gate_passed"]
    assert not inspect(raw + b"\n", encode(candidate), plan)["configuration_gate_passed"]
    print("PASS: parser, required features, unreviewed changes, release and baseline hash guards")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", nargs="?", type=Path)
    parser.add_argument("candidate", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan", type=Path, default=Path(__file__).resolve().parent.parent / "build-plan.json")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.baseline is None or args.candidate is None:
        parser.error("both baseline and candidate config paths are required")
    try:
        plan = json.loads(args.plan.read_text())
        result = inspect(args.baseline.read_bytes(), args.candidate.read_bytes(), plan)
    except (OSError, ValueError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["configuration_gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
