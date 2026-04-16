# TA-39 Product Roadmap

Living source-of-truth for the TA39 product roadmap. Two files own everything:

- **`TA39-Roadmap.md`** — the analytical narrative. Leadership-oriented, opinionated, and the input to every other surface (HTML dashboard, exec briefs, sprint plans). If it's not in the MD, it's not on the roadmap.
- **`TA39-Roadmap.html`** — an executive dashboard rendered from the MD. Theme portfolio matrix (Now / Next / Later per theme), per-item cards, announcement cross-reference, hidden-inventory table, and strategic call-outs. Open it in a browser — it's self-contained.

Both files are regenerated **every Sunday at 06:07 local time** by an automated job. Manual edits to these files in this repo are overwritten on the next run; to change content, change the source (the GitHub Projects board, or the skills that render it).

---

## What flows where

```
Humans (PM + engineering)
         │  create issues, move cards, label,
         │  set priority/size/iteration
         ▼
GitHub Projects board (org: TA-39, project #4 "TA39 Product Development")
         │  GraphQL pull (authenticated with a classic PAT)
         ▼
 ta39-roadmap-md skill  ──►  TA39-Roadmap.md    (analytical source of truth)
         │
         │  parse against a fixed 14-section structure
         ▼
 ta39-roadmap-html skill  ──►  TA39-Roadmap.html  (executive dashboard)
         │
         ▼
 git commit + PR + squash-merge  ──►  main
```

The MD is judgment-heavy (risks, realism notes, strategic framing); the HTML is deterministic (structure and styling from a fixed renderer). The job runs autonomously — no human gate on the merge.

---

## How the board gets populated (the upstream bit)

The automation is only as good as the data on the board. The board lives at **[TA-39 Project #4 — "TA39 Product Development"](https://github.com/orgs/TA-39/projects/4)** and spans issues from multiple repos (`frontend`, `api`, `graditron`, and others as needed).

**Who touches it:**

- **Product lead (`adnanwarsi`)** creates and owns all `Type=Feature` issues. Features are roadmap-level units — the things that appear in the MD and HTML as cards. The author-rule check in the skill enforces this: any `Type=Feature` authored by anyone else gets flagged weekly as a promote-or-downgrade decision.
- **Engineering** creates `Type=Task`, `Type=Bug`, and un-typed issues under those features. These do not appear on the roadmap — they're implementation detail.
- **Anyone** can move cards between Status columns as work progresses. The Status field is what drives the bucket assignment (see below).

**The fields the skills read:**

| Field | Purpose | Who sets it |
|---|---|---|
| `Status` | Drives which bucket the item lands in (RELEASED / NOW / NEXT / BLOCKED / LATER) | Engineering / PM, as work moves |
| `Priority` | Surfaced on cards; drives Q2 realism calls in NEXT | PM |
| `Size` | Surfaced on cards; drives shipability reads (L/XL from a cold start won't ship in 6 weeks) | PM + eng sizing |
| `Iteration` | Sprint assignment. Currently unpopulated — the skill calls that out as a standing risk | PM |
| `Labels` | `Competitive Parity` is the one that matters — it drives the ⚔️ overlay and the dedicated strategic call-out | PM |
| `Type` | Must be `Feature` for an issue to appear on the roadmap at all | Product lead |
| `isArchived` | Archived items are excluded from every bucket | PM |

**The Status → bucket mapping** (hard-coded in the skill):

| Status | Bucket | Meaning |
|---|---|---|
| `Testing in Production`, `In Production & Done` | RELEASED | Shipped and validating live |
| `In progress`, `Development Complete`, `Ready for Testing (Staging)`, `Testing in Staging`, `Testing Pre-Production`, `Testing Result Discussion` | NOW | Active build or QA |
| `Ready for Development` | NEXT | Unstarted but ready — **not** "about to ship" |
| `Blocked / Information Needed` | BLOCKED | Waiting on input |
| `Backlog` | LATER | Parked, not queued |
| `Archive` | ARCHIVED | Excluded from everything |

**Important:** `Ready for Development` means *unstarted*, not "almost shipping". `Testing in Production` means *released*. These are the two semantic traps the skill surfaces in the MD's Kanban glossary section so readers don't misread the columns.

---

## The two skills — what they are and how they run

A "skill" in this context is a **Cowork skill** — a self-contained bundle of instructions (`SKILL.md`), scripts (`scripts/`), and reference data (`references/`) that Claude loads on demand when a matching trigger phrase appears in a conversation or in an automated prompt. Skills are Claude's way of packaging a repeatable, versioned procedure with all its dependencies in one place.

### `ta39-roadmap-md`

**What it does:** Pulls the live GitHub Projects board via GraphQL, applies the bucket mapping above, and writes an analytical roadmap markdown to `TA39-Roadmap.md`.

**Anatomy:**

```
ta39-roadmap-md/
├── SKILL.md                        Instructions Claude follows (14 sections,
│                                   prose rules, voice examples, Competitive
│                                   Parity handling, author-rule policing).
├── scripts/
│   └── fetch_board.py              Stdlib-only Python. Reads the PAT (env var
│                                   or .secrets/github_pat), hits the GitHub
│                                   GraphQL API, emits a deterministic JSON
│                                   snapshot to /tmp/board_snapshot.json.
└── references/
    ├── announcements.md            community.ta-39.com posts → issue numbers.
    │                               Used to tag items [ANNOUNCED].
    └── features_page.md            www.ta-39.com/en/features claims → issue
                                    numbers. Used for the Marketing-vs-Ship
                                    Gap table.
```

**How it runs:**
1. Claude reads `SKILL.md` and starts executing the step list.
2. Step 1: resolve the PAT. Claude runs the fetch script as `python3 scripts/fetch_board.py > /tmp/board_snapshot.json`.
3. Step 2: read the JSON snapshot (36 feature items, counts per bucket, Competitive Parity list).
4. Step 3: read the two reference files to know which items get `[ANNOUNCED]` / `[FEATURED]` tags.
5. Step 4: **author the MD** — this is the judgment-heavy part. The script is deterministic; the MD prose is written fresh each run to reflect what the new data shows (which risks are sharper, which strategic call-outs are new, which items just moved). Voice rules, section order, and Competitive Parity handling are codified in `SKILL.md`.
6. Step 5: write the MD to the workspace folder as `TA39-Roadmap.md`.

### `ta39-roadmap-html`

**What it does:** Reads the freshly written `TA39-Roadmap.md` and renders an executive dashboard to `TA39-Roadmap.html`.

**Anatomy:**

```
ta39-roadmap-html/
├── SKILL.md                        Instructions: which MD to read, where to
│                                   write the HTML, what the renderer expects.
└── scripts/
    └── render_html.py              Stdlib-only Python. Parses the MD against
                                    the 14 section headers, builds the theme
                                    portfolio matrix, generates per-item cards
                                    with Competitive Parity ⚔️ overlays, emits
                                    a self-contained HTML page (Tailwind via
                                    CDN, inline theme palette, no build step).
```

**How it runs:**
1. Claude reads `SKILL.md`.
2. Runs `python3 scripts/render_html.py <path-to-TA39-Roadmap.md> <path-to-TA39-Roadmap.html>`.
3. The script parses the MD, classifies each card into a theme (topical home + parity overlay), builds the matrix, and writes the HTML. No judgment required — it's a pure transform.
4. Reports the output file path.

### What actually invokes the skills

Three ways the skills get invoked, in order of how often they run:

**1. The weekly scheduled task** — the main path. The `ta39-weekly-roadmap-refresh` task (in Cowork's Scheduled sidebar) fires every Sunday at 06:07 local time, opens a new Cowork session under the hood, and runs a self-contained prompt that says "invoke `ta39-roadmap-md`, then invoke `ta39-roadmap-html`, then commit + PR + auto-squash-merge into `TA-39/roadmap`." Claude reads each skill's `SKILL.md` when it hits the trigger phrase, executes the steps, and reports back.

**2. Manual Cowork invocation** — say "update TA39 roadmap" in any Cowork session that has the skills installed. Same pipeline, on demand. Useful for intra-week refreshes (e.g., right before a board meeting).

**3. Direct script execution** — advanced escape hatch. Running `python3 scripts/fetch_board.py > /tmp/board_snapshot.json` pulls a raw snapshot without any MD/HTML generation. Useful for debugging or for downstream scripts that want the board state as structured JSON.

**Where the skills physically live:**

- Packaged as `.skill` bundle files (zipped skill folders) in the Cowork workspace folder (canonical: `Product Roadmap Braintstorm`).
- Installed into Cowork's skills directory on `mnt/.claude/skills/` per session.
- **Not committed to this repo.** Intentionally — the skills are the pipeline; this repo is the output. Keeping them separate means a change to rendering logic doesn't pollute the roadmap history.

**Where the PAT lives:**

- Stored at `Product Roadmap Braintstorm/.secrets/github_pat` (never committed, never moved into this repo).
- The `fetch_board.py` resolver also checks `GITHUB_PAT` env var and a few deeper globs so the same skill works across Cowork sessions that mount different folders.
- Requires `repo` + `project` scopes on the `TA-39` org.

---

## How the weekly refresh works

A Cowork scheduled task (`ta39-weekly-roadmap-refresh`) runs every Sunday:

1. Invokes `ta39-roadmap-md` — pulls live board data via GraphQL, writes `TA39-Roadmap.md` in the mounted workspace folder.
2. Invokes `ta39-roadmap-html` — reads the fresh MD, writes `TA39-Roadmap.html` in the same folder.
3. Clones this repo to a scratch dir, creates branch `claude/roadmap-refresh-YYYY-MM-DD`, copies the two files in, commits.
4. Opens a PR against `main` with a change summary (bucket counts, items that moved buckets, new Competitive Parity flags, author-rule violations).
5. **Squash-merges the PR** via the REST API, deletes the branch.
6. Reports file links, PR link, merge status, and anything newly notable.

If nothing changed since last week, the task skips the PR entirely — no empty history churn. If the merge fails (e.g., someone added branch protection), the PR stays open for human review; the task does not bypass protections.

**Authentication:** a classic GitHub PAT with `repo` + `project` scopes, stored outside this repo and read from the scheduled session's environment. Never commit the PAT.

---

## Maintenance — the things that actually need human attention

The automation handles rendering. It does **not** handle the inputs that make the roadmap accurate. These are on you:

**1. Keep the GitHub Project #4 board clean.**
- Every feature-level item has `Type=Feature` and is authored by the product lead (`adnanwarsi`). If you see `Type=Feature` from another author, decide: promote (leave as-is, you're elevating it) or downgrade to Task. The skill flags these every week.
- Status field drives the bucket (`Ready for Development` → NEXT, `Testing in Production` → RELEASED, etc.). If status is wrong, the roadmap is wrong.
- Priority, Size, and Iteration fields are read and surfaced. Leave them blank and the skill calls that out as a gap.
- `Competitive Parity` label is the cross-cutting lens. Apply it consciously — it drives the ⚔️ overlay in the LATER themes and the dedicated strategic call-out section.

**2. Keep the reference files in the skill up to date.**

The `ta39-roadmap-md` skill bundles two reference files that Claude can't infer from GitHub alone:

- `references/announcements.md` — maps community.ta-39.com posts to issue numbers. When a new marquee feature ships with a community announcement, add a line here so the item gets `[ANNOUNCED]`.
- `references/features_page.md` — maps www.ta-39.com/en/features claims to issue numbers. When the marketing features page changes, update this so the "Marketing-vs-Ship Gap" table stays honest.

If a new announcement or features-page claim appears and isn't in these references, the weekly run flags it — but it won't fix the mapping on its own.

**3. React to the weekly PR.**

Even though the PR merges itself, the commit message and the `ta39-weekly-roadmap-refresh` report surface three things worth acting on:

- **Items newly promoted to RELEASED** → candidates for a community post.
- **Author-rule violations** → GitHub board hygiene.
- **Unprioritized High/Competitive-Parity items** → decisions needed from the product lead.

Treat the weekly refresh as a short standing meeting with yourself.

---

## Evolving the roadmap system

**To change what the MD says:**
edit `SKILL.md` and reference files in `ta39-roadmap-md`, then re-package and reinstall the skill. The 14-section structure is a hard contract with the HTML renderer — adding a new section means updating both skills together. Adding new *content* inside an existing section (a new risk, a new strategic call-out) is a prompt change only.

**To change what the HTML looks like:**
edit `ta39-roadmap-html`'s `scripts/render_html.py`. It parses the MD against the 14 section headers, so header order and wording matter. The theme palette, portfolio matrix, and card styling are all in that single file.

**To change the cadence:**
update the scheduled task's cron expression. `0 6 * * 0` = Sunday 06:00 local. Daily would be `0 6 * * *`. Minimum resolution is ~1 hour.

**To add a new output channel** (e.g., Slack digest, Notion sync, PDF export):
add a Step 4/5/6 to the scheduled task's prompt. The task already has the fresh MD and HTML in the workspace and the PAT in the environment — anything downstream just reads those.

**To change the commit target:**
the scheduled task's prompt hard-codes `TA-39/roadmap` and the `claude/roadmap-refresh-*` branch naming. Swap the repo name in the task's prompt if the target changes.

---

## Files in this repo

```
TA39-Roadmap.md      Auto-generated. Source of truth.
TA39-Roadmap.html    Auto-generated. Executive dashboard.
README.md            This file.
skills/              Snapshot of the two Cowork skills that produce the
                     roadmap. See skills/README.md for what's there and how
                     to evolve the pipeline. Kept here so a future maintainer
                     can understand — and reinstall — the production path
                     without spelunking through Cowork.
```

The PAT and the scheduled-task config still live outside this repo (the PAT for security, the task because it's a Cowork runtime concern). This repo is the publication surface AND a readable record of the pipeline — but Cowork is still where the weekly job actually runs.

---

## Operational notes

- **PR history = changelog.** Every weekly squash-merge is a dated commit on `main`. To see what changed between two Sundays, `git log --oneline` and `git diff` between the commits. The PR body for each merge carries the human-readable summary.
- **No CI.** The roadmap doesn't need tests — the skills self-validate against the board data. If either skill fails, the PR step is skipped and the failure surfaces in the task report.
- **Branch protection is off.** Intentionally, so the bot can merge cleanly. If you turn it on, either add a bypass rule for the PAT's identity or switch the automation to "open PR, notify human, do not merge."
- **Public hosting.** The repo is private. If you ever want the HTML dashboard publicly viewable, turn on GitHub Pages on `main` — the HTML is already self-contained (Tailwind via CDN, no build step).

---

## Related

- **Skills snapshot:** [`skills/`](./skills/) — unpacked source + packaged `.skill` bundles of `ta39-roadmap-md` and `ta39-roadmap-html`. Start there if you need to understand, modify, or reinstall the pipeline.
- **Scheduled task config:** `ta39-weekly-roadmap-refresh` in the Cowork Scheduled sidebar.
- **Upstream data:** [TA-39 Project #4](https://github.com/orgs/TA-39/projects/4).
