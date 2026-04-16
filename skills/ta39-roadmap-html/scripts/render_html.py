#!/usr/bin/env python3
"""
render_html.py — transform TA39-Roadmap.md into TA39-Roadmap.html.

Usage:
    python3 render_html.py <md_path> [<out_path>]

The HTML is an executive dashboard — visual, scannable, at-a-glance. It
answers three questions:

    1. What's out there?      (RELEASED column, ANN / FEAT badges)
    2. What's shipped silent? (RELEASED cards with no ANN badge)
    3. How soon?              (NOW / NEXT / LATER columns, left → right)

It is NOT a rendered version of the MD file. Analytical prose (risks,
strategic call-outs, ship-order reads, Q2 realism) lives in the MD. If
you find yourself about to dump a paragraph here, turn it into a chip, a
count, a color, or a badge — or leave it in the MD.

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
        "color": "#4f46e5", "bg": "#eef2ff",
        "border": "#c7d2fe", "text": "#312e81",
    },
    "Teacher-in-the-loop intelligence": {
        "color": "#059669", "bg": "#ecfdf5",
        "border": "#a7f3d0", "text": "#064e3b",
    },
    "Quality & evaluation stack": {
        "color": "#e11d48", "bg": "#fff1f2",
        "border": "#fecdd3", "text": "#881337",
    },
    "Integrations & LMS breadth": {
        "color": "#d97706", "bg": "#fffbeb",
        "border": "#fde68a", "text": "#78350f",
    },
    "Monetization": {
        "color": "#7c3aed", "bg": "#f5f3ff",
        "border": "#ddd6fe", "text": "#4c1d95",
    },
    "Competitive Parity": {
        "color": "#ea580c", "bg": "#fff7ed",
        "border": "#fed7aa", "text": "#9a3412",
    },
}

# Fallback for items that don't match any of the above — platform
# improvements, UX polish, misc. frontend. Rendered in neutral slate.
PLATFORM_THEME = "Platform & UX"

# ---------------------------------------------------------------------------
# Section header regexes. Load-bearing — change both sides (MD skill + this
# file) in the same commit.
# ---------------------------------------------------------------------------

STATUS_OVERVIEW_RE = _re.compile(r"^##\s+Status Overview\b", _re.M)
MARKETING_GAP_RE = _re.compile(r"^##\s+Marketing-vs-Ship Gap\b", _re.M)
ANNOUNCE_XREF_RE = _re.compile(r"^##\s+Announcement Cross-Reference\b", _re.M)
RELEASED_HEADER_RE = _re.compile(r"^##\s+RELEASED\b", _re.M)
NOW_HEADER_RE = _re.compile(r"^##\s+NOW\b", _re.M)
NEXT_HEADER_RE = _re.compile(r"^##\s+NEXT\b", _re.M)
LATER_HEADER_RE = _re.compile(r"^##\s+LATER\b", _re.M)
HIDDEN_INV_RE = _re.compile(r"^##\s+Shipped but NOT publicly announced\b", _re.M)
RISKS_RE = _re.compile(r"^##\s+Risks", _re.M)

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
    tbl = _extract_first_table(section)
    return tbl[1:] if len(tbl) > 1 else []


def _parse_issue_cell(cell: str) -> tuple[str | None, str | None, str]:
    m = ISSUE_LINK_RE.search(cell)
    if not m:
        return None, None, cell
    return m.group(1), m.group(2), cell[m.end():].strip()


def _has_parity_overlay(cell: str) -> bool:
    return "⚔" in cell


def _strip_md(s: str) -> str:
    s = _re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = _re.sub(r"\*(.+?)\*", r"\1", s)
    return s.strip()


def _strip_inline_links(s: str) -> str:
    return _re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s).strip()


# ---------------------------------------------------------------------------
# Theme classification — shared across all buckets
# ---------------------------------------------------------------------------

def classify_by_keyword(title: str) -> str | None:
    t = title.lower()
    if "copilot" in t or "agent" in t:
        return "Agentic / Copilot evolution"
    if any(k in t for k in ("rubric", "template", "exemplar", "revision", "learning loop", "class analysis", "analysis report")):
        return "Teacher-in-the-loop intelligence"
    if any(k in t for k in ("lms", "canvas", "classroom", "teams", "lti")):
        return "Integrations & LMS breadth"
    if any(k in t for k in ("eval", "sentinel", "quality", "confidence", "baseline")):
        return "Quality & evaluation stack"
    if any(k in t for k in ("stripe", "subscription", "paid")):
        return "Monetization"
    if "plagiarism" in t:
        return "Competitive Parity"
    if any(k in t for k in ("arabic", "rtl", "i18n", "international", "htr", "handwriting")):
        return "Quality & evaluation stack"
    return None


# ---------------------------------------------------------------------------
# Section parsers
# ---------------------------------------------------------------------------

def parse_retrieval_date(md: str) -> str:
    m = _re.search(r"\*\*Retrieved:\*\*\s+(\d{4}-\d{2}-\d{2})", md)
    if m:
        return m.group(1)
    m = _re.search(r"re-pulled\s+(\d{4}-\d{2}-\d{2})", md)
    return m.group(1) if m else ""


def parse_status_overview(md: str) -> list[tuple[str, str]]:
    """KPI tiles — drop ARCHIVED (not worth showing) and the totals row."""
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
        if label.upper() == "ARCHIVED":
            continue
        out.append((label, count))
    return out


def parse_marketing_gap(md: str) -> list[dict[str, str]]:
    section = _extract_section(md, MARKETING_GAP_RE, ANNOUNCE_XREF_RE)
    out: list[dict[str, str]] = []
    for row in _extract_table_rows(section):
        if len(row) < 4:
            continue
        claim = _strip_md(_strip_inline_links(row[0]))
        reality = _strip_md(_strip_inline_links(row[2])).lower()
        if "partial" in reality:
            status = "partial"
        elif "ambiguous" in reality:
            status = "ambiguous"
        elif "met" in reality or "shipped" in reality:
            status = "met"
        else:
            status = "partial"
        out.append({"claim": claim, "status": status})
    return out


def parse_announcement_xref(md: str) -> list[dict[str, Any]]:
    """Return the announced RELEASED items with ann/feat flags set."""
    # The section goes until NOW (or RELEASED if present).
    next_re = RELEASED_HEADER_RE if RELEASED_HEADER_RE.search(md) else NOW_HEADER_RE
    section = _extract_section(md, ANNOUNCE_XREF_RE, next_re)
    out: list[dict[str, Any]] = []
    for row in _extract_table_rows(section):
        if len(row) < 2:
            continue
        num, url, _ = _parse_issue_cell(row[0])
        if not num:
            continue
        tags_cell = row[-1]
        announced = "ANNOUNCED" in tags_cell.upper()
        featured = "FEATURED" in tags_cell.upper()
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(_strip_inline_links(row[1])),
            "bucket": "released",
            "announced": announced,
            "featured": featured,
            "parity_overlay": False,
        })
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
            "bucket": "released",
            "announced": False,
            "featured": False,
            "parity_overlay": False,
        })
    return out


def parse_released_explicit(md: str) -> list[dict[str, Any]]:
    """Parse an explicit `## RELEASED` section if the MD has one.

    Expected columns: Issue | Title | Repo | Status | Tags (optional).
    Tags cell is inspected for `[ANNOUNCED]` and `[FEATURED]`.

    Returns [] if the section doesn't exist — the renderer falls back
    to deriving RELEASED from announcement xref + hidden inventory.
    """
    section = _extract_section(md, RELEASED_HEADER_RE, NOW_HEADER_RE)
    out: list[dict[str, Any]] = []
    for row in _extract_table_rows(section):
        if len(row) < 2:
            continue
        num, url, _ = _parse_issue_cell(row[0])
        if not num:
            continue
        tags_cell = row[-1] if len(row) >= 5 else ""
        announced = "ANNOUNCED" in tags_cell.upper()
        featured = "FEATURED" in tags_cell.upper()
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(row[1]),
            "repo": row[2] if len(row) > 2 else "",
            "status": row[3] if len(row) > 3 else "",
            "bucket": "released",
            "announced": announced,
            "featured": featured,
            "parity_overlay": _has_parity_overlay(" | ".join(row)),
        })
    return out


def resolve_released(md: str) -> list[dict[str, Any]]:
    """Prefer an explicit `## RELEASED` section; fall back to the union
    of announcement xref + hidden inventory. Deduplicates by issue num.
    """
    explicit = parse_released_explicit(md)
    if explicit:
        return explicit
    merged: dict[str, dict[str, Any]] = {}
    for it in parse_announcement_xref(md):
        merged[it["num"]] = it
    for it in parse_hidden_inventory(md):
        # Don't let a hidden-inventory entry overwrite an announced one.
        if it["num"] not in merged:
            merged[it["num"]] = it
    return list(merged.values())


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
            "num": num, "url": url,
            "title": _strip_md(row[1]),
            "status": row[2], "priority": row[3], "size": row[4],
            "repo": row[5] if len(row) > 5 else "",
            "bucket": "now",
            "announced": False, "featured": False,
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
            "num": num, "url": url,
            "title": _strip_md(row[1]),
            "priority": row[2], "size": row[3],
            "tags": row[4] if len(row) > 4 else "",
            "bucket": "next",
            "announced": False, "featured": False,
            "parity_overlay": _has_parity_overlay(" | ".join(row)),
        })
    return out


def _normalize_theme_name(raw: str) -> str:
    name = raw.strip()
    name = _re.sub(r"\s*[—–-]\s*\*[^*]*\*\s*$", "", name).strip()
    name = _re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
    name = _re.sub(r"\s*[—–-]\s*$", "", name).strip()
    return name


def parse_later(md: str) -> dict[str, list[dict[str, Any]]]:
    section = _extract_section(md, LATER_HEADER_RE, HIDDEN_INV_RE)
    out: dict[str, list[dict[str, Any]]] = {}
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
                "num": num, "url": url,
                "title": _strip_md(row[1]) if len(row) > 1 else "",
                "priority": row[2] if len(row) > 2 else "",
                "size": row[3] if len(row) > 3 else "",
                "status": row[4] if len(row) > 4 else "",
                "bucket": "later",
                "announced": False, "featured": False,
                "parity_overlay": _has_parity_overlay(" | ".join(row)),
            })
        out[name] = items
    return out


# ---------------------------------------------------------------------------
# Palette + card components
# ---------------------------------------------------------------------------

_NEUTRAL_PALETTE = {
    "color": "#64748b", "bg": "#f8fafc",
    "border": "#e2e8f0", "text": "#334155",
}


def _palette_for(theme: str | None) -> dict[str, str]:
    if not theme or theme not in THEME_PALETTE:
        return _NEUTRAL_PALETTE
    return THEME_PALETTE[theme]


def _pill(num: str, url: str | None, item: dict[str, Any], theme: str | None) -> str:
    pal = _palette_for(theme)
    overlay = " ⚔️" if item.get("parity_overlay") else ""
    # Tiny ANN/FEAT markers inline in the pill, rendered as lowercase
    # initials so the pill stays compact.
    marks = []
    if item.get("featured"):
        marks.append("F")
    elif item.get("announced"):
        marks.append("A")
    mark_str = ("·" + "".join(marks)) if marks else ""
    href = _html.escape(url or "#")
    return (
        f'<a href="{href}" class="inline-flex items-center rounded-md '
        f'text-xs font-mono px-1.5 py-0.5 border" '
        f'style="color:{pal["text"]};background:{pal["bg"]};'
        f'border-color:{pal["border"]}">#{num}{mark_str}{overlay}</a>'
    )


def _badge(text: str, color: str, bg: str, border: str, title: str = "") -> str:
    title_attr = f' title="{_html.escape(title)}"' if title else ""
    return (
        '<span class="inline-flex items-center text-[9px] font-semibold uppercase '
        f'tracking-wider rounded px-1 py-0.5 border"{title_attr} '
        f'style="color:{color};background:{bg};border-color:{border}">{_html.escape(text)}</span>'
    )


_ANN_BADGE = ("ANN", "#0f766e", "#ccfbf1", "#5eead4",
              "community.ta-39.com announcement post exists")
_FEAT_BADGE = ("FEAT", "#b45309", "#fef3c7", "#fde68a",
               "Named on the www.ta-39.com/en/features page")
_PARITY_BADGE = ("⚔", "#9a3412", "#fff7ed", "#fed7aa",
                 "Carries the Competitive Parity label")
_SILENT_BADGE = ("SILENT", "#475569", "#f1f5f9", "#cbd5e1",
                 "Released with no community post")


def _card(item: dict[str, Any], theme: str | None) -> str:
    pal = _palette_for(theme)
    href = _html.escape(item.get("url") or "#")
    title = _html.escape(item.get("title", ""))
    num = item.get("num", "")

    # Top-right badges (visible at the card level, not just in the pill).
    badges: list[str] = []
    if item.get("featured"):
        badges.append(_badge(*_FEAT_BADGE))
    if item.get("announced"):
        badges.append(_badge(*_ANN_BADGE))
    if item.get("parity_overlay"):
        badges.append(_badge(*_PARITY_BADGE))
    # Silent = RELEASED but neither announced nor featured.
    if item.get("bucket") == "released" and not item.get("announced") and not item.get("featured"):
        badges.append(_badge(*_SILENT_BADGE))
    badges_html = " ".join(badges)

    # Meta pills (priority / size / status).
    pills = []
    for k, label in (("priority", "P"), ("size", "S")):
        v = (item.get(k) or "").strip()
        if v and v != "—":
            pills.append(
                '<span class="text-[10px] rounded px-1 py-0.5 bg-slate-100 text-slate-600">'
                f'{label}:{_html.escape(v)}</span>'
            )
    status = (item.get("status") or "").strip()
    if status and status != "—":
        pills.append(
            '<span class="text-[10px] rounded px-1 py-0.5 bg-slate-50 '
            f'text-slate-500 border border-slate-200">{_html.escape(status)}</span>'
        )
    pills_html = " ".join(pills)

    return (
        '<div class="relative rounded-lg border p-2 bg-white shadow-sm" '
        f'style="border-color:{pal["border"]}">'
        '<div class="flex items-start justify-between gap-2 mb-1">'
        f'<a href="{href}" class="font-mono text-xs leading-none pt-0.5" '
        f'style="color:{pal["color"]}">#{num}</a>'
        f'<div class="flex flex-wrap gap-0.5 justify-end">{badges_html}</div>'
        '</div>'
        f'<div class="text-[13px] leading-snug text-slate-800 mb-1">{title}</div>'
        f'<div class="flex flex-wrap gap-1">{pills_html}</div>'
        '</div>'
    )


# ---------------------------------------------------------------------------
# KPI strip + marketing gap chips
# ---------------------------------------------------------------------------

_KPI_COLOR = {
    "RELEASED": "#059669",
    "NOW": "#2563eb",
    "NEXT": "#7c3aed",
    "BLOCKED": "#e11d48",
    "LATER": "#475569",
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
    "met":       ("✓", "#059669", "#ecfdf5", "#a7f3d0"),
    "partial":   ("◐", "#d97706", "#fffbeb", "#fde68a"),
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

    released_items = resolve_released(md)
    now_items = parse_now(md)
    next_items = parse_next(md)
    later = parse_later(md)

    # Theme assignment for every bucket — LATER already has explicit themes
    # from `### Theme N — ...` headers. RELEASED / NOW / NEXT need keyword
    # inference. Fall back to Platform & UX for non-matching items.
    def classify(it: dict[str, Any]) -> str:
        for theme, items in later.items():
            if any(x["num"] == it["num"] for x in items):
                return theme
        kw = classify_by_keyword(it.get("title") or "")
        if kw:
            return kw
        return PLATFORM_THEME

    for lst in (released_items, now_items, next_items):
        for it in lst:
            it["_theme"] = classify(it)

    # Matrix: Theme → {released/now/next/later: [items]}
    themes_in_order = list(THEME_PALETTE.keys())
    for t in later.keys():
        if t not in themes_in_order:
            themes_in_order.append(t)

    matrix: dict[str, dict[str, list[dict[str, Any]]]] = {
        t: {"released": [], "now": [], "next": [], "later": []}
        for t in themes_in_order
    }

    def _bucket_add(t: str, bucket: str, item: dict[str, Any]) -> None:
        matrix.setdefault(t, {"released": [], "now": [], "next": [], "later": []})
        matrix[t][bucket].append(item)

    for it in released_items:
        _bucket_add(it["_theme"], "released", it)
    for it in now_items:
        _bucket_add(it["_theme"], "now", it)
    for it in next_items:
        _bucket_add(it["_theme"], "next", it)
    for theme, items in later.items():
        for it in items:
            it.setdefault("_theme", theme)
        matrix.setdefault(theme, {"released": [], "now": [], "next": [], "later": []})
        matrix[theme]["later"].extend(items)

    # Put the fallback theme last if any items ended up there.
    for t in list(matrix.keys()):
        if t not in themes_in_order:
            themes_in_order.append(t)

    # KPI strip
    kpi_html = "".join(_kpi_tile(lbl, cnt) for lbl, cnt in status_kpis)

    # Silent-inventory count for the context line
    silent_count = sum(
        1 for it in released_items
        if not it.get("announced") and not it.get("featured")
    )
    announced_count = sum(1 for it in released_items if it.get("announced"))
    released_total = len(released_items)

    # Legend (theme palette + badge key)
    theme_chips = "".join(
        f'<div class="flex items-center gap-2">'
        f'<span class="inline-block w-3 h-3 rounded-full" style="background:{p["color"]}"></span>'
        f'<span class="text-xs text-slate-700">{_html.escape(t)}</span>'
        f'</div>'
        for t, p in THEME_PALETTE.items()
    )
    badge_legend = (
        _badge(*_FEAT_BADGE) + ' <span class="text-xs text-slate-600">on features page</span>'
        + ' &nbsp; '
        + _badge(*_ANN_BADGE) + ' <span class="text-xs text-slate-600">community post</span>'
        + ' &nbsp; '
        + _badge(*_SILENT_BADGE) + ' <span class="text-xs text-slate-600">shipped, no post</span>'
        + ' &nbsp; '
        + _badge(*_PARITY_BADGE) + ' <span class="text-xs text-slate-600">Competitive Parity label</span>'
    )

    # Theme portfolio matrix (5 columns: Theme | RELEASED | NOW | NEXT | LATER)
    matrix_rows = []
    for theme in themes_in_order:
        if theme not in matrix:
            continue
        if not any(matrix[theme].values()):
            continue
        pal = _palette_for(theme)
        cells = []
        for bucket in ("released", "now", "next", "later"):
            pills = " ".join(
                _pill(it["num"], it.get("url"), it, theme)
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

    # Swim lanes: per-theme Kanban with 4 columns
    lanes = []
    for theme in themes_in_order:
        if theme not in matrix:
            continue
        if not any(matrix[theme].values()):
            continue
        pal = _palette_for(theme)
        cols = []
        for bucket_key, bucket_label in (
            ("released", "RELEASED"),
            ("now", "NOW"),
            ("next", "NEXT"),
            ("later", "LATER"),
        ):
            cards = "".join(
                _card(it, theme) for it in matrix[theme][bucket_key]
            ) or '<div class="text-xs text-slate-300">—</div>'
            count_html = (
                f'<span class="text-slate-400 font-normal">· {len(matrix[theme][bucket_key])}</span>'
                if matrix[theme][bucket_key] else ""
            )
            cols.append(
                f'<div class="flex-1 min-w-[15rem] space-y-2">'
                f'<div class="text-[11px] uppercase tracking-wider text-slate-500 mb-1 font-semibold">{bucket_label} {count_html}</div>'
                f'<div class="space-y-2">{cards}</div>'
                f'</div>'
            )
        lanes.append(
            f'<section class="border rounded-xl p-3 mb-3" '
            f'style="border-color:{pal["border"]};background:{pal["bg"]}30">'
            f'<div class="flex items-center gap-2 mb-3">'
            f'<span class="inline-block w-2.5 h-2.5 rounded-full" style="background:{pal["color"]}"></span>'
            f'<h3 class="text-sm font-semibold" style="color:{pal["text"]}">{_html.escape(theme)}</h3>'
            f'</div>'
            f'<div class="flex gap-3 flex-wrap">{"".join(cols)}</div>'
            f'</section>'
        )

    # Marketing-gap chips
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

    # Silent-inventory context line above the swim lanes
    silent_note = (
        f'{released_total} released · {announced_count} announced · '
        f'<span class="text-slate-900 font-semibold">{silent_count} silent</span>'
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
<header class="max-w-[1600px] mx-auto mb-4">
  <h1 class="text-2xl font-semibold">TA39 Product Roadmap</h1>
  <p class="text-sm text-slate-500 mt-1">
    Source: <code class="bg-slate-100 px-1 rounded">{_html.escape(_os.path.basename(md_path))}</code>
    {f"· retrieved {retrieval_date}" if retrieval_date else ""}
    · {silent_note}
  </p>
</header>

{f'<section class="max-w-[1600px] mx-auto mb-4"><div class="flex flex-wrap gap-2">{kpi_html}</div></section>' if kpi_html else ""}

<section class="max-w-[1600px] mx-auto mb-4 bg-white border border-slate-200 rounded-xl p-4">
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 mb-3">
    {theme_chips}
  </div>
  <div class="flex flex-wrap items-center gap-1 text-xs text-slate-500 pt-3 border-t border-slate-100">
    {badge_legend}
  </div>
</section>

<section class="max-w-[1600px] mx-auto mb-4">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Theme portfolio matrix</h2>
  <div class="overflow-x-auto">
  <table class="w-full border-collapse bg-white border border-slate-200 rounded-xl overflow-hidden text-sm">
    <thead>
      <tr class="bg-slate-50 text-slate-600">
        <th class="text-left p-2 border border-slate-200">Theme</th>
        <th class="text-left p-2 border border-slate-200">RELEASED</th>
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

<section class="max-w-[1600px] mx-auto mb-4">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Swim lanes — what's out there, what's coming</h2>
  {"".join(lanes)}
</section>

{f'''<section class="max-w-[1600px] mx-auto mb-4 bg-white border border-slate-200 rounded-xl p-4">
  <div class="flex items-baseline justify-between mb-2 gap-3 flex-wrap">
    <h2 class="text-sm font-semibold text-slate-700">Marketing-vs-ship gap</h2>
    <div class="text-xs">{gap_header}</div>
  </div>
  <div class="flex flex-wrap gap-2">{gap_chips}</div>
</section>''' if marketing_gap else ""}

<footer class="max-w-[1600px] mx-auto text-xs text-slate-400 mt-8">
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
