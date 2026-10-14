---
name: frijolito-receipts
description: Use when the user wants to notarize, witness, or record an agreement or moment between parties as a Frijolito receipt, or to check, verify, or validate a Frijolito receipt ID (FJ-…) or receipt hash.
---

# Frijolito receipts

Frijolito is a **notary, not a payment rail**. It witnesses a moment between parties and returns a signed, publicly verifiable receipt. No money moves through these tools.

Tools (from the `frijolito-receipts` MCP server):

- `verify_receipt`: public, read-only. Pass exactly one of `receipt_id` or `receipt_hash`.
- `notarize_moment`: **write**. It mints a permanent receipt and needs `FRIJOLITO_API_KEY`.

## Verifying

Report the verdict plainly:

| Verdict | Meaning | What to tell the user |
|---|---|---|
| `VALID` | Registry hit, hash and signatures check out | The receipt is genuine. Summarize parties, moment_label, created_at, status. |
| `INVALID` | The receipt fails a check | Do **not** trust it. Treat it as tampered or malformed and quote `detail`. |
| `UNKNOWN` | Well-formed, but this issuer never minted it (or it was deleted) | It cannot be confirmed. This is not the same as "fake", but it is not proof either. |

A `VALID` receipt whose `status` is `expired` or `revoked` was genuine but no longer stands. Say so.

Receipt IDs look like `FJ-YYYYMMDD-NNN-xxxxxxxxxxxx`; receipt hashes are 64 lowercase hex characters.

## Notarizing

Minting is permanent, so:

1. Before calling `notarize_moment`, show the user exactly what will be recorded (parties with roles, moment_label, and which document is being hashed) and get a clear yes.
2. Prefer `document_hash` (sha256 of the exact agreed bytes) over `document_text`. To hash a local file: `shasum -a 256 <file>`. `document_text` is hashed server-side and never stored.
3. Set `witness_model` to your own model identity (for example `claude-opus-5-5`).
4. Evidence pointers need a real 64-char sha256. Never invent or abbreviate one.
5. If a call fails or times out, **retry with the same `idempotency_key`** returned by the previous attempt. A new key could mint a duplicate.
6. After minting, give the user the `receipt_id` and `verify_url`.

## Errors

- `NOT_CONFIGURED`: the user must set `FRIJOLITO_API_KEY` (an `fj_test_…` key with the `notarize` scope) and restart Claude Code.
- `LIVE_KEY_BLOCKED`: a production key is set. Minting production receipts needs `FRIJOLITO_ALLOW_LIVE=1`; confirm with the user first.
- `401 UNAUTHORIZED`: the key is missing, revoked, or lacks the `notarize` scope.
- `422 UNPROCESSABLE`: a semantic rule failed, or an idempotency key was reused with a different payload. Quote `detail`; do not loop.
