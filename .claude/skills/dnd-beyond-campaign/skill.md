---
name: dnd-beyond-campaign
description: Scrape all D&D Beyond character sheets for the Podcast campaign and update the Google Sheet tracker or party markdown profiles. Also handles D&D Beyond character creation and campaign management via Playwright. Use this skill whenever the user wants to check on the party, update character stats, see who leveled up, check HP or spells, asks anything like "how's the party doing", "check the campaign", "update character sheets", "what level is everyone", "check the Podcast campaign", "create a character on D&D Beyond", or "add a character to the campaign".
---

# D&D Beyond Campaign Skill

**Before making any Google Doc updates, read `this-is-bullcrit/doc-formatting.md`** — it defines heading hierarchy, divider patterns, bolding conventions, and API patterns. Do not skip this step.

Three main workflows — read the relevant reference before starting:

## Workflow 1: Update the Campaign Tracker (Google Sheet)

Scrape all player characters and update the Google Sheet.

**Reference:** `references/campaign-tracker.md`

Steps: get Bearer token → fetch all characters → run Python script to update sheet.

## Workflow 2: Update Party Markdown Profiles

Scrape all characters and write/update markdown profile files in `this-is-bullcrit/party/` (relative to the repo root).

**Reference:** `references/campaign-tracker.md` (Steps 1-2 for token + fetch)

### File destinations

- Non-Thornecrest characters: create/overwrite `this-is-bullcrit/party/<slug>.md` (e.g. `rayne-willowshade.md`)
- Thornecrest characters (Kaelen, Darian): append a `## D&D Beyond Stats` section to their existing docs

### Profile format (standalone characters)

```markdown
# {Name}

**Player:** {player}  
**Class:** {Class Level}  
**Race:** {race}  
**Level:** {total_level}  
**HP:** {baseHitPoints}  
**Status:** Active / DECEASED

## Ability Scores

| STR | DEX | CON | INT | WIS | CHA |
|-----|-----|-----|-----|-----|-----|
| {val} ({mod}) | ... |

## Spells Known

- Spell Name

## Feats

- Feat Name

## Inventory

- Item Name

*Last updated: YYYY-MM-DD*
```

### Stat block format (appended to Thornecrest docs)

```markdown

---

## D&D Beyond Stats *(as of YYYY-MM-DD)*

**Class:** {class} | **Race:** {race} | **Level:** {level} | **HP:** {hp} | **Status:** Active/DECEASED

| STR | DEX | CON | INT | WIS | CHA |
|-----|-----|-----|-----|-----|-----|
| {val} ({mod}) | ... |

**Spells:** Spell1, Spell2, ...

**Inventory:** Item1, Item2, ...
```

### Python helpers

```python
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARTY_DIR = os.path.join(REPO_ROOT, 'this-is-bullcrit', 'party')

PLAYERS = {
    '152117866': 'Aricin',
    '153282190': 'jackle1127',
    '153546441': 'AngelFoxette',
    '153077893': 'TomThunder116',
    '152806918': 'Phxent23',
    '164100589': 'jackle1127',
}
DECEASED = {'153282190'}  # update if more characters die
THORNECREST_IDS = {'153282190', '164100589'}  # append to existing docs, don't overwrite

def mod(val):
    m = (val - 10) // 2
    return f'+{m}' if m >= 0 else str(m)

def get_stats(char):
    stats = {s['id']: s['value'] for s in char.get('stats', [])}
    bonuses = {s['id']: s['value'] or 0 for s in char.get('bonusStats', [])}
    overrides = {s['id']: s['value'] for s in char.get('overrideStats', [])}
    result = {}
    for sid in [1,2,3,4,5,6]:
        base = stats.get(sid, 10)
        val = overrides.get(sid) or (base + bonuses.get(sid, 0))
        result[sid] = val
    return result
```

Save `all_characters.json` to the repo root temporarily, then delete after processing.

## Workflow 3: Create a Character

Build a new character on D&D Beyond via Playwright.

**Reference:** `references/character-creation.md`

Key rule: **always create from within the campaign** (`/campaigns/7009985/create-unassigned-character`) so the campaign owner's purchased content (PHB, etc.) is available from the start.
