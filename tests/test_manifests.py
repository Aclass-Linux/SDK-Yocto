"""Regression checks for broken source compositions and release promotion."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("manifest_policy", ROOT / "ci/validate-manifests.py")
policy = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = policy
spec.loader.exec_module(policy)


class ManifestPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.base = (
            '<remote name="upstream" fetch="https://example.org/"/>'
            '<default remote="upstream"/>'
        )

    def write(self, path, body):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("<manifest>" + body + "</manifest>")

    def project(self, path="sources/example", revision="a" * 40, children=""):
        return (
            f'<project name="example" path="{path}" revision="{revision}" '
            f'upstream="refs/heads/wrynose">{children}</project>'
        )

    def test_repository_entries_are_pinned(self):
        for entry in policy.entries(ROOT):
            with self.subTest(entry=entry):
                self.assertTrue(policy.validate(ROOT, entry))

    def test_rejects_duplicate_base_in_board_composition(self):
        self.write("base.xml", self.base + self.project())
        self.write("entry.xml", '<include name="base.xml"/><include name="base.xml"/>')
        with self.assertRaisesRegex(policy.ManifestError, "one default"):
            policy.validate(self.root, "entry.xml")

    def test_rejects_include_cycle(self):
        self.write("a.xml", '<include name="b.xml"/>')
        self.write("b.xml", '<include name="a.xml"/>')
        with self.assertRaisesRegex(policy.ManifestError, "include cycle"):
            policy.validate(self.root, "a.xml")

    def test_rejects_traversal(self):
        self.write("entry.xml", '<include name="../outside.xml"/>')
        with self.assertRaisesRegex(policy.ManifestError, "unsafe relative path"):
            policy.validate(self.root, "entry.xml")

    def test_rejects_overlapping_checkout_paths(self):
        nested = self.project("sources/example/nested").replace('name="example"', 'name="nested"')
        self.write("entry.xml", self.base + self.project() + nested)
        with self.assertRaisesRegex(policy.ManifestError, "overlapping path"):
            policy.validate(self.root, "entry.xml")

    def test_rejects_floating_branch(self):
        self.write("entry.xml", self.base + self.project(revision="wrynose"))
        with self.assertRaisesRegex(policy.ManifestError, "full commit SHA"):
            policy.validate(self.root, "entry.xml")

    def test_rejects_unknown_remote(self):
        project = self.project().replace('name="example"', 'name="example" remote="missing"')
        self.write("entry.xml", self.base + project)
        with self.assertRaisesRegex(policy.ManifestError, "unknown remote"):
            policy.validate(self.root, "entry.xml")

    def test_release_cannot_promote_pending_board_migration(self):
        annotation = '<annotation name="migration-status" value="pending-wrynose"/>'
        self.write("releases/product/1.0.xml", self.base + self.project(children=annotation))
        with self.assertRaisesRegex(policy.ManifestError, "cannot enter a release"):
            policy.validate(self.root, "releases/product/1.0.xml")

    def test_xilinx_has_explicit_submodule_sync_policy(self):
        project = self.project().replace('name="example"', 'name="meta-xilinx"')
        self.write("entry.xml", self.base + project)
        with self.assertRaisesRegex(policy.ManifestError, "submodule"):
            policy.validate(self.root, "entry.xml")


if __name__ == "__main__":
    unittest.main()
