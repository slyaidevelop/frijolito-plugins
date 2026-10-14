#!/usr/bin/env python3
"""
Frijolito Receipts — MCP server (stdio, stdlib only, Python 3.9+).

Wraps the Frijolito core app's notary surface:
  verify_receipt   POST {BASE}/functions/verify_receipt    public, read-only
  notarize_moment  POST {BASE}/functions/notarize_moment   Bearer API key (scope: notarize)

Configuration comes from the plugin's userConfig, which Claude Code passes in
through the server's environment (see .mcp.json):
  FRIJOLITO_API_KEY      api_key: fj_test_… or fj_live_…, only needed for notarize_moment
  FRIJOLITO_ALLOW_LIVE   allow_live: "true" allows minting with an fj_live_ key

The API key never appears in tool output. Errors from the API are passed
through as the API's own {error, detail, request_id} envelope.
"""

import json
import os
import re
import sys
import uuid
import urllib.error
import urllib.request

SERVER_NAME = "frijolito-receipts"
SERVER_VERSION = "0.3.0"
DEFAULT_PROTOCOL = "2025-06-18"

BASE_URL = "https://frijolito.app"


def _config(name):
    value = (os.environ.get(name) or "").strip()
    # An option the user never set can arrive as the literal placeholder.
    return "" if value.startswith("${") else value


API_KEY = _config("FRIJOLITO_API_KEY")
ALLOW_LIVE = _config("FRIJOLITO_ALLOW_LIVE").lower() in ("1", "true")

RECEIPT_ID_RE = re.compile(r"^FJ-\d{8}-\d{3}-[0-9a-f]{12}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TIMEOUT_S = 30

# ---------------------------------------------------------------- tool schemas
# Mirrors base44/shared/notaryOpenApi.ts in the core app.

TOOLS = [
    {
        "name": "verify_receipt",
        "title": "Verify a Frijolito receipt",
        "description": (
            "Verify a Frijolito receipt by ID (FJ-YYYYMMDD-NNN-xxxxxxxxxxxx) or by its "
            "64-char sha256 receipt hash. Public and read-only: no API key, no side effects. "
            "Returns a verdict: VALID, INVALID, or UNKNOWN (well-formed but not in the registry)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "receipt_id": {"type": "string", "pattern": RECEIPT_ID_RE.pattern},
                "receipt_hash": {"type": "string", "pattern": SHA256_RE.pattern},
            },
            "description": "Exactly one of receipt_id or receipt_hash.",
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": True},
    },
    {
        "name": "notarize_moment",
        "title": "Notarize a moment (mint a receipt)",
        "description": (
            "Witness a moment between parties and mint a signed, publicly verifiable Frijolito "
            "receipt. WRITE: creates a permanent receipt record. No money moves. Requires an "
            "API key with the notarize scope, set in the plugin's settings. Provide document_hash (preferred) or "
            "document_text (hashed server-side, never stored). An idempotency_key is generated "
            "if omitted and returned so a retry can reuse it without minting twice."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "parties": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {"label": {"type": "string"}, "role": {"type": "string"}},
                        "required": ["label", "role"],
                    },
                },
                "moment_label": {"type": "string", "description": "Short human label for what was agreed or happened."},
                "witness_model": {"type": "string", "description": "Identity of the calling model/agent, recorded on the receipt."},
                "document_hash": {"type": "string", "pattern": SHA256_RE.pattern},
                "document_text": {"type": "string"},
                "evidence_pointers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "ref": {"type": "string"},
                            "sha256": {"type": "string", "pattern": SHA256_RE.pattern},
                        },
                        "required": ["type", "ref", "sha256"],
                    },
                },
                "external_ref": {"type": "string", "description": "Caller's correlation id; echoed back."},
                "idempotency_key": {"type": "string", "description": "Reuse on retry to replay instead of minting twice."},
            },
            "required": ["parties", "moment_label", "witness_model"],
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    },
]

# ---------------------------------------------------------------- HTTP


def _post(path, body, headers=None):
    """POST JSON; return (status, parsed_json_or_text). Never raises on HTTP errors."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(BASE_URL + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "%s/%s" % (SERVER_NAME, SERVER_VERSION))
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            status, raw = resp.status, resp.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    text = raw.decode("utf-8", "replace")
    try:
        return status, json.loads(text)
    except ValueError:
        return status, {"error": "NON_JSON_RESPONSE", "detail": text[:300]}


# ---------------------------------------------------------------- tools


def _result(payload, is_error=False):
    return {
        "content": [{"type": "text", "text": json.dumps(payload, indent=2)}],
        "structuredContent": payload,
        "isError": is_error,
    }


def tool_verify_receipt(args):
    rid = (args.get("receipt_id") or "").strip()
    rhash = (args.get("receipt_hash") or "").strip().lower()
    if bool(rid) == bool(rhash):
        return _result({"error": "BAD_REQUEST", "detail": "Provide exactly one of receipt_id or receipt_hash."}, True)
    if rid and not RECEIPT_ID_RE.match(rid):
        return _result({"error": "BAD_REQUEST", "detail": "receipt_id must look like FJ-YYYYMMDD-NNN-xxxxxxxxxxxx."}, True)
    if rhash and not SHA256_RE.match(rhash):
        return _result({"error": "BAD_REQUEST", "detail": "receipt_hash must be 64 lowercase hex chars."}, True)
    body = {"receipt_id": rid} if rid else {"receipt_hash": rhash}
    status, data = _post("/functions/verify_receipt", body)
    return _result({"http_status": status, **data} if isinstance(data, dict) else {"http_status": status, "body": data},
                   is_error=status != 200)


def tool_notarize_moment(args):
    if not API_KEY:
        return _result({"error": "NOT_CONFIGURED",
                        "detail": "No API key is set. Add your Frijolito API key in the plugin's settings (/plugin → Frijolito Receipts → Configure), then restart Claude. Verifying receipts works without a key."}, True)
    if API_KEY.startswith("fj_live_") and not ALLOW_LIVE:
        return _result({"error": "LIVE_KEY_BLOCKED",
                        "detail": "The API key is a live key. Turn on 'Allow production receipts' in the plugin's settings to mint production receipts."}, True)
    if not args.get("document_hash") and not args.get("document_text"):
        return _result({"error": "BAD_REQUEST", "detail": "Provide document_hash (preferred) or document_text."}, True)

    fields = ("parties", "moment_label", "witness_model", "document_hash",
              "document_text", "evidence_pointers", "external_ref")
    body = {k: args[k] for k in fields if args.get(k) not in (None, "", [])}
    idem = (args.get("idempotency_key") or "").strip() or str(uuid.uuid4())
    status, data = _post("/functions/notarize_moment", body, {
        "Authorization": "Bearer " + API_KEY,
        "Idempotency-Key": idem,
    })
    payload = {"http_status": status, "idempotency_key": idem}
    payload.update(data if isinstance(data, dict) else {"body": data})
    return _result(payload, is_error=status not in (200, 201))


HANDLERS = {"verify_receipt": tool_verify_receipt, "notarize_moment": tool_notarize_moment}

# ---------------------------------------------------------------- JSON-RPC over stdio


def _send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def _reply(mid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": mid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    _send(msg)


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    params = msg.get("params") or {}
    if mid is None:  # notification (e.g. notifications/initialized): no reply
        return
    if method == "initialize":
        _reply(mid, {
            "protocolVersion": params.get("protocolVersion") or DEFAULT_PROTOCOL,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
    elif method == "ping":
        _reply(mid, {})
    elif method == "tools/list":
        _reply(mid, {"tools": TOOLS})
    elif method == "tools/call":
        fn = HANDLERS.get(params.get("name"))
        if fn is None:
            _reply(mid, error={"code": -32602, "message": "Unknown tool: %s" % params.get("name")})
            return
        try:
            _reply(mid, fn(params.get("arguments") or {}))
        except Exception as e:  # network failure, timeout, etc.
            _reply(mid, _result({"error": "CLIENT_ERROR", "detail": str(e)[:300]}, True))
    else:
        _reply(mid, error={"code": -32601, "message": "Method not found: %s" % method})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            _send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})
            continue
        handle(msg)


if __name__ == "__main__":
    main()
