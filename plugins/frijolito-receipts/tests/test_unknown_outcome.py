"""Offline tests for notarizations whose outcome is unknown. No network:
_post is replaced with a stub that records each call.
Run: python3 -m unittest discover -s plugins/frijolito-receipts/tests
"""
import http.client
import os
import socket
import sys
import unittest
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "server"))
import frijolito_receipts_mcp as server  # noqa: E402

ARGS = {"parties": [], "moment_label": "test", "witness_model": "m", "document_hash": "a" * 64}


class StubPost:
    def __init__(self, outcome):
        self.outcome, self.calls = outcome, []

    def __call__(self, path, body, headers=None):
        self.calls.append(dict(headers or {}))
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome


class UnknownOutcomeTest(unittest.TestCase):
    def setUp(self):
        self.saved = (server.API_KEY, server.ALLOW_LIVE, server._post)
        server.API_KEY, server.ALLOW_LIVE = "fj_test_offline", False

    def tearDown(self):
        server.API_KEY, server.ALLOW_LIVE, server._post = self.saved

    def run_with(self, outcome, args=ARGS):
        stub = StubPost(outcome)
        server._post = stub
        return server.tool_notarize_moment(dict(args)), stub

    def assert_unknown(self, out, stub):
        sc = out["structuredContent"]
        self.assertTrue(out["isError"])
        self.assertTrue(sc["outcome_unknown"])
        self.assertEqual(len(stub.calls), 1, "must not retry")
        self.assertEqual(sc["idempotency_key"], stub.calls[0]["Idempotency-Key"])
        return sc

    def test_url_error_returns_the_generated_key(self):
        out, stub = self.run_with(urllib.error.URLError("connection reset"))
        sc = self.assert_unknown(out, stub)
        self.assertEqual(sc["error"], "OUTCOME_UNKNOWN")
        self.assertTrue(sc["idempotency_key"])

    def test_timeout_returns_the_generated_key(self):
        out, stub = self.run_with(socket.timeout("timed out"))
        self.assertEqual(self.assert_unknown(out, stub)["error"], "OUTCOME_UNKNOWN")

    def test_cut_off_reply_returns_the_generated_key(self):
        out, stub = self.run_with(http.client.IncompleteRead(b"{"))
        self.assertEqual(self.assert_unknown(out, stub)["error"], "OUTCOME_UNKNOWN")

    def test_explicit_key_is_preserved(self):
        out, stub = self.run_with(urllib.error.URLError("down"), dict(ARGS, idempotency_key="my-key-1"))
        self.assertEqual(self.assert_unknown(out, stub)["idempotency_key"], "my-key-1")

    def test_server_error_is_flagged(self):
        out, stub = self.run_with((503, {"error": "UNAVAILABLE"}))
        sc = self.assert_unknown(out, stub)
        self.assertEqual(sc["http_status"], 503)

    def test_non_json_success_is_flagged(self):
        out, stub = self.run_with((200, {"error": "NON_JSON_RESPONSE", "detail": "<html>"}))
        self.assert_unknown(out, stub)

    def test_clear_rejection_is_not_flagged(self):
        out, stub = self.run_with((400, {"error": "BAD_REQUEST"}))
        self.assertTrue(out["isError"])
        self.assertNotIn("outcome_unknown", out["structuredContent"])

    def test_success_is_unchanged(self):
        out, stub = self.run_with((201, {"receipt_id": "FJ-TEST"}))
        sc = out["structuredContent"]
        self.assertFalse(out["isError"])
        self.assertNotIn("outcome_unknown", sc)
        self.assertEqual(sc["idempotency_key"], stub.calls[0]["Idempotency-Key"])

    def test_two_failures_without_a_key_get_different_keys(self):
        # Documents the remaining limit: only reusing the returned key replays.
        a, _ = self.run_with(urllib.error.URLError("x"))
        b, _ = self.run_with(urllib.error.URLError("x"))
        self.assertNotEqual(a["structuredContent"]["idempotency_key"], b["structuredContent"]["idempotency_key"])

    def test_not_configured_still_makes_no_call(self):
        server.API_KEY = ""
        out, stub = self.run_with(urllib.error.URLError("x"))
        self.assertEqual(out["structuredContent"]["error"], "NOT_CONFIGURED")
        self.assertEqual(stub.calls, [])


if __name__ == "__main__":
    unittest.main()
