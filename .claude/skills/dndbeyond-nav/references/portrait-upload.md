# Portrait Upload

## Generating a Portrait

Use the local AI server at `192.168.1.202:8000`. Python is at `C:/Users/Jack/AppData/Local/Programs/Python/Python313/python.exe`.

```python
import json, urllib.request

url = "http://192.168.1.202:8000/image/generate"
payload = {
    "prompt": "portrait of ..., fantasy illustration, warm lighting",
    "lora": "fantasy",   # use "fantasy" lora for D&D characters
    "width": 512,
    "height": 512,
    "steps": 30,
    "seed": 42           # change seed to get different variations
}
data = json.dumps(payload).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=120) as resp:
    raw = resp.read()

# Server returns raw PNG bytes
out_path = "C:/Users/Jack/Workspace/dnd-campaign/portrait.png"
with open(out_path, "wb") as f:
    f.write(raw)
print(f"Saved to {out_path}")
```

Save to the workspace directory (not Downloads) - `browser_file_upload` only allows workspace paths.

---

## Uploading to D&D Beyond

The portrait upload dialog is accessed from the **character builder** (not the character sheet).

### 1. Navigate to the builder home page
```
https://www.dndbeyond.com/characters/{id}/builder/home/basic
```

### 2. Click the portrait area
```javascript
// This element is the visible portrait (img) in the builder page header
await page.locator('[data-testid="character-portrait"]').click();
```
This opens the "Manage Portrait" dialog.

### 3. Trigger the file chooser
```javascript
await page.locator('input[type="file"]').click();
// Modal state: [File chooser] - can now call browser_file_upload
```

### 4. Upload the file
```javascript
await fileChooser.setFiles(["C:/Users/Jack/Workspace/dnd-campaign/portrait.png"])
```

### 5. Set the portrait
After upload, a preview appears with a "Set Portrait" or "Change Portrait" button:
```javascript
const btns = document.querySelectorAll('button');
for (const btn of btns) {
  if (btn.innerText && (btn.innerText.includes('Set Portrait') || btn.innerText.includes('Change Portrait'))) {
    btn.click();
    break;
  }
}
```

### 6. Apply
```javascript
Array.from(document.querySelectorAll('button'))
  .find(b => b.innerText?.trim() === 'Apply')?.click();
```

The dialog closes and the new portrait is saved automatically.

---

## Notes

- The portrait API endpoint (`/portrait`, `/avatar`, `/portaitUrl`) returns 404 - use the builder UI method above.
- If you get "Current Custom Portrait" at the top of the dialog, the previous portrait is shown there. The upload section below it will replace it.
- D&D Beyond recommends 150x150px but 512x512 works fine (it crops/scales).
