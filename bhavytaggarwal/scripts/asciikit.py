"""Turn text (or an image) into a grid of ramp characters, then into an SVG.

The wordmark is your name set large in JetBrains Mono Bold, rasterised, then
resampled down to a coarse grid and mapped through the character ramp. Same
ramp the year strip uses, so the two graphics visibly belong together.

Why a grid of characters rather than just big text: it announces that the page
is generated. That is the whole point of the profile - the graphic is evidence
of the pipeline, not decoration on top of it.
"""

import os

from PIL import Image, ImageDraw, ImageFont

import fontkit
import theme

HERE = os.path.dirname(os.path.abspath(__file__))
BOLD = os.path.join(HERE, "fonts", "JetBrainsMono-Bold.ttf")


def _rasterise(lines: list[str], px: int = 220) -> Image.Image:
    """Draw the text large and tight-cropped, white on black."""
    font = ImageFont.truetype(BOLD, px)
    widths, heights = [], []
    for line in lines:
        box = font.getbbox(line)
        widths.append(box[2] - box[0])
        heights.append(box[3] - box[1])

    pad = px // 6
    line_gap = int(px * 0.18)
    w = max(widths) + pad * 2
    h = sum(heights) + line_gap * (len(lines) - 1) + pad * 2

    img = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(img)
    y = pad
    for line, lh in zip(lines, heights):
        box = font.getbbox(line)
        draw.text((pad - box[0], y - box[1]), line, fill=255, font=font)
        y += lh + line_gap
    return img


def to_grid(img: Image.Image, cols: int, ramp: str = theme.RAMP) -> list[str]:
    """Resample to `cols` wide and map luminance onto the ramp.

    Row count compensates for the cell being 0.600 em wide and 1.0 em tall, so
    the result is not vertically stretched.
    """
    aspect = fontkit.ADVANCE_EM  # cell width / cell height
    rows = max(1, round(cols * aspect * img.height / img.width))
    small = img.resize((cols, rows), Image.LANCZOS)

    px = small.load()
    out = []
    for y in range(rows):
        row = []
        for x in range(cols):
            level = int(px[x, y] / 256 * len(ramp))
            row.append(ramp[min(level, len(ramp) - 1)])
        out.append("".join(row).rstrip())
    # Trim fully blank rows top and bottom.
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def grid_svg(
    grid: list[str],
    font_size: int = 13,
    title: str = "",
    animate: bool = True,
    ramp: str = theme.RAMP,
) -> str:
    """Render a character grid as an SVG, one <text> per row.

    Each row fades in on a short stagger. SMIL, not CSS animation and not
    JavaScript - GitHub strips scripts from READMEs, but SVG animation elements
    survive the sanitiser.
    """
    cell_w = font_size * fontkit.ADVANCE_EM
    line_h = font_size * 1.0
    cols = max((len(r) for r in grid), default=0)
    pad = font_size

    width = round(cols * cell_w) + pad * 2
    height = round(len(grid) * line_h) + pad * 2

    # Tone class per ramp index: quiet characters recede, loud ones take accent.
    tone = ["faint", "faint", "mute", "mute", "ink", "accent"]

    rows = []
    for i, line in enumerate(grid):
        y = pad + i * line_h + line_h / 2
        # Split the row into runs of the same tone so we emit few <tspan>s.
        spans, run, run_tone = [], "", None
        for ch in line:
            t = tone[min(ramp.index(ch) if ch in ramp else 0, len(tone) - 1)]
            if t != run_tone and run:
                spans.append((run_tone, run))
                run = ""
            run_tone, run = t, run + ch
        if run:
            spans.append((run_tone, run))

        body = "".join(
            f'<tspan class="{t}">{s.replace("&", "&amp;").replace("<", "&lt;")}</tspan>'
            for t, s in spans
        )
        fade = ""
        if animate:
            delay = round(i * 0.045, 3)
            fade = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'dur="0.5s" begin="{delay}s" fill="freeze"/>'
            )
        # Note: no opacity="0" start state. The element's default opacity is 1
        # and the animation runs 0 -> 1 over it, so if SMIL is ever unavailable
        # the text is simply visible rather than invisible.
        rows.append(
            f'<text x="{pad}" y="{y:.1f}" font-size="{font_size}">'
            f"{body}{fade}</text>"
        )

    chars = "".join(sorted(set("".join(grid))))
    style = theme.style_block(fontkit.face(chars, "regular"))
    return theme.svg(width, height, "".join(rows), style, title)


def wordmark(lines: list[str], cols: int = 62, font_size: int = 12) -> str:
    """The page's opening graphic: a name, rendered as ramp characters."""
    img = _rasterise([l.upper() for l in lines])
    grid = to_grid(img, cols)
    return grid_svg(grid, font_size=font_size, title=" ".join(lines))


def portrait(path: str, cols: int = 74, font_size: int = 11) -> str:
    """Same pipeline, fed a photo instead. Unused by default - kept because
    swapping the wordmark for a portrait should be a one-line change."""
    img = Image.open(path).convert("L")
    return grid_svg(to_grid(img, cols), font_size=font_size, title="portrait")
