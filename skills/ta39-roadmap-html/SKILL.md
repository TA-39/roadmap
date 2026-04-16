---
name: ta39-roadmap-html
description: >
  Transform the TA39 roadmap markdown (TA39-Roadmap.md) into an executive-grade
  HTML dashboard (TA39-Roadmap.html) showing a theme portfolio matrix
  (Now / Next / Later per theme) and per-theme swim lanes with cards for every
  feature. Use this skill whenever the user says "regenerate the roadmap HTML",
  "refresh the roadmap diagram", "rebuild the roadmap dashboard", "update
  roadmap html", "roadmap visualization", or any variant asking for a visual
  or HTML roadmap view. Also triggered automatically by ta39-roadmap-md after
  an unqualified "update TA39 roadmap" command. If the user asks for the
  dashboard but the MD file isn't in an obvious place, ask for its path
  rather than inventing data. Do NOT trigger for non-TA39 roadmaps or for
  arbitrary HTML generation unrelated to the TA39 product roadmap.
---

# TA39 Roadmap HTML Renderer

Produce `TA39-Roadmap.html` — an executive dashboard that visualizes the
roadmap captured in `TA39-Roadmap.md`. The HTML is a **view**, not a source
of truth: it derives everything from the MD. If the MD is wrong, the HTML
is wrong — so fix the MD and regenerate, never hand-edit the HTML.

## Inputs

- **Source MD path** (required). If not supplied, look for
  `TA39-Roadmap.md` under `/sessions/*/mnt/*/`. If none found, ask the user.
- **Output path** (optional). Default: same folder as the MD, named
  `TA39-Roadmap.html`.

## Step 1 — Locate the MD

```bash
ls /sessions/*/mnt/*/TA39-Roadmap.md 2>/dev/null
```

If exactly one result: use it. If multiple: ask the user which one. If none:
ask for the path. Do not invent content without an MD file to derive from.

## Step 2 — Render

```bash
python3 "$SKILL_DIR/scripts/render_html.py" <md_path> <out_path>
```

The script:
- Parses the MD's NOW, NEXT, and LATER theme tables
- Detects `Competitive Parity` items (both pure parity plays and ⚔️-flagged
  items with topical themes)
- Builds the theme portfolio matrix (rows = themes, columns = Now/Next/Later)
- Builds swim lanes per theme with cards showing issue #, title, status,
  size, priority, tags, and a short realism/notes snippet
- Emits a standalone HTML file using Tailwind via CDN (no build step) and
  inline CSS variables for the theme palette

## Design rules

### Themes (fixed palette)

| Theme | Color role | Notes |
|---|---|---|
| Agentic / Copilot evolution | indigo | #547, #649 and anything explicitly agentic |
| Teacher-in-the-loop intelligence | emerald | #331, #113; #328 is HITL with ⚔️ overlay |
| Quality & evaluation stack | rose | Sentinel, graditron eval harness, confidence scoring |
| Integrations & LMS breadth | amber | #473, #226, #474, #701 |
| Monetization | violet | #374 carries ⚔️ overlay |
| Arabic NLP / i18n | sky | #596, #166, #99, #532 |
| UX / UI polish | slate | #720, #297, #188 |
| Content / rubric tools | teal | #343, #344, #440 |
| **Competitive Parity** | **orange (#ea580c)** | Own theme row for pure parity plays (e.g. #327 Plagiarism); overlay ⚔️ on items in other themes |

### Layout

1. **Header band** — title, retrieval date pulled from the MD's first
   section, a one-line strategic summary if present.
2. **Legend** — color chip per theme, with a distinct treatment for the
   Competitive Parity overlay semantic. Include a small note listing the
   three (or current count of) parity-flagged items with hyperlinks.
3. **Theme portfolio matrix** — grid with rows = themes (ordered most to
   least shipped-adjacent), columns = Now / Next / Later. Cells contain
   pills for each issue (`#697`, `#740`, etc.), color-matched to the row
   theme. Pills for items in a topical theme that ALSO carry the parity
   label get a ⚔️ postfix in the pill.
4. **Swim lanes** — one row per theme, showing cards in each of
   Now / Next / Later columns. Cards carry issue #, title, size pill
   (S / M / L / XL), priority pill (High / Medium / Low), status,
   tags (`[ANNOUNCED]` / `[FEATURED]` / `Competitive Parity`), and the
   realism note from the MD if present.
5. **Hidden inventory strip** at the bottom — the "Shipped but NOT
   publicly announced" items as a single-line card row, because they're
   strategic but visually distinct from the main portfolio.
6. **Footer** — link back to the source MD path, the data retrieval time
   from the MD's meta block, and the list of strategic call-outs as
   collapsible detail sections.

### Typography and density

- Wide, executive-review layout. Target ~1440px.
- Cards are dense but breathable — ~3 cards per swim-lane column on a
  wide screen.
- Tags render as small pills, never bold prose.
- Competitive Parity overlay uses the ⚔️ emoji in the pill AND an orange
  dot in the card corner. Dual coding so it's obvious even in monochrome.

### What NOT to do

- **Don't re-pull from GitHub.** If the data looks stale, tell the user
  to run `ta39-roadmap-md` first. Keeping the two skills separate means
  you can tweak the diagram without touching the data pipeline.
- **Don't invent themes not present in the MD.** The MD's section
  headers are the authority; the HTML mirrors them.
- **Don't embed secrets, PATs, or raw API responses.** The HTML is
  sharable — treat it as a read-only view.

## Step 3 — Report

Share the output as a computer:// link. If the MD changed meaningfully
(new issues added, buckets reshuffled), call out the diff in one or two
sentences so the user knows what's new.

## Troubleshooting

- **HTML shows empty swim lanes** → the MD's theme tables are malformed.
  Re-run `ta39-roadmap-md` or ask the user to check the MD section
  headers match the expected theme names.
- **Parity items not marked ⚔️** → the MD's call-out (f) is missing the
  issue list, or the theme tables don't have the ⚔️ emoji. Fix the MD.
- **Colors look wrong** → the fixed palette above is the source of truth.
  Update `render_html.py`'s `THEME_PALETTE` dict if the palette should
  change, not the theme list.
