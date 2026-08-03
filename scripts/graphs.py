"""The graphics that go stale: the year calendar, the streak counters, and the
language split. Everything here is redrawn by the scheduled workflow.
"""

import datetime as dt

import fontkit
import theme

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun",
          "jul", "aug", "sep", "oct", "nov", "dec"]


def _level(count: int, scale: int) -> int:
    """Map a day's count onto a ramp index. `scale` is a high percentile of the
    year, so a quiet year still shows contrast instead of one flat tone."""
    if count <= 0:
        return 0
    for i, frac in enumerate((0.12, 0.30, 0.55, 0.80), start=1):
        if count <= max(1, round(scale * frac)):
            return i
    return 5


def year_calendar(days, font_size: int = 13, width: int = 562) -> str:
    """53 weeks across, 7 days down, one ramp character per day.

    The same ramp as the wordmark: quiet to loud. A blank cell is a day with
    nothing, which is information, not a gap to be embarrassed about.
    """
    counts = sorted((n for _, n in days if n), reverse=True)
    scale = counts[max(0, len(counts) // 12)] if counts else 1

    # Pad the front so column 0 starts on a Sunday.
    lead = (days[0][0].weekday() + 1) % 7 if days else 0
    cells = [None] * lead + list(days)

    weeks: list[list] = []
    for i in range(0, len(cells), 7):
        weeks.append(cells[i : i + 7])

    cell_w = font_size * fontkit.ADVANCE_EM
    line_h = font_size * 1.15
    pad = font_size
    label_w = cell_w * 4

    # Month label row: mark the week where each month first appears.
    labels = [" "] * len(weeks)
    seen = set()
    for wi, week in enumerate(weeks):
        for day in week:
            if day and day[0].month not in seen and day[0].day <= 7:
                seen.add(day[0].month)
                labels[wi] = MONTHS[day[0].month - 1]
                break
    label_line = ""
    wi = 0
    while wi < len(labels):
        if labels[wi] != " ":
            label_line += labels[wi]
            wi += 3
        else:
            label_line += " "
            wi += 1

    tone = ["faint", "faint", "mute", "mute", "ink", "accent"]
    rows = []
    y = pad + line_h
    rows.append(
        f'<text x="{pad + label_w:.1f}" y="{y:.1f}" font-size="{font_size}" '
        f'class="faint">{label_line}</text>'
    )

    day_labels = ["", "mon", "", "wed", "", "fri", ""]
    for d in range(7):
        y += line_h
        spans, run, run_tone = [], "", None
        for week in weeks:
            day = week[d] if d < len(week) else None
            if day is None:
                ch, t = " ", "faint"
            else:
                lv = _level(day[1], scale)
                ch, t = theme.RAMP[lv], tone[lv]
            if t != run_tone and run:
                spans.append((run_tone, run))
                run = ""
            run_tone, run = t, run + ch
        if run:
            spans.append((run_tone, run))
        body = "".join(f'<tspan class="{t}">{s}</tspan>' for t, s in spans)
        rows.append(
            f'<text x="{pad}" y="{y:.1f}" font-size="{font_size}" class="faint">'
            f'{day_labels[d]:<4}</text>'
            f'<text x="{pad + label_w:.1f}" y="{y:.1f}" font-size="{font_size}">{body}'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.7s" '
            f'begin="{round(d * 0.06, 2)}s" fill="freeze"/></text>'
        )

    height = round(y + pad)
    chars = "".join(sorted(set(theme.RAMP + label_line + "monwedfri")))
    style = theme.style_block(fontkit.face(chars))
    total = sum(n for _, n in days)
    return theme.svg(
        width, height, "".join(rows), style,
        f"{total} contributions in the last year",
    )


def streak_card(current: int, longest: int, total: int,
                font_size: int = 13, width: int = 562) -> str:
    """Three numbers, set large, with quiet labels underneath."""
    stats = [(str(total), "contributions"), (str(current), "current streak"),
             (str(longest), "longest streak")]
    pad = font_size
    col = (width - pad * 2) / 3
    big = font_size * 2.4

    body = []
    for i, (value, label) in enumerate(stats):
        cx = pad + col * i + col / 2
        body.append(
            f'<text x="{cx:.1f}" y="{pad + big * 0.75:.1f}" font-size="{big:.1f}" '
            f'text-anchor="middle" class="accent" font-weight="700">{value}</text>'
            f'<text x="{cx:.1f}" y="{pad + big * 1.5:.1f}" font-size="{font_size}" '
            f'text-anchor="middle" class="mute" letter-spacing="0.5">{label}</text>'
        )
        if i:
            x = pad + col * i
            body.append(
                f'<line x1="{x:.1f}" y1="{pad}" x2="{x:.1f}" '
                f'y2="{pad + big * 1.7:.1f}" class="rule" stroke-width="1"/>'
            )

    height = round(pad * 2 + big * 1.7)
    chars = "".join(sorted(set("".join(v + l for v, l in stats))))
    style = theme.style_block(
        fontkit.face(chars, "regular") + fontkit.face("0123456789", "bold")
    )
    return theme.svg(width, height, "".join(body), style,
                     f"{current} day current streak, {longest} longest")


def language_bar(langs, top: int = 5, font_size: int = 13,
                 width: int = 562) -> str:
    """A stacked bar plus a legend. Public non-fork repositories only."""
    langs = langs[:top]
    total = sum(size for _, size, _ in langs) or 1
    pad = font_size
    bar_w = width - pad * 2
    bar_h = font_size * 0.7
    line_h = font_size * 1.5

    body, x = [], float(pad)
    for i, (_, size, colour) in enumerate(langs):
        w = bar_w * size / total
        r = 'rx="2"' if i in (0, len(langs) - 1) else ""
        body.append(
            f'<rect x="{x:.1f}" y="{pad}" width="{w:.1f}" height="{bar_h:.1f}" '
            f'{r} fill="{colour}"><animate attributeName="width" from="0" '
            f'to="{w:.1f}" dur="0.8s" fill="freeze"/></rect>'
        )
        x += w

    y = pad + bar_h + line_h
    for name, size, colour in langs:
        pct = 100 * size / total
        body.append(
            f'<circle cx="{pad + 4}" cy="{y - font_size * 0.35:.1f}" r="4" '
            f'fill="{colour}"/>'
            f'<text x="{pad + 16}" y="{y - font_size * 0.35:.1f}" '
            f'font-size="{font_size}" class="ink">{name}</text>'
            f'<text x="{width - pad}" y="{y - font_size * 0.35:.1f}" '
            f'font-size="{font_size}" class="mute" text-anchor="end">'
            f'{pct:.1f}%</text>'
        )
        y += line_h

    height = round(y - line_h + pad + font_size * 0.5)
    chars = "".join(sorted(set("".join(n for n, _, _ in langs) + "0123456789.%")))
    style = theme.style_block(fontkit.face(chars))
    return theme.svg(width, height, "".join(body), style, "top languages")
