---
name: dnd-session-image
description: Generate a highlight scene image for one or more D&D session notes. Reads the session markdown, identifies the dramatic highlight, loads character reference images, and generates a watercolor fantasy scene using gpt-image-2. Use when the user wants to generate or regenerate session art ("make an image for the last session", "generate session highlights", "/dnd-session-image"). Args: optional session filename(s) or date(s); if omitted, process all sessions missing highlight images.
---

# D&D Session Highlight Image Generator

Generates a watercolor fantasy scene illustrating the dramatic highlight of a session, using character portrait images as visual references for consistency. Uses gpt-image-2.

## Campaign path

```
/home/jack/workspace/dnd-campaign/this-is-bullcrit/
  sessions/           ← session markdown files + highlight PNGs
  party/              ← party character images
  npcs/               ← NPC images
```

## Runner script

**Always use the existing script first:**

```bash
# Generate all sessions missing images
python /home/jack/workspace/dnd-campaign/generate_session_images.py

# Force-regenerate a specific session (won't skip even if image exists)
python /home/jack/workspace/dnd-campaign/generate_session_images.py 2026-04-24
```

Passing any substring of the session filename as an arg targets that session and skips the "already exists" check.

## Output

- Image saved as `sessions/<session-date>-highlight.png` (landscape 1536x1024)
- Session markdown updated: `![](filename.png)` inserted after the `# date` heading
- If image already exists and no arg given, session is skipped

## Character image map

| Name(s) in notes | Image path |
|-----------------|-----------|
| Alarak | `party/alarak-vaelor-veltharion.png` |
| Darian | `party/darian-thornecrest.png` |
| Fib, Fib Noodlecork | `party/fib-noodlecork.png` |
| Slick, Kaelen | `party/kaelen-thornecrest-1.png` |
| Szeth | `party/szeth-stormblessed.png` |
| Bristle | `npcs/bristle.png` |
| Helga | `npcs/helga.png` |
| Inkus | `npcs/inkus.png` |
| Grimshaw | `npcs/grimshaw.png` |
| Dendros, Lord Dendros | `npcs/lord-halvar-dendros.png` |

Characters without images (Rayne, Vacir, Briggs): describe appearance in the prompt from their `.md` file.

## Costume continuity rules

- **Sessions in Vaultspire prison** (before 2026-02-27 escape): party members wear **orange prison uniforms**
- **Sessions after escape** (2026-03-13 onward): party members wear traveler's/adventuring clothes
- **Helga**: always in food service apron — never a prisoner
- **Grimshaw**: prisoner, so orange uniform during prison sessions

## Style

```
Watercolor fantasy illustration, soft washes of color, painterly and expressive, sweeping scene with warm dramatic lighting. No text, no letters, no labels, no watermarks.
```

## API pattern (gpt-image-2)

```python
import base64, keyring
from openai import OpenAI
from pathlib import Path

client = OpenAI(api_key=keyring.get_password("openai", "api-key"))

def generate_session_image(prompt, char_image_paths):
    STYLE = "Watercolor fantasy illustration, soft washes of color, painterly and expressive, sweeping scene with warm dramatic lighting. No text, no letters, no labels, no watermarks."
    full_prompt = prompt + " " + STYLE

    if char_image_paths:
        handles = [open(p, "rb") for p in char_image_paths if Path(p).exists()]
        try:
            response = client.images.edit(
                model="gpt-image-2",
                image=handles,
                prompt=full_prompt,
                size="1536x1024",
            )
        finally:
            for h in handles: h.close()
    else:
        response = client.images.generate(
            model="gpt-image-2",
            prompt=full_prompt,
            size="1536x1024",
            quality="auto",
            n=1,
        )

    return base64.b64decode(response.data[0].b64_json)
```

- Use `images.edit` with character PNGs as references for visual consistency (max 4 refs)
- Use `images.generate` when no character images are relevant
- Response is always `b64_json` — decode with `base64.b64decode`

## Adding a new session

1. Add an entry to `SESSIONS_DATA` in `generate_session_images.py`
2. Write a 2-3 sentence scene description (who, what action, where)
3. List up to 4 character image paths as refs
4. Apply costume continuity rules above
5. Run the script
