# D&D Beyond UI Patterns

D&D Beyond is a React app. Most UI elements are custom-built and do NOT behave like native HTML elements.

---

## Comboboxes (Dropdowns)

D&D Beyond uses custom `button[role="combobox"]` elements, not native `<select>`. There are often many on the page at once.

### Open a combobox
```javascript
// Find by its current text label
const combos = document.querySelectorAll('button[role="combobox"]');
const target = Array.from(combos).find(b => b.innerText.trim() === 'Current Value');
target.click();
```

### Select an option
After opening, the option list appears as `.styles_optionList__u567h`. There may be MULTIPLE on the page (one per open dropdown). Find the right one by which is closest in Y position to the button you just opened:

```javascript
const optLists = document.querySelectorAll('.styles_optionList__u567h');
let targetList = null;
let closestDist = Infinity;
const btnY = target.getBoundingClientRect().y;
for (const list of optLists) {
  const rect = list.getBoundingClientRect();
  if (rect.width > 0 && rect.height > 0) {
    const dist = Math.abs(rect.y - btnY);
    if (dist < closestDist) { closestDist = dist; targetList = list; }
  }
}
// Now click the option
const items = Array.from(targetList.children);
items.find(el => el.textContent.trim() === 'Desired Value')?.click();
```

### Full pattern (open + select in one shot)
```javascript
// 1. Find and click the combobox
const combos = document.querySelectorAll('button[role="combobox"]');
const btn = Array.from(combos).find(b => b.innerText.includes('- Choose a Skill -'));
btn.click();

// 2. Wait for list to render, then select
const btnY = btn.getBoundingClientRect().y;
const optLists = document.querySelectorAll('.styles_optionList__u567h');
let list = null, best = Infinity;
for (const l of optLists) {
  const r = l.getBoundingClientRect();
  if (r.width > 0 && Math.abs(r.y - btnY) < best) { best = Math.abs(r.y - btnY); list = l; }
}
Array.from(list.children).find(el => el.textContent.trim() === 'Stealth')?.click();
```

### Keyboard navigation (more reliable for some dropdowns)
```javascript
// Focus and open the combobox
btn.focus();
btn.click();
// Then via Playwright keyboard:
await page.keyboard.press('ArrowDown');
await page.keyboard.press('Enter');
```

---

## Feature Rows (Details/Summary)

Class feature rows in the builder are `<details>` elements. Click `<summary>` to expand:

```javascript
const summaries = document.querySelectorAll('summary');
const expertise = Array.from(summaries).find(s => s.innerText.includes('Expertise'));
expertise.click();
```

---

## React Text Inputs

Plain `input.value = 'text'` won't trigger React's onChange. Use the native setter:

```javascript
const input = document.querySelector('input[name="characterName"]');
const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
nativeSetter.call(input, 'Fib Noodlecork');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

For the character name field in the builder, `browser_type` on the input element is more reliable than JS.

---

## Finding Buttons by Text

When CSS selectors fail, scan by innerText:

```javascript
// Single button
const btn = Array.from(document.querySelectorAll('button'))
  .find(b => b.innerText.trim() === 'Apply');
btn?.click();

// When text is nested (button contains child elements)
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
let node;
while ((node = walker.nextNode())) {
  if (node.tagName === 'BUTTON' && node.children.length === 0 && node.textContent.trim() === 'Set Portrait') {
    node.click();
    break;
  }
}
```

---

## Bearer Token

Required for direct API calls. Has a **5-minute TTL** - always get a fresh one right before use:

```javascript
// Run inside browser_evaluate on a logged-in dndbeyond.com page
const r = await fetch('https://auth-service.dndbeyond.com/v1/cobalt-token', {
  method: 'POST',
  credentials: 'include'
});
const data = await r.json();
return data.token; // JWT string
```

---

## Python on this Machine

Python is at `C:/Users/Jack/AppData/Local/Programs/Python/Python313/python.exe`. Run scripts with that path directly - `python3` and `py` aliases don't work reliably in bash.

---

## File Upload Restriction

`browser_file_upload` only accepts files within Playwright's allowed roots (the workspace directory). Copy files there first:

```bash
cp /c/Users/Jack/Downloads/portrait.png /c/Users/Jack/Workspace/dnd-campaign/portrait.png
```

Then upload from the workspace path.
