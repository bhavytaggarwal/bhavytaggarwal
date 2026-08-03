"""Subset JetBrains Mono to just the glyphs a graphic uses, inline it as base64.

Every SVG in this repo carries its own typeface. Two reasons:
  1. Nothing loads from a third-party server, so nothing can rate-limit or go dark.
  2. The portrait's grid assumes an advance width of exactly 0.600 em. A viewer
     whose default monospace is narrower would see it squeezed.

Subsetting keeps each file small — a full TTF is ~270 KB, a 40-character subset
is ~4 KB.
"""

import base64
import io
import os

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

# JetBrains Mono: 1000 units/em, 600 units advance.
ADVANCE_EM = 0.600

_cache: dict[tuple[str, str], str] = {}


def _path(weight: str) -> str:
    name = "JetBrainsMono-Bold.ttf" if weight == "bold" else "JetBrainsMono-Regular.ttf"
    return os.path.join(FONTS, name)


def subset_b64(text: str, weight: str = "regular") -> str:
    """Return a base64 woff2 of the font, keeping only characters in `text`."""
    chars = "".join(sorted(set(text) | set(" ")))
    key = (weight, chars)
    if key in _cache:
        return _cache[key]

    font = TTFont(_path(weight), recalcTimestamp=False)
    options = subset.Options()
    options.flavor = "woff2"
    options.desubroutinize = True
    options.layout_features = []
    options.hinting = False
    options.notdef_outline = False
    options.drop_tables += ["DSIG"]
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=chars)
    subsetter.subset(font)

    # fontTools stamps head.modified with the current time on save, which would
    # make every run produce different bytes - and the scheduled workflow would
    # then commit all fourteen graphics every single day. Pin it.
    font["head"].created = font["head"].modified = 3_600_000_000

    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    font.close()

    out = base64.b64encode(buf.getvalue()).decode("ascii")
    _cache[key] = out
    return out


def face(text: str, weight: str = "regular", family: str = "JBM") -> str:
    """An @font-face rule with the subset inlined. Drop this in an SVG <style>."""
    b64 = subset_b64(text, weight)
    css_weight = 700 if weight == "bold" else 400
    return (
        f"@font-face{{font-family:'{family}';font-style:normal;"
        f"font-weight:{css_weight};src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
    )


def faces(regular_text: str = "", bold_text: str = "") -> str:
    """Both weights at once. Pass empty string to skip a weight."""
    out = []
    if regular_text:
        out.append(face(regular_text, "regular"))
    if bold_text:
        out.append(face(bold_text, "bold"))
    return "".join(out)
