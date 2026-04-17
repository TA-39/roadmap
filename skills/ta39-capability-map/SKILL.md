---
name: ta39-capability-map
description: >
  Render TA39-Capability-Map.html — a simplified, user-facing capability
  diagram of TA39 organized by what a user actually does (Set up → Collect
  work → Give feedback → Steer & report, plus a Foundations & breadth row).
  Subtle notation distinguishes shipped capabilities from pipeline ones,
  and the capability list is derived from a curated mapping file combined
  with live status from TA39-Roadmap.md. Use this skill whenever the user
  asks to "update the capability map", "refresh the capability diagram",
  "rebuild the capability map", "generate the capability view", or any
  variant naming the capability map, capability diagram, or impact
  diagram. Also trigger when the user asks for a "simple one-page view of
  what TA39 does" tied to the roadmap. Do NOT use this for non-TA39
  capability maps, general product diagrams, or arbitrary HTML generation.
---

# TA39 Capability Map Renderer

Produce `TA39-Capability-Map.html` — a one-page, outcome-organized view of
what TA39 does for the user. This is **not** the roadmap. The roadmap lists
every tracked feature; this map distills them into the handful of user-
visible capabilities and shows which are live versus in the pipeline.

The map has two axes:

1. **Horizontal user journey** — four columns following what a teacher
   actually does: *Set up → Collect work → Give feedback → Steer & report*.
2. **A bottom Foundations & breadth row** — cross-cutting items that don't
   belong to a single step (internationalization, monetization, plagiarism
   detection, agentic).

Status is binary and visual:

- **Shipped** — solid card with a 3px teal left-edge accent.
- **Pipeline** — dashed slate border, muted text, tiny dot in the top-right
  corner. The dot + dash are deliberately quiet so the eye lands on what's
  live first.

## Inputs

- **Source MD path** (required). Default: look for `TA39-Roadmap.md` under
  `/sessions/*/mnt/*/`. If none found, ask the user.
- **Mapping file** (bundled). Default: `references/capabilities.json`
  inside this skill. The mapping is the editorial source of truth for what
  capabilities exist and what they're called. Issue numbers in the mapping
  link back to the roadmap so status stays in sync automatically.
- **Output path** (optional). Default: same folder as the MD, named
  `TA39-Capability-Map.html`.

## Step 1 — Locate the MD

```bash
ls /sessions/*/mnt/*/TA39-Roadmap.md 2>/dev/null
```

If exactly one result: use it. If multiple: ask the user which one. If
none: ask for the path, or remind the user to run `ta39-roadmap-md` first.

## Step 2 — Render

```bash
python3 "$SKILL_DIR/scripts/render_capability_map.py" <md_path> <out_path>
```

The script:

- Parses the MD's section structure (`## RELEASED`, `## NOW`, `## NEXT`,
  `## LATER`) and records the status bucket for every tracked issue.
- Loads `capabilities.json` for the curated capability list, column
  assignment, short blurb, and linked issue numbers.
- For each capability: status = `shipped` if ANY linked issue is in
  RELEASED, else `pipeline`. A capability can also pin an explicit
  `status` in the mapping if it doesn't trace to a single issue (e.g.
  "AI feedback on any submission" is a composite of the whole platform).
- Emits a standalone HTML file using Tailwind via CDN with inline CSS
  variables for shipped/pipeline treatment.

## Mapping file — `references/capabilities.json`

Structure:

```json
{
  "columns": [
    {"id": "set_up",  "number": "1", "title": "Set up",       "subtitle": "Describe what 'good' looks like, once."},
    {"id": "collect", "number": "2", "title": "Collect work", "subtitle": "From wherever students already are."},
    {"id": "feedback","number": "3", "title": "Give feedback","subtitle": "Fast, rubric-aligned, revision-aware."},
    {"id": "steer",   "number": "4", "title": "Steer & report","subtitle": "Teacher stays in the driver's seat."}
  ],
  "capabilities": [
    {"column": "set_up", "name": "Build rubrics with AI",
     "blurb": "Draft and refine criteria in minutes instead of hours.",
     "issues": [343]}
  ],
  "foundations": [
    {"name": "Internationalization",
     "blurb": "Multi-language UI scaffolding.",
     "issues": [532]}
  ]
}
```

Per-capability fields:

- `column` (required for `capabilities`; not used for `foundations`) — one
  of the `columns[].id` values.
- `name` (required) — the user-facing capability label. This is an
  editorial choice, not the raw issue title. Keep it short and outcome-
  focused ("Save feedback templates", not "Feedback Template creation
  (Simplify)").
- `blurb` (required) — one short sentence explaining the benefit. Write
  for a non-technical reader.
- `issues` (optional) — list of GitHub issue numbers that back this
  capability. If ANY of them is in `## RELEASED` in the MD, the capability
  renders as shipped. Multiple issues are allowed (e.g. Copilots spans
  #384/#385/#366) — it's considered shipped if any one ships.
- `status` (optional) — `shipped` or `pipeline`. An explicit value
  overrides the issue-derived one. Use this for composite capabilities
  that don't map to a single issue (e.g. "AI feedback on any submission").

## When to edit the mapping

Edit `capabilities.json` whenever:

- A new tracked issue lands that represents a net-new user-visible
  capability (add an entry).
- The editorial framing of an existing capability changes (rename,
  rewrite the blurb).
- A capability should move columns because the user journey reframes.

Do NOT edit it to change shipped/pipeline status — that's derived from
the roadmap MD. Fix the MD (or ship the issue) if the status is wrong.

## Design rules

- **Tone is outcome-first.** Every card name should read like a benefit,
  not a feature ticket. "Save feedback templates" beats "Template CRUD".
- **No issue numbers on cards.** The capability map is for people who
  don't care about project hygiene. Issue numbers live in the roadmap.
- **Subtle notation for pipeline.** Dashed border, slate dot top-right,
  muted body text. The reader should naturally land on shipped cards
  first; pipeline cards are there for context, not to compete for
  attention.
- **Four columns, always equal width.** The user-journey columns are the
  primary reading order. Don't let one column's length determine
  alignment — use CSS grid with `1fr` columns and thin arrow columns
  between them.
- **Foundations row is visually separate.** Place it below the four-
  column grid with its own small header. These items are important but
  don't fit the left-to-right narrative; keeping them apart preserves
  the clarity of the top grid.
- **Footer links back to the roadmap.** Anyone who wants per-feature
  detail should have a one-click path to `TA39-Roadmap.html`.

## Step 3 — Report

Share the output as a computer:// link. If the mapping or roadmap
triggered a status change (a capability flipped shipped ↔ pipeline), call
it out in one line so the user knows what moved.

## Troubleshooting

- **All cards render as pipeline** → the MD parsing missed the
  `## RELEASED` section. Check that the MD has that heading and the
  standard `| [#N](...) | ...` table format.
- **A capability you expect is missing** → it's not in
  `capabilities.json`. Add it there; do not hand-edit the HTML.
- **A capability has the wrong status** → either its `issues` list is
  wrong in the mapping, or the underlying issue is in the wrong status
  bucket in the roadmap. Fix whichever one is wrong; the HTML is a view.
- **Columns wrap to a new row on wide screens** → the script emits a
  CSS grid with `1fr 24px 1fr 24px 1fr 24px 1fr` so all four content
  columns and three arrow gutters fit on one row. If the grid template
  is altered, rewrap will happen.
