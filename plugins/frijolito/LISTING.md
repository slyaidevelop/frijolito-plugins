# Listing copy

The text and images for a directory listing. Nothing here is loaded by the plugin.

| Field | Value |
|---|---|
| Name | Frijolito |
| Slug | `frijolito` |
| Tagline | Ask, follow and verify. Quietly. |
| Short description | Ask Frijolito, file and follow requests with the team, and verify signed receipts. Verifying needs no account and no key. |
| Category | Productivity |
| Homepage | https://frijolito.app |
| Support | concierge@frijolito.app |
| Privacy | https://frijolito.app/privacy |
| Terms | https://frijolito.app/terms |
| Icon | `assets/icon.png` (512 × 512), source `assets/icon.svg` |

## Long description

Frijolito is a build companion and a notary. This plugin brings both into Claude Code.

**Ask.** `/frijolito:ask` talks to Frijolito, the concierge. `/frijolito:request` files work with the team, after showing you exactly what will be sent. `/frijolito:status` lists your requests and projects, with anything waiting on you first. You sign in once in your browser, and the plugin only ever sees your own account.

**Verify.** `/frijolito:verify` checks any Frijolito receipt and gives a plain verdict: VALID, INVALID or UNKNOWN. It is free and needs no account and no key. Claude says what a receipt proves and what it doesn't.

**Record, if you want to.** With a key, you can record a moment as a signed, self-reported receipt. Nothing is minted without your yes. Optional hook receipts can leave a signed record of each action Claude Code takes. They are off until you turn them on, and they never block a call.

Frijolito keeps signed receipts, not payments. No money moves through this plugin.

## Images

1600 × 1000, in `assets/listing/`. They are illustrations with sample data, and each one says so.

1. `1-ask.png`: Ask Frijolito, right where you work.
2. `2-verify.png`: Check any receipt in one line.
3. `3-receipt.png`: Signed receipts, not payments.

To change them, edit `assets/listing/listing.html` and run `node assets/listing/render.cjs`.
