#!/usr/bin/env python3
"""Generate character/location images using gpt-image-2 (watercolor style).
Defaults to gpt-image-2. Pass --local to use the local AI server (fantasy LoRA) instead."""

import os
import sys
import base64
import requests

CAMPAIGN = os.path.join(os.path.dirname(__file__), "this-is-bullcrit")
SERVER = "http://192.168.1.202:8000"
USE_LOCAL = "--local" in sys.argv

STYLE = "Watercolor fantasy illustration, soft washes of color, painterly and expressive. No text, no letters, no labels, no watermarks."

ENTRIES = [
    {
        "md": f"{CAMPAIGN}/party/alarak-vaelor-veltharion.md",
        "img": f"{CAMPAIGN}/party/alarak-vaelor-veltharion.png",
        "prompt": "A dhampir paladin warrior. Pale undead complexion, subtle fangs, striking charismatic face. Half plate armor, greatsword over his shoulder. Dark and brooding but magnetic, a vampire-touched holy warrior.",
        "size": "1024x1024", "width": 512, "height": 512,
    },
    {
        "md": f"{CAMPAIGN}/npcs/grimshaw.md",
        "img": f"{CAMPAIGN}/npcs/grimshaw.png",
        "prompt": "An elderly half-elf man in his 70s. Slightly pointed ears, kind tired eyes, deeply weathered face, tattered ragged clothing. Gentle and generous expression, the kind of man who gives away his last meal.",
        "size": "1024x1024", "width": 512, "height": 512,
    },
    {
        "md": f"{CAMPAIGN}/npcs/bristle.md",
        "img": f"{CAMPAIGN}/npcs/bristle.png",
        "prompt": "A small sassy woodland creature with huge dark liquid eyes, soft gray-brown fur, and a long bushy tail, mid-glide between two trees — all four legs stretched wide, a thin furred skin membrane stretching from its front wrists to its back ankles like a cape, no wings.",
        "size": "1024x1024", "width": 512, "height": 512,
    },
    {
        "md": f"{CAMPAIGN}/party/fib-noodlecork.md",
        "img": f"{CAMPAIGN}/party/fib-noodlecork.png",
        "prompt": "An elderly forest gnome bard sitting on a tree stump playing the lute for a small audience of crickets in a moonlit forest clearing. Small stature, warm expressive face, twinkling mischievous eyes, short white beard, bushy eyebrows, blue robe. Weathered but full of life.",
        "size": "1024x1024", "width": 512, "height": 512,
    },
    {
        "md": f"{CAMPAIGN}/npcs/inkus.md",
        "img": f"{CAMPAIGN}/npcs/inkus.png",
        "prompt": "A mysterious lower-tier deity and warlock patron manifesting in a dream. An unsettling half-formed figure wreathed in dark cosmic energy, glowing eldritch eyes. Neither fully human nor alien, dreamlike and disturbing.",
        "size": "1024x1024", "width": 512, "height": 512,
    },
    {
        "md": f"{CAMPAIGN}/npcs/lord-halvar-dendros.md",
        "img": f"{CAMPAIGN}/npcs/lord-halvar-dendros.png",
        "prompt": "A short stout human nobleman in his 50s. Silver-streaked hair, lined commanding face, gravitas of a man who has wielded power for decades. Polished plate armor with noble insignia. Calculating and authoritative expression.",
        "size": "1024x1024", "width": 512, "height": 512,
    },
    {
        "md": f"{CAMPAIGN}/locations/silver-oak.md",
        "img": f"{CAMPAIGN}/locations/silver-oak.png",
        "prompt": "Interior of a grand medieval feast hall inside a stone fortress. Long banquet tables set for a lavish feast, ornate dark wood beams overhead, warm torchlight from iron chandeliers, silver oak tree motifs carved into the pillars.",
        "size": "1536x1024", "width": 896, "height": 512,
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
        model="gpt-image-2",
        prompt=entry["prompt"] + " " + STYLE,
        size=entry["size"],
        quality="auto",
        n=1,
    )
    return base64.b64decode(response.data[0].b64_json)


backend = "local AI server (fantasy LoRA)" if USE_LOCAL else "gpt-image-2"
print(f"Using: {backend}\n")

target = next((a for a in sys.argv[1:] if not a.startswith("--")), None)

for entry in ENTRIES:
    img_path = entry["img"]
    img_filename = os.path.basename(img_path)
    md_path = entry["md"]
    name = os.path.basename(md_path).replace(".md", "")

    if target and target not in name:
        continue

    print(f"[{name}] Generating...")
    try:
        img_bytes = generate_local(entry) if USE_LOCAL else generate_openai(entry)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    with open(img_path, "wb") as f:
        f.write(img_bytes)
    print(f"  Saved {img_path}")
    prepend_image_ref(md_path, img_filename)

print("\nDone.")
