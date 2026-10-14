<p align="center">
  <img src="assets/logo.png" alt="Frijolito logo" width="160">
</p>

<h1 align="center">Frijolito Receipts</h1>

<p align="center">
  Notarize moments and verify signed, tamper-evident receipts from Claude.
</p>

---

[Frijolito](https://frijolito.app) is a notary for agents and people. It witnesses a moment between parties, such as an agreement, an approval or a handoff, and returns a **signed receipt** that anyone can verify later. Frijolito never moves money, holds balances or stores your documents.

This plugin brings Frijolito into Claude, Cowork and Claude Code.

## What you can do

| | What it does | Needs an API key |
|---|---|---|
| **Verify a receipt** | Check any receipt ID (`FJ-…`) or receipt hash and get a verdict: **VALID**, **INVALID** or **UNKNOWN**, plus who the parties were, what was recorded and when. | No |
| **Notarize a moment** | Record an agreement between parties and get back a receipt ID and a public verification link. | Yes |

Just ask in plain language: *"Is receipt FJ-20261014-001-f4094fcae7d7 legit?"* or *"Notarize that Acme and Beta agreed to the attached terms."*

In Claude Code you can also use the slash commands:

- `/verify-receipt <receipt ID or hash>`
- `/notarize <what was agreed, between whom>`

## Safety by design

- **Nothing is minted without your yes.** Before notarizing, Claude shows you exactly what will be recorded and waits for confirmation.
- **Your document stays yours.** Claude sends only a SHA-256 fingerprint of the document when it can. If document text is sent instead, Frijolito hashes it and discards the text immediately.
- **No accidental duplicates.** Every notarization carries an idempotency key, so a retry replays the original receipt instead of minting a second one.
- **Test keys can't make production receipts.** `fj_test_` keys mint demo receipts that are clearly marked and can never verify as production. `fj_live_` keys are refused unless you explicitly allow them.
- **Your API key is never shown.** It is read locally and never appears in Claude's output.

## Getting an API key

Verifying receipts is free and needs no key.

To notarize, request a key from **concierge@frijolito.app**. You'll receive a test key (`fj_test_…`) to try things out, and a live key (`fj_live_…`) when you're ready for production receipts.

Then save the key in a private file on your computer:

```bash
mkdir -p ~/.config/frijolito && chmod 700 ~/.config/frijolito
printf '%s\n' 'fj_test_YOUR_KEY_HERE' > ~/.config/frijolito/api_key
chmod 600 ~/.config/frijolito/api_key
```

Or set it as an environment variable instead:

```bash
export FRIJOLITO_API_KEY=fj_test_YOUR_KEY_HERE
```

Restart Claude after adding the key.

### Settings

| Variable | Default | Purpose |
|---|---|---|
| `FRIJOLITO_API_KEY` | (none) | Your API key. Takes priority over the key file. |
| `FRIJOLITO_API_KEY_FILE` | `~/.config/frijolito/api_key` | Where to read the key from. |
| `FRIJOLITO_ALLOW_LIVE` | `0` | Set to `1` to allow minting production receipts with an `fj_live_` key. |
| `FRIJOLITO_BASE_URL` | `https://frijolito.app` | The Frijolito API address. |

## Requirements

- Python 3.9 or newer (preinstalled on macOS). No extra packages.

## Data handling

This plugin talks only to `https://frijolito.app`.

- **Verifying** sends the receipt ID or hash you provide.
- **Notarizing** sends the party labels and roles, a short label for the moment, the name of the AI model acting as witness, and either a SHA-256 fingerprint of the document or the document text (which Frijolito hashes and discards right away). Optional evidence pointers and a reference ID are sent only if you provide them.
- Receipts are public by design: anyone with a receipt ID can verify it and see its parties and label. Don't put anything in a party label or moment label that you wouldn't want a verifier to see.
- No data is sent to anyone other than Frijolito, and the plugin stores nothing on your computer except the API key you put there.

## Support

Questions, key requests or problems: **concierge@frijolito.app** · [frijolito.app](https://frijolito.app)

## License

[MIT](LICENSE) © 2026 Frijolito
