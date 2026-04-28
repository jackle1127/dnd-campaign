---
name: dndbeyond-nav
description: Navigate the D&D Beyond website via Playwright to create characters, level them up, upload portraits, manage spells, and interact with the character builder. Use this skill for any D&D Beyond UI interaction including character creation, leveling up, portrait upload, managing spells, or editing character sheet fields.
---

# D&D Beyond Navigation Skill

All D&D Beyond UI interaction is done via Playwright MCP. Read the relevant reference before starting.

## References

- **UI Patterns** - `references/ui-patterns.md` — comboboxes, option lists, dropdowns, React quirks
- **Character Creation** - `references/character-creation.md` — full builder walkthrough step-by-step
- **Portrait Upload** - `references/portrait-upload.md` — generating and uploading AI portraits
- **Level Up** - `references/level-up.md` — leveling a character via the builder

## Key Rules

- **Always read the relevant reference first** - don't wing UI patterns from memory
- **The builder auto-saves** - no explicit save button needed between steps
- **Bearer token expires in 5 minutes** - get a fresh one right before any API call
- **File uploads** are restricted to workspace roots - copy files there first
- **Never use `browser_file_upload` directly** - click `input[type="file"]` first to open the chooser, then call `browser_file_upload`
