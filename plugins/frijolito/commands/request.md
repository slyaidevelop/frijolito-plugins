---
description: File a request with the Frijolito team (asks before sending)
argument-hint: <what you need>
---

File this with Frijolito: $ARGUMENTS

1. Turn it into a short `title` (a few words) and a plain `summary` of the outcome wanted. Ask if the outcome is unclear.
2. Show the user the title and summary and wait for a clear yes.
3. Call `invoke_file_frijolito_request` with a new `client_ref`. On a retry, reuse the same `client_ref`.
4. Confirm it landed and say they can follow it with `/frijolito:status`. Filing does not approve, build or charge anything.

If the tool is missing or answers 401, follow "Signing in" in the frijolito skill.
