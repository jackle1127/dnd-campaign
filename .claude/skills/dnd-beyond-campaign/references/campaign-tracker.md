# Campaign Tracker Reference

## Campaign & Sheet

- **Campaign URL:** https://www.dndbeyond.com/campaigns/7009985
- **Google Sheet:** https://docs.google.com/spreadsheets/d/1zkA0YN0AZyDxQXzRO_21hQIrOV-4vL7HkEWBEFJwcM0

### Characters

| ID | Name | Player | Status |
|----|------|--------|--------|
| 152117866 | Alarak Vaelor Veltharion | Aricin | Active (NO-FETCH) |
| 153282190 | Kaelen "Slick" Thornecrest | jackle1127 | DECEASED (3/28/2026) |
| 153546441 | Rayne Willowshade | AngelFoxette | Active |
| 153077893 | Szeth Stormblessed | TomThunder116 | Active |
| 152806918 | Vacir | Phxent23 | Active |
| 164100589 | Darian Thornecrest | jackle1127 | Active |
| 164913938 | Fib Noodlecork | jackle1127 | Active |

**NO-FETCH** = character sheet is in a different D&D Beyond campaign (not Podcast). The Bearer token from the Podcast campaign cannot fetch it. Skip these characters during scrapes — never delete or overwrite their party markdown files. Keep them in the party folder as-is.

## Step 1 - Get Bearer Token

Navigate to any character sheet (use Alarak's):
```
mcp__playwright__browser_navigate → https://www.dndbeyond.com/characters/152117866
```

If redirected to login, user must log in via Google. Then navigate again.

Capture the Bearer token:
```
mcp__playwright__browser_network_requests
  filter: "character-service.*character/152117866"
  requestHeaders: true
```

Extract the `authorization` header value (starts with `Bearer eyJ...`).

## Step 2 - Fetch All Character Data

```javascript
async () => {
  const token = 'Bearer eyJ...'; // from step 1
  const ids = [152117866, 153282190, 153546441, 153077893, 152806918, 164100589];
  const results = {};
  for (const id of ids) {
    const resp = await fetch(
      `https://character-service.dndbeyond.com/character/v5/character/${id}?includeCustomItems=true`,
      { headers: { 'Authorization': token, 'Accept': 'application/json' } }
    );
    results[id] = await resp.json();
  }
  return JSON.stringify(results);
}
```

Save to `~/Downloads/dndbeyond-campaign/all_characters.json`.

## Step 3 - Update Google Sheet

```python
import sys, os, json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.expanduser('~'), '.claude', 'reusable-scripts'))
from google_credentials import get_credentials
from googleapiclient.discovery import build

SHEET_ID = '1zkA0YN0AZyDxQXzRO_21hQIrOV-4vL7HkEWBEFJwcM0'
DECEASED = {'153282190'}  # update if more characters die

creds = get_credentials(['https://www.googleapis.com/auth/spreadsheets'])
sheets = build('sheets', 'v4', credentials=creds)

raw = Path('C:/Users/Jack/Downloads/dndbeyond-campaign/all_characters.json').read_text(encoding='utf-8').strip()
if raw.startswith('"'): raw = json.loads(raw)
all_chars = json.loads(raw)

players = {
    '152117866': 'Aricin',
    '153282190': 'jackle1127',
    '153546441': 'AngelFoxette',
    '153077893': 'TomThunder116',
    '152806918': 'Phxent23',
    '164100589': 'jackle1127',
}

now = datetime.now().strftime('%Y-%m-%d %H:%M')
rows = [['Character','Player','Class','Level','Race','HP','STR','DEX','CON','INT','WIS','CHA',
         'Spells Known','Spell List','Items','Status','Last Updated']]

for char_id, resp in all_chars.items():
    char = resp.get('data', {})
    if not char or not char.get('name'): continue
    classes = char.get('classes', [])
    stats = {s['id']: s['value'] for s in char.get('stats', [])}
    spells = [s['definition']['name'] for cs in char.get('classSpells',[]) for s in cs.get('spells',[])]
    items = [i['definition']['name'] for i in char.get('inventory',[]) if i.get('definition')]
    rows.append([
        char['name'], players.get(char_id,'?'),
        ', '.join(c['definition']['name'] for c in classes),
        sum(c['level'] for c in classes),
        char.get('race',{}).get('fullName','?') if char.get('race') else '?',
        char.get('baseHitPoints','?'),
        stats.get(1,''), stats.get(2,''), stats.get(3,''),
        stats.get(4,''), stats.get(5,''), stats.get(6,''),
        len(spells), ', '.join(spells), ', '.join(items[:10]),
        'DECEASED' if char_id in DECEASED else 'Active',
        now,
    ])

sheets.spreadsheets().values().update(
    spreadsheetId=SHEET_ID, range='Characters!A1',
    valueInputOption='RAW', body={'values': rows}
).execute()
print(f"Updated {len(rows)-1} characters at {now}")
```

## Key Technical Notes

- The character-service API **requires a Bearer JWT token** - cookies alone won't work
- The token is **short-lived** (~5 min) - must be captured fresh from a page load each time
- Token is extracted from the `authorization` request header in network requests
- Fetching from within the page context (`browser_evaluate`) uses the token correctly
- If a character returns `Unauthorized Access Attempt`, the token expired - reload and recapture

## After Updating

Display a summary table in chat:

| Character | Class | Race | HP | Notable |
|-----------|-------|------|----|---------|

Then share the sheet link:
https://docs.google.com/spreadsheets/d/1zkA0YN0AZyDxQXzRO_21hQIrOV-4vL7HkEWBEFJwcM0
