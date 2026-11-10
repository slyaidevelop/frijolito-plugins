# Frijolito

Ask Frijolito, follow your requests, and verify signed receipts from Claude Code.

![Asking Frijolito from Claude Code](assets/listing/1-ask.png)

---

## Install

```
/plugin install frijolito --marketplace slyaidevelop/frijolito-plugins
```

On older versions of Claude Code, run `/plugin marketplace add slyaidevelop/frijolito-plugins`, then `/plugin install frijolito@frijolito`.

## First run

Nothing to set up. Verifying a receipt works right away, with no account and no key. The first time you ask Frijolito something about your account, your browser opens once to sign in.

## Commands

| Command | What it does | Needs |
|---|---|---|
| `/frijolito:ask` | Talk to Frijolito, the concierge | Sign-in |
| `/frijolito:request` | File a request with the team. Claude shows it to you first and waits for your yes | Sign-in |
| `/frijolito:status` | Your requests and open projects, with anything waiting on you at the top | Sign-in |
| `/frijolito:verify` | Check a receipt ID or hash: **VALID**, **INVALID** or **UNKNOWN** | Nothing |

You can also just ask in plain language: *"Check receipt FJ-20261014-001-f4094fcae7d7."*

## Receipts

[Frijolito](https://frijolito.app) keeps signed receipts for agents and people. A receipt records a moment that a person or an agent reported, such as an agreement, an approval or a handoff, and Frijolito signs it so anyone can check later that the record is intact and that Frijolito issued it. Frijolito never moves money, holds balances or stores your documents.

There are two kinds of receipt, and they prove different things:

- **`FJ-` receipts** are self-reported. The caller tells Frijolito what happened and Frijolito signs that record. A valid `FJ-` receipt proves what was reported, by whom and when, and that it hasn't been changed since. It does not prove that the event happened or that its claims are true.
- **`FJ2-` receipts** come from a connector that reports an outside event, such as a Shopify order event, instead of from the caller. The prefix alone doesn't prove independent observation: Claude reports what each receipt's own evidence says about its source, separately from whether its signature checks out.

![Verifying a receipt in one line](assets/listing/2-verify.png)

A VALID verdict means the record is intact and Frijolito issued it. It also says whether the receipt is sealed in a daily root anchored in Bitcoin.

The images on this page are illustrations. The receipt they show is a real demo receipt that anyone can verify.

## What it connects to

Nothing runs on your computer. The plugin holds instructions for Claude and the addresses of two Frijolito servers:

| Server | Address | Sign-in |
|---|---|---|
| Your Frijolito account | `https://frijolito.app/api/mcp` | Once, in your browser |
| Receipt verifier | `https://frijolito.app/api/functions/frijolitoVerifyMcp` | None |

The account server only ever sees your own account. Filing a request does not approve, build or charge anything. If the account tools go missing, reconnect **frijolito** (in Claude Code, run `/mcp`).

## Safety by design

- **Nothing is sent without your yes.** Before filing a request, Claude shows you the title and summary and waits.
- **Verifying is read-only.** It needs no account and changes nothing.
- **No keys.** The plugin has no settings and asks for no API key, password or token.
- **No recording.** This plugin does not create receipts. Developers who want to record receipts from Claude Code can use the separate Frijolito Receipts plugin in the same repository.

## Data handling

This plugin talks only to `https://frijolito.app`.

- **Asking, requests and status** go to your own Frijolito account after you sign in: what you type, and the title and summary of a request you approve.
- **Verifying** sends the receipt ID or hash you provide. The verifier's own [privacy page](https://frijolito.app/connectors/verify/privacy) says what it keeps.
- Receipts are public by design: anyone with a receipt ID can verify it and see what it records.
- No data is sent to anyone other than Frijolito, and the plugin stores nothing on your computer.

See Frijolito's [privacy policy](https://frijolito.app/privacy) and [terms](https://frijolito.app/terms).

## Support

Questions, key requests or problems: **concierge@frijolito.app** · [frijolito.app](https://frijolito.app)

## License

[MIT](LICENSE) © 2026 Frijolito
