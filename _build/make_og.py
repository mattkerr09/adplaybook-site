#!/usr/bin/env python3
"""Generate og.png, the card social platforms show when the site is shared.

A script rather than a checked-in binary, so the card can be regenerated when
the positioning changes and so the next person can see how it was made.

It reads its colours from render.py's design tokens instead of restating them,
because a hex value typed in two files is the drift this project keeps finding
elsewhere. Run from the repo root:

    python3 _build/make_og.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "og.png"
W, H = 1200, 630          # what Facebook, LinkedIn, X and Slack all expect

#: SF Pro ships as a variable font on macOS; PIL cannot select a weight from it,
#: so bold text uses the Helvetica family, which is metrically close enough at
#: card sizes and is present on every Mac.
FONTS = {
    "bold": ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/SFNS.ttf"],
    "regular": ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/SFNS.ttf"],
    "mono": ["/System/Library/Fonts/SFNSMono.ttf", "/System/Library/Fonts/Menlo.ttc"],
}


def font(kind: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    for path in FONTS[kind]:
        try:
            return ImageFont.truetype(path, size, index=index)
        except (OSError, ValueError):
            continue
    return ImageFont.load_default()


def tokens() -> dict[str, str]:
    """Pull the palette out of render.py rather than restating it here."""
    css = (ROOT / "_build" / "render.py").read_text(encoding="utf-8", errors="replace")
    want = {"black": "#000000", "white": "#f5f7fa", "grey": "#8a8f98",
            "blue": "#4c8dff", "hair": "#1c2029"}
    found = dict(want)
    for name in want:
        m = re.search(rf"--{name}\s*:\s*(#[0-9a-fA-F]{{3,8}})", css)
        if m:
            found[name] = m.group(1)
    return found


def rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main() -> int:
    t = tokens()
    img = Image.new("RGB", (W, H), rgb(t["black"]))
    d = ImageDraw.Draw(img)

    # A soft blue wash top-left, matching the site's radial glow. Drawn as
    # concentric translucent ellipses because PIL has no gradient primitive.
    glow = Image.new("RGB", (W, H), rgb(t["black"]))
    gd = ImageDraw.Draw(glow)
    br, bg, bb = rgb(t["blue"])
    for i in range(46, 0, -1):
        f = i / 46
        r = int(760 * f)
        gd.ellipse([-260 - r // 3, -300 - r // 3, -260 + r, -300 + r],
                   fill=(int(br * (1 - f) * 0.30), int(bg * (1 - f) * 0.30), int(bb * (1 - f) * 0.34)))
    img = Image.blend(img, glow, 0.85)
    d = ImageDraw.Draw(img)

    M = 84                                  # margin
    d.line([(M, 128), (M + 54, 128)], fill=rgb(t["blue"]), width=4)
    d.text((M, 146), "ADPLAYBOOK", font=font("mono", 26), fill=rgb(t["blue"]))

    # The headline is the site's actual proposition, not a tagline invented for
    # the card - a card that promises something the page does not is its own
    # small false claim.
    d.text((M, 214), "It writes the ad.", font=font("bold", 82, index=1), fill=rgb(t["white"]))
    d.text((M, 306), "Then it tries to", font=font("bold", 82, index=1), fill=rgb(t["white"]))
    d.text((M, 398), "prove you wrong.", font=font("bold", 82, index=1), fill=rgb(t["blue"]))

    d.line([(M, 520), (W - M, 520)], fill=rgb(t["hair"]), width=1)
    d.text((M, 548), "Every claim traced to a source  ·  8 platforms  ·  Mac",
           font=font("regular", 27), fill=rgb(t["grey"]))

    img.save(OUT, "PNG", optimize=True)
    kb = OUT.stat().st_size // 1024
    print(f"  wrote {OUT.relative_to(ROOT)}  {W}x{H}  {kb}KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
