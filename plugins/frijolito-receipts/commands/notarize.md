---
description: Notarize a moment and mint a Frijolito receipt
argument-hint: <what was agreed, who the parties are, and the document or file>
---

Prepare a Frijolito receipt for: $ARGUMENTS

1. Work out the parties (label and role for each), a short `moment_label`, and the document. If a local file is named, compute its sha256 with `shasum -a 256` and use it as `document_hash`.
2. Ask for anything missing. Do not guess parties or roles.
3. Show the user the exact payload that will be recorded and wait for a clear yes.
4. Only then call `notarize_moment`, with `witness_model` set to your model identity.
5. Return the `receipt_id`, `verify_url`, and the `idempotency_key` used.

Follow the frijolito-receipts skill for retries and error handling.
