# Frijolito plugin marketplace

## frijolito-receipts

Claude Code plugin for the Frijolito core app's notary API (`https://frijolito.app/functions/...`).

- `/verify-receipt <FJ-… id or hash>`: public, read-only verification (VALID / INVALID / UNKNOWN)
- `/notarize <description>`: mints a receipt after showing the payload and getting a yes
- Skill `frijolito-receipts`: lets Claude use the tools on its own when receipts come up

### Install

```bash
/plugin marketplace add <path-or-git-url-of-this-repo>
/plugin install frijolito-receipts@frijolito
```

### Configure (only needed for notarizing)

```bash
export FRIJOLITO_API_KEY=fj_test_...        # needs the notarize scope
# export FRIJOLITO_ALLOW_LIVE=1             # required to mint with an fj_live_ key
# export FRIJOLITO_BASE_URL=https://...     # default https://frijolito.app
```

Restart Claude Code after changing these. Requires `python3` (3.9+); no packages.
