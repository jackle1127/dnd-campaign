---
name: dnd-character-portrait
description: Generate or regenerate D&D character/NPC/location images using gpt-image-2 (watercolor style). Use when the user wants to generate a portrait, character art, or location image — or iterate on an existing one ("redo Fib", "regenerate Bristle", "make an image for X"). Also handles new characters not yet in the script.
---

# D&D Character/Location Image Generator

Generates watercolor fantasy portraits and location images using gpt-image-2.

## Campaign path

```
/home/jack/workspace/dnd-campaign/this-is-bullcrit/
  party/      ← player character images (square 1024x1024)
  npcs/       ← NPC images (square 1024x1024)
  locations/  ← location/map images (landscape 1536x1024)
```

## Runner script

```bash
# Regenerate a specific character (pass any substring of the filename)
python /home/jack/workspace/dnd-campaign/generate_images.py fib-noodlecork
python /home/jack/workspace/dnd-campaign/generate_images.py bristle

# Regenerate all entries
python /home/jack/workspace/dnd-campaign/generate_images.py

# Use local AI server instead (fantasy LoRA)
python /home/jack/workspace/dnd-campaign/generate_images.py --local
```

## Style

```
Watercolor fantasy illustration, soft washes of color, painterly and expressive. No text, no letters, no labels, no watermarks.
```

## Image placement rules (doc-formatting.md)

- **Characters/NPCs:** image goes before the `# title` (prepended to top of file)
- **Locations/Maps:** image goes after the `# title`
- The script's `prepend_image_ref()` handles characters/NPCs automatically

## Sizes

| Type | gpt-image-2 size | Local server |
|------|-----------------|--------------|
| Character/NPC | `1024x1024` | 512x512 |
| Location/Map | `1536x1024` | 896x512 |

## API pattern (gpt-image-2)

```python
import base64, keyring
from openai import OpenAI

client = OpenAI(api_key=keyring.get_password("openai", "api-key"))

response = client.images.generate(
    model="gpt-image-2",
    prompt=prompt + " " + STYLE,
    size="1024x1024",   # or "1536x1024" for landscape
    quality="auto",
    n=1,
)
img_bytes = base64.b64decode(response.data[0].b64_json)
```

## Adding a new character

1. Add an entry to `ENTRIES` in `generate_images.py` with `md`, `img`, `prompt`, `size`, `width`, `height`
2. Write a 2-3 sentence appearance description as the prompt
3. Run the script with the character name as arg
4. The script will prepend `![](<filename>.png)` to the markdown file automatically

## Current entries

| Character | File |
|-----------|------|
| Alarak Vaelor Veltharion | `party/alarak-vaelor-veltharion.png` |
| Grimshaw | `npcs/grimshaw.png` |
| Bristle | `npcs/bristle.png` |
| Fib Noodlecork | `party/fib-noodlecork.png` |
| Inkus | `npcs/inkus.png` |
| Lord Halvar Dendros | `npcs/lord-halvar-dendros.png` |
| The Silver Oak (location) | `locations/silver-oak.png` |
