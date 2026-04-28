# Character Creation Walkthrough

## Golden Rule: Always Create From Within the Campaign

Never create standalone and join later - campaign owner's purchased content (PHB, sourcebooks) isn't available until the character is in the campaign.

```
https://www.dndbeyond.com/campaigns/{campaign-id}/create-unassigned-character
```

Podcast campaign: `https://www.dndbeyond.com/campaigns/7009985/create-unassigned-character`

---

## Builder URL Pattern

`https://www.dndbeyond.com/characters/{id}/builder/{step}/{action}`

Steps in order:
1. `home/basic` — name, portrait, privacy, advancement settings
2. `class/manage` — class, level, subclass, skill proficiencies, features
3. `description/manage` — background, ability score bonuses
4. `species/choose` → `species/manage` — race selection and sub-choices
5. `ability-scores/manage` — stat assignment
6. `equipment/manage` — starting gear
7. `whats-next` — done

---

## Step 1: home/basic

Set name via `browser_type` on the Character Name input (JS assignment won't persist in React).

Set preferences via radio buttons — these must be set or the character stays "Incomplete":
```javascript
document.querySelector('input[value="2"][name*="privacy"], #privacyType_2').click(); // Campaign Only
document.querySelector('input[name="advancementType"][value="1"]').click();    // Milestone
document.querySelector('input[name="hitPointType"][value="1"]').click();       // Fixed HP
document.querySelector('input[name="encumbranceType"][value="2"]').click();    // No Encumbrance
document.querySelector('input[name="abilityScoreDisplayType"][value="1"]').click(); // Scores Top
```

Portrait upload is also done here — see `portrait-upload.md`.

---

## Step 2: class/manage

### Set class level

The level dropdown is `button[role="combobox"]` showing the current level. The option list class is `.styles_optionList__u567h`. The keyboard approach is most reliable:

```javascript
// 1. Open the level combobox
const combos = document.querySelectorAll('button[role="combobox"]');
const levelBtn = Array.from(combos).find(b => b.textContent.trim() === '1');
levelBtn.focus();
levelBtn.click();
```
Then via Playwright keyboard:
```
ArrowDown → Enter   (selects level 2)
```

Or find the option directly:
```javascript
// After opening, find the right option list near the button
const btnY = levelBtn.getBoundingClientRect().y;
const optLists = document.querySelectorAll('.styles_optionList__u567h');
let list = null, best = Infinity;
for (const l of optLists) {
  const r = l.getBoundingClientRect();
  if (r.width > 0 && Math.abs(r.y - btnY) < best) { best = Math.abs(r.y - btnY); list = l; }
}
Array.from(list.children).find(el => el.textContent.trim() === '2')?.click();
```

### Select skill proficiencies

Skill choice dropdowns also use `button[role="combobox"]`. Filter by placeholder text:
```javascript
const unset = Array.from(document.querySelectorAll('button[role="combobox"]'))
  .filter(b => b.innerText.includes('- Choose a Skill -'));
```
Then open each and pick from the option list (see ui-patterns.md).

### Expertise (level 2+)

Expertise is inside a `<details>` element. Click its `<summary>` to expand:
```javascript
const summaries = document.querySelectorAll('summary');
Array.from(summaries).find(s => s.innerText.includes('Expertise'))?.click();
```
Then there are 2 `button[role="combobox"]` dropdowns with text "- Choose a Skill Expertise -". Filter for those and pick from the option lists as above.

---

## Step 3: description/manage (Background)

The background selection uses a combobox. After choosing the background, ability score bonus dropdowns appear. Find unset ones:
```javascript
const unset = Array.from(document.querySelectorAll('button[role="combobox"]'))
  .filter(b => b.innerText.trim().startsWith('-'));
```

---

## Step 4: species/choose → species/manage

### Search for species

React search inputs need the native setter trick:
```javascript
const input = document.querySelector('input[placeholder*="Search"]') || document.querySelector('#search-input');
const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
nativeSetter.call(input, 'Gnome');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

### Confirm species selection

After clicking a species card, a confirmation modal appears. Find and click Confirm:
```javascript
Array.from(document.querySelectorAll('button'))
  .find(b => b.innerText.trim() === 'Confirm')?.click();
```

### Species sub-choices (species/manage)

After selecting a species, sub-choices appear as `button[role="combobox"]` dropdowns. Filter for the ones with placeholder text (`- Choose -`, etc.) and fill them.

For Forest Gnome specifically:
- Gnomish Lineage → "Forest Gnome"
- Gnomish Lineage Spells → choose the casting stat that matches your class (e.g. Charisma for Bard)
- Languages → Gnomish + one free choice

---

## Step 5: ability-scores/manage

### Select generation method
Click the "Standard Array" (or other method) radio/button.

### Assign scores
Six comboboxes, one per stat. Open each and pick values. The standard array values are: 15, 14, 13, 12, 10, 8. Background bonuses are applied automatically after.

Order of comboboxes on the page: STR, DEX, CON, INT, WIS, CHA.

---

## Step 6: equipment/manage

Two equipment packages to select (class package + background package). Each is a radio-style option group. Click the desired option for each.

---

## Completion

Navigate to `whats-next` — if no errors show, the character is saved and ready. The builder auto-saves at each step.

To verify: check `Character Level: N` in the builder header matches the expected level.

---

## Character Name Reversion Bug

The character name sometimes reverts to "jackle1127's Character" when navigating between steps. If this happens, type the correct name directly into the Character Name field on whichever step you're on. The field is always visible at the top of the builder.
