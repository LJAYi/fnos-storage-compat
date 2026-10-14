#!/usr/bin/env python3
"""Inspect unpublished image/headers archives; never install or extract them."""
import hashlib
import argparse
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile

RELEASE = "7.2.6-fnos1-amd64"
VERSION = "7.2.6-1~fnos13+1"


def safe_name(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe archive member: {name}")
    return str(path)


def scan(package, control=False):
    command = "--ctrl-tarfile" if control else "--fsys-tarfile"
    proc = subprocess.Popen(["dpkg-deb", command, str(package)], stdout=subprocess.PIPE)
    names, payloads = set(), {}
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as archive:
            for member in archive:
                name = safe_name(member.name)
                names.add(name)
                if (member.uid, member.gid) != (0, 0):
                    raise ValueError(f"Non-root archive ownership: {name}")
                if member.isdev() or member.isfifo() or member.mode & 0o6000:
                    raise ValueError(f"Unexpected special member: {name}")
                if name.endswith(("signing_key.pem", ".key")):
                    raise ValueError(f"Potential private key in archive: {name}")
                if member.isfile() and (control or name.startswith("boot/")):
                    data = archive.extractfile(member).read()
                    payloads[name] = data if control else hashlib.sha256(data).hexdigest()
        if proc.wait() != 0:
            raise RuntimeError(f"dpkg-deb failed for {package}")
    finally:
        proc.stdout.close()
        if proc.poll() is None:
            proc.terminate()
            proc.wait()
    return names, payloads


def main(work, release=RELEASE, version=VERSION):
    source = work / "linux-source-7.2"
    expected = {
        f"lib/modules/{release}/kernel/{line.removesuffix('.o')}.ko.xz"
        for line in (source / "modules.order").read_text().splitlines()
    }
    report = {"release": release, "version": version, "packages": [],
              "scope": "Archive structure/content only; boot, runtime and signatures need separate validation."}
    for kind in ("image", "headers"):
        name = f"linux-{kind}-{release}"
        package = work / f"{name}_{version}_amd64.deb"
        fields = subprocess.check_output(
            ["dpkg-deb", "-f", str(package), "Package", "Version", "Architecture"], text=True)
        for field, value in (("Package", name), ("Version", version), ("Architecture", "amd64")):
            if f"{field}: {value}\n" not in fields:
                raise ValueError(f"Wrong {field}: {fields}")
        names, payloads = scan(package)
        _, control = scan(package, control=True)
        entry = {"name": name, "bytes": package.stat().st_size,
                 "members": len(names), "control": {k: v.decode() for k, v in control.items() if k != "md5sums"}}
        if kind == "image":
            actual = {n for n in names if n.endswith(".ko.xz")}
            if actual != expected:
                raise ValueError(f"Module mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
            for archive_name, source_name in (
                (f"boot/config-{release}", ".config"),
                (f"boot/vmlinuz-{release}", "arch/x86/boot/bzImage"),
                (f"boot/System.map-{release}", "System.map"),
            ):
                if payloads[archive_name] != hashlib.sha256((source / source_name).read_bytes()).hexdigest():
                    raise ValueError(f"Payload differs from compiled source: {archive_name}")
            for script in ("preinst", "postinst", "prerm", "postrm"):
                if b"run-parts" not in control[script] or b"/etc/kernel" not in control[script]:
                    raise ValueError(f"Missing native kernel hook: {script}")
            entry["module_count"] = len(actual)
        else:
            for suffix in ("Makefile", "Module.symvers", "include/generated/utsrelease.h", "scripts/mod/modpost"):
                if f"usr/src/linux-headers-{release}/{suffix}" not in names:
                    raise ValueError(f"Missing header build file: {suffix}")
            if f"lib/modules/{release}/build" not in names:
                raise ValueError("Missing module build link")
        report["packages"].append(entry)
    report["archive_gate_passed"] = True
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        assert safe_name("./boot/config") == "boot/config"
        for bad in ("/etc/passwd", "../etc/passwd", "usr/../../root/key"):
            try:
                safe_name(bad)
            except ValueError:
                pass
            else:
                raise AssertionError(bad)
        print("PASS: archive path checks")
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("work", type=Path)
        parser.add_argument("--plan", type=Path, default=Path(__file__).resolve().parent.parent / "build-plan.json")
        args = parser.parse_args()
        plan = json.loads(args.plan.read_text()) if args.plan else {}
        main(args.work, plan.get("candidate_kernelrelease", RELEASE),
             plan.get("candidate_kernel_package_version", VERSION))
