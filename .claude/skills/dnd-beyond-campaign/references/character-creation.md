# Character Creation via Playwright

## Golden Rule: Always Create From Within the Campaign

Never create a character standalone and join later. The campaign owner may have purchased PHB and sourcebooks that unlock subclasses, species, and content. Creating from within the campaign gives you all purchased content from the start.

Use the campaign's create URL:
```
https://www.dndbeyond.com/campaigns/7009985/create-unassigned-character
```

General pattern: `https://www.dndbeyond.com/campaigns/{campaign-id}/create-unassigned-character`

---

## Builder URL Pattern

All builder pages follow: `https://www.dndbeyond.com/characters/{id}/builder/{step}/{action}`

Steps in order:
1. `home/basic` - name, privacy, advancement settings
2. `class/manage` - class, level, subclass, skills
3. `description/manage` - background, alignment, lifestyle
4. `species/choose` → `species/manage` - race selection
5. `ability-scores/manage` - stat assignment
6. `equipment/manage` - starting gear
7. `whats-next` - completion

---

## Combobox Pattern (Used Everywhere)

D&D Beyond uses custom button-based dropdowns, not native `<select>`:
```javascript
// Open the dropdown
document.getElementById('someButton').click();
// Select an option
const label = Array.from(document.getElementById('someDropdown').querySelectorAll('label'))
  .find(l => l.textContent.trim() === 'Option Name');
label.click();
```

---

## Step 1: home/basic

**Must set ALL of these or character stays "Incomplete":**
```javascript
document.getElementById('privacyType_2').click(); // Campaign Only

document.querySelector('input[name="advancementType"][value="1"]').click(); // Milestone
document.querySelector('input[name="hitPointType"][value="1"]').click();    // Fixed
document.querySelector('input[name="encumbranceType"][value="2"]').click(); // No Encumbrance
document.querySelector('input[name="abilityScoreDisplayType"][value="1"]').click(); // Scores Top
```

Portrait upload is also on this page (see Portrait section below).

---

## Step 2: class/manage

**Class level combobox** - uses `data-index` labels:
```javascript
document.getElementById('class-level-select-8Button').click();
document.getElementById('class-level-select-8Dropdown').querySelector('[data-index="2"]').click(); // level 2
```

**Milestone level** - separate combobox, must also be set:
```javascript
document.getElementById('set-levelButton').click();
Array.from(document.getElementById('set-levelDropdown').querySelectorAll('label'))
  .find(l => l.textContent.trim() === '2').click();
```

**Skill proficiencies:**
```javascript
document.getElementById('detail-choice-select-2-1597Button').click();
Array.from(document.getElementById('detail-choice-select-2-1597Dropdown').querySelectorAll('label'))
  .find(l => l.textContent.trim() === 'Arcana').click();
```

**Subclass** - inside a `<details>` element:
```javascript
const allDetails = document.querySelectorAll('details');
allDetails[4].querySelector('summary').click(); // expand Arcane Tradition (index varies)
// Then select from the combobox inside
```

Note: School of Divination requires PHB purchase. Basic Rules (SRD) only includes School of Evocation. If created from within campaign with PHB purchased, Divination is available.

---

## Step 3: description/manage (Background)

Find unset comboboxes and fill them:
```javascript
const unset = Array.from(document.querySelectorAll('button[role="combobox"]'))
  .filter(b => b.textContent.trim().startsWith('-'));
```

---

## Step 4: species/choose → species/manage

React input requires native setter (plain `input.value =` won't trigger React):
```javascript
const input = document.getElementById('search-input-...');
const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
nativeSetter.call(input, 'Human');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

Species selection opens a **confirmation modal** - click "Confirm" after selecting.

---

## Step 5: ability-scores/manage

Select generation method first, then assign via comboboxes (`qry_9` through `qry_14` for STR→CHA):
```javascript
// qry_9=STR, qry_10=DEX, qry_11=CON, qry_12=INT, qry_13=WIS, qry_14=CHA
document.getElementById('qry_12Button').click(); // open INT
Array.from(document.getElementById('qry_12Dropdown').querySelectorAll('label'))
  .find(l => l.textContent.trim() === '15').click();
```

---

## Character Name

Use `browser_type` with the Character Name textbox ref. Using JS `input.value =` directly won't persist in React.

---

## Portrait Upload

Use `browser_run_code` with `setInputFiles` (not `browser_file_upload`) to trigger React's onChange:
```javascript
async (page) => {
  await page.locator('.ct-decoration-manager__upload-file-input').setInputFiles('/path/to/portrait.png');
  await page.waitForTimeout(2000);
}
```
Then click the **"Set Portrait"** button:
```javascript
Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === 'Set Portrait').click();
```

---

## Spells (from Character Sheet, not Builder)

Spells are managed from the character sheet's Spells tab, not the builder.

1. Click Spells tab → click "Manage Spells"
2. Expand the "Spellbook" collapsible in the sidebar
3. Click "Learn" to add spells to spellbook

**Important D&D Beyond quirk**: "Learn" = add to spellbook. D&D Beyond counts cantrips toward the spellbook cap. For a Wizard 2 with 3 cantrips, only 5 1st-level spells can be added before Learn buttons become disabled (3 + 5 = 8 = cap). Prepared spells = INT mod + level (separate concept).

If Learn buttons are disabled, the API can be called directly:
```
POST https://character-service.dndbeyond.com/character/v5/spell
Body: {"characterId": ID, "characterClassId": CLASS_ID, "spellId": SPELL_ID, "id": ENTITY_ID, "entityTypeId": 435869154}
```
Capture these IDs from network requests when clicking a working Learn button.

---

## Joining a Campaign

Navigate to the join URL, click the character, then confirm:
```javascript
// URL: https://www.dndbeyond.com/campaigns/join/70099853388621188
document.querySelector('[data-character-id="164100589"]').click();
Array.from(document.querySelectorAll('button'))
  .find(b => b.textContent.trim() === 'Join with this Character').click();
// Redirects to campaign page on success
```

Podcast campaign invite: `https://www.dndbeyond.com/campaigns/join/70099853388621188`
