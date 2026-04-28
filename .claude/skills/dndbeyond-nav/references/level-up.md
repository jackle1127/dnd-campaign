# Level Up via Builder

## Navigate to Class Manager

```
https://www.dndbeyond.com/characters/{id}/builder/class/manage
```

## Change the Level

The level field is a `button[role="combobox"]`. The keyboard approach is the most reliable:

```javascript
// 1. Find and focus the level combobox
const combos = document.querySelectorAll('button[role="combobox"]');
const levelBtn = Array.from(combos).find(b => /^\d+$/.test(b.textContent.trim()));
levelBtn.focus();
levelBtn.click();
```

Then use Playwright keyboard - each `ArrowDown` moves one level up:
```
ArrowDown → Enter   (1 → 2)
ArrowDown → ArrowDown → Enter   (1 → 3)
```

Or find the option directly after opening (see ui-patterns.md combobox section).

## Handle New Feature Choices

After leveling up, new feature rows appear. Check for ones with a `!` indicator (unresolved choices).

Feature rows are `<details>/<summary>` elements:
```javascript
// Expand a feature row
const summaries = document.querySelectorAll('summary');
Array.from(summaries).find(s => s.innerText.includes('Feature Name'))?.click();
```

Inside each expanded feature, choices are comboboxes with placeholder text like `- Choose a Skill Expertise -`. Use the combobox pattern from ui-patterns.md to fill them.

## Verify Completion

Navigate to `whats-next`:
```
https://www.dndbeyond.com/characters/{id}/builder/whats-next
```

If the page shows "View Character Sheet" and "Export to PDF" with no error banners, the level-up is complete and saved.

Check the builder header shows `Character Level: N` with the correct level and `Max Hit Points: X`.

## HP After Level Up

D&D Beyond calculates HP automatically based on the HP setting:
- **Fixed HP**: Uses the fixed value per level (class average, e.g. d8 = 5)
- **Max HP first level**: Always 8 for a d8 class at level 1

Verify the displayed Max Hit Points matches expectations before leaving.
