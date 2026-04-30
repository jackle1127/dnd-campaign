#!/usr/bin/env python3
"""Generate highlight scene images for D&D session notes using gpt-image-2."""

import base64, sys, os
import keyring
from openai import OpenAI
from pathlib import Path

CAMPAIGN = Path(__file__).parent / "this-is-bullcrit"
SESSIONS = CAMPAIGN / "sessions"

STYLE = "Watercolor fantasy illustration, soft washes of color, painterly and expressive, sweeping scene with warm dramatic lighting. No text, no letters, no labels, no watermarks."

client = OpenAI(api_key=keyring.get_password("openai", "api-key"))

def img(rel): return str(CAMPAIGN / rel)

# Each entry: session filename, scene prompt, list of char image paths (max 4)
# Characters without images are described directly in the prompt.
SESSIONS_DATA = [
    {
        "file": "2025-10-24-one-year-in-vaultspire.md",
        "prompt": (
            "A young woman named Elyra Vance with a warm smile, flour on her hands, "
            "holds out a freshly baked quiche to a pale, roguish young man across a "
            "rough wooden table in a dimly lit tavern. Warm candlelight. A moment of "
            "quiet kindness in a cold northern city."
        ),
        "refs": [img("party/kaelen-thornecrest-1.png")],
    },
    {
        "file": "2026-01-16-prison-setup-breakout-planning.md",
        "prompt": (
            "A grim prison cafeteria with stone walls and iron bars casting long shadows. "
            "Five prisoners — a pale dhampir warrior, a dark-cloaked warlock, and three others "
            "in drab prison clothes — huddle over bowls of grey slop, whispering urgently "
            "with a crude map scratched into the table. Guards loom distantly in the background."
        ),
        "refs": [
            img("party/alarak-vaelor-veltharion.png"),
            img("party/szeth-stormblessed.png"),
            img("party/kaelen-thornecrest-1.png"),
        ],
    },
    {
        "file": "2026-01-30-prong-gathering-lockpick-attempt.md",
        "prompt": (
            "Inside a dimly lit prison mine shaft, a weathered elderly half-elf man with kind "
            "tired eyes quietly slips his mining quota stones to a pale, brooding dhampir warrior "
            "beside him. Nearby, a warlock elbow-deep in a prison trash can searches frantically "
            "for something. The scene is tense but quietly humane."
        ),
        "refs": [
            img("npcs/grimshaw.png"),
            img("party/alarak-vaelor-veltharion.png"),
            img("party/szeth-stormblessed.png"),
        ],
    },
    {
        "file": "2026-02-13-escape-attempt-meets-helga.md",
        "prompt": (
            "On a dark prison stairwell, a pale dhampir warrior and a tattooed warlock freeze "
            "mid-step as a stout, no-nonsense dwarven woman in a food service apron appears "
            "from the shadows above, hands on her hips, blocking their escape route. The only "
            "light is a guttering torch. The moment hangs on a knife's edge."
        ),
        "refs": [
            img("party/alarak-vaelor-veltharion.png"),
            img("party/szeth-stormblessed.png"),
            img("npcs/helga.png"),
        ],
    },
    {
        "file": "2026-02-27-escape-from-vaultspire.md",
        "prompt": (
            "A large hawk with fierce golden eyes snatches a tiny brown rat tumbling through "
            "the air mid-fall, talons open, wings spread wide — the rat barely caught before "
            "hitting the rocky road below. A wooden wagon rumbles away in the background "
            "through a grey morning landscape. An absurd and desperate rescue."
        ),
        "refs": [img("party/kaelen-thornecrest-1.png")],
    },
    {
        "file": "2026-03-13-ironwood-fortress-soup-kitchen.md",
        "prompt": (
            "Inside a stone soup kitchen storeroom, a small sassy flying squirrel perches "
            "in the rafters looking thoroughly unimpressed, staring down at a roguish man "
            "below who is gesturing frantically at a glowing voice-activated door lock, "
            "mid-argument with the mechanism. The alarm blares. Other escaped prisoners "
            "scramble for a hole in the wall."
        ),
        "refs": [
            img("npcs/bristle.png"),
            img("party/kaelen-thornecrest-1.png"),
            img("party/szeth-stormblessed.png"),
        ],
    },
    {
        "file": "2026-03-27-cindy-dies-slick-down.md",
        "prompt": (
            "Inside a chaotic soup kitchen, a massive brown bear — a wildshifted druid — "
            "drags a gravely wounded rogue toward a narrow window while guards flood in "
            "through the door. Two arrows are lodged in the rogue's side. The scene is "
            "desperate, loud, and barely controlled."
        ),
        "refs": [
            img("party/kaelen-thornecrest-1.png"),
            img("npcs/bristle.png"),
        ],
    },
    {
        "file": "2026-03-28-slick-dies-in-ironwood-fortress.md",
        "prompt": (
            "A pale roguish man lies still on the stone floor of a chaotic soup kitchen, "
            "two arrows in his chest, eyes closed. A massive brown bear stands over him "
            "protectively, wounded guards backing away. A stout dwarven woman shouts from "
            "across the room. The party is already fleeing through the window. Tragedy."
        ),
        "refs": [
            img("party/kaelen-thornecrest-1.png"),
            img("npcs/helga.png"),
        ],
    },
    {
        "file": "2026-04-10-darian-joins-the-crew.md",
        "prompt": (
            "In a moonlit forest clearing, a well-dressed nobleman kneels beside a wrapped "
            "body on the ground, head bowed in prayer, tears on his cheeks. Around him "
            "stand a pale dhampir warrior and a small flying squirrel on a log — all silent "
            "witnesses to a family farewell. A moment of grief before a new beginning."
        ),
        "refs": [
            img("party/darian-thornecrest.png"),
            img("party/alarak-vaelor-veltharion.png"),
            img("npcs/bristle.png"),
        ],
    },
    {
        "file": "2026-04-24.md",
        "prompt": (
            "On the ivy-covered outer wall of a grand stone feast hall at night, a tiny "
            "flying squirrel and a small brown rat cling to the stonework just below an "
            "open window, torchlight spilling from inside. The squirrel braces the window "
            "open while the rat slips inside. Below, elegant guests arrive at the main gate "
            "in fine carriages. A caper mid-heist."
        ),
        "refs": [
            img("npcs/bristle.png"),
            img("party/darian-thornecrest.png"),
            img("party/szeth-stormblessed.png"),
        ],
    },
]


def generate_image(prompt, refs, out_path):
    full_prompt = prompt + " " + STYLE
    if refs:
        handles = [open(p, "rb") for p in refs if os.path.exists(p)]
        try:
            response = client.images.edit(
                model="gpt-image-2",
                image=handles,
                prompt=full_prompt,
                size="1536x1024",
            )
        finally:
            for h in handles:
                h.close()
    else:
        response = client.images.generate(
            model="gpt-image-2",
            prompt=full_prompt,
            size="1536x1024",
            quality="auto",
            n=1,
        )
    return base64.b64decode(response.data[0].b64_json)


def inject_image(md_path, img_filename):
    content = md_path.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i + 1, f"\n![]({img_filename})\n")
            break
    md_path.write_text("\n".join(lines))


target = sys.argv[1] if len(sys.argv) > 1 else None

for entry in SESSIONS_DATA:
    fname = entry["file"]
    if target and target not in fname:
        continue

    md_path = SESSIONS / fname
    stem = fname.replace(".md", "")
    img_filename = f"{stem}-highlight.png"
    img_path = SESSIONS / img_filename

    if img_path.exists() and not target:
        print(f"[SKIP] {fname} — image already exists")
        continue

    print(f"[{stem}] Generating...")
    try:
        img_bytes = generate_image(entry["prompt"], entry["refs"], img_path)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    img_path.write_bytes(img_bytes)
    print(f"  Saved {img_path}")

    if f"![]({img_filename})" not in md_path.read_text():
        inject_image(md_path, img_filename)
        print(f"  Updated {fname}")

print("\nDone.")
