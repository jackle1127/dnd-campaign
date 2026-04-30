#!/usr/bin/env python3
"""Generate character/location images. Defaults to local AI server (fantasy LoRA).
Pass --openai to use DALL-E 3 instead."""

import os
import sys
import urllib.request
import requests

CAMPAIGN = os.path.join(os.path.dirname(__file__), "this-is-bullcrit")
SERVER = "http://192.168.1.202:8000"
USE_OPENAI = "--openai" in sys.argv

# Applied to every prompt to enforce a consistent art style
STYLE = "Fantasy illustration style, painterly and expressive, rich color and detail filling the entire canvas edge to edge with no white or empty areas, consistent fantasy RPG aesthetic. No text, no letters, no words, no labels, no watermarks, no writing of any kind anywhere in the image."

ENTRIES = [
    {
        "md": f"{CAMPAIGN}/party/alarak-vaelor-veltharion.md",
        "img": f"{CAMPAIGN}/party/alarak-vaelor-veltharion.png",
        "prompt": "A dhampir paladin warrior. Pale undead complexion, subtle fangs, striking charismatic face. Half plate armor, greatsword over his shoulder. Dark and brooding but magnetic, a vampire-touched holy warrior.",
        "width": 512, "height": 512, "size": "1024x1024",
    },
    {
        "md": f"{CAMPAIGN}/npcs/grimshaw.md",
        "img": f"{CAMPAIGN}/npcs/grimshaw.png",
        "prompt": "An elderly half-elf man in his 70s. Slightly pointed ears, kind tired eyes, deeply weathered face, tattered ragged clothing. Gentle and generous expression, the kind of man who gives away his last meal.",
        "width": 512, "height": 512, "size": "1024x1024",
    },
    {
        "md": f"{CAMPAIGN}/npcs/bristle.md",
        "img": f"{CAMPAIGN}/npcs/bristle.png",
        "prompt": "A small sassy flying squirrel with expressive mischievous eyes, fluffy fur, gliding membranes spread wide. Perched confidently on a branch. A beloved fantasy animal companion full of attitude.",
        "width": 512, "height": 512, "size": "1024x1024",
    },
    {
        "md": f"{CAMPAIGN}/party/fib-noodlecork.md",
        "img": f"{CAMPAIGN}/party/fib-noodlecork.png",
        "prompt": "An elderly forest gnome bard. Small stature, warm expressive face, twinkling mischievous eyes full of old secrets. Layered traveler clothes for cold weather, a borrowed lute on his back. Decades of tavern life written on his face.",
        "width": 512, "height": 512, "size": "1024x1024",
    },
    {
        "md": f"{CAMPAIGN}/npcs/inkus.md",
        "img": f"{CAMPAIGN}/npcs/inkus.png",
        "prompt": "A mysterious lower-tier deity and warlock patron manifesting in a dream. An unsettling half-formed figure wreathed in dark cosmic energy, glowing eldritch eyes. Neither fully human nor alien, dreamlike and disturbing.",
        "width": 512, "height": 512, "size": "1024x1024",
    },
    {
        "md": f"{CAMPAIGN}/npcs/lord-halvar-dendros.md",
        "img": f"{CAMPAIGN}/npcs/lord-halvar-dendros.png",
        "prompt": "A short stout human nobleman in his 50s. Silver-streaked hair, lined commanding face, gravitas of a man who has wielded power for decades. Polished plate armor with noble insignia. Calculating and authoritative expression.",
        "width": 512, "height": 512, "size": "1024x1024",
    },
    {
        "md": f"{CAMPAIGN}/locations/silver-oak.md",
        "img": f"{CAMPAIGN}/locations/silver-oak.png",
        "prompt": "Interior of a grand medieval feast hall inside a stone fortress. Long banquet tables set for a lavish feast, ornate dark wood beams overhead, warm torchlight from iron chandeliers, silver oak tree motifs carved into the pillars.",
        "width": 896, "height": 512, "size": "1792x1024",
    },
]

def prepend_image_ref(md_path, img_filename):
    with open(md_path, "r") as f:
        content = f.read()
    if content.startswith("![]("):
        return
    with open(md_path, "w") as f:
        f.write(f"![]({img_filename})\n\n{content}")
    print(f"  Updated {md_path}")

def generate_local(entry):
    resp = requests.post(f"{SERVER}/image/generate", json={
        "prompt": entry["prompt"] + " " + STYLE,
        "lora": "fantasy",
        "width": entry["width"],
        "height": entry["height"],
        "steps": 30,
    }, timeout=300)
    if resp.status_code != 200:
        raise RuntimeError(f"Server error {resp.status_code}: {resp.text}")
    return resp.content

def generate_openai(entry):
    import keyring
    from openai import OpenAI
    client = OpenAI(api_key=keyring.get_password("openai", "api-key"))
    response = client.images.generate(
        model="dall-e-3",
        prompt=entry["prompt"] + " " + STYLE,
        size=entry["size"],
        quality="standard",
        n=1,
    )
    url = response.data[0].url
    with urllib.request.urlopen(url) as r:
        return r.read()

backend = "OpenAI DALL-E 3" if USE_OPENAI else "local AI server (fantasy LoRA)"
print(f"Using: {backend}\n")

for entry in ENTRIES:
    img_path = entry["img"]
    img_filename = os.path.basename(img_path)
    md_path = entry["md"]
    name = os.path.basename(md_path).replace(".md", "")

    print(f"[{name}] Generating...")
    try:
        img_bytes = generate_openai(entry) if USE_OPENAI else generate_local(entry)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    with open(img_path, "wb") as f:
        f.write(img_bytes)
    print(f"  Saved {img_path}")
    prepend_image_ref(md_path, img_filename)

print("\nDone.")
