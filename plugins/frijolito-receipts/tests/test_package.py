"""Offline checks on the package text and metadata. No network.
Run: python3 -m unittest discover -s plugins/frijolito-receipts/tests
"""
import json
import os
import re
import unittest

PLUGIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
REPO = os.path.join(PLUGIN, "..", "..")


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


class VersionTest(unittest.TestCase):
    def test_versions_agree(self):
        manifest = json.loads(read(PLUGIN, ".claude-plugin", "plugin.json"))
        market = json.loads(read(REPO, ".claude-plugin", "marketplace.json"))
        entry = next(p for p in market["plugins"] if p["name"] == "frijolito-receipts")
        server = re.search(r'SERVER_VERSION = "([^"]+)"', read(PLUGIN, "server", "frijolito_receipts_mcp.py")).group(1)
        self.assertEqual(manifest["version"], "0.6.0")
        self.assertEqual(entry["version"], manifest["version"])
        self.assertEqual(server, manifest["version"])

    def test_identity(self):
        manifest = json.loads(read(PLUGIN, ".claude-plugin", "plugin.json"))
        market = json.loads(read(REPO, ".claude-plugin", "marketplace.json"))
        self.assertEqual(manifest["name"], "frijolito-receipts")
        self.assertEqual(market["name"], "frijolito")
        self.assertNotIn("renames", market)
        self.assertTrue(manifest["userConfig"]["api_key"]["sensitive"])
        self.assertFalse(manifest["userConfig"]["allow_live"]["default"])
        self.assertTrue(manifest["userConfig"]["hook_key"]["sensitive"])
        self.assertNotIn("default", manifest["userConfig"]["hook_key"])
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, manifest["icon"])))


class WordingTest(unittest.TestCase):
    DOCS = [("README.md",), ("skills", "frijolito-receipts", "SKILL.md"), ("commands", "notarize.md"),
            ("commands", "verify-receipt.md")]

    def text(self):
        return "\n".join(read(PLUGIN, *d) for d in self.DOCS) + read(PLUGIN, "server", "frijolito_receipts_mcp.py")

    def test_no_overclaims(self):
        t = self.text()
        for phrase in ("is genuine", "was genuine", "witnesses a moment", "Witness a moment",
                       "No accidental duplicates", "without minting twice",
                       "Every notarization carries an idempotency key", "claude-opus"):
            self.assertNotIn(phrase, t, phrase)

    def test_fj2_prefix_is_not_proof_of_observation(self):
        t = self.text()
        for phrase in ("Only these may be described as independently witnessed",
                       "observed from an outside source", "FJ2- observed"):
            self.assertNotIn(phrase, t, phrase)
        self.assertIn("prefix alone", read(PLUGIN, "skills", "frijolito-receipts", "SKILL.md"))

    def test_two_kinds_of_receipt_are_explained(self):
        for doc in (("README.md",), ("skills", "frijolito-receipts", "SKILL.md")):
            t = read(PLUGIN, *doc)
            self.assertIn("self-reported", t, doc)
            self.assertIn("FJ2-", t, doc)

    def test_host_claim_is_claude_code_only(self):
        readme = read(PLUGIN, "README.md")
        self.assertIn("not proven to run in Claude on the web", readme)
        self.assertNotIn("brings Frijolito into Claude, Cowork and Claude Code", readme)
        root = read(REPO, "README.md")
        self.assertNotIn("From the Claude plugin directory", root)

    def test_retry_is_never_automatic(self):
        skill = read(PLUGIN, "skills", "frijolito-receipts", "SKILL.md")
        self.assertIn("Never retry on your own", skill)
        self.assertIn("Never say a retry is safe", skill)

    def test_hook_receipts_are_described_as_self_reported_and_off_by_default(self):
        for doc in (("README.md",), ("skills", "frijolito-receipts", "SKILL.md")):
            t = read(PLUGIN, *doc)
            self.assertIn("self-reported", t, doc)
            self.assertIn("never blocks", t, doc)
        self.assertIn("off by default", read(PLUGIN, "README.md").lower())

    def test_no_generated_files_are_tracked(self):
        self.assertIn("__pycache__/", read(REPO, ".gitignore"))


if __name__ == "__main__":
    unittest.main()
