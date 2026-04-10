# D&D Campaign Repo

Campaign content lives in subfolders by campaign name.

## Campaigns

- [this-is-bullcrit/](this-is-bullcrit/) - active campaign

## Prerequisites

Install these before running campaign skills:

```bash
# Python packages
python -m pip install google-api-python-client google-auth playwright

# Playwright browsers (Chromium only)
python -m playwright install chromium

# Playwright MCP server (user scope, applies to all projects)
claude mcp add --scope user playwright npx "@playwright/mcp@latest"
```

## Session Notes

Session notes live in `this-is-bullcrit/sessions/`. Each session is a file named with the date and a short highlight of the session:

```
2026-04-10-escaped-vaultspire.md
```

The filename is finalized when the session wraps - start with just the date, rename once the highlight is clear.

Always check system time (`date` / `Get-Date`) to confirm the current date before creating a session file.

## Instructions

- All campaign info lives in this repo. Do not use any external memory systems.
- Always read the relevant files in this repo to get up-to-date context before answering questions or making changes.
- Multiple agents may work on this campaign - treat this repo as the single source of truth.
