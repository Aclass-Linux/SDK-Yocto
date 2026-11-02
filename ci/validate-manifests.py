#!/usr/bin/env python3
"""Validate this repository's deliberately small manifest vocabulary offline.

This is a project policy check, not a replacement for git-repo's XML parser.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"[0-9a-f]{40}\Z")
SUPPORTED = {"include", "remote", "default", "project", "notice"}


class ManifestError(ValueError):
    pass


@dataclass
class Project:
    name: str
    path: str
    url: str
    revision: str
    upstream: str
    annotations: dict


def relative_path(value, context):
    """Reject paths whose meaning depends on traversal or repo internals."""
    path = PurePosixPath(value)
    parts = value.split("/")
    if (
        not value
        or path.is_absolute()
        or "\\" in value
        or any(part in {"", ".", "..", ".git", ".repo"} for part in parts)
    ):
        raise ManifestError(f"{context}: unsafe relative path {value!r}")
    return path


def read_xml(path):
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise ManifestError(f"{path}: {exc}") from exc
    if root.tag != "manifest":
        raise ManifestError(f"{path}: root must be <manifest>")
    return root


def expand(root, name, stack=()):
    relative_path(name, "include")
    if name in stack:
        raise ManifestError("include cycle: " + " -> ".join((*stack, name)))
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ManifestError(f"include escapes repository: {name}")
    nodes = []
    for node in read_xml(path):
        if node.tag not in SUPPORTED:
            raise ManifestError(f"{name}: unsupported element <{node.tag}>")
        if node.tag == "include":
            nodes.extend(expand(root, node.get("name", ""), (*stack, name)))
        else:
            nodes.append((name, node))
    return nodes


def validate(root, entry):
    nodes = expand(root, entry)
    remotes = {}
    defaults = [node.attrib for _, node in nodes if node.tag == "default"]
    if len(defaults) != 1:
        raise ManifestError(f"{entry}: expected one default, got {len(defaults)}")
    default = defaults[0]
    for source, node in nodes:
        if node.tag != "remote":
            continue
        name, fetch = node.get("name"), node.get("fetch", "")
        if not name or name in remotes:
            raise ManifestError(f"{source}: missing or duplicate remote {name!r}")
        if not fetch.startswith("https://") or not fetch.endswith("/"):
            raise ManifestError(f"{source}: fetch must be an HTTPS prefix ending in /")
        remotes[name] = node.attrib
    if default.get("remote") not in remotes:
        raise ManifestError(f"{entry}: default refers to an unknown remote")

    projects = []
    names, paths = set(), set()
    for source, node in nodes:
        if node.tag != "project":
            continue
        name, path = node.get("name", ""), node.get("path", "")
        relative_path(name, source)
        relative_path(path, source)
        if not path.startswith("sources/"):
            raise ManifestError(f"{source}: project path must start with sources/")
        if name in names or any(
            path == other or path.startswith(other + "/") or other.startswith(path + "/")
            for other in paths
        ):
            raise ManifestError(f"{entry}: duplicate project or overlapping path: {name}, {path}")
        names.add(name)
        paths.add(path)
        remote = remotes.get(node.get("remote", default.get("remote")))
        if remote is None:
            raise ManifestError(f"{source}: unknown remote for {name}")
        revision = node.get("revision", remote.get("revision", default.get("revision", "")))
        if not SHA.fullmatch(revision):
            raise ManifestError(f"{source}: {name} must use a full commit SHA, got {revision!r}")
        upstream = node.get("upstream", "")
        if not upstream.startswith("refs/heads/"):
            raise ManifestError(f"{source}: {name} needs an explicit refs/heads/ upstream")
        annotations = {}
        for child in node:
            if child.tag != "annotation" or not child.get("name") or child.get("value") is None:
                raise ManifestError(f"{source}: unsupported or malformed project child")
            if child.get("name") in annotations:
                raise ManifestError(f"{source}: duplicate annotation {child.get('name')}")
            annotations[child.get("name")] = child.get("value")
        if name == "meta-xilinx" and node.get("sync-s", default.get("sync-s")) != "true":
            raise ManifestError(f"{source}: project policy requires explicit submodule sync for meta-xilinx")
        if annotations.get("yocto-series") not in {None, "wrynose"}:
            if not annotations.get("migration-status", "").startswith("pending-"):
                raise ManifestError(f"{source}: older-series project needs an explicit migration status")
        if entry.startswith("releases/") and annotations.get("migration-status"):
            raise ManifestError(f"{entry}: pending BSP migrations cannot enter a release")
        projects.append(Project(name, path, remote["fetch"] + name, revision, upstream, annotations))
    if not projects:
        raise ManifestError(f"{entry}: no projects")
    return projects


def entries(root):
    result = ["default.xml"]
    for directory in ("products", "releases", "workspaces"):
        result.extend(str(path.relative_to(root)) for path in sorted((root / directory).rglob("*.xml")))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="*", help="repository-relative entry paths; default: all entries")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        for path in sorted(root.rglob("*.xml")):
            if ".git" not in path.parts and ".repo" not in path.parts:
                read_xml(path)
        selected = args.manifests or entries(root)
        if not selected:
            raise ManifestError("no entry manifests")
        for entry in selected:
            projects = validate(root, entry)
            pending = [p.name for p in projects if p.annotations.get("migration-status")]
            suffix = "; migration pending: " + ", ".join(pending) if pending else ""
            print(f"PASS {entry}: {len(projects)} pinned projects{suffix}")
        for target in re.findall(r"-m\s+([\w./-]+\.xml)", (root / "README.md").read_text()):
            if not (root / target).is_file():
                raise ManifestError(f"README references missing entry: {target}")
    except (ManifestError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

