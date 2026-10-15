---
name: frijolito-receipts
description: Use when the user wants to notarize, witness, or record an agreement or moment between parties as a Frijolito receipt, or to check, verify, or validate a Frijolito receipt ID (FJ-…) or receipt hash.
---

# Frijolito receipts

Frijolito is a **notary, not a payment rail**. It witnesses a moment between parties and returns a signed, publicly verifiable receipt. No money moves through these tools.

Tools (from the `frijolito-receipts` MCP server):

- `verify_receipt`: public, read-only. Pass exactly one of `receipt_id` or `receipt_hash`.
- `notarize_moment`: **write**. It mints a permanent receipt and needs an API key, set in the plugin's settings.

## Verifying

Report the verdict plainly:

| Verdict | Meaning | What to tell the user |
|---|---|---|
| `VALID` | Registry hit, hash and signatures check out | The receipt is genuine. Summarize parties, moment_label, created_at, status. |
| `INVALID` | The receipt fails a check | Do **not** trust it. Treat it as tampered or malformed and quote `detail`. |
| `UNKNOWN` | Well-formed, but this issuer never minted it (or it was deleted) | It cannot be confirmed. This is not the same as "fake", but it is not proof either. |

A `VALID` receipt whose `status` is `expired` or `revoked` was genuine but no longer stands. Say so.

Receipt IDs look like `FJ-YYYYMMDD-NNN-xxxxxxxxxxxx` (notarized moments) or `FJ2-` followed by 64 hex characters (connector receipts, such as a Shopify order event). Receipt hashes are 64 lowercase hex characters; to look up an FJ2 receipt by hash, also pass `receipt_version: "2"`.

### Daily roots

A `VALID` verdict also carries `root`. Each UTC day, Frijolito signs one root over every receipt of that day (Ed25519 and SLH-DSA, both required) and anchors it in Bitcoin through OpenTimestamps.

- `root` present: the receipt is sealed in that day's root. Mention `root_seq` and `anchor_status` (`pending` means submitted to OpenTimestamps; `confirmed` means it is in a Bitcoin block).
- `root: null` with `root_reason: "not_yet_rooted"`: the receipt is genuine but its day has not been sealed yet. This is normal for receipts from today.
- Any other `root_reason`: say the receipt itself is valid but the root proof could not be produced, and quote the reason.

## Notarizing

Minting is permanent, so:

1. Before calling `notarize_moment`, show the user exactly what will be recorded (parties with roles, moment_label, and which document is being hashed) and get a clear yes.
2. Prefer `document_hash` (sha256 of the exact agreed bytes) over `document_text`. To hash a local file: `shasum -a 256 <file>`. `document_text` is hashed server-side and never stored.
3. Set `witness_model` to your own model identity (for example `claude-opus-5-5`).
4. Evidence pointers need a real 64-char sha256. Never invent or abbreviate one.
5. If a call fails or times out, **retry with the same `idempotency_key`** returned by the previous attempt. A new key could mint a duplicate.
6. After minting, give the user the `receipt_id` and `verify_url`.

## Errors

- `NOT_CONFIGURED`: no API key is set. Verifying still works. To notarize, the user requests a key from concierge@frijolito.app, adds it in the plugin's settings (`/plugin` → Frijolito Receipts → Configure), and restarts Claude.
- `LIVE_KEY_BLOCKED`: a production key is set. Minting production receipts needs the plugin's "Allow production receipts" setting turned on; confirm with the user first.
- `401 UNAUTHORIZED`: the key is missing, revoked, or lacks the `notarize` scope.
- `422 UNPROCESSABLE`: a semantic rule failed, or an idempotency key was reused with a different payload. Quote `detail`; do not loop.
