#!/usr/bin/env python3
"""
Render TA39-Capability-Map.html from TA39-Roadmap.md + references/capabilities.json.

Reads the bucket status (RELEASED / NOW / NEXT / LATER) for every tracked
issue in the MD, cross-references it against the editorial capability
mapping, and emits a standalone HTML file with the four user-journey
columns plus a Foundations & breadth row.

Usage:
  render_capability_map.py <md_path> [<out_path>] [--mapping <path>]

Output:
  Writes the HTML to <out_path> (default: same folder as MD, named
  TA39-Capability-Map.html). Prints a one-line summary to stdout.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from datetime import datetime
from typing import Any

# --------------------------------------------------------------------------
# MD parsing: which bucket is each issue in?
# --------------------------------------------------------------------------

SECTION_HEADINGS = {
    "released": r"^##\s+RELEASED\s*$",
    "now":      r"^##\s+NOW\s*$",
    "next":     r"^##\s+NEXT\s*$",
    "later":    r"^##\s+LATER\s*$",
    # end markers we bump into
    "end":      r"^##\s+(Shipped but NOT|Risks|Strategic|Changes|Appendix|Follow-ups)\b",
}

ISSUE_LINK_RE = re.compile(r"\[#(\d+)\]\([^)]+\)")


def parse_buckets(md: str) -> dict[int, str]:
    """Return {issue_number: bucket_name} for every issue that appears in a
    RELEASED/NOW/NEXT/LATER section. Bucket name is one of the keys above
    except 'end'. If an issue appears in multiple sections, the first
    (earliest-ranked) wins: released > now > next > later."""
    rank = {"released": 0, "now": 1, "next": 2, "later": 3}
    lines = md.splitlines()
    current: str | None = None
    out: dict[int, str] = {}
    section_pats = {
        name: re.compile(pat, re.IGNORECASE)
        for name, pat in SECTION_HEADINGS.items()
    }

    for line in lines:
        # section transitions
        matched_section: str | None = None
        for name, pat in section_pats.items():
            if pat.match(line):
                matched_section = name
                break
        if matched_section is not None:
            if matched_section == "end":
                current = None
            else:
                current = matched_section
            continue

        if current is None:
            continue

        # capture every issue reference on this line
        for m in ISSUE_LINK_RE.finditer(line):
            num = int(m.group(1))
            prev = out.get(num)
            if prev is None or rank[current] < rank[prev]:
                out[num] = current
    return out


def extract_meta_date(md: str) -> str | None:
    """Pull the retrieval date from the MD's first meta block if present."""
    m = re.search(r"retrieved\s+on\s+\*\*(\d{4}-\d{2}-\d{2})", md, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"^\*+Retrieved:\*+\s*(\d{4}-\d{2}-\d{2})", md, re.MULTILINE)
    if m:
        return m.group(1)
    return None


# --------------------------------------------------------------------------
# Mapping resolution
# --------------------------------------------------------------------------

def load_mapping(path: str) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def resolve_status(entry: dict[str, Any], buckets: dict[int, str]) -> str:
    """Return 'shipped' or 'pipeline'. Explicit status wins."""
    explicit = entry.get("status")
    if explicit in ("shipped", "pipeline"):
        return explicit
    for issue in entry.get("issues", []):
        if buckets.get(int(issue)) == "released":
            return "shipped"
    return "pipeline"


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------

HTML_SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TA39 — Capability Map</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  :root {{
    --ink: #0f172a;
    --muted: #64748b;
    --hair: #e2e8f0;
    --bg: #fafaf9;
    --accent: #0f766e;      /* teal — shipped */
    --pipeline: #94a3b8;    /* slate — pipeline */
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    background-image:
      radial-gradient(ellipse 80% 40% at 20% 0%, rgba(15,118,110,0.05) 0%, transparent 55%),
      radial-gradient(ellipse 60% 40% at 80% 0%, rgba(37,99,235,0.04) 0%, transparent 55%);
    background-attachment: fixed;
    -webkit-font-smoothing: antialiased;
    color: var(--ink);
  }}
  .display {{ letter-spacing: -0.03em; }}

  /* Shipped capability — filled card with a teal left edge */
  .cap-shipped {{
    background: #ffffff;
    border: 1px solid var(--hair);
    border-left: 3px solid var(--accent);
    box-shadow: 0 1px 0 rgba(15,23,42,0.03);
  }}
  /* Pipeline capability — dashed, muted, with a slate dot top-right */
  .cap-pipeline {{
    background: transparent;
    border: 1px dashed var(--pipeline);
    color: #64748b;
  }}
  .cap-pipeline .cap-label {{ color: #64748b; }}
  .cap-pipeline::after {{
    content: "";
    position: absolute;
    top: 6px; right: 6px;
    width: 4px; height: 4px;
    border-radius: 50%;
    background: var(--pipeline);
  }}

  .flow-arrow {{
    color: #cbd5e1;
    font-size: 18px;
    line-height: 1;
    user-select: none;
  }}

  .cluster-title {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #334155;
  }}
  .cluster-sub {{
    font-size: 12px;
    color: #64748b;
    line-height: 1.4;
  }}

  /* 4 equal content columns with thin arrow columns between them.
     Stacks on narrow screens. */
  .flow-grid {{
    display: grid;
    grid-template-columns: 1fr;
  }}
  @media (min-width: 1024px) {{
    .flow-grid {{
      grid-template-columns: 1fr 24px 1fr 24px 1fr 24px 1fr;
    }}
  }}
</style>
</head>
<body class="p-6 md:p-10">

<div class="max-w-[1400px] mx-auto">

  <header class="mb-8">
    <div class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500 mb-2">TA-39 · Capability Map</div>
    <h1 class="display text-4xl md:text-5xl font-extrabold leading-[1.05]">
      {title}
    </h1>
    <p class="text-slate-600 mt-3 max-w-3xl">
      {subtitle}
    </p>

    <div class="flex flex-wrap items-center gap-4 mt-5 text-xs text-slate-600">
      <div class="flex items-center gap-2">
        <span class="inline-block w-6 h-3 rounded-sm border border-slate-200" style="background:#fff;border-left:3px solid var(--accent);"></span>
        <span><span class="font-semibold text-slate-800">Shipped</span> — live in product today</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-block w-6 h-3 rounded-sm" style="border:1px dashed var(--pipeline);"></span>
        <span><span class="font-semibold text-slate-700">In the pipeline</span> — committed, not yet in users' hands</span>
      </div>
      <div class="ml-auto text-[11px] text-slate-400 tabular-nums">Snapshot {snapshot}</div>
    </div>
  </header>

  <div class="flow-grid gap-3 items-start">
{columns_block}
  </div>

  <section class="mt-10">
    <div class="cluster-title mb-3">Foundations &amp; breadth</div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
{foundations_block}
    </div>
  </section>

  <section class="mt-10 pt-6 border-t" style="border-color:var(--hair);">
    <div class="cluster-title mb-2">Takeaway</div>
    <p class="text-slate-700 max-w-3xl leading-relaxed">
      The full loop — <span class="font-semibold">set up → collect → feedback → steer</span> —
      is {shipped_count} of {total_count} capabilities live today. The pipeline extends
      that same loop into the remaining {pipeline_count} committed capabilities. Every
      dashed box is a tracked piece of work on the live roadmap, not a speculative wish.
    </p>
  </section>

  <footer class="mt-8 text-[11px] text-slate-400">
    Derived from the live TA39 roadmap (project #4). See
    <a href="TA39-Roadmap.html" class="underline hover:text-slate-600">TA39-Roadmap.html</a>
    for per-feature detail.
  </footer>

</div>
</body>
</html>
"""


def render_card(entry: dict[str, Any], status: str) -> str:
    klass = "cap-shipped" if status == "shipped" else "cap-pipeline"
    text_cls = "text-slate-500" if status == "shipped" else ""
    return (
        f'      <div class="{klass} relative rounded-md p-3">\n'
        f'        <div class="cap-label text-[13px] font-semibold">{html.escape(entry["name"])}</div>\n'
        f'        <div class="text-[11px] {text_cls} mt-1 leading-snug">{html.escape(entry["blurb"])}</div>\n'
        f"      </div>"
    )


def render_column(col: dict[str, Any], entries: list[tuple[dict[str, Any], str]]) -> str:
    header = (
        f'    <section class="space-y-3">\n'
        f"      <div>\n"
        f'        <div class="cluster-title">{html.escape(col["number"])} · {html.escape(col["title"])}</div>\n'
        f'        <div class="cluster-sub">{html.escape(col["subtitle"])}</div>\n'
        f"      </div>"
    )
    cards = "\n".join(render_card(e, s) for e, s in entries)
    return header + ("\n" + cards if cards else "") + "\n    </section>"


def render_arrow() -> str:
    return (
        '    <div class="hidden lg:flex items-center justify-center pt-16">\n'
        '      <span class="flow-arrow">›</span>\n'
        "    </div>"
    )


def build_columns_block(mapping: dict[str, Any], buckets: dict[int, str]) -> tuple[str, int, int]:
    shipped = 0
    pipeline = 0
    by_col: dict[str, list[tuple[dict[str, Any], str]]] = {c["id"]: [] for c in mapping["columns"]}
    for entry in mapping["capabilities"]:
        status = resolve_status(entry, buckets)
        if status == "shipped":
            shipped += 1
        else:
            pipeline += 1
        by_col.setdefault(entry["column"], []).append((entry, status))

    parts: list[str] = []
    for i, col in enumerate(mapping["columns"]):
        if i > 0:
            parts.append(render_arrow())
        parts.append(render_column(col, by_col.get(col["id"], [])))
    return "\n\n".join(parts), shipped, pipeline


def build_foundations_block(mapping: dict[str, Any], buckets: dict[int, str]) -> tuple[str, int, int]:
    shipped = 0
    pipeline = 0
    cards: list[str] = []
    for entry in mapping.get("foundations", []):
        status = resolve_status(entry, buckets)
        if status == "shipped":
            shipped += 1
        else:
            pipeline += 1
        cards.append(render_card(entry, status))
    return "\n".join(cards), shipped, pipeline


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip())
    ap.add_argument("md_path", help="Path to TA39-Roadmap.md")
    ap.add_argument("out_path", nargs="?", help="Output HTML path (default: alongside MD)")
    ap.add_argument(
        "--mapping",
        help="Path to capabilities.json (default: references/capabilities.json alongside this script)",
    )
    args = ap.parse_args(argv)

    md_path = os.path.abspath(args.md_path)
    if not os.path.isfile(md_path):
        print(f"error: MD not found at {md_path}", file=sys.stderr)
        return 2
    out_path = args.out_path or os.path.join(
        os.path.dirname(md_path), "TA39-Capability-Map.html"
    )

    mapping_path = args.mapping or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "references",
        "capabilities.json",
    )
    mapping_path = os.path.abspath(mapping_path)
    if not os.path.isfile(mapping_path):
        print(f"error: mapping file not found at {mapping_path}", file=sys.stderr)
        return 2

    with open(md_path) as f:
        md = f.read()
    mapping = load_mapping(mapping_path)
    buckets = parse_buckets(md)

    columns_block, cap_shipped, cap_pipeline = build_columns_block(mapping, buckets)
    foundations_block, fnd_shipped, fnd_pipeline = build_foundations_block(mapping, buckets)

    total = cap_shipped + cap_pipeline + fnd_shipped + fnd_pipeline
    shipped_total = cap_shipped + fnd_shipped
    pipeline_total = cap_pipeline + fnd_pipeline

    snapshot = extract_meta_date(md) or datetime.now().strftime("%Y-%m-%d")

    html_doc = HTML_SHELL.format(
        title=html.escape(mapping.get("title", "What TA39 does for you")),
        subtitle=html.escape(mapping.get("subtitle", "")),
        snapshot=html.escape(snapshot),
        columns_block=columns_block,
        foundations_block=foundations_block,
        shipped_count=shipped_total,
        pipeline_count=pipeline_total,
        total_count=total,
    )

    with open(out_path, "w") as f:
        f.write(html_doc)

    print(
        f"wrote {out_path} — {shipped_total} shipped / {pipeline_total} pipeline "
        f"({total} capabilities total)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
