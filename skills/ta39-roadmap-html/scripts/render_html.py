#!/usr/bin/env python3
"""
render_html.py — transform TA39-Roadmap.md into TA39-Roadmap.html.

Usage:
    python3 render_html.py <md_path> [<out_path>]

The HTML is an executive dashboard — visual, scannable, at-a-glance. It is
NOT a rendered version of the MD file. The MD carries the analytical prose
(risks, strategic call-outs, ship-order reads, tagging rules). The HTML
carries the data: KPI counts, theme portfolio, swim lanes, marketing-gap
status, announcement coverage, hidden inventory.

If you find yourself about to dump a paragraph of MD prose onto this page,
stop — the MD reader already has that context. Turn the insight into a
chip, a count, a color, or a dot; or leave it in the MD.

No external Python deps — stdlib only.
"""

from __future__ import annotations

import html as _html
import os as _os
import re as _re
import sys as _sys
from typing import Any

# ---------------------------------------------------------------------------
# Theme palette — keys must match the MD skill's LATER theme names verbatim
# (after normalization). Adding a theme here requires adding a matching
# `### Theme N — <name>` header in the MD skill.
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Section header regexes. Load-bearing — change both sides (MD skill + this
# file) in the same commit.
# ---------------------------------------------------------------------------

STATUS_OVERVIEW_RE = _re.compile(r"^##\s+Status Overview\b", _re.M)
MARKETING_GAP_RE = _re.compile(r"^##\s+Marketing-vs-Ship Gap\b", _re.M)
ANNOUNCE_XREF_RE = _re.compile(r"^##\s+Announcement Cross-Reference\b", _re.M)
NOW_HEADER_RE = _re.compile(r"^##\s+NOW\b", _re.M)
NEXT_HEADER_RE = _re.compile(r"^##\s+NEXT\b", _re.M)
LATER_HEADER_RE = _re.compile(r"^##\s+LATER\b", _re.M)
HIDDEN_INV_RE = _re.compile(r"^##\s+Shipped but NOT publicly announced\b", _re.M)
RISKS_RE = _re.compile(r"^##\s+Risks", _re.M)

# Capture the full theme label up to end-of-line; post-process to drop the
# count "(N)" and any trailing italic commentary. The simpler the regex,
# the fewer things it can miscapture — normalization happens in Python.
THEME_HEADER_RE = _re.compile(r"^###\s+Theme\s+\d+\s+[—–-]\s+(.+?)\s*$", _re.M)

ISSUE_LINK_RE = _re.compile(
    r"\[#(\d+)\]\((https?://github\.com/[^)]+/issues/\d+)\)"
)


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _extract_section(
    md: str, start_re: _re.Pattern, next_re: _re.Pattern | None
) -> str:
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


def _extract_first_table(section: str) -> list[list[str]]:
    """Return the entire first pipe-delimited table including the header
    row; separator rows are stripped.
    """
    rows: list[list[str]] = []
    in_table = False
    saw_sep = False
    for line in section.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s[1:-1].split("|")]
            if all(_re.fullmatch(r":?-+:?", c) for c in cells):
                saw_sep = True
                continue
            rows.append(cells)
            in_table = True
        elif in_table and not s:
            break
    return rows if saw_sep else []


def _extract_table_rows(section: str) -> list[list[str]]:
    """Back-compat shim: data rows of the first table (header stripped)."""
    tbl = _extract_first_table(section)
    return tbl[1:] if len(tbl) > 1 else []


def _parse_issue_cell(cell: str) -> tuple[str | None, str | None, str]:
    m = ISSUE_LINK_RE.search(cell)
    if not m:
        return None, None, cell
    issue_num = m.group(1)
    url = m.group(2)
    remainder = cell[m.end():].strip()
    return issue_num, url, remainder


def _has_parity_overlay(cell: str) -> bool:
    return "⚔" in cell


def _strip_md(s: str) -> str:
    s = _re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = _re.sub(r"\*(.+?)\*", r"\1", s)
    return s.strip()


def _strip_inline_links(s: str) -> str:
    """[label](url) → label, for plain-text cell rendering."""
    return _re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s).strip()


# ---------------------------------------------------------------------------
# Section parsers — only the ones that feed visual elements
# ---------------------------------------------------------------------------

def parse_retrieval_date(md: str) -> str:
    m = _re.search(r"\*\*Retrieved:\*\*\s+(\d{4}-\d{2}-\d{2})", md)
    if m:
        return m.group(1)
    m = _re.search(r"re-pulled\s+(\d{4}-\d{2}-\d{2})", md)
    return m.group(1) if m else ""


def parse_status_overview(md: str) -> list[tuple[str, str]]:
    """Return [(label, count), ...] for the KPI strip."""
    section = _extract_section(md, STATUS_OVERVIEW_RE, MARKETING_GAP_RE)
    out: list[tuple[str, str]] = []
    for row in _extract_table_rows(section):
        if len(row) < 2:
            continue
        label = row[0].replace("**", "").strip()
        count = row[1].replace("**", "").strip()
        if not label or not count:
            continue
        if label.lower().startswith("in-scope total"):
            continue
        out.append((label, count))
    return out


def parse_marketing_gap(md: str) -> list[dict[str, str]]:
    """Return a compact representation of the features-page claims:
    [{claim, status, risk}, ...] where status is one of
    'met' | 'partial' | 'ambiguous'.
    """
    section = _extract_section(md, MARKETING_GAP_RE, ANNOUNCE_XREF_RE)
    out: list[dict[str, str]] = []
    for row in _extract_table_rows(section):
        if len(row) < 4:
            continue
        claim = _strip_md(_strip_inline_links(row[0]))
        reality = _strip_md(_strip_inline_links(row[2])).lower()
        risk = row[3].strip()
        if "partial" in reality:
            status = "partial"
        elif "ambiguous" in reality:
            status = "ambiguous"
        elif "met" in reality or "shipped" in reality:
            status = "met"
        else:
            status = "partial"
        out.append({"claim": claim, "status": status, "risk": risk})
    return out


def parse_announcement_xref(md: str) -> int:
    """Return the count of announced items."""
    section = _extract_section(md, ANNOUNCE_XREF_RE, NOW_HEADER_RE)
    return len(_extract_table_rows(section))


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
            "status": row[2],
            "priority": row[3],
            "size": row[4],
            "repo": row[5] if len(row) > 5 else "",
            "tags": row[6] if len(row) > 6 else "",
            "parity_overlay": _has_parity_overlay(" | ".join(row)),
        })
    return out


def parse_next(md: str) -> list[dict[str, Any]]:
    section = _extract_section(md, NEXT_HEADER_RE, LATER_HEADER_RE)
    out: list[dict[str, Any]] = []
    for row in _extract_table_rows(section):
        if len(row) < 5:
            continue
        num, url, _ = _parse_issue_cell(row[0])
        if not num:
            continue
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(row[1]),
            "priority": row[2],
            "size": row[3],
            "tags": row[4] if len(row) > 4 else "",
            "notes": row[5] if len(row) > 5 else "",
            "parity_overlay": _has_parity_overlay(" | ".join(row)),
        })
    return out


def _normalize_theme_name(raw: str) -> str:
    """Clean a captured theme label into a palette key.

    The MD skill writes theme headers like:
      Theme 3 — Quality & evaluation stack (7) — *dependency risk concentrated here*
    We drop the count and the italic commentary so the name matches
    THEME_PALETTE keys.
    """
    name = raw.strip()
    # Strip " — *...*" italic commentary (em-dash, en-dash, or hyphen).
    name = _re.sub(r"\s*[—–-]\s*\*[^*]*\*\s*$", "", name).strip()
    # Strip trailing "(…)" counts or qualifiers.
    name = _re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
    # Strip a stray trailing dash.
    name = _re.sub(r"\s*[—–-]\s*$", "", name).strip()
    return name


def parse_later(md: str) -> dict[str, list[dict[str, Any]]]:
    """Return {theme_name: [items...]} for each Theme section."""
    section = _extract_section(md, LATER_HEADER_RE, HIDDEN_INV_RE)
    out: dict[str, list[dict[str, Any]]] = {}

    # Cut off at the Cross-cutting sub-section — its items are duplicates
    # of topical-home entries and we don't want them rendered twice.
    cross_cut = _re.search(r"^###\s+Cross-cutting\b", section, _re.M)
    scope = section[: cross_cut.start()] if cross_cut else section

    theme_matches = list(THEME_HEADER_RE.finditer(scope))
    for i, m in enumerate(theme_matches):
        name = _normalize_theme_name(m.group(1))
        start = m.end()
        end = (
            theme_matches[i + 1].start()
            if i + 1 < len(theme_matches)
            else len(scope)
        )
        body = scope[start:end]
        rows = _extract_table_rows(body)
        items: list[dict[str, Any]] = []
        for row in rows:
            if not row:
                continue
            num, url, _ = _parse_issue_cell(row[0])
            if not num:
                continue
            items.append({
                "num": num,
                "url": url,
                "title": _strip_md(row[1]) if len(row) > 1 else "",
                "priority": row[2] if len(row) > 2 else "",
                "size": row[3] if len(row) > 3 else "",
                "status": row[4] if len(row) > 4 else "",
                "parity_overlay": _has_parity_overlay(" | ".join(row)),
            })
        out[name] = items
    return out


def parse_hidden_inventory(md: str) -> list[dict[str, Any]]:
    section = _extract_section(md, HIDDEN_INV_RE, RISKS_RE)
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
            "repo": row[2] if len(row) > 2 else "",
            "shipped": row[3] if len(row) > 3 else row[2],
        })
    return out


# ---------------------------------------------------------------------------
# Theme classification + pill / card components
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# KPI strip + marketing-gap chips
# ---------------------------------------------------------------------------

_KPI_COLOR = {
    "RELEASED": "#059669",
    "NOW": "#2563eb",
    "NEXT": "#7c3aed",
    "BLOCKED": "#e11d48",
    "LATER": "#475569",
    "ARCHIVED": "#94a3b8",
}


def _kpi_tile(label: str, count: str) -> str:
    color = _KPI_COLOR.get(label.upper(), "#334155")
    return (
        '<div class="bg-white border border-slate-200 rounded-xl px-4 py-3 flex-1 min-w-[7rem]">'
        f'<div class="text-[10px] uppercase tracking-wider font-semibold" style="color:{color}">{_html.escape(label)}</div>'
        f'<div class="text-2xl font-semibold text-slate-900 leading-none mt-1">{_html.escape(count)}</div>'
        '</div>'
    )


_GAP_STATUS_STYLE = {
    "met": ("✓", "#059669", "#ecfdf5", "#a7f3d0"),
    "partial": ("◐", "#d97706", "#fffbeb", "#fde68a"),
    "ambiguous": ("?", "#e11d48", "#fff1f2", "#fecdd3"),
}


def _gap_chip(claim: str, status: str) -> str:
    icon, color, bg, border = _GAP_STATUS_STYLE.get(status, _GAP_STATUS_STYLE["partial"])
    return (
        '<div class="inline-flex items-center gap-2 rounded-lg border px-2.5 py-1.5" '
        f'style="background:{bg};border-color:{border}">'
        f'<span class="font-semibold text-sm leading-none" style="color:{color}">{icon}</span>'
        f'<span class="text-xs text-slate-700">{_html.escape(claim)}</span>'
        '</div>'
    )


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render(md_path: str, out_path: str) -> None:
    md = open(md_path, encoding="utf-8").read()

    retrieval_date = parse_retrieval_date(md)
    status_kpis = parse_status_overview(md)
    marketing_gap = parse_marketing_gap(md)
    announced_count = parse_announcement_xref(md)
    now_items = parse_now(md)
    next_items = parse_next(md)
    later = parse_later(md)
    hidden = parse_hidden_inventory(md)

    # Classify NOW/NEXT items into themes via LATER, then heuristic.
    def classify(it: dict[str, Any]) -> str | None:
        t = _theme_for_item(it["num"], later)
        if t:
            return t
        title = (it.get("title") or "").lower()
        if "copilot" in title or "agent" in title:
            return "Agentic / Copilot evolution"
        if any(k in title for k in ("rubric", "template", "exemplar", "revision", "learning loop")):
            return "Teacher-in-the-loop intelligence"
        if any(k in title for k in ("lms", "canvas", "classroom", "teams", "lti")):
            return "Integrations & LMS breadth"
        if any(k in title for k in ("eval", "sentinel", "quality", "confidence", "baseline")):
            return "Quality & evaluation stack"
        if any(k in title for k in ("stripe", "subscription", "paid")):
            return "Monetization"
        if "plagiarism" in title:
            return "Competitive Parity"
        if any(k in title for k in ("arabic", "rtl", "i18n", "international", "htr", "handwriting")):
            return "Quality & evaluation stack"
        return None

    for lst in (now_items, next_items):
        for it in lst:
            it["_theme"] = classify(it)

    # Build the theme matrix
    themes_in_order = list(THEME_PALETTE.keys())
    for t in later.keys():
        if t not in themes_in_order:
            themes_in_order.append(t)

    matrix: dict[str, dict[str, list[dict[str, Any]]]] = {
        t: {"now": [], "next": [], "later": []} for t in themes_in_order
    }
    for it in now_items:
        key = it["_theme"] or "Uncategorized"
        matrix.setdefault(key, {"now": [], "next": [], "later": []})
        matrix[key]["now"].append(it)
    for it in next_items:
        key = it["_theme"] or "Uncategorized"
        matrix.setdefault(key, {"now": [], "next": [], "later": []})
        matrix[key]["next"].append(it)
    for theme, items in later.items():
        matrix.setdefault(theme, {"now": [], "next": [], "later": []})
        matrix[theme]["later"].extend(items)
    for t in matrix.keys():
        if t not in themes_in_order:
            themes_in_order.append(t)

    # Parity callout chips (tiny — just a link strip)
    parity_items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for bucket_items in (now_items, next_items):
        for it in bucket_items:
            if it.get("parity_overlay") and it["num"] not in seen:
                parity_items.append(it)
                seen.add(it["num"])
    for theme, items in later.items():
        for it in items:
            if (it.get("parity_overlay") or theme == "Competitive Parity") and it["num"] not in seen:
                parity_items.append(it)
                seen.add(it["num"])
    parity_links = " · ".join(
        f'<a class="underline" href="{_html.escape(p["url"] or "#")}">#{p["num"]}</a>'
        for p in parity_items
    )

    # Legend
    legend_items = "".join(
        f'<div class="flex items-center gap-2">'
        f'<span class="inline-block w-3 h-3 rounded-full" style="background:{p["color"]}"></span>'
        f'<span class="text-xs text-slate-700">{_html.escape(t)}</span>'
        f'</div>'
        for t, p in THEME_PALETTE.items()
    )

    # Portfolio matrix rows
    matrix_rows = []
    for theme in themes_in_order:
        if theme not in matrix:
            continue
        if not any(matrix[theme].values()):
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

    # Swim lanes
    lanes = []
    for theme in themes_in_order:
        if theme not in matrix:
            continue
        if not any(matrix[theme].values()):
            continue
        pal = _palette_for(theme)
        cols = []
        for bucket_key, bucket_label in (("now", "NOW"), ("next", "NEXT"), ("later", "LATER")):
            cards = "".join(
                _card(it, theme, bucket_label) for it in matrix[theme][bucket_key]
            ) or '<div class="text-xs text-slate-300">—</div>'
            cols.append(
                f'<div class="flex-1 space-y-2 min-w-[14rem]">'
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
            f'<div class="flex gap-3 flex-wrap">{"".join(cols)}</div>'
            f'</section>'
        )

    # KPI strip
    kpi_html = "".join(_kpi_tile(lbl, cnt) for lbl, cnt in status_kpis)

    # Marketing-gap chip row — counts first, chips second
    met_count = sum(1 for g in marketing_gap if g["status"] == "met")
    partial_count = sum(1 for g in marketing_gap if g["status"] == "partial")
    ambiguous_count = sum(1 for g in marketing_gap if g["status"] == "ambiguous")
    gap_chips = " ".join(_gap_chip(g["claim"], g["status"]) for g in marketing_gap)
    gap_header = (
        f'<span class="text-slate-700 font-semibold">{met_count} met</span>'
        f' · <span class="text-amber-700">{partial_count} partial</span>'
        f' · <span class="text-rose-700">{ambiguous_count} ambiguous</span>'
        if marketing_gap else ""
    )

    # Hidden inventory strip
    hidden_cards = "".join(
        f'<div class="rounded-lg border border-slate-200 bg-white p-2 min-w-[14rem]">'
        f'<div class="font-mono text-xs text-slate-500">#{h["num"]} · {_html.escape(h.get("repo",""))}</div>'
        f'<div class="text-sm text-slate-800 leading-snug">{_html.escape(h["title"])}</div>'
        f'</div>'
        for h in hidden
    )

    # Assemble
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
<header class="max-w-[1440px] mx-auto mb-4">
  <h1 class="text-2xl font-semibold">TA39 Product Roadmap</h1>
  <p class="text-sm text-slate-500 mt-1">
    Source of truth: <code class="bg-slate-100 px-1 rounded">{_html.escape(_os.path.basename(md_path))}</code>
    {f"· retrieved {retrieval_date}" if retrieval_date else ""}
  </p>
</header>

{f'<section class="max-w-[1440px] mx-auto mb-4"><div class="flex flex-wrap gap-2">{kpi_html}</div></section>' if kpi_html else ""}

<section class="max-w-[1440px] mx-auto mb-4 bg-white border border-slate-200 rounded-xl p-4">
  <div class="flex items-center justify-between mb-2">
    <h2 class="text-sm font-semibold text-slate-700">Themes</h2>
    <div class="text-[11px] text-slate-500">⚔️ = <code class="bg-slate-100 px-1 rounded">Competitive Parity</code> label{f" · {parity_links}" if parity_links else ""}</div>
  </div>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
    {legend_items}
  </div>
</section>

<section class="max-w-[1440px] mx-auto mb-4">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Theme portfolio matrix</h2>
  <div class="overflow-x-auto">
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
  </div>
</section>

<section class="max-w-[1440px] mx-auto mb-4">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Swim lanes</h2>
  {"".join(lanes)}
</section>

{f'''<section class="max-w-[1440px] mx-auto mb-4 bg-white border border-slate-200 rounded-xl p-4">
  <div class="flex items-baseline justify-between mb-2 gap-3 flex-wrap">
    <h2 class="text-sm font-semibold text-slate-700">Marketing-vs-ship gap</h2>
    <div class="text-xs">{gap_header}</div>
  </div>
  <div class="flex flex-wrap gap-2">{gap_chips}</div>
</section>''' if marketing_gap else ""}

{f'''<section class="max-w-[1440px] mx-auto mb-4 bg-white border border-slate-200 rounded-xl p-4">
  <div class="flex items-baseline justify-between mb-2 gap-3 flex-wrap">
    <h2 class="text-sm font-semibold text-slate-700">Hidden inventory — shipped, not announced</h2>
    <div class="text-xs text-slate-500">{announced_count} announced · {len(hidden)} silent</div>
  </div>
  <div class="flex gap-2 overflow-x-auto pb-2">{hidden_cards}</div>
</section>''' if hidden else ""}

<footer class="max-w-[1440px] mx-auto text-xs text-slate-400 mt-8">
  Regenerate with the <code>ta39-roadmap-html</code> skill. Data source: {_html.escape(md_path)}
  <br>Analytical commentary (risks, strategic call-outs, ship-order reads) lives in the MD file — this dashboard is the data view.
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
