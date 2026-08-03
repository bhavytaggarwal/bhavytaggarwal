"""One palette, used by every graphic.

Colours are declared as CSS custom properties inside each SVG with a
prefers-color-scheme override, so a single file works on both GitHub themes.
Caveat worth knowing: the media query follows the *browser/OS* setting, not the
GitHub theme dropdown. Someone with a light OS who forces GitHub dark will see
the light variant. In practice these two agree.
"""

# Slate ink on transparent paper, with a single deep-teal accent.
# Deliberately not the near-black + acid-green terminal cliche, and not the
# cream + terracotta look that shows up on every generated profile.
LIGHT = {
    "ink": "#15181c",
    "mute": "#5c666f",
    "faint": "#aab3bb",
    "accent": "#12695d",
    "accent_soft": "#5aa79a",
    "rule": "#d8dee4",
}

DARK = {
    "ink": "#e8eef4",
    "mute": "#95a1ac",
    "faint": "#4a545e",
    "accent": "#57c4ae",
    "accent_soft": "#2c7d70",
    "rule": "#2b3138",
}

# Quiet to loud. Shared by the wordmark and the year strip so the page reads as
# one system rather than a pile of unrelated widgets.
RAMP = " .:+#@"


def style_block(font_faces: str = "", extra: str = "") -> str:
    """The <style> element every graphic opens with."""
    light = ";".join(f"--{k}:{v}" for k, v in LIGHT.items())
    dark = ";".join(f"--{k}:{v}" for k, v in DARK.items())
    return (
        "<style>"
        f"{font_faces}"
        f"svg{{{light}}}"
        f"@media (prefers-color-scheme:dark){{svg{{{dark}}}}}"
        "text{font-family:'JBM',ui-monospace,SFMono-Regular,Menlo,monospace;"
        "white-space:pre;dominant-baseline:middle}"
        ".ink{fill:var(--ink)}.mute{fill:var(--mute)}.faint{fill:var(--faint)}"
        ".accent{fill:var(--accent)}.soft{fill:var(--accent_soft)}"
        ".rule{stroke:var(--rule)}"
        f"{extra}"
        "</style>"
    )


def svg(width: int, height: int, body: str, style: str, title: str = "") -> str:
    """Wrap body content in a root <svg>. Width/height in px at 1x."""
    label = f"<title>{title}</title>" if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{title}">'
        f"{label}{style}{body}</svg>"
    )
