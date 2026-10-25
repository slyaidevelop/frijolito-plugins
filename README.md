<p align="center">
  <img src="plugins/frijolito-receipts/assets/logo.png" alt="Frijolito logo" width="140">
</p>

<h1 align="center">Frijolito plugins for Claude</h1>

<p align="center">
  Official <a href="https://frijolito.app">Frijolito</a> plugins for Claude, Cowork, Claude Code and Gemini.
</p>

---

## Plugins

| Plugin | What it does |
|---|---|
| [**frijolito-receipts**](plugins/frijolito-receipts) | Notarize moments and verify signed, tamper-evident receipts. Verification is free and needs no key. |
| [**frijolito** for Gemini](#gemini) | Verify receipts, read your Frijolito context, and file or follow requests with the team, from Gemini CLI. |

## Install

From the Claude plugin directory, search for **Frijolito Receipts**.

Or add this repository as a marketplace in Claude Code:

```
/plugin marketplace add slyaidevelop/frijolito-plugins
/plugin install frijolito-receipts@frijolito
```

See the [plugin README](plugins/frijolito-receipts/README.md) for API keys, settings and data handling.

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

## Support

concierge@frijolito.app · [frijolito.app](https://frijolito.app)

## License

[MIT](LICENSE) © 2026 Frijolito
