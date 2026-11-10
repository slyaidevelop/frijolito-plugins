---
description: Verify a Frijolito receipt by ID or hash (no account, no key)
argument-hint: <FJ-… or FJ2-… receipt ID, or 64-char receipt hash>
---

Verify this Frijolito receipt with the `verify_frijolito_receipt` tool from the `frijolito-verify` MCP server: $ARGUMENTS

If it starts with `FJ-` or `FJ2-`, pass it as `receipt_id`. If it is 64 hex characters, pass it as `receipt_hash`. Pass exactly one. If nothing was given, ask for one.

Lead with the verdict (VALID, INVALID or UNKNOWN), then the key facts: what was recorded, when, whether it is self-reported or came from a connector, and whether it is sealed in a daily root. Follow "Receipts" in the frijolito skill for how to explain each verdict. This needs no sign-in.
