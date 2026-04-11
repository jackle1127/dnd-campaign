---
name: dnd-beyond-campaign
description: Scrape all D&D Beyond character sheets for the Podcast campaign and update the Google Sheet tracker. Also handles D&D Beyond character creation and campaign management via Playwright. Use this skill whenever the user wants to check on the party, update character stats, see who leveled up, check HP or spells, asks anything like "how's the party doing", "check the campaign", "update character sheets", "what level is everyone", "check the Podcast campaign", "create a character on D&D Beyond", or "add a character to the campaign".
---

# D&D Beyond Campaign Skill

Two main workflows — read the relevant reference before starting:

## Workflow 1: Update the Campaign Tracker

Scrape all player characters and update the Google Sheet.

**Reference:** `references/campaign-tracker.md`

Steps: get Bearer token → fetch all characters → run Python script to update sheet.

## Workflow 2: Create a Character

Build a new character on D&D Beyond via Playwright.

**Reference:** `references/character-creation.md`

Key rule: **always create from within the campaign** (`/campaigns/7009985/create-unassigned-character`) so the campaign owner's purchased content (PHB, etc.) is available from the start.
