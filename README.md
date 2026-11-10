<p align="center">
  <img src="plugins/frijolito/assets/icon.png" alt="Frijolito" width="120">
</p>

<h1 align="center">Frijolito plugins for Claude</h1>

<p align="center">
  <a href="https://frijolito.app">Frijolito</a> plugins for Claude Code, Gemini and Chrome.
</p>

---

## Plugins

| Plugin | What it does |
|---|---|
| [**Frijolito**](plugins/frijolito) | Claude. Ask Frijolito, file and follow requests with the team, and verify signed receipts. Nothing runs on your computer, and verifying needs no account and no key. |
| [**Frijolito Receipts**](plugins/frijolito-receipts) | Claude Code, for developers. Record signed, self-reported receipts with an API key, and optionally leave a receipt for each tool call. Runs a small local program. |
| [**Frijolito for Chrome**](chrome) | Ask Frijolito anything and verify a receipt from any page, in Chrome's side panel. |
| [**frijolito** for Gemini](#gemini) | Verify receipts, read your Frijolito context, and file or follow requests with the team, from Gemini CLI. |

## Install

In Claude Code:

```
/plugin install frijolito --marketplace slyaidevelop/frijolito-plugins
```

On older versions, run `/plugin marketplace add slyaidevelop/frijolito-plugins`, then `/plugin install frijolito@frijolito`.

| Command | What it does |
|---|---|
| `/frijolito:ask` | Talk to Frijolito, the concierge |
| `/frijolito:request` | File a request with the team (asks before sending) |
| `/frijolito:status` | Your requests and open projects |
| `/frijolito:verify` | Check a receipt by ID or hash, no account needed |

See the [plugin README](plugins/frijolito/README.md) for sign-in and data handling, and [Frijolito Receipts](plugins/frijolito-receipts/README.md) for recording receipts and hook receipts.

## Gemini

```
gemini extensions install https://github.com/slyaidevelop/frijolito-plugins
```

The first Frijolito call opens your browser to sign in. Then:

| Command | What it does |
|---|---|
| `/frijolito:ask` | Talk to Frijolito, the concierge |
| `/frijolito:request` | File a request with the team (asks before sending) |
| `/frijolito:status` | Your requests and open projects |
| `/frijolito:verify` | Check a receipt by ID or hash |

It connects to Frijolito's MCP server at `https://frijolito.app/api/mcp` and only ever sees your own account. Nothing is approved, built or charged by filing a request. If tools go missing, run `/mcp auth frijolito`.

## Chrome

Load the [`chrome`](chrome) folder unpacked from `chrome://extensions`, or install it from the Chrome Web Store once it is listed. See the [Chrome README](chrome/README.md).

## Support

concierge@frijolito.app · [frijolito.app](https://frijolito.app)

## License

[MIT](LICENSE) © 2026 Frijolito
