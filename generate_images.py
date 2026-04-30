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

ENTRIES = [
    {
        "md": f"{CAMPAIGN}/party/alarak-vaelor-veltharion.md",
        "img": f"{CAMPAIGN}/party/alarak-vaelor-veltharion.png",
        "prompt": "a dhampir paladin warrior, pale undead complexion, subtle fangs, striking charismatic face, half plate armor, greatsword, dark and brooding but magnetic, vampire-touched holy warrior, dramatic candlelit lighting, painterly dark fantasy portrait",
        "width": 512, "height": 768, "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/npcs/grimshaw.md",
        "img": f"{CAMPAIGN}/npcs/grimshaw.png",
        "prompt": "an elderly half-elf man with slightly pointed ears, kind tired eyes, weathered face, tattered prison rags, gentle expression, the kind of man who gives away his food, dark dungeon stone background, painterly fantasy portrait",
        "width": 512, "height": 768, "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/npcs/bristle.md",
        "img": f"{CAMPAIGN}/npcs/bristle.png",
        "prompt": "a small sassy flying squirrel with expressive mischievous eyes, fluffy with gliding membranes spread, perched confidently, fantasy animal companion with attitude, whimsical painterly illustration",
        "width": 512, "height": 512, "size": "1024x1024",
    },
    {
        "md": f"{CAMPAIGN}/party/fib-noodlecork.md",
        "img": f"{CAMPAIGN}/party/fib-noodlecork.png",
        "prompt": "an elderly forest gnome bard, small stature, warm expressive face, twinkling mischievous eyes full of old secrets, traveler's clothes layered for cold weather, borrowed lute on his back, decades of tavern life written on his face, painterly fantasy portrait, warm candlelit lighting",
        "width": 512, "height": 768, "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/npcs/inkus.md",
        "img": f"{CAMPAIGN}/npcs/inkus.png",
        "prompt": "a mysterious ethereal deity manifesting in a dream, warlock patron, half-formed in swirling dark cosmic void, glowing eldritch eyes, neither fully human nor fully alien, dreamlike and disturbing, painterly dark fantasy portrait",
        "width": 512, "height": 768, "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/npcs/lord-halvar-dendros.md",
        "img": f"{CAMPAIGN}/npcs/lord-halvar-dendros.png",
        "prompt": "a short stout human nobleman wearing polished shiny plate armor with noble insignia, distinguished bearing, authoritative and calculating expression, the face of a man accustomed to getting what he wants, painterly fantasy portrait, dramatic lighting",
        "width": 512, "height": 768, "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/locations/silver-oak.md",
        "img": f"{CAMPAIGN}/locations/silver-oak.png",
        "prompt": "a grand medieval feast hall interior inside a fortress, long banquet tables set for a feast, ornate dark wood beams, warm torchlight from iron chandeliers, silver oak tree motifs carved into pillars, atmospheric and opulent, painterly fantasy illustration",
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
        "prompt": entry["prompt"],
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
    prompt = entry["prompt"] + " No text, no words, no labels, no watermarks."
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
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
