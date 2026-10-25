# Frijolito

Frijolito is a build companion and a notary. The `frijolito` MCP server connects to the signed-in customer's own Frijolito account. It never reads anyone else's data.

## Tools

| Tool | What it does | Writes? |
|---|---|---|
| `invoke_frijolito_guide` | Public facts about Frijolito and each place (Core, Portal, Social, Motion, Labs) | No |
| `invoke_my_frijolito_context` | The customer's approved profile, priorities, constraints and open projects | No |
| `invoke_my_frijolito_requests` | The customer's recent requests and their state | No |
| `invoke_verify_frijolito_receipt` | Checks a receipt: VALID, INVALID or UNKNOWN | No |
| `invoke_file_frijolito_request` | Files new work on the request queue | Yes |
| `invoke_add_build_note` | Adds one note to a project's open work | Yes |
| `invoke_request_specialist_review` | Brings a specialist onto a project | Yes |
| `message_frijolito` | Talks to Frijolito, the concierge | Yes |

## Rules

- Before any tool that writes, show the user exactly what will be sent and wait for a clear yes.
- When filing a request, pass a `client_ref` and reuse it on retry, so a retry never files twice.
- Filing a request does not approve, build or charge anything. Say so if the user asks.
- Use the customer's voice from `invoke_my_frijolito_context` when drafting for them, and avoid their listed phrases.
- Answer in short, plain sentences. No hype.

## Receipts

Pass exactly one of `receipt_id` (`FJ-…` or `FJ2-…`) or `receipt_hash` (64 lowercase hex). Lead with the verdict.

- `VALID`: the receipt is genuine. Give parties, moment, date and status. If the status is `expired` or `revoked`, it was genuine but no longer stands.
- `INVALID`: do not trust it. Quote the detail.
- `UNKNOWN`: well formed, but Frijolito never minted it. Not proof either way.

`FJ2-` receipts are witnessed from outside (for example a Shopify order). `FJ-` receipts are reported by an app and signed by Frijolito; never call them independently witnessed.

## Sign in

The first call opens a browser to sign in to Frijolito. If tools are missing or return 401, run `/mcp auth frijolito`.
