---
name: frijolito-receipts
description: Use when the user wants to record an agreement or moment between parties as a Frijolito receipt, or to check, verify, or validate a Frijolito receipt ID (FJ-… or FJ2-…) or receipt hash.
---

# Frijolito receipts

Frijolito keeps **signed receipts, not payments**. No money moves through these tools.

Two kinds of receipt prove different things. Never blur them:

- `FJ-` receipts are **self-reported**: the caller told Frijolito what happened and Frijolito signed that record. A valid one proves what was reported, by whom and when, and that the record is unchanged. It does not prove the event happened or that its claims are true.
- `FJ2-` receipts are **observed from an outside source**, such as a Shopify order event. Only these may be described as independently witnessed.

Tools (from the `frijolito-receipts` MCP server):

- `verify_receipt`: public, read-only. Pass exactly one of `receipt_id` or `receipt_hash`.
- `notarize_moment`: **write**, optional. It mints a permanent self-reported receipt and needs an API key, set in the plugin's settings.

## Verifying

Report the verdict plainly:

| Verdict | Meaning | What to tell the user |
|---|---|---|
| `VALID` | Registry hit, hash and signatures check out | The record is intact and Frijolito issued it. Summarize parties, moment_label, created_at, status, and say which kind it is (`FJ-` self-reported or `FJ2-` observed). |
| `INVALID` | The receipt fails a check | Do **not** trust it. Treat it as tampered or malformed and quote `detail`. |
| `UNKNOWN` | Well-formed, but this issuer never minted it (or it was deleted) | It cannot be confirmed. This is not the same as "fake", but it is not proof either. |

A `VALID` receipt whose `status` is `expired` or `revoked` was issued by Frijolito but no longer stands. Say so.

Receipt IDs look like `FJ-YYYYMMDD-NNN-xxxxxxxxxxxx` (notarized moments) or `FJ2-` followed by 64 hex characters (connector receipts, such as a Shopify order event). Receipt hashes are 64 lowercase hex characters; to look up an FJ2 receipt by hash, also pass `receipt_version: "2"`.

### Daily roots

A `VALID` verdict also carries `root`. Each UTC day, Frijolito signs one root over every receipt of that day (Ed25519 and SLH-DSA, both required) and anchors it in Bitcoin through OpenTimestamps.

- `root` present: the receipt is sealed in that day's root. Mention `root_seq` and `anchor_status` (`pending` means submitted to OpenTimestamps; `confirmed` means it is in a Bitcoin block).
- `root: null` with `root_reason: "not_yet_rooted"`: the receipt is valid but its day has not been sealed yet. This is normal for receipts from today.
- Any other `root_reason`: say the receipt itself is valid but the root proof could not be produced, and quote the reason.

## Notarizing

Minting is permanent, so:

1. Before calling `notarize_moment`, show the user exactly what will be recorded (parties with roles, moment_label, and which document is being hashed) and get a clear yes.
2. Prefer `document_hash` (sha256 of the exact agreed bytes) over `document_text`. To hash a local file: `shasum -a 256 <file>`. `document_text` is hashed server-side and never stored.
3. Set `witness_model` to your own model identity (for example `claude-opus-5-5`).
4. Evidence pointers need a real 64-char sha256. Never invent or abbreviate one.
5. **Never retry on your own.** If a call times out, the connection drops, or Frijolito answers with a server error, the outcome is unknown: a receipt may or may not exist. Tell the user that plainly, give them the `idempotency_key` if the result shows one, and try again only if they ask, with that same key. A new key can mint a second receipt. Never say a retry is safe.
6. After minting, give the user the `receipt_id` and `verify_url`.

## Errors

- `NOT_CONFIGURED`: no API key is set. Verifying still works. To notarize, the user requests a key from concierge@frijolito.app, adds it in the plugin's settings (`/plugin` → Frijolito Receipts → Configure), and restarts Claude.
- `LIVE_KEY_BLOCKED`: a production key is set. Minting production receipts needs the plugin's "Allow production receipts" setting turned on; confirm with the user first.
- `401 UNAUTHORIZED`: the key is missing, revoked, or lacks the `notarize` scope.
- `422 UNPROCESSABLE`: a semantic rule failed, or an idempotency key was reused with a different payload. Quote `detail`; do not loop.
