---
name: ta39-roadmap-md
description: >
  Generate or refresh the TA39 product roadmap markdown document
  (TA39-Roadmap.md) by pulling live data from the TA-39 GitHub Projects board
  (project #4 "TA39 Product Development"). Use this skill whenever the user
  says "update TA39 roadmap", "refresh the roadmap", "regenerate roadmap md",
  "pull the latest roadmap from GitHub", "update the product roadmap markdown",
  "refresh TA39 roadmap data", or any variant that implies re-syncing the
  roadmap source of truth from GitHub. Also trigger on "update TA39 roadmap"
  with no qualifier — in that case, run this skill first and then hand off
  to ta39-roadmap-html so the HTML dashboard is regenerated from the fresh MD.
  Do NOT trigger for unrelated GitHub project pulls or non-TA39 roadmaps.
---

# TA39 Roadmap MD Generator

Produce `TA39-Roadmap.md` — the living roadmap document for the TA39 product
team. This file is the **source of truth**: it holds the data (bucketed
issues, cross-references to announcements, strategic call-outs) that the
`ta39-roadmap-html` skill later visualizes.

The document is a leadership-oriented analytical narrative — it is not a dump
of the GitHub board. It interprets the board through a specific lens and
carries opinionated call-outs. Preserve that voice: direct, decisive, honest
about gaps, no marketing gloss.

## How the pieces fit together

```
GitHub Projects board (project #4)
          │
          ▼
 scripts/fetch_board.py   ──►  /tmp/board_snapshot.json  (data only)
          │
          │  + references/announcements.md
          │  + references/features_page.md
          ▼
    Claude assembles the final MD  ──►  <workspace>/TA39-Roadmap.md
```

The script is deterministic. The MD assembly is a judgment-heavy step Claude
does — the references supply the stable cross-refs, but the prose (risks,
strategic call-outs, realism notes) is authored each run based on what the
fresh data shows.

## Step 1 — Locate the GitHub PAT

The fetch script looks for a classic PAT (with `repo` + `project` scopes)
in, in order:

1. `GITHUB_PAT` environment variable
2. `~/.secrets/github_pat`
3. **`/sessions/*/mnt/.claude/ta39-secrets/github_pat` — the canonical,
   cross-session location.** `.claude/` maps to `~/.claude/` on the user's
   Mac, which Cowork mounts into every session regardless of which folder
   the user picks. Set the PAT here once and it's found forever.
4. `/sessions/*/mnt/.secrets/github_pat` (legacy — mount root)
5. `/sessions/*/mnt/*/.secrets/github_pat` (legacy — one level deep)
6. `/sessions/*/mnt/*/*/.secrets/github_pat` (legacy — two levels deep)

If none are present, stop and tell the user to run:

```bash
mkdir -p /sessions/*/mnt/.claude/ta39-secrets
# then paste the PAT into /sessions/*/mnt/.claude/ta39-secrets/github_pat
```

…or simpler, have them drop the PAT file into the `.claude/ta39-secrets/`
folder inside whatever Cowork folder they currently have mounted. Do not
proceed without a PAT.

## Step 2 — Run the fetch script

```bash
python3 "$SKILL_DIR/scripts/fetch_board.py" > /tmp/board_snapshot.json
```

The script:
- Queries org `TA-39`, project `#4` via the GraphQL API
- Pulls every non-archived item with `Type=Feature`
- Captures: repo, number, title, URL, issue author, labels, Status, Priority,
  Size, and a `bucket` it assigns based on Status
- Also surfaces the `Competitive Parity` label — this is a cross-cutting
  strategic lens, not a topical theme

Read the resulting JSON. Check:
- `meta.fetched_at` (matches today)
- `meta.counts` (RELEASED / NOW / NEXT / BLOCKED / LATER / ARCHIVED totals
  — Archive count is reported but archived items are excluded from all other
  lists)
- `items[*].bucket` for each item

## Step 3 — Determine the output path

Default: the mounted session workspace folder. Detection logic:
1. List `/sessions/*/mnt/` (glob) and pick the first non-hidden directory as
   the workspace.
2. If multiple non-hidden directories exist, ask the user which one.
3. If none exist, fall back to writing into the session root and tell the
   user where it went.

The filename is **always** `TA39-Roadmap.md` (no date prefix — the filename
is constant, the content updates).

## Step 4 — Read the reference mappings

- `references/announcements.md` — known community.ta-39.com posts mapped to
  issues. Use this to populate the **Announcement Cross-Reference** table and
  to tag the right items `[ANNOUNCED]` / `[FEATURED]`.
- `references/features_page.md` — known www.ta-39.com/en/features claims
  mapped to issues. Use this to populate the **Marketing-vs-Ship Gap** table.

If a new announcement or features-page claim appears that isn't in these
references, flag it to the user and ask whether to append.

## Step 5 — Write the MD

The document has 15 sections in a fixed order. Follow the structure exactly;
the HTML skill parses against these headers.

### Section list (in order)

1. **Header block** — title, source, scope (feature count, author rule,
   retrieval date), horizon.
2. **Public-surface tagging rules** — definitions of `[ANNOUNCED]` and
   `[FEATURED]`, plus the note that the tags signal "things users have
   already been told about."
3. **Kanban Status Glossary** — full Status → meaning → position-in-flow
   table. This is important because the reader must understand that
   `Ready for Development` means *unstarted* and `Testing in Production`
   means *released*.
4. **Status Overview** — bucket counts table + "Velocity context" paragraph
   drawing on shipped-dates trend.
5. **Marketing-vs-Ship Gap** — one row per features-page claim with a
   reality column and a risk column. Use `references/features_page.md` as
   the input; annotate the current status of each anchor issue from the
   fetched data.
6. **Announcement Cross-Reference** — table of items with a dedicated
   community post. `[FEATURED]` applies only when the item is released
   AND named on the features page.
7. **RELEASED** — the full released inventory. One row per item whose
   bucket = RELEASED (i.e., Status `Testing in Production` or `Done`).
   Header must be exactly `## RELEASED` so the HTML renderer can find it.
   Use the same table shape as NOW/NEXT so the renderer parses it
   uniformly:

   ```
   | # | Title | Repo | Priority | Size | Status | Tags |
   ```

   The Tags column carries `[ANNOUNCED]` when the item is in the
   Announcement Cross-Reference, `[FEATURED]` when it's on the features
   page, and `[SILENT]` when neither applies (these are the hidden
   inventory — they still belong in this section, with the silent tag).
   Keep the Announcement Cross-Reference and Shipped-but-NOT-announced
   sections too — those are analytical cuts on the same data. This
   section is the complete, flat list.
8. **NOW** — active build or QA. Items whose bucket = NOW. Add a
   "Ship-order read" paragraph and a note on anything recently promoted
   from NOW to RELEASED.
9. **NEXT** — `Ready for Development` items. Include a **Q2 realism**
   column for each row (Must-start / Defer to Q3 / etc.) based on size,
   priority, and labels. Explicitly note:
   - L/XL items from a cold start won't ship in ~6 weeks
   - Items carrying the `Competitive Parity` label get a "parity play"
     flag in the Tags column (use the literal `` `Competitive Parity` label ``)
10. **LATER** — organized by theme:
    - Theme 1: Agentic / Copilot evolution
    - Theme 2: Teacher-in-the-loop intelligence
    - Theme 3: Quality & evaluation stack (flag that dependency risk is
      concentrated here — all High priority, all Blocked or unprioritized)
    - Theme 4: Integrations & LMS breadth
    - Theme 5: Monetization (flag under-weighting risk)

    For any item carrying the `Competitive Parity` label that fits a topical
    theme, annotate it with ⚔️ in the theme table and add a footnote:
    `*⚔️ = also carries the GitHub \`Competitive Parity\` label.*`
11. **Shipped but NOT publicly announced** — hidden inventory. Released
    items with no announcement and no features-page name. Recommend the
    top 3 for retroactive posts. This is the same data as the `[SILENT]`
    rows in RELEASED, surfaced here with recommendations attached.
12. **Risks & Dependencies** — at least 5 numbered risks:
    - Public surface vs. shipped product (the marketing gap)
    - Blocked High-priority items in the quality/eval stack
    - Cross-repo dependencies (Arabic NLP spans frontend, api, graditron)
    - Missing Iteration/Sprint field population
    - Author-rule violations (non-adnanwarsi `Type=Feature` issues)
13. **Strategic Call-outs** — lettered (a) through at least (f):
    - (a) Agentic is the right "Later" bet
    - (b) Monetization is underweighted
    - (c) Eval Harness M2/M3/M4 have no Priority set
    - (d) Google Classroom re-use is Low Backlog but marketed first-class
    - (e) Hidden inventory = pitch ammunition
    - (f) **Competitive Parity is a distinct lens.** List every item
      carrying the label, noting pure parity plays vs. topical items
      with a parity overlay. Frame as a portfolio question for
      leadership: under-investing loses enterprise RFPs, over-investing
      burns differentiation capacity.
14. **Changes vs. the board today** — numbered action list (retag #113,
    set priorities on Eval Harness items, populate Iteration fields, etc.)
15. **Follow-ups I can generate on request** — menu of next steps
    (exec version, sprint plan, competitive frame, refreshed xlsx tracker,
    etc.)

### Prose rules

- **Write in decisive, analytical prose.** No hedging, no "it could be
  argued." If something is under-prioritized, say so and explain why.
- **Respect the status semantics.** `Testing in Production` = Released.
  `Ready for Development` = unstarted. Surface any confusion this creates
  for readers (e.g., stakeholders who think "Ready" means "about to ship").
- **Competitive Parity is cross-cutting.** Items with no topical home
  (like Plagiarism Detection) get their own theme. Items with a topical
  home (HITL, Monetization) keep that theme and add a ⚔️ overlay.
- **Don't fabricate announcement posts.** If the references file doesn't
  list a post, the item does not get `[ANNOUNCED]`.
- **Author rule.** `Type=Feature` is reserved for the product lead
  (`adnanwarsi`). Any feature-typed issue by a different author is either
  a roadmap-level feature the lead has consciously elevated, or an
  incorrectly-typed task. Flag it.

### Voice examples

Wrong (marketing gloss):
> "Our innovative Revision Rounds feature empowers students to iterate
> seamlessly across drafts!"

Right (analytical):
> "[#697](https://github.com/TA-39/frontend/issues/697) is
> **Testing in Production** — i.e., released and being validated live."

Wrong (hedge):
> "It might be worth considering whether #374 should perhaps be a higher
> priority, depending on various factors."

Right (direct):
> "Monetization is underweighted. [#374](...) is Low priority Backlog.
> If individual-user revenue matters in 2026, this is mis-prioritized.
> If not, archive and stop carrying the noise."

## Step 6 — After writing

Report the file path to the user as a computer:// link. Then:

- If the user said **"update TA39 roadmap"** (no qualifier), automatically
  hand off to `ta39-roadmap-html` to regenerate the dashboard from the
  fresh MD. Do not ask.
- If the user said **"update TA39 roadmap md"** (qualified), stop and
  offer: "MD refreshed at <path>. Want me to regenerate the HTML
  dashboard from it?"

## Reference Files

- **`references/announcements.md`** — community.ta-39.com posts mapped to
  issues. Update this file when a new announcement ships.
- **`references/features_page.md`** — www.ta-39.com/en/features claims
  mapped to issues. Update when the public features page changes.
