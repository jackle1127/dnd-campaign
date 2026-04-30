#!/usr/bin/env python3
"""Generate missing character/location images using OpenAI DALL-E 3."""

import keyring
import os
import urllib.request
from openai import OpenAI

client = OpenAI(api_key=keyring.get_password("openai", "api-key"))
CAMPAIGN = os.path.join(os.path.dirname(__file__), "this-is-bullcrit")

ENTRIES = [
    {
        "md": f"{CAMPAIGN}/party/alarak-vaelor-veltharion.md",
        "img": f"{CAMPAIGN}/party/alarak-vaelor-veltharion.png",
        "prompt": "Digital fantasy portrait of Alarak Vaelor Veltharion, a dhampir paladin. Pale undead complexion, subtle fangs, striking and charismatic face. Wearing half plate armor, a greatsword at his back. Dark and brooding but magnetic — a vampire-touched holy warrior. Dramatic candlelit lighting, painterly dark fantasy art style, detailed.",
        "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/npcs/grimshaw.md",
        "img": f"{CAMPAIGN}/npcs/grimshaw.png",
        "prompt": "Digital fantasy portrait of Grimshaw, an elderly half-elf prisoner. Slightly pointed ears, weathered and kind face, tired but warm eyes. Wearing tattered prison rags. The kind of man who gives away his food to someone who needs it more. Dark dungeon stone background, painterly fantasy art style, soft lighting.",
        "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/npcs/bristle.md",
        "img": f"{CAMPAIGN}/npcs/bristle.png",
        "prompt": "Digital fantasy illustration of Bristle, a small sassy flying squirrel. Expressive mischievous eyes, fluffy with gliding membranes spread, perched confidently like he owns the place. Fantasy animal companion with attitude. Whimsical painterly art style, detailed fur texture, warm natural lighting.",
        "size": "1024x1024",
    },
    {
        "md": f"{CAMPAIGN}/party/fib-noodlecork.md",
        "img": f"{CAMPAIGN}/party/fib-noodlecork.png",
        "prompt": "Digital fantasy portrait of Fib Noodlecork, an elderly forest gnome bard. Small stature, warm expressive face, twinkling eyes full of mischief and old secrets. Wearing traveler's clothes layered for cold weather, a borrowed lute slung on his back. The kind of gnome who has spent decades listening in warm taverns. Rich painterly fantasy art style, detailed, warm candlelit lighting.",
        "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/npcs/inkus.md",
        "img": f"{CAMPAIGN}/npcs/inkus.png",
        "prompt": "Digital fantasy portrait of Inkus, a mysterious lower-tier deity and warlock patron who visits his charge in dreams. An ethereal and unsettling presence, half-formed in swirling dark cosmic void, eyes that glow with eldritch light. Neither fully human nor fully alien. Dreamlike and disturbing, painterly dark fantasy art.",
        "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/npcs/lord-halvar-dendros.md",
        "img": f"{CAMPAIGN}/npcs/lord-halvar-dendros.png",
        "prompt": "Digital fantasy portrait of Lord Halvar Dendros, a short stout human nobleman. Wearing polished shiny plate armor with noble insignia. Distinguished bearing, authoritative and calculating expression, the face of a man accustomed to getting what he wants. Painterly fantasy art style, dramatic lighting.",
        "size": "1024x1792",
    },
    {
        "md": f"{CAMPAIGN}/locations/silver-oak.md",
        "img": f"{CAMPAIGN}/locations/silver-oak.png",
        "prompt": "Digital fantasy illustration of the Silver Oak feast hall interior, a grand medieval banquet venue inside Ironwood Fortress. Long tables set for a feast, ornate dark wood beams overhead, warm torchlight from iron chandeliers, silver oak tree motifs carved into pillars. Atmospheric and opulent, painterly fantasy art style.",
        "size": "1792x1024",
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

for entry in ENTRIES:
    img_path = entry["img"]
    img_filename = os.path.basename(img_path)
    md_path = entry["md"]
    name = os.path.basename(md_path).replace(".md", "")

    print(f"\n[{name}] Generating...")
    response = client.images.generate(
        model="dall-e-3",
        prompt=entry["prompt"],
        size=entry["size"],
        quality="standard",
        n=1,
    )

    url = response.data[0].url
    urllib.request.urlretrieve(url, img_path)
    print(f"  Saved {img_path}")
    prepend_image_ref(md_path, img_filename)

print("\nDone.")
