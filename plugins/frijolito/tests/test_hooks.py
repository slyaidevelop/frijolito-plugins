"""Hook receipts: off without a key, never block, never relay a decision.
Uses a local HTTP server. No outside network.
Run: python3 -m unittest discover -s plugins/frijolito/tests
"""
import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

PLUGIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRIPT = os.path.join(PLUGIN, "hooks", "hook_receipt.py")
EVENT = {"session_id": "s1", "tool_use_id": "t1", "hook_event_name": "PreToolUse",
         "tool_name": "Bash", "tool_input": {"command": "ls"}}


class Handler(BaseHTTPRequestHandler):
    calls = []
    reply = (200, "{}")

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        Handler.calls.append((self.path, self.headers.get("Authorization"), json.loads(body)))
        status, text = Handler.reply
        self.send_response(status)
        self.end_headers()
        self.wfile.write(text.encode())

    def log_message(self, *args):
        pass


class HookTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        Handler.calls = []
        Handler.reply = (200, "{}")

    def run_hook(self, mode, key="fjh_test_abc", stdin=None, base=None):
        env = {k: v for k, v in os.environ.items()
               if k not in ("CLAUDE_PLUGIN_OPTION_HOOK_KEY", "FRIJOLITO_HOOK_KEY")}
        env["FRIJOLITO_HOOK_BASE_URL"] = base or self.base
        if key is not None:
            env["CLAUDE_PLUGIN_OPTION_HOOK_KEY"] = key
        data = json.dumps(EVENT) if stdin is None else stdin
        return subprocess.run([sys.executable, SCRIPT, mode], input=data.encode(), env=env,
                              capture_output=True, timeout=20)

    def test_off_without_a_key(self):
        for key in (None, "", "  ", "${user_config.hook_key}"):
            done = self.run_hook("gate", key=key)
            self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"", b""), key)
        self.assertEqual(Handler.calls, [])

    def test_gate_opens_and_relays_only_the_note(self):
        Handler.reply = (200, json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "additionalContext": "Frijolito receipt FJ-HK-20261110-0123456789abcdef opened for this call."}}))
        done = self.run_hook("gate")
        self.assertEqual(done.returncode, 0)
        out = json.loads(done.stdout)
        self.assertEqual(out, {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "Frijolito receipt FJ-HK-20261110-0123456789abcdef opened for this call."}})
        path, auth, body = Handler.calls[0]
        self.assertEqual((path, auth, body), ("/functions/hookGate", "Bearer fjh_test_abc", EVENT))

    def test_result_closes_quietly(self):
        done = self.run_hook("result")
        self.assertEqual((done.returncode, done.stdout), (0, b""))
        self.assertEqual(Handler.calls[0][0], "/functions/hookResult")

    def test_errors_never_block_or_print(self):
        for reply in ((401, "nope"), (500, "boom"), (200, "not json"), (200, '{"hookSpecificOutput":7}')):
            Handler.reply = reply
            done = self.run_hook("gate")
            self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"", b""), reply)
        done = self.run_hook("gate", base="http://127.0.0.1:1")
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"", b""))
        done = self.run_hook("gate", stdin="not json")
        self.assertEqual((done.returncode, done.stdout), (0, b""))
        done = self.run_hook("nonsense")
        self.assertEqual((done.returncode, done.stdout), (0, b""))

    def test_key_never_appears_in_output(self):
        Handler.reply = (401, "bad key fjh_test_abc")
        done = self.run_hook("gate")
        self.assertNotIn(b"fjh_test_abc", done.stdout + done.stderr)

    def test_hooks_file(self):
        with open(os.path.join(PLUGIN, "hooks", "hooks.json"), encoding="utf-8") as f:
            hooks = json.load(f)["hooks"]
        self.assertEqual(sorted(hooks), ["PostToolUse", "PostToolUseFailure", "PreToolUse"])
        for event, groups in hooks.items():
            for group in groups:
                for hook in group["hooks"]:
                    self.assertEqual(hook["type"], "command")
                    self.assertIn("hook_receipt.py", hook["command"])
                    self.assertNotIn("user_config", hook["command"])


if __name__ == "__main__":
    unittest.main()
