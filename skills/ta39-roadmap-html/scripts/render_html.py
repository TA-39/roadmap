#!/usr/bin/env python3
"""
render_html.py — transform TA39-Roadmap.md into TA39-Roadmap.html.

Usage:
    python3 render_html.py <md_path> [<out_path>]

Parses all 14 MD sections — public-surface tagging rules, Kanban glossary,
status overview, marketing gap, announcement cross-reference, NOW, NEXT,
LATER (themed), hidden inventory, risks, strategic call-outs, changes, and
follow-ups — and emits a standalone HTML dashboard using Tailwind via CDN
plus custom CSS variables for the theme palette.

No external Python deps — stdlib only.

Section-header parsing is a contract with the MD skill. If you rename a
section in `ta39-roadmap-md/SKILL.md`, update the matching regex here in
the same commit.
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
# Section header regexes. These are load-bearing — the MD skill guarantees
# the 14-section ordering. Change both sides in the same commit.
# ---------------------------------------------------------------------------

# Anchor-style headers (level-2 ##)
PUBLIC_TAGGING_RE = _re.compile(r"^##\s+Public-surface tagging rules\b", _re.M)
KANBAN_RE = _re.compile(r"^##\s+Kanban Status Glossary\b", _re.M)
STATUS_OVERVIEW_RE = _re.compile(r"^##\s+Status Overview\b", _re.M)
MARKETING_GAP_RE = _re.compile(r"^##\s+Marketing-vs-Ship Gap\b", _re.M)
ANNOUNCE_XREF_RE = _re.compile(r"^##\s+Announcement Cross-Reference\b", _re.M)
NOW_HEADER_RE = _re.compile(r"^##\s+NOW\b", _re.M)
NEXT_HEADER_RE = _re.compile(r"^##\s+NEXT\b", _re.M)
LATER_HEADER_RE = _re.compile(r"^##\s+LATER\b", _re.M)
HIDDEN_INV_RE = _re.compile(r"^##\s+Shipped but NOT publicly announced\b", _re.M)
RISKS_RE = _re.compile(r"^##\s+Risks", _re.M)
STRATEGIC_RE = _re.compile(r"^##\s+Strategic Call-outs\b", _re.M)
CHANGES_RE = _re.compile(r"^##\s+Changes vs\. the board today\b", _re.M)
FOLLOWUPS_RE = _re.compile(r"^##\s+Follow-ups I can generate\b", _re.M)

# Capture the full theme label up to end-of-line; post-process to drop the
# count "(N)" and any trailing italic commentary. The simpler the regex,
# the fewer things it can miscapture — we normalize in Python, not regex.
THEME_HEADER_RE = _re.compile(r"^###\s+Theme\s+\d+\s+[—–-]\s+(.+?)\s*$", _re.M)

# Match links like [#697](https://github.com/TA-39/frontend/issues/697)
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


def _extract_all_tables(section: str) -> list[list[list[str]]]:
    """Return every pipe-delimited table in the section. Each table is a
    list of rows; the first row is the header, separator rows are stripped.
    """
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    saw_sep = False
    in_table = False
    for line in section.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s[1:-1].split("|")]
            if all(_re.fullmatch(r":?-+:?", c) for c in cells):
                saw_sep = True
                continue
            current.append(cells)
            in_table = True
        else:
            if in_table:
                if current and saw_sep:
                    tables.append(current)
                current = []
                saw_sep = False
                in_table = False
    if current and saw_sep:
        tables.append(current)
    return tables


def _extract_table_rows(section: str) -> list[list[str]]:
    """Back-compat shim: return the data rows of the first table in a
    section (i.e. rows after the header)."""
    tables = _extract_all_tables(section)
    if not tables:
        return []
    first = tables[0]
    return first[1:] if len(first) > 1 else []


def _extract_first_table_with_header(section: str) -> list[list[str]]:
    """Return the entire first table including the header row."""
    tables = _extract_all_tables(section)
    return tables[0] if tables else []


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


def _strip_md(s: str) -> str:
    # Light cleanup for plain-text rendering in tooltips / card titles.
    s = _re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = _re.sub(r"\*(.+?)\*", r"\1", s)
    return s.strip()


def _inline_md(text: str) -> str:
    """Convert a narrow set of inline markdown to safe HTML: escape first,
    then re-introduce `code`, **bold**, *italic*, and [label](url) links.

    We explicitly do NOT parse block-level markdown here — use md_prose_to_html
    for multi-paragraph prose sections.
    """
    escaped = _html.escape(text)
    # Links: [label](url) — re-enable the anchor while keeping the text escaped.
    def _link_sub(m: _re.Match) -> str:
        label = m.group(1)
        url = m.group(2)
        return (
            f'<a class="underline decoration-slate-300 hover:decoration-slate-500" '
            f'href="{url}">{label}</a>'
        )
    escaped = _re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link_sub, escaped)
    # Inline code
    escaped = _re.sub(r"`([^`]+)`", r'<code class="bg-slate-100 px-1 rounded">\1</code>', escaped)
    # Bold then italic (order matters so ** isn't eaten by the single-* rule).
    escaped = _re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = _re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def _parse_list_block(lines: list[str]) -> tuple[str, list[str]]:
    """Given a run of list lines, return ('ol' or 'ul', list-of-item-html).
    An ordered list is any line starting with `<digits>.` — mixing with
    bullets in the same block is treated as ordered.
    """
    kind = "ul"
    items: list[str] = []
    for ln in lines:
        m = _re.match(r"^\s*(\d+)\.\s+(.*)$", ln)
        if m:
            kind = "ol"
            items.append(_inline_md(m.group(2)))
            continue
        m = _re.match(r"^\s*[-*]\s+(.*)$", ln)
        if m:
            items.append(_inline_md(m.group(1)))
            continue
        # Continuation of the previous item (rare)
        if items:
            items[-1] += " " + _inline_md(ln.strip())
    return kind, items


def md_prose_to_html(text: str) -> str:
    """Render a slice of MD prose (paragraphs, ordered lists, bulleted
    lists, inline markup) to HTML. Tables and headers are skipped here —
    they're handled by the dedicated parsers. This keeps the renderer
    deterministic and side-steps pulling in a full markdown lib.
    """
    out: list[str] = []
    block: list[str] = []
    mode: str | None = None  # None | "para" | "list"

    def _flush_para() -> None:
        if not block:
            return
        joined = " ".join(b.strip() for b in block).strip()
        if joined:
            out.append(f'<p class="text-sm text-slate-700 leading-relaxed mb-3">{_inline_md(joined)}</p>')

    def _flush_list() -> None:
        if not block:
            return
        kind, items = _parse_list_block(block)
        if not items:
            return
        tag = "ol" if kind == "ol" else "ul"
        cls = "list-decimal" if kind == "ol" else "list-disc"
        li_html = "".join(f'<li class="text-sm text-slate-700 leading-relaxed mb-1">{it}</li>' for it in items)
        out.append(f'<{tag} class="{cls} pl-5 mb-3">{li_html}</{tag}>')

    def _flush() -> None:
        nonlocal mode, block
        if mode == "para":
            _flush_para()
        elif mode == "list":
            _flush_list()
        mode = None
        block = []

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            _flush()
            continue
        # Skip MD headers and table rows — those are handled elsewhere.
        if stripped.startswith("#"):
            _flush()
            continue
        if stripped.startswith("|"):
            _flush()
            continue
        # Horizontal rule
        if _re.fullmatch(r"-{3,}", stripped):
            _flush()
            continue
        is_list = bool(_re.match(r"^\s*(\d+\.|[-*])\s+", line))
        if is_list:
            if mode != "list":
                _flush()
                mode = "list"
            block.append(line)
        else:
            if mode != "para":
                _flush()
                mode = "para"
            block.append(line)
    _flush()
    return "".join(out)


# ---------------------------------------------------------------------------
# Section parsers
# ---------------------------------------------------------------------------

def parse_retrieval_date(md: str) -> str:
    m = _re.search(r"\*\*Retrieved:\*\*\s+(\d{4}-\d{2}-\d{2})", md)
    if m:
        return m.group(1)
    m = _re.search(r"re-pulled\s+(\d{4}-\d{2}-\d{2})", md)
    return m.group(1) if m else ""


def parse_public_tagging_prose(md: str) -> str:
    return _extract_section(md, PUBLIC_TAGGING_RE, KANBAN_RE)


def parse_kanban_glossary(md: str) -> list[list[str]]:
    section = _extract_section(md, KANBAN_RE, STATUS_OVERVIEW_RE)
    return _extract_first_table_with_header(section)


def parse_status_overview(md: str) -> tuple[list[list[str]], str]:
    section = _extract_section(md, STATUS_OVERVIEW_RE, MARKETING_GAP_RE)
    table = _extract_first_table_with_header(section)
    # Everything after the table is the velocity-context prose.
    # Find where the first table ends.
    prose_start = section
    # Simple split: prose is whatever follows the last "|" line.
    lines = section.splitlines()
    last_table_line = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|"):
            last_table_line = i
    prose = "\n".join(lines[last_table_line + 1:])
    return table, prose


def parse_marketing_gap(md: str) -> tuple[str, list[list[str]], str]:
    section = _extract_section(md, MARKETING_GAP_RE, ANNOUNCE_XREF_RE)
    lines = section.splitlines()
    first_table_line = next(
        (i for i, ln in enumerate(lines) if ln.strip().startswith("|")), len(lines)
    )
    last_table_line = first_table_line - 1
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|"):
            last_table_line = i
    intro = "\n".join(lines[:first_table_line])
    outro = "\n".join(lines[last_table_line + 1:])
    table = _extract_first_table_with_header(section)
    return intro, table, outro


def parse_announcement_xref(md: str) -> tuple[str, list[list[str]], str]:
    section = _extract_section(md, ANNOUNCE_XREF_RE, NOW_HEADER_RE)
    lines = section.splitlines()
    first_table_line = next(
        (i for i, ln in enumerate(lines) if ln.strip().startswith("|")), len(lines)
    )
    last_table_line = first_table_line - 1
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|"):
            last_table_line = i
    intro = "\n".join(lines[:first_table_line])
    outro = "\n".join(lines[last_table_line + 1:])
    table = _extract_first_table_with_header(section)
    return intro, table, outro


def parse_now(md: str) -> tuple[list[dict[str, Any]], str]:
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
            "notes": "",
            "parity_overlay": _has_parity_overlay(" | ".join(row)),
        })
    # Prose after the table
    lines = section.splitlines()
    last_table_line = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|"):
            last_table_line = i
    prose = "\n".join(lines[last_table_line + 1:])
    return out, prose


def parse_next(md: str) -> tuple[list[dict[str, Any]], str, str]:
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
    lines = section.splitlines()
    first_table_line = next(
        (i for i, ln in enumerate(lines) if ln.strip().startswith("|")), len(lines)
    )
    last_table_line = first_table_line - 1
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|"):
            last_table_line = i
    intro = "\n".join(lines[:first_table_line])
    outro = "\n".join(lines[last_table_line + 1:])
    return out, intro, outro


def _normalize_theme_name(raw: str) -> str:
    """Clean a captured theme label into a palette key.

    The MD skill sometimes includes a count `(7)` and a trailing italic
    commentary like ` — *dependency risk concentrated here*`. Drop both
    plus any leftover dash, so the cleaned name matches THEME_PALETTE keys.
    """
    name = raw.strip()
    # Strip " — *...*" commentary (em-dash, en-dash, or hyphen).
    name = _re.sub(r"\s*[—–-]\s*\*[^*]*\*\s*$", "", name).strip()
    # Strip trailing "(…)" counts or qualifiers.
    name = _re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
    # Strip a stray trailing dash left behind by earlier passes.
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


def parse_hidden_inventory(md: str) -> tuple[list[dict[str, Any]], str]:
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
            "note": row[4] if len(row) > 4 else "",
        })
    # Retro-post recommendation prose after the table.
    lines = section.splitlines()
    last_table_line = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|"):
            last_table_line = i
    prose = "\n".join(lines[last_table_line + 1:])
    return out, prose


def parse_risks(md: str) -> str:
    return _extract_section(md, RISKS_RE, STRATEGIC_RE)


def parse_strategic(md: str) -> str:
    return _extract_section(md, STRATEGIC_RE, CHANGES_RE)


def parse_changes(md: str) -> str:
    return _extract_section(md, CHANGES_RE, FOLLOWUPS_RE)


def parse_followups(md: str) -> str:
    return _extract_section(md, FOLLOWUPS_RE, None)


# ---------------------------------------------------------------------------
# Theme inference + pill / card components
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
# KPI strip + generic table / details components
# ---------------------------------------------------------------------------

def _kpi_tile(label: str, count: str, meaning: str, color: str) -> str:
    return (
        '<div class="bg-white border border-slate-200 rounded-xl p-3 flex-1 min-w-[9rem]">'
        f'<div class="text-[10px] uppercase tracking-wider font-semibold mb-1" style="color:{color}">{_html.escape(label)}</div>'
        f'<div class="text-2xl font-semibold text-slate-900 leading-none">{_html.escape(count)}</div>'
        f'<div class="text-xs text-slate-500 mt-1 leading-snug">{_html.escape(meaning)}</div>'
        '</div>'
    )


def _status_overview_kpis(table: list[list[str]]) -> str:
    """Render the Status Overview table as a row of KPI tiles."""
    if not table or len(table) < 2:
        return ""
    color_map = {
        "RELEASED": "#059669",
        "NOW": "#2563eb",
        "NEXT": "#7c3aed",
        "BLOCKED": "#e11d48",
        "LATER": "#475569",
        "ARCHIVED": "#94a3b8",
    }
    tiles: list[str] = []
    for row in table[1:]:
        if len(row) < 3:
            continue
        label_raw = row[0].replace("**", "").strip()
        count = row[1].replace("**", "").strip()
        meaning = row[2].strip()
        # Skip the total row — it's a summary line, rendered separately.
        if label_raw.lower().startswith("in-scope total"):
            continue
        # Normalize label for color lookup
        color = color_map.get(label_raw.upper(), "#334155")
        tiles.append(_kpi_tile(label_raw, count, meaning, color))
    return (
        '<div class="flex flex-wrap gap-2 mb-3">'
        + "".join(tiles)
        + "</div>"
    )


def _simple_table_html(
    header: list[str],
    rows: list[list[str]],
    align_first_col_left: bool = True,
) -> str:
    """Render a markdown table as a styled HTML table with inline-MD cells."""
    thead = (
        '<thead><tr class="bg-slate-50 text-slate-600">'
        + "".join(
            f'<th class="text-left p-2 border border-slate-200 text-xs font-semibold">{_inline_md(h)}</th>'
            for h in header
        )
        + "</tr></thead>"
    )
    body_rows = []
    for row in rows:
        cells = []
        for idx, c in enumerate(row):
            align = "text-left" if (idx == 0 and align_first_col_left) else "text-left"
            cells.append(
                f'<td class="{align} align-top p-2 border border-slate-200 text-sm text-slate-700">{_inline_md(c)}</td>'
            )
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    tbody = "<tbody>" + "".join(body_rows) + "</tbody>"
    return (
        '<div class="overflow-x-auto">'
        '<table class="w-full border-collapse bg-white border border-slate-200 rounded-xl overflow-hidden">'
        + thead + tbody +
        "</table></div>"
    )


def _details(
    title: str,
    subtitle: str,
    body_html: str,
    open_by_default: bool = False,
) -> str:
    open_attr = " open" if open_by_default else ""
    return (
        f'<details class="bg-white border border-slate-200 rounded-xl p-4 mb-3 group"{open_attr}>'
        '<summary class="cursor-pointer list-none flex items-center justify-between">'
        '<div>'
        f'<h3 class="text-sm font-semibold text-slate-800">{_html.escape(title)}</h3>'
        + (f'<p class="text-xs text-slate-500 mt-0.5">{_html.escape(subtitle)}</p>' if subtitle else "")
        + '</div>'
        '<span class="text-slate-400 text-xs ml-3 group-open:rotate-180 transition-transform">▼</span>'
        '</summary>'
        f'<div class="mt-3">{body_html}</div>'
        '</details>'
    )


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render(md_path: str, out_path: str) -> None:
    md = open(md_path, encoding="utf-8").read()

    retrieval_date = parse_retrieval_date(md)

    public_tagging_prose = parse_public_tagging_prose(md)
    kanban_table = parse_kanban_glossary(md)
    status_table, velocity_prose = parse_status_overview(md)
    mkt_intro, mkt_table, mkt_outro = parse_marketing_gap(md)
    ann_intro, ann_table, ann_outro = parse_announcement_xref(md)
    now_items, now_prose = parse_now(md)
    next_items, next_intro, next_outro = parse_next(md)
    later = parse_later(md)
    hidden, hidden_prose = parse_hidden_inventory(md)
    risks_section = parse_risks(md)
    strategic_section = parse_strategic(md)
    changes_section = parse_changes(md)
    followups_section = parse_followups(md)

    # ----- Classify NOW/NEXT items into themes via LATER, then heuristic.
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
        if any(k in title for k in ("plagiarism",)):
            return "Competitive Parity"
        if any(k in title for k in ("arabic", "rtl", "i18n", "international", "htr", "handwriting")):
            # Arabic NLP items are part of the evaluation / enablement stack
            # for this roadmap; bucket to Quality stack if nothing better.
            return "Quality & evaluation stack"
        return None

    for lst in (now_items, next_items):
        for it in lst:
            it["_theme"] = classify(it)

    # ----- Build the theme matrix (Theme × Now/Next/Later).
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

    # ----- Parity callout chips
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

    # ----- Legend
    legend_items = "".join(
        f'<div class="flex items-center gap-2">'
        f'<span class="inline-block w-3 h-3 rounded-full" style="background:{p["color"]}"></span>'
        f'<span class="text-xs text-slate-700">{_html.escape(t)}</span>'
        f'</div>'
        for t, p in THEME_PALETTE.items()
    )

    # ----- Portfolio matrix rows
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

    # ----- Swim lanes
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
            f'<div class="flex gap-3 flex-wrap">{"".join(cols)}</div>'
            f'</section>'
        )

    # ----- Hidden inventory strip
    hidden_cards = "".join(
        f'<div class="rounded-lg border border-slate-200 bg-white p-2 min-w-[14rem]">'
        f'<div class="font-mono text-xs text-slate-500">#{h["num"]} · shipped {_html.escape(h.get("shipped",""))}</div>'
        f'<div class="text-sm text-slate-800 leading-snug">{_html.escape(h["title"])}</div>'
        f'</div>'
        for h in hidden
    )

    # ----- Build section HTML blocks
    status_kpi_html = _status_overview_kpis(status_table)
    velocity_html = md_prose_to_html(velocity_prose)

    # Marketing-gap table
    mkt_table_html = ""
    if mkt_table and len(mkt_table) >= 2:
        mkt_table_html = _simple_table_html(mkt_table[0], mkt_table[1:])
    mkt_intro_html = md_prose_to_html(mkt_intro)
    mkt_outro_html = md_prose_to_html(mkt_outro)

    # Announcement xref table
    ann_table_html = ""
    if ann_table and len(ann_table) >= 2:
        ann_table_html = _simple_table_html(ann_table[0], ann_table[1:])
    ann_intro_html = md_prose_to_html(ann_intro)
    ann_outro_html = md_prose_to_html(ann_outro)

    # NOW prose
    now_prose_html = md_prose_to_html(now_prose)
    # NEXT prose
    next_intro_html = md_prose_to_html(next_intro)
    next_outro_html = md_prose_to_html(next_outro)
    # Hidden prose
    hidden_prose_html = md_prose_to_html(hidden_prose)

    # Risks, Strategic, Changes, Followups → collapsible details blocks.
    risks_html = md_prose_to_html(risks_section)
    strategic_html = md_prose_to_html(strategic_section)
    changes_html = md_prose_to_html(changes_section)
    followups_html = md_prose_to_html(followups_section)
    public_tagging_html = md_prose_to_html(public_tagging_prose)

    # Kanban table
    kanban_table_html = ""
    if kanban_table and len(kanban_table) >= 2:
        kanban_table_html = _simple_table_html(kanban_table[0], kanban_table[1:])

    # ----- Assemble the HTML document
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
  details > summary::-webkit-details-marker {{ display: none; }}
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

<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Status overview</h2>
  {status_kpi_html}
  <div class="bg-white border border-slate-200 rounded-xl p-4">
    {velocity_html}
  </div>
</section>

<section class="max-w-[1440px] mx-auto mb-6 bg-white border border-slate-200 rounded-xl p-4">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Legend</h2>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
    {legend_items}
  </div>
  <div class="text-[11px] text-slate-500 mt-3">
    ⚔️ = also carries the GitHub <code class="bg-slate-100 px-1 rounded">Competitive Parity</code> label.
    {f"Items: {parity_links}" if parity_links else ""}
  </div>
</section>

<section class="max-w-[1440px] mx-auto mb-6">
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

<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Swim lanes</h2>
  {"".join(lanes)}
</section>

{f'''<section class="max-w-[1440px] mx-auto mb-6 bg-white border border-slate-200 rounded-xl p-4">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">NOW — ship-order read</h2>
  {now_prose_html}
</section>''' if now_prose_html else ""}

{f'''<section class="max-w-[1440px] mx-auto mb-6 bg-white border border-slate-200 rounded-xl p-4">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">NEXT — Q2 realism</h2>
  {next_intro_html}{next_outro_html}
</section>''' if (next_intro_html or next_outro_html) else ""}

<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Marketing-vs-Ship Gap</h2>
  <div class="bg-white border border-slate-200 rounded-xl p-4 mb-3">{mkt_intro_html}</div>
  {mkt_table_html}
  {f'<div class="bg-white border border-slate-200 rounded-xl p-4 mt-3">{mkt_outro_html}</div>' if mkt_outro_html else ""}
</section>

<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Announcement Cross-Reference</h2>
  <div class="bg-white border border-slate-200 rounded-xl p-4 mb-3">{ann_intro_html}</div>
  {ann_table_html}
  {f'<div class="bg-white border border-slate-200 rounded-xl p-4 mt-3">{ann_outro_html}</div>' if ann_outro_html else ""}
</section>

{f'''<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Hidden inventory — shipped, not announced</h2>
  <div class="flex gap-2 overflow-x-auto pb-2 mb-3">{hidden_cards}</div>
  {f'<div class="bg-white border border-slate-200 rounded-xl p-4">{hidden_prose_html}</div>' if hidden_prose_html else ""}
</section>''' if hidden else ""}

<section class="max-w-[1440px] mx-auto mb-6">
  <h2 class="text-sm font-semibold text-slate-700 mb-2">Analysis &amp; actions</h2>

  {_details("Risks & Dependencies",
            "Where the roadmap can quietly slip.",
            risks_html,
            open_by_default=True) if risks_html else ""}

  {_details("Strategic Call-outs",
            "Themed reads that don't fit any one bucket.",
            strategic_html,
            open_by_default=True) if strategic_html else ""}

  {_details("Changes vs. the board today",
            "Concrete actions the product lead should take after reading this.",
            changes_html) if changes_html else ""}

  {_details("Kanban Status Glossary",
            "Read this before interpreting any status column.",
            kanban_table_html) if kanban_table_html else ""}

  {_details("Public-surface tagging rules",
            "How [ANNOUNCED] and [FEATURED] are applied throughout the roadmap.",
            public_tagging_html) if public_tagging_html else ""}

  {_details("Follow-ups I can generate on request",
            "Derived views that can be produced from this roadmap.",
            followups_html) if followups_html else ""}
</section>

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
