"""Section headings as SVG.

GitHub strips CSS from README markdown, so an image is the only way to put the
page's own typeface into a heading. Each one is a label plus a rule that runs to
the right margin - the rule is doing work, not decoration: it sets the page's
column width so every graphic below it aligns to the same edge.
"""

import fontkit
import theme

FONT_SIZE = 13
WIDTH = 562  # matches the wordmark at 72 cols / 13px, so the page has one edge


def heading(label: str, font_size: int = FONT_SIZE, width: int = WIDTH) -> str:
    label = label.lower()
    cell = font_size * fontkit.ADVANCE_EM
    pad = font_size
    baseline = font_size * 1.6

    text_w = len(label) * cell
    rule_x1 = pad + text_w + cell * 1.5
    rule_x2 = width - pad

    body = (
        f'<text x="{pad}" y="{baseline}" font-size="{font_size}" '
        f'class="accent" letter-spacing="1.5">{label}</text>'
        f'<line x1="{rule_x1:.1f}" y1="{baseline}" x2="{rule_x2}" y2="{baseline}" '
        f'class="rule" stroke-width="1">'
        f'<animate attributeName="x2" from="{rule_x1:.1f}" to="{rule_x2}" '
        f'dur="0.6s" fill="freeze"/></line>'
    )

    style = theme.style_block(fontkit.face(label, "regular"))
    return theme.svg(width, round(font_size * 2.4), body, style, label)
