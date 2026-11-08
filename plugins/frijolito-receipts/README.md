<p align="center">
  <img src="assets/logo.png" alt="Frijolito logo" width="160">
</p>

<h1 align="center">Frijolito Receipts</h1>

<p align="center">
  Notarize moments and verify signed, tamper-evident receipts from Claude.
</p>

---

[Frijolito](https://frijolito.app) keeps signed receipts for agents and people. A receipt records a moment that a person or an agent reported, such as an agreement, an approval or a handoff, and Frijolito signs it so anyone can check later that the record is intact and that Frijolito issued it. Frijolito never moves money, holds balances or stores your documents.

There are two kinds of receipt, and they prove different things:

- **`FJ-` receipts** are self-reported. The caller tells Frijolito what happened and Frijolito signs that record. A valid `FJ-` receipt proves what was reported, by whom and when, and that it hasn't been changed since. It does not prove that the event happened or that its claims are true.
- **`FJ2-` receipts** come from a connector that reports an outside event, such as a Shopify order event, instead of from the caller. The prefix alone doesn't prove independent observation: Claude reports what each receipt's own evidence says about its source, separately from whether its signature checks out.

This plugin is for **Claude Code**. It runs a small local Python server on your computer, so it is not proven to run in Claude on the web (claude.ai), and it hasn't been tested in Cowork.

## What you can do

| | What it does | Needs an API key |
|---|---|---|
| **Verify a receipt** | Check any receipt ID (`FJ-…` or `FJ2-…`) or receipt hash and get a verdict: **VALID**, **INVALID** or **UNKNOWN**, plus who the parties were, what was recorded and when, and whether it is sealed in a daily root anchored in Bitcoin. VALID means the record is intact and Frijolito issued it. | No |
| **Notarize a moment** (optional) | Record what the parties say was agreed and get back a signed, self-reported `FJ-` receipt ID and a public verification link. | Yes |

Just ask in plain language: *"Check receipt FJ-20261014-001-f4094fcae7d7."* or *"Record that Acme and Beta agreed to the attached terms."*

In Claude Code you can also use the slash commands:

- `/verify-receipt <receipt ID or hash>`
- `/notarize <what was agreed, between whom>`

## Safety by design

- **Nothing is minted without your yes.** Before notarizing, Claude shows you exactly what will be recorded and waits for confirmation.
- **Your document stays yours.** Claude sends only a SHA-256 fingerprint of the document when it can. If document text is sent instead, Frijolito hashes it and discards the text immediately.
- **Retries need care.** You can pass an idempotency key, and Frijolito replays the original receipt when the same key is sent again. If you don't pass one, each call gets a new key, so two calls without a key are not idempotent. If a call times out or the connection drops before Frijolito answers, the outcome is **unknown**: a receipt may or may not have been minted. The result then says `outcome_unknown` and gives back the exact key that was sent. Claude never retries on its own. If you choose to try again, reuse that key; whether Frijolito replays depends on its server still holding the first attempt, so it is not a promise of no duplicates. A new key can mint a second receipt.
- **Test keys can't make production receipts.** `fj_test_` keys mint demo receipts that are clearly marked and can never verify as production. `fj_live_` keys are refused unless you explicitly allow them.
- **Your API key is never shown.** It is kept in Claude's secure credential store and never appears in Claude's output.

## Getting an API key

Verifying receipts is free and needs no key.

To notarize, request a key from **concierge@frijolito.app**. You'll receive a test key (`fj_test_…`) to try things out, and a live key (`fj_live_…`) when you're ready for production receipts.

Then add it in Claude Code: run `/plugin`, open **Frijolito Receipts**, choose **Configure**, and paste the key into **Frijolito API key**. Claude stores it in your system's secure credential store, never in a plain settings file. Restart Claude afterwards.

### Settings

| Setting | Default | Purpose |
|---|---|---|
| **Frijolito API key** | (none) | Your API key. Only needed to notarize. Stored securely. |
| **Allow production receipts** | Off | Turn on to let an `fj_live_` key mint production receipts. |

## Requirements

- Claude Code.
- Python 3.9 or newer (preinstalled on macOS). No extra packages.

## Data handling

This plugin talks only to `https://frijolito.app`.

- **Verifying** sends the receipt ID or hash you provide.
- **Notarizing** sends the party labels and roles, a short label for the moment, the name of the AI model that recorded it, and either a SHA-256 fingerprint of the document or the document text (which Frijolito hashes and discards right away). Optional evidence pointers and a reference ID are sent only if you provide them.
- Receipts are public by design: anyone with a receipt ID can verify it and see its parties and label. Don't put anything in a party label or moment label that you wouldn't want a verifier to see.
- No data is sent to anyone other than Frijolito, and the plugin stores nothing on your computer. Your API key is kept in Claude's secure credential store.

See Frijolito's [privacy policy](https://frijolito.app/privacy) and [terms](https://frijolito.app/terms).

## Support

Questions, key requests or problems: **concierge@frijolito.app** · [frijolito.app](https://frijolito.app)

## License

[MIT](LICENSE) © 2026 Frijolito
