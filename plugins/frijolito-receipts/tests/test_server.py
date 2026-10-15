"""Offline tests for the MCP server: no network, the HTTP call is stubbed.
Run: python3 -m unittest discover -s plugins/frijolito-receipts/tests
"""
import importlib.util
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location("server", os.path.join(HERE, "..", "server", "frijolito_receipts_mcp.py"))
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)

FJ1 = "FJ-20261014-001-f4094fcae7d7"
HASH = "ab" * 32
FJ2 = "FJ2-" + HASH


class VerifyReceiptTest(unittest.TestCase):
    def setUp(self):
        self.calls = []

        def fake_post(path, body, headers=None):
            self.calls.append((path, body))
            return 200, {"verdict": "VALID", "valid": True, "root": None, "root_reason": "not_yet_rooted"}

        self._real = server._post
        server._post = fake_post

    def tearDown(self):
        server._post = self._real

    def test_fj1_id_is_forwarded(self):
        out = server.tool_verify_receipt({"receipt_id": FJ1})
        self.assertFalse(out["isError"])
        self.assertEqual(self.calls, [("/functions/verify_receipt", {"receipt_id": FJ1})])

    def test_fj2_id_is_forwarded(self):
        out = server.tool_verify_receipt({"receipt_id": FJ2})
        self.assertFalse(out["isError"])
        self.assertEqual(self.calls, [("/functions/verify_receipt", {"receipt_id": FJ2})])
        self.assertEqual(out["structuredContent"]["root_reason"], "not_yet_rooted")

    def test_hash_with_version_2(self):
        server.tool_verify_receipt({"receipt_hash": HASH.upper(), "receipt_version": "2"})
        self.assertEqual(self.calls, [("/functions/verify_receipt", {"receipt_hash": HASH, "receipt_version": "2"})])

    def test_plain_hash_has_no_version(self):
        server.tool_verify_receipt({"receipt_hash": HASH})
        self.assertEqual(self.calls, [("/functions/verify_receipt", {"receipt_hash": HASH})])

    def test_rejected_inputs_never_reach_the_api(self):
        for args in ({}, {"receipt_id": FJ1, "receipt_hash": HASH}, {"receipt_id": "FJ2-abc"},
                     {"receipt_id": "FJ3-" + HASH}, {"receipt_hash": "xyz"},
                     {"receipt_hash": HASH, "receipt_version": "3"}):
            self.assertTrue(server.tool_verify_receipt(args)["isError"], args)
        self.assertEqual(self.calls, [])

    def test_tool_schema_matches_the_validator(self):
        verify = next(t for t in server.TOOLS if t["name"] == "verify_receipt")
        self.assertEqual(verify["inputSchema"]["properties"]["receipt_id"]["pattern"], server.RECEIPT_ID_RE.pattern)
        self.assertIn("receipt_version", verify["inputSchema"]["properties"])


class NotarizeGuardsTest(unittest.TestCase):
    def test_live_key_needs_allow_live(self):
        real_key, real_allow = server.API_KEY, server.ALLOW_LIVE
        server.API_KEY, server.ALLOW_LIVE = "fj_live_x", False
        try:
            out = server.tool_notarize_moment({"parties": [], "moment_label": "x", "witness_model": "m", "document_text": "t"})
            self.assertEqual(out["structuredContent"]["error"], "LIVE_KEY_BLOCKED")
        finally:
            server.API_KEY, server.ALLOW_LIVE = real_key, real_allow


class StdioProtocolTest(unittest.TestCase):
    def test_initialize_reports_version(self):
        sent = []
        real = server._send
        server._send = sent.append
        try:
            server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        finally:
            server._send = real
        self.assertEqual(sent[0]["result"]["serverInfo"]["version"], "0.4.0")


if __name__ == "__main__":
    unittest.main()
