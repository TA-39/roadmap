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
    # Arabic / Multilingual — the market-bet theme. Distinct teal so it
    # reads as its own investment line, not Platform housekeeping.
    "Arabic / Multilingual": {
        "color": "#0d9488", "bg": "#f0fdfa",
        "border": "#99f6e4", "text": "#134e4a",
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


def _extract_table(section: str) -> tuple[list[str], list[list[str]]]:
    """Return (headers, data_rows). Empty lists if no table found."""
    tbl = _extract_first_table(section)
    if not tbl:
        return [], []
    return tbl[0], tbl[1:]


def _col_idx(headers: list[str], *candidates: str) -> int:
    """Return the index of the first header that matches any candidate,
    case-insensitive, on either the full header or a substring match.
    -1 if nothing matches."""
    if not headers:
        return -1
    lowered = [h.strip().lower() for h in headers]
    for cand in candidates:
        c = cand.strip().lower()
        if c in lowered:
            return lowered.index(c)
    for cand in candidates:
        c = cand.strip().lower()
        for i, h in enumerate(lowered):
            if c and c in h:
                return i
    return -1


def _cell(row: list[str], idx: int, default: str = "") -> str:
    """Safe cell accessor — returns default if idx is -1 or out of range."""
    if idx < 0 or idx >= len(row):
        return default
    return row[idx]


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
    """FALLBACK ONLY. The canonical source of a feature's theme is the
    `Theme` column in the MD (or the `### Theme N — ...` header for LATER).
    This function only runs when a row has no Theme column value and isn't
    under a LATER theme header — and when it fires we warn on stderr so the
    MD can be fixed.
    """
    t = title.lower()
    if "copilot" in t or "agent" in t:
        return "Agentic / Copilot evolution"
    if any(k in t for k in ("rubric", "template", "exemplar", "revision", "learning loop", "class analysis", "analysis report")):
        return "Teacher-in-the-loop intelligence"
    # Arabic / Multilingual is its own strategic theme — check before
    # LMS / eval keywords to avoid Arabic-NLP work leaking into Quality & eval.
    if any(k in t for k in ("arabic", "rtl", "htr", "handwriting", "i18n", "multilingual", "internationalization")):
        return "Arabic / Multilingual"
    if any(k in t for k in ("lms", "canvas", "classroom", "teams", "lti")):
        return "Integrations & LMS breadth"
    if any(k in t for k in ("eval", "sentinel", "quality", "confidence", "baseline")):
        return "Quality & evaluation stack"
    if any(k in t for k in ("stripe", "subscription", "paid")):
        return "Monetization"
    if "plagiarism" in t:
        return "Competitive Parity"
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
    headers, rows = _extract_table(section)
    issue_i = _col_idx(headers, "issue", "#")
    title_i = _col_idx(headers, "title")
    theme_i = _col_idx(headers, "theme")
    tags_i = _col_idx(headers, "tags")
    out: list[dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        issue_cell = _cell(row, issue_i if issue_i >= 0 else 0)
        num, url, _ = _parse_issue_cell(issue_cell)
        if not num:
            continue
        tags_cell = _cell(row, tags_i if tags_i >= 0 else len(row) - 1)
        announced = "ANNOUNCED" in tags_cell.upper()
        featured = "FEATURED" in tags_cell.upper()
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(_strip_inline_links(_cell(row, title_i if title_i >= 0 else 1))),
            "theme_raw": _cell(row, theme_i),
            "bucket": "released",
            "announced": announced,
            "featured": featured,
            "parity_overlay": False,
        })
    return out


def parse_hidden_inventory(md: str) -> list[dict[str, Any]]:
    section = _extract_section(md, HIDDEN_INV_RE, RISKS_RE)
    headers, rows = _extract_table(section)
    issue_i = _col_idx(headers, "issue", "#")
    title_i = _col_idx(headers, "title")
    theme_i = _col_idx(headers, "theme")
    repo_i = _col_idx(headers, "repo")
    status_i = _col_idx(headers, "status")
    out: list[dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        issue_cell = _cell(row, issue_i if issue_i >= 0 else 0)
        num, url, _ = _parse_issue_cell(issue_cell)
        if not num:
            continue
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(_cell(row, title_i if title_i >= 0 else 1)),
            "theme_raw": _cell(row, theme_i),
            "repo": _cell(row, repo_i),
            "status": _cell(row, status_i),
            "bucket": "released",
            "announced": False,
            "featured": False,
            "parity_overlay": False,
        })
    return out


def parse_released_explicit(md: str) -> list[dict[str, Any]]:
    """Parse an explicit `## RELEASED` section if the MD has one.

    Columns are read by header name so shape evolves gracefully. The
    Theme column (when present) is captured as `theme_raw` and resolved
    by `resolve_theme()` once all parsers have run.

    Returns [] if the section doesn't exist — the renderer falls back
    to deriving RELEASED from announcement xref + hidden inventory.
    """
    section = _extract_section(md, RELEASED_HEADER_RE, NOW_HEADER_RE)
    headers, rows = _extract_table(section)
    issue_i = _col_idx(headers, "issue", "#")
    title_i = _col_idx(headers, "title")
    theme_i = _col_idx(headers, "theme")
    repo_i = _col_idx(headers, "repo")
    priority_i = _col_idx(headers, "priority")
    size_i = _col_idx(headers, "size")
    status_i = _col_idx(headers, "status")
    tags_i = _col_idx(headers, "tags")
    out: list[dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        issue_cell = _cell(row, issue_i if issue_i >= 0 else 0)
        num, url, _ = _parse_issue_cell(issue_cell)
        if not num:
            continue
        tags_cell = _cell(row, tags_i if tags_i >= 0 else len(row) - 1)
        announced = "ANNOUNCED" in tags_cell.upper()
        featured = "FEATURED" in tags_cell.upper()
        out.append({
            "num": num,
            "url": url,
            "title": _strip_md(_cell(row, title_i if title_i >= 0 else 1)),
            "theme_raw": _cell(row, theme_i),
            "repo": _cell(row, repo_i),
            "priority": _cell(row, priority_i),
            "size": _cell(row, size_i),
            "status": _cell(row, status_i),
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
    headers, rows = _extract_table(section)
    issue_i = _col_idx(headers, "issue", "#")
    title_i = _col_idx(headers, "title")
    theme_i = _col_idx(headers, "theme")
    status_i = _col_idx(headers, "status")
    priority_i = _col_idx(headers, "priority")
    size_i = _col_idx(headers, "size")
    repo_i = _col_idx(headers, "repo")
    tags_i = _col_idx(headers, "tags")
    out: list[dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        num, url, _ = _parse_issue_cell(_cell(row, issue_i if issue_i >= 0 else 0))
        if not num:
            continue
        out.append({
            "num": num, "url": url,
            "title": _strip_md(_cell(row, title_i if title_i >= 0 else 1)),
            "theme_raw": _cell(row, theme_i),
            "status": _cell(row, status_i),
            "priority": _cell(row, priority_i),
            "size": _cell(row, size_i),
            "repo": _cell(row, repo_i),
            "tags": _cell(row, tags_i),
            "bucket": "now",
            "announced": False, "featured": False,
            "parity_overlay": _has_parity_overlay(" | ".join(row)),
        })
    return out


def parse_next(md: str) -> list[dict[str, Any]]:
    section = _extract_section(md, NEXT_HEADER_RE, LATER_HEADER_RE)
    headers, rows = _extract_table(section)
    issue_i = _col_idx(headers, "issue", "#")
    title_i = _col_idx(headers, "title")
    theme_i = _col_idx(headers, "theme")
    priority_i = _col_idx(headers, "priority")
    size_i = _col_idx(headers, "size")
    tags_i = _col_idx(headers, "tags")
    realism_i = _col_idx(headers, "q2 realism", "realism")
    out: list[dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        num, url, _ = _parse_issue_cell(_cell(row, issue_i if issue_i >= 0 else 0))
        if not num:
            continue
        out.append({
            "num": num, "url": url,
            "title": _strip_md(_cell(row, title_i if title_i >= 0 else 1)),
            "theme_raw": _cell(row, theme_i),
            "priority": _cell(row, priority_i),
            "size": _cell(row, size_i),
            "tags": _cell(row, tags_i),
            "realism": _cell(row, realism_i),
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


_THEME_SHORT = {
    "Agentic / Copilot evolution": "Agentic",
    "Teacher-in-the-loop intelligence": "Teacher-in-loop",
    "Quality & evaluation stack": "Quality & eval",
    "Arabic / Multilingual": "Arabic",
    "Integrations & LMS breadth": "Integrations",
    "Monetization": "Monetization",
    "Competitive Parity": "Parity",
    "Platform & UX": "Platform",
}


# Alias table — accepts the various names the MD has historically used
# and normalizes to a canonical theme. Extend when adding new aliases; do
# NOT rename the canonical keys in THEME_PALETTE without updating both
# skills in the same commit.
_THEME_ALIASES = {
    # canonical → canonical (identity)
    "agentic / copilot evolution": "Agentic / Copilot evolution",
    "agentic": "Agentic / Copilot evolution",
    "copilot": "Agentic / Copilot evolution",
    "teacher-in-the-loop intelligence": "Teacher-in-the-loop intelligence",
    "teacher-in-the-loop": "Teacher-in-the-loop intelligence",
    "teacher-in-loop": "Teacher-in-the-loop intelligence",
    "hitl": "Teacher-in-the-loop intelligence",
    "quality & evaluation stack": "Quality & evaluation stack",
    "quality & eval": "Quality & evaluation stack",
    "quality and evaluation stack": "Quality & evaluation stack",
    "eval": "Quality & evaluation stack",
    "arabic / multilingual": "Arabic / Multilingual",
    "arabic": "Arabic / Multilingual",
    "multilingual": "Arabic / Multilingual",
    "i18n": "Arabic / Multilingual",
    "integrations & lms breadth": "Integrations & LMS breadth",
    "integrations": "Integrations & LMS breadth",
    "lms": "Integrations & LMS breadth",
    "monetization": "Monetization",
    "competitive parity": "Competitive Parity",
    "parity": "Competitive Parity",
    "platform & ux": "Platform & UX",
    "platform": "Platform & UX",
    "ux": "Platform & UX",
}


def _canonicalize_theme(raw: str | None) -> str | None:
    """Normalize a theme string from the MD into a canonical theme name.
    Returns None if the input is empty / dash / cannot be resolved."""
    if not raw:
        return None
    s = raw.strip()
    # Strip markdown italics / quotes / parentheticals
    s = _re.sub(r"^[*`_\"']+|[*`_\"']+$", "", s).strip()
    s = _re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    if not s or s in ("—", "-", "–"):
        return None
    key = s.lower()
    if key in _THEME_ALIASES:
        return _THEME_ALIASES[key]
    # Loose match — try the canonical palette keys directly
    for canonical in THEME_PALETTE.keys():
        if key == canonical.lower():
            return canonical
    if s == PLATFORM_THEME:
        return PLATFORM_THEME
    return None


# ---------------------------------------------------------------------------
# Card title cleanup
# ---------------------------------------------------------------------------
#
# GitHub issue titles are written for engineers, not for a 220px-wide card on
# an exec dashboard. They pack in Epic markers, acronym expansions, subsystem
# qualifiers, and marketing-adjacent phrasing that all read as noise on a
# poster. We do two things:
#
#   1. Hand-curated overrides for the titles that no rule-set cleans up well.
#      The key is the issue number. Keep these tight — 2 to 5 words, strong
#      nouns, real-world language an exec would recognize.
#   2. A rule-based cleanup as the fallback: strip leading bracket tags,
#      strip trailing parentheticals, drop common verbose prefixes, collapse
#      whitespace, and length-cap with an ellipsis.
#
# The short title is what appears on the card. The full title remains in the
# tooltip (title="...") so anyone hovering sees the verbatim GitHub title.

_TITLE_OVERRIDES: dict[str, str] = {
    # Released / announced
    "697": "Revision Rounds",
    "343": "Rubric UI Overhaul",
    "344": "Feedback Template Creation",
    "440": "Assignment Exemplars",
    "384": "Teacher Copilot",
    "385": "Student Copilot",
    "366": "Context-Aware Copilot Panels",
    "378": "Google Docs Submissions (LTI)",
    "20":  "Eval Harness M1 — Foundations",
    "188": "Class Analysis Report UI",
    "297": "Markdown Rendering in Text Pane",
    "532": "Internationalization (i18n)",
    "720": "UI Refresh — Revolt Design",
    # Now (in flight)
    "6":   "Sentinel Baseline Evaluation",
    "166": "Arabic Summary Report",
    "596": "Arabic NLP Enablement",
    # Next (Ready for Dev)
    "99":  "Arabic Handwriting Recognition",
    "327": "Plagiarism Detection",
    "701": "Microsoft Teams LMS Integration",
    "740": "Revision Rounds — Learning Loop",
    # Later — Agentic
    "547": "Agentic Instruction Platform",
    "649": "Agentic Copilot in Core UI",
    "474": "Voice-Based Assignments",
    # Later — HITL
    "328": "Student-Teacher Feedback Disputes",
    "331": "Teacher-Led AI Calibration",
    "113": "Socratic Writing Feedback",
    # Later — Quality & eval
    "7":   "Sentinel Manager UI",
    "14":  "Eval Harness — Multi-Metric Framework",
    "19":  "Eval Harness M2 — Observability",
    "21":  "Eval Harness M3 — Quality Gates",
    "22":  "Eval Harness M4 — Governance",
    "29":  "Two-Stage Feedback Architecture",
    "35":  "Confidence Scoring",
    # Later — Integrations
    "473": "Canvas Discussions as Source",
    "226": "Google Classroom Re-use",
    # Later — Monetization
    "374": "Stripe Individual Subscriptions",
}


_LEADING_TAG_RE = _re.compile(r"^\s*(?:\[[^\]]+\]\s*)+")
_TRAILING_PAREN_RE = _re.compile(r"\s*\([^)]*\)\s*$")


def _clean_title(raw: str, num: str | int = "") -> str:
    """Shorten a verbose GitHub issue title into something that reads
    well on a card. Prefers the hand-curated override when present."""
    key = str(num or "").strip()
    if key and key in _TITLE_OVERRIDES:
        return _TITLE_OVERRIDES[key]

    t = (raw or "").strip()
    # Strip leading bracket tags — e.g., "[Stream 3][Epic] ", "[Evaluation Harness] "
    t = _LEADING_TAG_RE.sub("", t)
    # Strip a single trailing parenthetical (acronym expansion / qualifier)
    t = _TRAILING_PAREN_RE.sub("", t)
    # Common verbose-prefix removals
    for prefix in (
        "Update UI for ",
        "User Requirement — ",
        "User Requirement - ",
        "Evolve TA39 Into an ",
        "Evolve TA39 Into a ",
        "Support for ",
        "Support ",
    ):
        if t.startswith(prefix):
            t = t[len(prefix):]
            break
    # Shorten a couple of long nouns in place
    t = t.replace("Evaluation Harness", "Eval Harness")
    # Collapse whitespace
    t = _re.sub(r"\s+", " ", t).strip()
    # Length cap — soft, at a word boundary
    MAX = 52
    if len(t) > MAX:
        cut = t[:MAX].rsplit(" ", 1)[0].rstrip(" ,:;—–-")
        t = (cut or t[:MAX]) + "…"
    return t


_PRIORITY_STYLE = {
    "HIGH":   ("High",   "#b91c1c", "#fee2e2"),
    "MEDIUM": ("Medium", "#b45309", "#fef3c7"),
    "LOW":    ("Low",    "#475569", "#f1f5f9"),
}


def _priority_pill(priority: str) -> str:
    key = (priority or "").strip().upper()
    if key not in _PRIORITY_STYLE:
        return ""
    label, fg, bg = _PRIORITY_STYLE[key]
    return (
        '<span class="inline-flex items-center gap-1 text-[10px] font-medium rounded px-1.5 py-0.5" '
        f'style="color:{fg};background:{bg}">'
        f'<span class="inline-block w-1.5 h-1.5 rounded-full" style="background:{fg}"></span>'
        f'{label}</span>'
    )


def _card(item: dict[str, Any], theme: str | None) -> str:
    """A clean card that keeps the information density a PM needs at a glance.

    We show: theme (named, not just colored), issue number, title, priority
    (colored dot + label), plus the public-surface badges. We drop abbreviated
    P:/S: chips and the repo column — those are easy to click through for.
    """
    pal = _palette_for(theme)
    href = _html.escape(item.get("url") or "#")
    raw_title = item.get("title", "")
    num = item.get("num", "")
    short_title = _clean_title(raw_title, num)
    title = _html.escape(short_title)
    tooltip = _html.escape(raw_title, quote=True)
    theme_label = _THEME_SHORT.get(theme or "", theme or "")

    badges: list[str] = []
    if item.get("featured"):
        badges.append(_badge(*_FEAT_BADGE))
    if item.get("announced"):
        badges.append(_badge(*_ANN_BADGE))
    if item.get("parity_overlay"):
        badges.append(_badge(*_PARITY_BADGE))
    if item.get("bucket") == "released" and not item.get("announced") and not item.get("featured"):
        badges.append(_badge(*_SILENT_BADGE))
    badges_html = " ".join(badges)

    # Bottom meta row: priority pill + optional in-flight status.
    meta_bits: list[str] = []
    p_pill = _priority_pill(item.get("priority", ""))
    if p_pill:
        meta_bits.append(p_pill)
    status = (item.get("status") or "").strip()
    if status and status not in ("", "—") and item.get("bucket") == "next":
        meta_bits.append(
            '<span class="text-[10px] text-slate-500">'
            f'{_html.escape(status)}</span>'
        )
    meta_html = " ".join(meta_bits)

    return (
        '<a href="' + href + '" class="block group rounded-xl bg-white '
        'border border-slate-200 shadow-[0_1px_2px_rgba(15,23,42,0.04)] '
        'hover:shadow-[0_4px_12px_rgba(15,23,42,0.10)] hover:-translate-y-0.5 '
        'transition-all duration-150 overflow-hidden" '
        f'title="{tooltip}" '
        f'style="border-left:3px solid {pal["color"]}">'
        '<div class="p-3">'
        # Theme label + badges
        '<div class="flex items-start justify-between gap-2 mb-1.5">'
        f'<span class="text-[10px] font-semibold uppercase tracking-wider" '
        f'style="color:{pal["color"]}">{_html.escape(theme_label)}</span>'
        f'<div class="flex flex-wrap gap-0.5 justify-end">{badges_html}</div>'
        '</div>'
        # Number + title
        '<div class="flex items-baseline gap-2 mb-2">'
        f'<span class="font-mono text-[11px] text-slate-400 tabular-nums leading-none">#{num}</span>'
        f'<span class="text-[13px] leading-snug text-slate-800 group-hover:text-slate-900 font-medium">{title}</span>'
        '</div>'
        # Meta row
        f'<div class="flex flex-wrap items-center gap-1.5">{meta_html}</div>'
        '</div>'
        '</a>'
    )


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

_PRIORITY_ORDER = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "": 0,
    "—": 0,
    "NONE": 0,
}


def _priority_rank(item: dict[str, Any]) -> int:
    p = (item.get("priority") or "").strip().upper()
    return _PRIORITY_ORDER.get(p, 0)


def _num_desc(item: dict[str, Any]) -> int:
    """Issue number as a recency proxy — higher numbers tend to be
    more recently filed. Cross-repo numbers aren't directly comparable
    but within ta-39 this gets us roughly the right stacking for
    RELEASED until the fetch script captures real shipped dates."""
    try:
        return int(item.get("num") or 0)
    except (TypeError, ValueError):
        return 0


def _sort_general(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Priority descending. Stable within priority."""
    return sorted(items, key=lambda it: -_priority_rank(it))


def _sort_released(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Priority descending, then recency (issue number) descending."""
    return sorted(items, key=lambda it: (-_priority_rank(it), -_num_desc(it)))


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
    # Theme resolution — explicit Theme column from the MD first, then
    # LATER subsection assignment, and only as a last resort the keyword
    # inference (warning on stderr so the MD can be fixed).
    inferred: list[tuple[str, str]] = []  # (num, inferred theme)

    def classify(it: dict[str, Any]) -> str:
        explicit = _canonicalize_theme(it.get("theme_raw"))
        if explicit:
            return explicit
        for theme, items in later.items():
            if any(x["num"] == it["num"] for x in items):
                return theme
        kw = classify_by_keyword(it.get("title") or "")
        chosen = kw or PLATFORM_THEME
        inferred.append((it.get("num", "?"), chosen))
        return chosen

    for lst in (released_items, now_items, next_items):
        for it in lst:
            it["_theme"] = classify(it)

    if inferred:
        pairs = ", ".join(f"#{n}→{t}" for n, t in inferred)
        print(
            f"[ta39-roadmap-html] WARN: theme inferred for {len(inferred)} "
            f"item(s) — add a `Theme` column entry to the MD to fix: {pairs}",
            file=_sys.stderr,
        )

    # Flatten LATER — we don't need per-theme grouping anymore. Each
    # card carries its theme color on the left border, which is enough
    # identity at the card level.
    later_flat: list[dict[str, Any]] = []
    for theme, items in later.items():
        for it in items:
            it.setdefault("_theme", theme)
            it.setdefault("bucket", "later")
            later_flat.append(it)

    # Merge NOW + NEXT into a single NEXT column. The distinction between
    # "Ready for Development" and "In Progress" matters in planning docs,
    # not on an executive dashboard.
    for it in now_items:
        it["bucket"] = "next"
    for it in next_items:
        it["bucket"] = "next"
    for it in released_items:
        it.setdefault("bucket", "released")

    next_merged = now_items + next_items

    # Sort each column.
    released_sorted = _sort_released(released_items)
    next_sorted = _sort_general(next_merged)
    later_sorted = _sort_general(later_flat)

    # KPI strip (still useful at the top for absolute counts).
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

    # Build the three Kanban columns. Cards are clustered by theme
    # inside each column so the reader can see "where investment sits"
    # per theme, while still sorting each cluster by priority desc.
    def _kanban_column(label: str, sub: str, accent: str,
                       items: list[dict[str, Any]]) -> str:
        # Group items by theme, preserving canonical theme order.
        by_theme: dict[str, list[dict[str, Any]]] = {}
        for it in items:
            by_theme.setdefault(it.get("_theme") or PLATFORM_THEME, []).append(it)

        theme_order = [t for t in THEME_PALETTE.keys() if t in by_theme]
        for t in by_theme:
            if t not in theme_order:
                theme_order.append(t)

        if not items:
            body = (
                '<div class="text-xs text-slate-300 italic py-8 text-center '
                'border-2 border-dashed border-slate-200 rounded-xl">Nothing here yet</div>'
            )
        else:
            groups_html: list[str] = []
            for t in theme_order:
                pal = _palette_for(t)
                short = _THEME_SHORT.get(t, t)
                group_items = by_theme[t]
                cards = "".join(_card(it, t) for it in group_items)
                groups_html.append(
                    '<div class="mb-5 last:mb-0">'
                    # Theme cluster label
                    '<div class="flex items-center justify-between mb-2 px-1">'
                    '<div class="flex items-center gap-1.5">'
                    f'<span class="inline-block w-1.5 h-1.5 rounded-full" style="background:{pal["color"]}"></span>'
                    f'<span class="text-[10px] font-bold uppercase tracking-wider" style="color:{pal["text"]}">{_html.escape(short)}</span>'
                    '</div>'
                    f'<span class="text-[10px] font-medium tabular-nums text-slate-400">{len(group_items)}</span>'
                    '</div>'
                    f'<div class="space-y-2">{cards}</div>'
                    '</div>'
                )
            body = "".join(groups_html)

        return (
            '<div class="kanban-col">'
            '<div class="mb-5">'
            f'<div class="h-1 rounded-full mb-4" style="background:{accent}"></div>'
            '<div class="flex items-baseline justify-between">'
            '<div>'
            f'<h2 class="text-lg font-bold tracking-tight" style="color:{accent}">{label}</h2>'
            f'<p class="text-[11px] text-slate-500 mt-0.5">{sub}</p>'
            '</div>'
            '<div class="text-right">'
            f'<div class="text-3xl font-extrabold tabular-nums" style="color:{accent}">{len(items)}</div>'
            '</div>'
            '</div>'
            '</div>'
            f'{body}'
            '</div>'
        )

    released_col = _kanban_column(
        "Released", f"{released_total} shipped · {announced_count} announced · {silent_count} silent",
        "#059669", released_sorted,
    )
    next_col = _kanban_column(
        "Next", "In build or queued for this quarter",
        "#2563eb", next_sorted,
    )
    later_col = _kanban_column(
        "Later", "Beyond Q2 — strategic backlog",
        "#64748b", later_sorted,
    )

    # Compute per-theme bucket counts — shared by the portfolio matrix.
    theme_buckets: dict[str, dict[str, int]] = {}
    for it in released_items:
        theme_buckets.setdefault(it["_theme"], {"r": 0, "n": 0, "l": 0})["r"] += 1
    for it in next_merged:
        theme_buckets.setdefault(it["_theme"], {"r": 0, "n": 0, "l": 0})["n"] += 1
    for it in later_flat:
        theme_buckets.setdefault(it["_theme"], {"r": 0, "n": 0, "l": 0})["l"] += 1

    # Theme portfolio matrix — themes as rows, buckets as columns,
    # each cell shows the item pills. A 3-bucket matrix since NOW
    # is merged into NEXT.
    def _bucket_pills(items: list[dict[str, Any]], theme: str) -> str:
        items_sorted = _sort_general(items)
        if not items_sorted:
            return '<span class="text-slate-300 text-xs">—</span>'
        return " ".join(
            _pill(it["num"], it.get("url"), it, theme) for it in items_sorted
        )

    matrix_rows_html_list: list[str] = []
    for t in list(THEME_PALETTE.keys()) + [k for k in theme_buckets if k not in THEME_PALETTE]:
        if t not in theme_buckets:
            continue
        released_for_theme = [it for it in released_sorted if it.get("_theme") == t]
        next_for_theme = [it for it in next_sorted if it.get("_theme") == t]
        later_for_theme = [it for it in later_sorted if it.get("_theme") == t]
        total = len(released_for_theme) + len(next_for_theme) + len(later_for_theme)
        if total == 0:
            continue
        pal = _palette_for(t)
        short = _THEME_SHORT.get(t, t)
        matrix_rows_html_list.append(
            '<tr class="border-t hairline align-top">'
            '<td class="py-3 pr-4 pl-4">'
            '<div class="flex items-center gap-2">'
            f'<span class="inline-block w-2 h-2 rounded-full flex-none" style="background:{pal["color"]}"></span>'
            f'<span class="text-sm font-semibold text-slate-800">{_html.escape(short)}</span>'
            '</div>'
            f'<div class="text-[11px] text-slate-400 mt-0.5 tabular-nums">{total} total</div>'
            '</td>'
            '<td class="py-3 px-3"><div class="flex flex-wrap gap-1">'
            f'{_bucket_pills(released_for_theme, t)}'
            '</div></td>'
            '<td class="py-3 px-3"><div class="flex flex-wrap gap-1">'
            f'{_bucket_pills(next_for_theme, t)}'
            '</div></td>'
            '<td class="py-3 pl-3 pr-4"><div class="flex flex-wrap gap-1">'
            f'{_bucket_pills(later_for_theme, t)}'
            '</div></td>'
            '</tr>'
        )
    theme_matrix_html = "".join(matrix_rows_html_list)

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
  :root {{
    --bg: #fafaf9;
    --ink: #0f172a;
    --muted: #64748b;
    --hair: #e2e8f0;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    background-image:
      radial-gradient(ellipse 80% 40% at 20% 0%, rgba(16,185,129,0.05) 0%, transparent 55%),
      radial-gradient(ellipse 60% 40% at 80% 0%, rgba(37,99,235,0.05) 0%, transparent 55%);
    background-attachment: fixed;
    font-feature-settings: "ss01", "cv11";
    -webkit-font-smoothing: antialiased;
  }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .tabular-nums {{ font-variant-numeric: tabular-nums; }}
  .display {{ letter-spacing: -0.03em; font-feature-settings: "ss01", "cv11"; }}
  .card-hover:hover {{ transform: translateY(-1px); }}
  .hairline {{ border-color: var(--hair); }}
</style>
</head>
<body class="text-slate-900 p-6 md:p-12">

<!-- ================ HERO ================ -->
<header class="max-w-[1400px] mx-auto mb-12">
  <div class="flex items-baseline justify-between gap-6 flex-wrap">
    <div>
      <div class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500 mb-3">
        TA-39 · Product Development
      </div>
      <h1 class="display text-5xl md:text-6xl font-extrabold text-slate-900 leading-[1.05]">
        Roadmap
      </h1>
      <p class="text-base text-slate-500 mt-3 max-w-2xl tabular-nums">
        36 tracked features across 6 themes.
        {f"Snapshot taken {retrieval_date}." if retrieval_date else ""}
        <span class="text-slate-900 font-medium">{silent_note}.</span>
      </p>
    </div>
    <div class="flex flex-wrap items-center gap-2">
      {badge_legend}
    </div>
  </div>
</header>

<!-- ================ PILLAR METRICS ================ -->
<section class="max-w-[1400px] mx-auto mb-10">
  <div class="grid grid-cols-3 gap-4">
    <div class="bg-white rounded-2xl border hairline p-5 relative overflow-hidden">
      <div class="absolute top-0 left-0 right-0 h-1" style="background:#059669"></div>
      <div class="text-[10px] font-bold uppercase tracking-widest text-emerald-700 mb-2">Released</div>
      <div class="display text-5xl font-extrabold text-slate-900 tabular-nums leading-none">{released_total}</div>
      <div class="text-xs text-slate-500 mt-2 tabular-nums">{announced_count} announced · {silent_count} silent</div>
    </div>
    <div class="bg-white rounded-2xl border hairline p-5 relative overflow-hidden">
      <div class="absolute top-0 left-0 right-0 h-1" style="background:#2563eb"></div>
      <div class="text-[10px] font-bold uppercase tracking-widest text-blue-700 mb-2">Next</div>
      <div class="display text-5xl font-extrabold text-slate-900 tabular-nums leading-none">{len(next_merged)}</div>
      <div class="text-xs text-slate-500 mt-2">In build or queued for this quarter</div>
    </div>
    <div class="bg-white rounded-2xl border hairline p-5 relative overflow-hidden">
      <div class="absolute top-0 left-0 right-0 h-1" style="background:#64748b"></div>
      <div class="text-[10px] font-bold uppercase tracking-widest text-slate-700 mb-2">Later</div>
      <div class="display text-5xl font-extrabold text-slate-900 tabular-nums leading-none">{len(later_flat)}</div>
      <div class="text-xs text-slate-500 mt-2">Strategic backlog beyond Q2</div>
    </div>
  </div>
</section>

<!-- ================ THEME PORTFOLIO MATRIX ================ -->
<section class="max-w-[1400px] mx-auto mb-10">
  <div class="flex items-baseline justify-between mb-4">
    <h2 class="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">Theme portfolio</h2>
    <span class="text-xs text-slate-400">What's where, by theme</span>
  </div>
  <div class="bg-white rounded-2xl border hairline overflow-hidden">
    <table class="w-full text-sm">
      <thead>
        <tr class="bg-slate-50 text-[10px] font-bold uppercase tracking-widest text-slate-500">
          <th class="text-left py-3 px-4 w-48">Theme</th>
          <th class="text-left py-3 px-3" style="color:#059669">Released</th>
          <th class="text-left py-3 px-3" style="color:#2563eb">Next</th>
          <th class="text-left py-3 px-4" style="color:#64748b">Later</th>
        </tr>
      </thead>
      <tbody>
        {theme_matrix_html}
      </tbody>
    </table>
  </div>
</section>

{f'''<!-- ================ MARKETING GAP ================ -->
<section class="max-w-[1400px] mx-auto mb-10">
  <div class="flex items-baseline justify-between mb-4">
    <h2 class="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">Marketing vs. ship</h2>
    <div class="text-xs tabular-nums">{gap_header}</div>
  </div>
  <div class="bg-white rounded-2xl border hairline p-5">
    <div class="flex flex-wrap gap-2">{gap_chips}</div>
  </div>
</section>''' if marketing_gap else ""}

<!-- ================ THE KANBAN ================ -->
<section class="max-w-[1400px] mx-auto mb-12">
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    {released_col}
    {next_col}
    {later_col}
  </div>
</section>

<!-- ================ FOOTER ================ -->
<footer class="max-w-[1400px] mx-auto text-xs text-slate-400 pt-8 border-t hairline">
  <div class="flex flex-wrap items-center gap-3">
    <span>Cards sorted by priority, then recency within Released.</span>
    <span class="text-slate-300">·</span>
    <span>Click any card to open the GitHub issue.</span>
    <span class="text-slate-300">·</span>
    <span>Deeper analysis in <code class="bg-slate-100 px-1.5 py-0.5 rounded">{_html.escape(_os.path.basename(md_path))}</code>.</span>
  </div>
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
