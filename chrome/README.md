# Frijolito for Chrome

Ask Frijolito anything and verify a Frijolito receipt from any page.

- Click the bean in the toolbar to open Frijolito in the side panel.
- Type a question, or paste a receipt ID (`FJ-…`, `FJ2-…`) or hash to check it.
- Select text on any page and right-click: **Ask Frijolito about "…"** or **Verify with Frijolito**.

## Privacy

The extension never reads the pages you visit. It only sends what you type or select to Frijolito's two public endpoints, `coreConcierge` and `verify_receipt` on `frijolito.app`. The conversation is kept in the browser session and cleared when Chrome closes. No account and no key.

## Try it

1. Open `chrome://extensions` and turn on **Developer mode**.
2. Click **Load unpacked** and choose this `chrome` folder.

## Publish

Zip the contents of this folder (`cd chrome && zip -r ../frijolito-chrome.zip .`) and upload it in the [Chrome Web Store developer dashboard](https://chrome.google.com/webstore/devconsole). Permissions to justify: `sidePanel` (the chat), `contextMenus` (right-click ask and verify), `storage` (keep the conversation for the session), and `frijolito.app` (the two public endpoints).
