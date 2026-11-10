#!/usr/bin/env python3
"""Frijolito hook receipts for Claude Code. Observe only.

Usage: hook_receipt.py gate|result   (the hook event JSON arrives on stdin)

  gate    PreToolUse                        -> POST {BASE}/functions/hookGate
  result  PostToolUse, PostToolUseFailure   -> POST {BASE}/functions/hookResult

Off unless a hook receipt key is set in the plugin's settings (exported by
Claude Code as CLAUDE_PLUGIN_OPTION_HOOK_KEY). Without a key nothing is sent.
The key comes only from that setting, and it only ever goes to frijolito.app.

This script never blocks a tool call: it always exits 0, never prints a
permission decision, and stays silent on any error. Frijolito stores hashes
and a one-line redacted summary, not the call's input or output.
Standard library only.
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://frijolito.app"
ENDPOINTS = {"gate": "/functions/hookGate", "result": "/functions/hookResult"}
TIMEOUT_SECONDS = 5
USER_AGENT = "frijolito-hook-receipts/0.6.0"


def hook_key():
    value = os.environ.get("CLAUDE_PLUGIN_OPTION_HOOK_KEY", "").strip()
    # An unset option can arrive as an unexpanded placeholder.
    if not value or value.startswith("${"):
        return ""
    return value


def gate_output(body):
    """Pass on only the receipt note. A permission decision is never relayed."""
    try:
        note = json.loads(body)["hookSpecificOutput"]["additionalContext"]
    except (ValueError, KeyError, TypeError):
        return None
    if not isinstance(note, str) or not note:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": note[:300]}}


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    key = hook_key()
    if mode not in ENDPOINTS or not key:
        return 0
    try:
        event = sys.stdin.buffer.read()
        json.loads(event)
        req = urllib.request.Request(BASE_URL + ENDPOINTS[mode], data=event, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", "Bearer " + key)
        req.add_header("User-Agent", USER_AGENT)
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            body = res.read(65536).decode("utf-8", "replace")
        if mode == "gate":
            out = gate_output(body)
            if out:
                sys.stdout.write(json.dumps(out))
    except Exception:  # noqa: BLE001 - a receipt must never get in the way of the call
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
