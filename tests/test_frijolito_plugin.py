"""The main Frijolito plugin must stay within what Anthropic's directory accepts
from an organization that is not Verified: no program on the user's computer,
and only Markdown, text, JSON, YAML and image files. These tests live outside
the plugin folder for the same reason. No network.
Run: python3 -m unittest discover -s tests
"""
import json
import os
import re
import unittest

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PLUGIN = os.path.join(REPO, "plugins", "frijolito")
ALLOWED = (".md", ".txt", ".json", ".yaml", ".yml", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico")
IMAGES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico")


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


def files():
    for root, _dirs, names in os.walk(PLUGIN):
        for name in names:
            yield os.path.join(root, name)


class DirectoryRulesTest(unittest.TestCase):
    def test_only_allowed_file_types(self):
        for path in files():
            name = os.path.basename(path)
            self.assertTrue(name == "LICENSE" or name.lower().endswith(ALLOWED), path)
            self.assertNotIn(name, (".DS_Store", "Thumbs.db", "desktop.ini"), path)
            with open(path, "rb") as f:
                data = f.read()
            self.assertFalse(data.startswith(b"#!"), path)
            if not name.lower().endswith(IMAGES):
                self.assertNotIn(b"\x00", data, path)
                data.decode("utf-8")
                self.assertLess(len(data), 256 * 1024, path)

    def test_nothing_runs_on_the_users_computer(self):
        servers = json.loads(read(PLUGIN, ".mcp.json"))["mcpServers"]
        self.assertEqual(servers, {
            "frijolito": {"type": "http", "url": "https://frijolito.app/api/mcp"},
            "frijolito-verify": {"type": "http", "url": "https://frijolito.app/api/functions/frijolitoVerifyMcp"},
        })
        for name in ("hooks", "server", "scripts", "bin", "tests", "agents"):
            self.assertFalse(os.path.exists(os.path.join(PLUGIN, name)), name)
        manifest = json.loads(read(PLUGIN, ".claude-plugin", "plugin.json"))
        for key in ("userConfig", "hooks", "mcpServers", "lspServers", "monitors"):
            self.assertNotIn(key, manifest)

    def test_manifest_and_marketplace(self):
        manifest = json.loads(read(PLUGIN, ".claude-plugin", "plugin.json"))
        market = json.loads(read(REPO, ".claude-plugin", "marketplace.json"))
        entry = next(p for p in market["plugins"] if p["name"] == "frijolito")
        self.assertEqual((manifest["name"], manifest["displayName"]), ("frijolito", "Frijolito"))
        self.assertEqual(manifest["version"], "0.7.0")
        self.assertEqual(entry["version"], manifest["version"])
        self.assertEqual(entry["source"], "./plugins/frijolito")
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, manifest["icon"])))
        for key in ("privacyPolicyUrl", "termsOfServiceUrl", "supportUrl", "documentationUrl", "homepage"):
            self.assertTrue(manifest[key].startswith("https://"), key)
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, "LICENSE")))

    def test_readme_is_a_listing(self):
        readme = read(PLUGIN, "README.md")
        self.assertNotIn("<img", readme)
        self.assertGreaterEqual(len(re.sub(r"```.*?```", "", readme, flags=re.S).split()), 40)
        for image in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme):
            self.assertTrue(os.path.isfile(os.path.join(PLUGIN, image)), image)
        for path in files():
            if path.endswith((".md", ".json")):
                self.assertIsNone(re.search(r"`[^`\n]*\.(png|svg|jpg|jpeg|gif|webp|ico)`", read(path)), path)


class BehaviourTest(unittest.TestCase):
    def test_commands(self):
        for name in ("ask", "request", "status", "verify"):
            text = read(PLUGIN, "commands", name + ".md")
            self.assertTrue(text.startswith("---\ndescription: "), name)
        self.assertEqual(sorted(os.listdir(os.path.join(PLUGIN, "commands"))),
                         ["ask.md", "request.md", "status.md", "verify.md"])
        self.assertIn("wait for a clear yes", read(PLUGIN, "commands", "request.md"))
        verify = read(PLUGIN, "commands", "verify.md")
        self.assertIn("`verify_frijolito_receipt`", verify)
        self.assertIn("`frijolito-verify`", verify)

    def test_wording(self):
        skill = read(PLUGIN, "skills", "frijolito", "SKILL.md")
        text = skill + read(PLUGIN, "README.md") + "".join(
            read(PLUGIN, "commands", n) for n in os.listdir(os.path.join(PLUGIN, "commands")))
        for phrase in ("is genuine", "was genuine", "witnesses a moment", "independently witnessed\n",
                       "notarize_moment", "API key in", "hook receipt key"):
            self.assertNotIn(phrase, text, phrase)
        self.assertIn("self-reported", skill)
        self.assertIn("prefix alone", skill)
        self.assertIn("wait for a clear yes", skill)
        self.assertIn("Never ask for a password", skill)
        self.assertIn("does not record new receipts", skill)


if __name__ == "__main__":
    unittest.main()
