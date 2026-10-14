---
description: Verify a Frijolito receipt by ID or hash
argument-hint: <FJ-… receipt ID or 64-char receipt hash>
---

Verify this Frijolito receipt with the `verify_receipt` tool: $ARGUMENTS

If it starts with `FJ-`, pass it as `receipt_id`; if it is 64 hex characters, pass it as `receipt_hash`. If nothing was given, ask for one.

Lead with the verdict (VALID / INVALID / UNKNOWN), then the key facts: parties, moment, created date, status. Follow the frijolito-receipts skill for how to explain each verdict.
