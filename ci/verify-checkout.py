#!/usr/bin/env python3
"""Check that a repo workspace contains the selected manifest's exact sources."""

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def git(path, *args):
    return subprocess.check_output(
        ["git", "-C", str(path), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", required=True, help="entry passed to repo init -m, or default.xml")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("manifest_policy", ROOT / "ci/validate-manifests.py")
    policy = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = policy
    spec.loader.exec_module(policy)
    workspace = args.workspace.resolve()
    try:
        projects = policy.validate(ROOT, args.entry)
        selected = workspace / ".repo/manifest.xml"
        expected = workspace / ".repo/manifests" / args.entry
        if not selected.is_file():
            raise ValueError("workspace is not initialized with repo")
        if selected.is_symlink():
            if selected.resolve() != expected.resolve():
                raise ValueError("selected manifest does not match --entry")
        else:
            includes = ET.parse(selected).getroot().findall("include")
            if len(includes) != 1 or includes[0].get("name") != args.entry:
                raise ValueError("selected manifest does not match --entry")
        if (workspace / ".repo/local_manifests").exists():
            if any((workspace / ".repo/local_manifests").glob("*.xml")):
                raise ValueError("local manifests must be removed or audited separately")
        # Ensure this policy/XML checkout is the workspace's actual manifest.
        if (workspace / ".repo/manifests").resolve() != ROOT:
            raise ValueError("run the checker from this workspace's .repo/manifests/ci directory")
        if git(ROOT, "status", "--porcelain", "--untracked-files=all"):
            raise ValueError("manifest checkout has uncommitted or untracked changes")
        for project in projects:
            path = (workspace / project.path).resolve()
            if not path.is_relative_to(workspace):
                raise ValueError(f"checkout escapes workspace: {project.path}")
            if git(path, "rev-parse", "HEAD") != project.revision:
                raise ValueError(f"wrong HEAD: {project.path}")
            if git(path, "status", "--porcelain", "--untracked-files=all", "--ignore-submodules=none"):
                raise ValueError(f"uncommitted or untracked source changes: {project.path}")
            submodules = git(path, "submodule", "status", "--recursive")
            if any(line[0] in "-+U" for line in submodules.splitlines() if line):
                raise ValueError(f"submodule missing or at wrong revision: {project.path}")
            print(f"PASS {project.path}: {project.revision}")
        print(f"Verified {len(projects)} pinned checkouts; build/boot qualification is separate.")
    except (policy.ManifestError, ValueError, OSError, ET.ParseError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
