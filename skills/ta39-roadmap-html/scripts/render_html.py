#!/usr/bin/env python3
"""
render_html.py — transform TA39-Roadmap.md into TA39-Roadmap.html.

Usage:
    python3 render_html.py <md_path> [<out_path>]

Parses the MD's NOW / NEXT / LATER (themed) tables and the Strategic
Call-outs, then emits a standalone HTML dashboard using Tailwind via CDN
plus custom CSS variables for the theme palette.

No external Python deps — stdlib only.
"""

from __future__ import annotations

import html as _html
import os as _os
import re as _re
import sys as _sys
from typing import Any

# Fixed theme palette.  Adding a theme here requires updating the MD section
# headers the renderer looks for.
THEME_PALETTE: dict[str, dict[str, str]] = {
    "Agentic / Copilot evolution": {
        "key": "agentic",
        "color": "#4f46e5",
        "bg": "#eef2ff",
        "border": "#c7d2fe",
        "text": "#312e81",
    },
    "Teacher-in-the-loop intelligence": {
        "key": "hitl",
        "color": "#059669",
        "bg": "#ecfdf5",
        "border": "#a7f3d0",
        "text": "#064e3b",
    },
    "Quality & evaluation stack": {
        "key": "quality",
        "color": "#e11d48",
        "bg": "#fff1f2",
        "border": "#fecdd3",
        "text": "#881337",
    },
    "Integrations & LMS breadth": {
        "key": "lms",
        "color": "#d97706",
        "bg": "#fffbeb",
        "border": "#fde68a",
        "text": "#78350f",
    },
    "Monetization": {
        "key": "monetization",
        "color": "#7c3aed",
        "bg": "#f5f3ff",
        "border": "#ddd6fe",
        "text": "#4c1d95",
    },
    "Competitive Parity": {
        "key": "parity",
        "color": "#ea580c",
        "bg": "#fff7ed",
        "border": "#fed7aa",
        "text": "#9a3412",
    },
}

# Match links like [#697](https://github.com/TA-39/frontend/issues/697)
ISSUE_LINK_RE = _re.compile(
    r"\[#(\d+)\]\((https?://github\.com/[^)]+/issues/\d+)\)"
)

# Match bucket section headers
NOW_HEADER_RE = _re.compile(r"^##\s+NOW\b", _re.M)
NEXT_HEADER_RE = _re.compile(r"^##\s+NEXT\b", _re.M)
LATER_HEADER_RE = _re.compile(r"^##\s+LATER\b", _re.M)
THEME_HEADER_RE = _re.compile(r"^###\s+Theme\s+\d+\s+[—–-]\s+(.+?)(?:\s+\*.*)?$", _re.M)
HIDDEN_INV_RE = _re.compile(r"^##\s+Shipped but NOT publicly announced\b", _re.M)


def _extract_section(md: str, start_re: _re.Pattern, next_re: _re.Pattern | None) -> str:
    m = start_re.search(md)
    if not m:
        return ""
    start = m.end()
    if next_re:
        nm = next_re.search(md, start)
        end = nm.start() if nm else len(md)
    else:
        end = len(md)
    return md[start:end]


def _extract_table_rows(section: str) -> list[list[str]]:
    """Return list of rows, each a list of cell strings, for the first
    pipe-delimited table in the section."""
    rows: list[list[str]] = []
    in_table = False
    for line in section.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s[1:-1].split("|")]
            # skip the header separator row (|---|---|...)
            if all(_re.fullmatch(r":?-+:?", c) for c in cells):
                in_table = True
                continue
            rows.append(cells)
            in_table = True
        elif in_table and not s:
            # blank line ends the first table
            break
    # The first non-separator row is the header; remove it
    return rows[1:] if len(rows) > 1 else []


def _parse_issue_cell(cell: str) -> tuple[str | None, str | None, str]:
    """Return (issue_number, issue_url, remaining_text_after_link)."""
    m = ISSUE_LINK_RE.search(cell)
    if not m:
        return None, None, cell
    issue_num = m.group(1)
    url = m.group(2)
    remainder = cell[m.end():].strip()
    return issue_num, url, remainder


def _has_parity_overlay(cell: str) -> bool:
    return "⚔" in cell  # matches ⚔️ (with or without variation selector)


def parse_now(md: str) -> list[dict[str, Any]]:
    section = _extract_section(md, NOW_HEADER_RE, NEXT_HEADER_RE)
    out: list[dict[str, Any]] = []
    for row in _extract_table_rows(section):
        if len(row) < 6:
            continue
        num, url, _ = _parse_issue_cell(row[0])
        if not num:
            continue
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(row[1]),
            "repo": row[2],
            "status": row[3],
            "priority": row[4],
            "size": row[5],
            "tags": row[6] if len(row) > 6 else "",
            "notes": "",
            "parity_overlay": _has_parity_overlay(" | ".join(row)),
        })
    return out


def parse_next(md: str) -> list[dict[str, Any]]:
    section = _extract_section(md, NEXT_HEADER_RE, LATER_HEADER_RE)
    out: list[dict[str, Any]] = []
    for row in _extract_table_rows(section):
        if len(row) < 6:
            continue
        num, url, _ = _parse_issue_cell(row[0])
        if not num:
            continue
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(row[1]),
            "repo": row[2],
            "priority": row[3],
            "size": row[4],
            "tags": row[5],
            "notes": row[6] if len(row) > 6 else "",
            "parity_overlay": _has_parity_overlay(" | ".join(row)),
        })
    return out


def parse_later(md: str) -> dict[str, list[dict[str, Any]]]:
    """Return {theme_name: [items...]} for each Theme section."""
    section = _extract_section(md, LATER_HEADER_RE, HIDDEN_INV_RE)
    out: dict[str, list[dict[str, Any]]] = {}

    theme_matches = list(THEME_HEADER_RE.finditer(section))
    for i, m in enumerate(theme_matches):
        name = m.group(1).strip()
        # Strip trailing parenthetical qualifiers like "(the next platform bet)"
        # so the name matches THEME_PALETTE keys.
        name = _re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
        start = m.end()
        end = (
            theme_matches[i + 1].start()
            if i + 1 < len(theme_matches)
            else len(section)
        )
        body = section[start:end]
        rows = _extract_table_rows(body)
        items: list[dict[str, Any]] = []
        for row in rows:
            if not row:
                continue
            num, url, remainder = _parse_issue_cell(row[0])
            if not num:
                continue
            items.append({
                "num": num,
                "url": url,
                "title": _strip_md(row[1]) if len(row) > 1 else "",
                "status": row[-3] if len(row) >= 4 else "",
                "priority": row[-2] if len(row) >= 3 else "",
                "size": row[-1] if len(row) >= 2 else "",
                "parity_overlay": _has_parity_overlay(" | ".join(row)),
            })
        out[name] = items
    return out


def parse_hidden_inventory(md: str) -> list[dict[str, Any]]:
    section = _extract_section(md, HIDDEN_INV_RE, _re.compile(r"^##\s+Risks", _re.M))
    out: list[dict[str, Any]] = []
    for row in _extract_table_rows(section):
        if len(row) < 3:
            continue
        num, url, _ = _parse_issue_cell(row[0])
        if not num:
            continue
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(row[1]),
            "shipped": row[2],
            "note": row[3] if len(row) > 3 else "",
        })
    return out


def parse_retrieval_date(md: str) -> str:
    m = _re.search(r"re-pulled\s+(\d{4}-\d{2}-\d{2})", md)
    return m.group(1) if m else ""


def _strip_md(s: str) -> str:
    # very light cleanup for common inline md
    s = _re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = _re.sub(r"\*(.+?)\*", r"\1", s)
    return s.strip()


def _theme_for_item(num: str, later: dict[str, list[dict[str, Any]]]) -> str | None:
    for theme, items in later.items():
        for it in items:
            if it["num"] == num:
                return theme
    return None


def _palette_for(theme: str | None) -> dict[str, str]:
    if not theme or theme not in THEME_PALETTE:
        return {
            "color": "#64748b",
            "bg": "#f8fafc",
            "border": "#e2e8f0",
            "text": "#334155",
        }
    return THEME_PALETTE[theme]


def _pill(num: str, url: str | None, parity: bool, theme: str | None) -> str:
    pal = _palette_for(theme)
    overlay = " ⚔️" if parity else ""
    href = _html.escape(url or "#")
    return (
        f'<a href="{href}" class="inline-flex items-center gap-0.5 '
        f'rounded-md text-xs font-mono px-1.5 py-0.5 border" '
        f'style="color:{pal["text"]};background:{pal["bg"]};'
        f'border-color:{pal["border"]}">#{num}{overlay}</a>'
    )


def _card(item: dict[str, Any], theme: str | None, bucket_label: str) -> str:
    pal = _palette_for(theme)
    overlay_dot = (
        f'<span class="absolute top-1 right-1 w-2 h-2 rounded-full" '
        f'style="background:{THEME_PALETTE["Competitive Parity"]["color"]}" '
        f'title="Competitive Parity"></span>'
        if item.get("parity_overlay")
        else ""
    )
    href = _html.escape(item.get("url") or "#")
    title = _html.escape(item.get("title", ""))
    num = item.get("num", "")
    pills = []
    for k, label in (("priority", "priority"), ("size", "size")):
        v = (item.get(k) or "").strip()
        if v and v != "—":
            pills.append(
                '<span class="text-[10px] uppercase tracking-wide rounded '
                'px-1 py-0.5 bg-slate-100 text-slate-600">'
                f'{label}: {_html.escape(v)}</span>'
            )
    status = (item.get("status") or "").strip()
    if status and status != "—":
        pills.append(
            '<span class="text-[10px] rounded px-1 py-0.5 bg-slate-50 '
            f'text-slate-500 border border-slate-200">{_html.escape(status)}</span>'
        )
    tags = _html.escape(item.get("tags") or "").replace("`", "")
    pills_html = " ".join(pills)
    bucket_tag = _html.escape(bucket_label)
    tags_block = (
        f'<div class="text-[11px] text-slate-500 mt-1">{tags}</div>' if tags else ""
    )
    return (
        '<div class="relative rounded-lg border p-2 bg-white shadow-sm" '
        f'style="border-color:{pal["border"]}">'
        f'{overlay_dot}'
        '<div class="flex items-baseline gap-1.5 mb-1">'
        f'<a href="{href}" class="font-mono text-xs" '
        f'style="color:{pal["color"]}">#{num}</a>'
        f'<span class="text-xs text-slate-400">{bucket_tag}</span>'
        '</div>'
        f'<div class="text-sm leading-snug text-slate-800 mb-1">{title}</div>'
        f'<div class="flex flex-wrap gap-1">{pills_html}</div>'
        f'{tags_block}'
        '</div>'
    )


def render(md_path: str, out_path: str) -> None:
    md = open(md_path, encoding="utf-8").read()

    retrieval_date = parse_retrieval_date(md)
    now_items = parse_now(md)
    next_items = parse_next(md)
    later = parse_later(md)
    hidden = parse_hidden_inventory(md)

    # Determine each NOW/NEXT item's theme by cross-referencing LATER themes
    # and by simple keyword inference for items not listed in LATER.
    def classify(it: dict[str, Any]) -> str | None:
        # parity overlay items still keep their primary theme
        t = _theme_for_item(it["num"], later)
        if t:
            return t
        title = (it.get("title") or "").lower()
        if "copilot" in title or "agent" in title:
            return "Agentic / Copilot evolution"
        if any(k in title for k in ("arabic", "rtl", "i18n", "international")):
            return "Arabic NLP / i18n"
        if any(k in title for k in ("rubric", "template", "exemplar")):
            return "Content / rubric tools"
        if any(k in title for k in ("lms", "canvas", "classroom", "teams", "lti")):
            return "Integrations & LMS breadth"
        if any(k in title for k in ("eval", "sentinel", "quality", "confidence")):
            return "Quality & evaluation stack"
        if any(k in title for k in ("stripe", "subscription", "paid")):
            return "Monetization"
        if any(k in title for k in ("plagiarism",)):
            return "Competitive Parity"
        return None

    for lst in (now_items, next_items):
        for it in lst:
            it["_theme"] = classify(it)

    # Compose the portfolio matrix: rows = themes (in palette order), cols = Now/Next/Later
    themes_in_order = list(THEME_PALETTE.keys())
    # also include any LATER themes not already in the palette
    for t in later.keys():
        if t not in themes_in_order:
            themes_in_order.append(t)

    matrix: dict[str, dict[str, list[dict[str, Any]]]] = {
        t: {"now": [], "next": [], "later": []} for t in themes_in_order
    }
    for it in now_items:
        matrix.setdefault(it["_theme"] or "Uncategorized", {"now": [], "next": [], "later": []})
        matrix[it["_theme"] or "Uncategorized"]["now"].append(it)
    for it in next_items:
        matrix.setdefault(it["_theme"] or "Uncategorized", {"now": [], "next": [], "later": []})
        matrix[it["_theme"] or "Uncategorized"]["next"].append(it)
    for theme, items in later.items():
        matrix.setdefault(theme, {"now": [], "next": [], "later": []})
        matrix[theme]["later"].extend(items)

    # After setdefault may have introduced new themes (from classify inference
    # or "Uncategorized"), extend themes_in_order so they render in the matrix
    # and swim lanes.  Keep palette themes first, then any LATER themes
    # already appended, then inferred themes discovered during classification.
    for t in matrix.keys():
        if t not in themes_in_order:
            themes_in_order.append(t)

    # Render HTML
    parity_items = []
    for bucket_items in (now_items, next_items):
        for it in bucket_items:
            if it.get("parity_overlay"):
                parity_items.append(it)
    for theme, items in later.items():
        for it in items:
            if it.get("parity_overlay") or theme == "Competitive Parity":
                parity_items.append(it)
    parity_links = " · ".join(
        f'<a class="underline" href="{_html.escape(p["url"] or "#")}">#{p["num"]}</a>'
        for p in parity_items
    )

    # legend
    legend_items = "".join(
        f'<div class="flex items-center gap-2">'
        f'<span class="inline-block w-3 h-3 rounded-full" style="background:{p["color"]}"></span>'
        f'<span class="text-xs text-slate-700">{_html.escape(t)}</span>'
        f'</div>'
        for t, p in THEME_PALETTE.items()
    )

    # portfolio matrix
    matrix_rows = []
    for theme in themes_in_order:
        if theme not in matrix:
            continue
        pal = _palette_for(theme)
        cells = []
        for bucket in ("now", "next", "later"):
            pills = " ".join(
                _pill(it["num"], it.get("url"), it.get("parity_overlay", False), theme)
                for it in matrix[theme][bucket]
            )
            empty_cell = '<span class="text-slate-300 text-xs">—</span>'
            cell_content = pills if pills else empty_cell
            cells.append(
                '<td class="align-top p-2 border border-slate-200">'
                f'<div class="flex flex-wrap gap-1">{cell_content}</div>'
                '</td>'
            )
        matrix_rows.append(
            f'<tr>'
            f'<th class="text-left align-top p-2 border border-slate-200 text-sm font-semibold" '
            f'style="color:{pal["text"]};background:{pal["bg"]};border-color:{pal["border"]}">'
            f'{_html.escape(theme)}</th>'
            f'{"".join(cells)}'
            f'</tr>'
        )

    # swim lanes
    lanes = []
    for theme in themes_in_order:
        if theme not in matrix:
            continue
        pal = _palette_for(theme)
        cols = []
        for bucket_key, bucket_label in (("now", "NOW"), ("next", "NEXT"), ("later", "LATER")):
            cards = "".join(
                _card(it, theme, bucket_label) for it in matrix[theme][bucket_key]
            ) or '<div class="text-xs text-slate-300">—</div>'
            cols.append(
                f'<div class="flex-1 space-y-2">'
                f'<div class="text-[11px] uppercase tracking-wider text-slate-500 mb-1">{bucket_label}</div>'
                f'{cards}</div>'
            )
        lanes.append(
            f'<section class="border rounded-xl p-3 mb-3" '
            f'style="border-color:{pal["border"]};background:{pal["bg"]}30">'
            f'<div class="flex items-center gap-2 mb-2">'
            f'<span class="inline-block w-2.5 h-2.5 rounded-full" style="background:{pal["color"]}"></span>'
            f'<h3 class="text-sm font-semibold" style="color:{pal["text"]}">{_html.escape(theme)}</h3>'
            f'</div>'
            f'<div class="flex gap-3">{"".join(cols)}</div>'
            f'</section>'
        )

    # hidden inventory strip
    hidden_cards = "".join(
        f'<div class="rounded-lg border border-slate-200 bg-white p-2 min-w-[14rem]">'
        f'<div class="font-mono text-xs text-slate-500">#{h["num"]} · shipped {h["shipped"]}</div>'
        f'<div class="text-sm text-slate-800 leading-snug">{_html.escape(h["title"])}</div>'
        f'</div>'
        for h in hidden
    )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TA39 Product Roadmap</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
</style>
</head>
<body class="bg-slate-50 text-slate-900 p-6">
<header class="max-w-[1440px] mx-auto mb-6">
  <h1 class="text-2xl font-semibold">TA39 Product Roadmap</h1>
  <p class="text-sm text-slate-500 mt-1">
    Source of truth: <code class="bg-slate-100 px-1 rounded">{_html.escape(_os.path.basename(md_path))}</code>
    {f"· retrieved {retrieval_date}" if retrieval_date else ""}
  </p>
</header>

<section class="max-w-[1440px] mx-auto mb-6 bg-white border border-slate-200 rounded-xl p-4">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Legend</h2>
  <div class="grid grid-cols-3 md:grid-cols-6 gap-2">
    {legend_items}
  </div>
  <div class="text-[11px] text-slate-500 mt-3">
    ⚔️ = also carries the GitHub <code class="bg-slate-100 px-1 rounded">Competitive Parity</code> label.
    {f"Items: {parity_links}" if parity_links else ""}
  </div>
</section>

<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Theme portfolio matrix</h2>
  <table class="w-full border-collapse bg-white border border-slate-200 rounded-xl overflow-hidden text-sm">
    <thead>
      <tr class="bg-slate-50 text-slate-600">
        <th class="text-left p-2 border border-slate-200">Theme</th>
        <th class="text-left p-2 border border-slate-200">NOW</th>
        <th class="text-left p-2 border border-slate-200">NEXT</th>
        <th class="text-left p-2 border border-slate-200">LATER</th>
      </tr>
    </thead>
    <tbody>
      {"".join(matrix_rows)}
    </tbody>
  </table>
</section>

<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Swim lanes</h2>
  {"".join(lanes)}
</section>

{f'''
<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Hidden inventory — shipped, not announced</h2>
  <div class="flex gap-2 overflow-x-auto pb-2">{hidden_cards}</div>
</section>''' if hidden else ""}

<footer class="max-w-[1440px] mx-auto text-xs text-slate-400 mt-8">
  Regenerate with the <code>ta39-roadmap-html</code> skill. Data source: {_html.escape(md_path)}
</footer>
</body>
</html>
"""

    _os.makedirs(_os.path.dirname(_os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)


def main() -> None:
    if len(_sys.argv) < 2:
        print("Usage: render_html.py <md_path> [<out_path>]", file=_sys.stderr)
        _sys.exit(2)
    md_path = _sys.argv[1]
    out_path = (
        _sys.argv[2]
        if len(_sys.argv) > 2
        else _os.path.join(_os.path.dirname(md_path), "TA39-Roadmap.html")
    )
    render(md_path, out_path)
    print(out_path)


if __name__ == "__main__":
    main()
