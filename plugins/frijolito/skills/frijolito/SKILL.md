---
name: frijolito
description: Use when the user wants to talk to Frijolito, file or follow a request with the Frijolito team, read their Frijolito context or projects, or asks how to set up or sign in to the Frijolito plugin.
---

# Frijolito

Frijolito is a build companion and a notary. This plugin has two parts:

- The `frijolito` MCP server is the signed-in person's own Frijolito account: the concierge, their requests, their context. It never reads anyone else's data.
- The `frijolito-receipts` MCP server verifies receipts with no account and no key. See the frijolito-receipts skill for receipts.

## First run

Keep it to one line: verifying a receipt works right away, and anything about their account opens a browser once to sign in. Do not walk through settings unless asked. No key is needed for asking, requests, status or verifying.

## Signing in

The first call to a `frijolito` tool opens a browser to sign in. If the tools are missing or answer 401, tell the user to run `/mcp`, choose **frijolito** and authenticate, then try again. Never ask for a password, a code or a token in the conversation.

## Account tools

| Tool | What it does | Writes? |
|---|---|---|
| `invoke_frijolito_guide` | Public facts about Frijolito and each place | No |
| `invoke_my_frijolito_context` | The person's approved profile, priorities, constraints and open projects | No |
| `invoke_my_frijolito_requests` | Their recent requests and each one's state | No |
| `invoke_file_frijolito_request` | Files new work on the request queue | Yes |
| `message_frijolito` | Talks to Frijolito, the concierge | Yes |

The server may offer more tools than these. Read each tool's own description before using it.

## Rules

- Before any tool that writes, show exactly what will be sent and wait for a clear yes.
- When filing a request, pass a `client_ref` and reuse it on a retry, so a retry never files twice.
- Filing a request does not approve, build or charge anything. Say so if asked.
- When drafting for the person, use the voice in `invoke_my_frijolito_context` and avoid their listed phrases.
- Answer in short, plain sentences. No hype.

## Hook receipts (optional, off by default)

With a hook receipt key in the plugin's settings, each Bash, Edit, Write and MCP call in Claude Code opens a Frijolito receipt (`FJ-HK-…`) and closes it with the result's hash. Claude Code's hook event for the call is sent; Frijolito keeps hashes and a one-line redacted summary, not the input or the result. These receipts are self-reported: Claude Code describes the call and Frijolito signs that description. Nothing witnesses the call from outside, and Frijolito never blocks or changes a call. Without a key, nothing is sent. To turn them off, clear the key in `/plugin` > Frijolito > Configure.
