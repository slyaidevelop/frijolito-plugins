---
name: frijolito
description: Use when the user wants to talk to Frijolito, file or follow a request with the Frijolito team, read their Frijolito context or projects, check or verify a Frijolito receipt ID (FJ-… or FJ2-…) or receipt hash, or asks how to sign in to the Frijolito plugin.
---

# Frijolito

Frijolito is a build companion and a notary. This plugin connects to two Frijolito servers:

- `frijolito` is the signed-in person's own Frijolito account: the concierge, their requests, their context. It never reads anyone else's data.
- `frijolito-verify` checks receipts. It is public and read-only, with no sign-in and no key.

## First run

Keep it to one line: verifying a receipt works right away, and anything about their account opens a browser once to sign in. Do not walk through settings unless asked.

## Signing in

The first call to a `frijolito` tool opens a browser to sign in. If the tools are missing or answer 401, tell the user to reconnect **frijolito** (in Claude Code: run `/mcp`, choose **frijolito** and authenticate), then try again. Never ask for a password, a code or a token in the conversation.

## Account tools

| Tool | What it does | Writes? |
|---|---|---|
| `invoke_frijolito_guide` | Public facts about Frijolito and each place | No |
| `invoke_my_frijolito_context` | The person's approved profile, priorities, constraints and open projects | No |
| `invoke_my_frijolito_requests` | Their recent requests and each one's state | No |
| `invoke_file_frijolito_request` | Files new work on the request queue | Yes |
| `message_frijolito` | Talks to Frijolito, the concierge | Yes |

The server may offer more tools than these. Read each tool's own description before using it.

## Rules

- Before any tool that writes, show exactly what will be sent and wait for a clear yes.
- When filing a request, pass a `client_ref` and reuse it on a retry, so a retry never files twice.
- Filing a request does not approve, build or charge anything. Say so if asked.
- When drafting for the person, use the voice in `invoke_my_frijolito_context` and avoid their listed phrases.
- Answer in short, plain sentences. No hype.

## Receipts

Frijolito keeps **signed receipts, not payments**. No money moves through these tools.

Verify with `verify_frijolito_receipt` on the `frijolito-verify` server. Pass exactly one of `receipt_id` (`FJ-…` or `FJ2-…`) or `receipt_hash` (64 lowercase hex).

Two kinds of receipt prove different things. Never blur them:

- `FJ-` receipts are **self-reported**: the caller told Frijolito what happened and Frijolito signed that record. A valid one proves what was reported, by whom and when, and that the record is unchanged. It does not prove the event happened or that its claims are true.
- `FJ2-` receipts come from a **connector that reports an outside event**, such as a Shopify order event. The prefix alone does not make a receipt independently witnessed. Describe how a particular receipt was observed only from what its own fields show, and keep that apart from the signature check, which proves integrity only.

Report the verdict plainly:

| Verdict | Meaning | What to tell the user |
|---|---|---|
| `VALID` | Registry hit, hash and signatures check out | The record is intact and Frijolito issued it. Say what was recorded and when, and which kind it is. |
| `INVALID` | The receipt fails a check | Do **not** trust it. Treat it as tampered or malformed and quote the detail. |
| `UNKNOWN` | Well-formed, but Frijolito never minted it (or it was deleted) | It cannot be confirmed. This is not the same as "fake", but it is not proof either. |

A `VALID` receipt that is expired or revoked was issued by Frijolito but no longer stands. Say so. A demo receipt is a test record: say it is a demo.

Each UTC day Frijolito signs one root over that day's receipts and anchors it in Bitcoin. If the answer says the receipt is in a daily root, mention it. A receipt from today may not be sealed yet, which is normal.

This plugin does not record new receipts.
