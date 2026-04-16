# Skills snapshot — the production pipeline

This folder is a **snapshot** of the two Cowork skills that produce `TA39-Roadmap.md` and `TA39-Roadmap.html`. It is here for documentation and reproducibility, not for runtime: the skills actually execute from the installed location inside a Cowork session (see the root `README.md` for the full pipeline).

Treat these files as **source code for the roadmap pipeline**. If you change anything here, you also need to update the live skill (or replace it with the packaged `.skill` bundle) — otherwise the weekly job keeps running the old version.

---

## What's in here

```
skills/
├── README.md                       This file.
├── ta39-roadmap-md.skill           Packaged bundle (zip) — reinstall in Cowork.
├── ta39-roadmap-html.skill         Packaged bundle (zip) — reinstall in Cowork.
├── ta39-roadmap-md/                Unpacked source of the MD skill.
│   ├── SKILL.md                    Instructions Claude follows each run.
│   ├── scripts/
│   │   └── fetch_board.py          GraphQL pull from Project #4 → JSON.
│   └── references/
│       ├── announcements.md        community.ta-39.com → issue mapping.
│       └── features_page.md        www.ta-39.com/en/features → issue mapping.
└── ta39-roadmap-html/              Unpacked source of the HTML skill.
    ├── SKILL.md
    └── scripts/
        └── render_html.py          Parses MD → renders dashboard HTML.
```

**The `.skill` bundle files** are zipped copies of the unpacked folders. They exist so a new Cowork session can install the skills in one click without having to reassemble the directory structure. If you edit the unpacked source, re-pack the `.skill` bundle so the two stay in sync.

---

## The `ta39-roadmap-md` skill

Pulls the GitHub Projects board and writes the analytical markdown roadmap.

**Trigger phrases** (from the skill description): "update TA39 roadmap", "refresh the roadmap", "regenerate roadmap md", "pull the latest roadmap from GitHub", "update the product roadmap markdown", "refresh TA39 roadmap data".

**Key design decisions baked in:**

- **The script is deterministic; the MD prose is not.** `fetch_board.py` always emits the same JSON for the same board state. The MD on top of that JSON is re-authored every run — risks sharpen, strategic call-outs shift, new items land. If you want identical output run-over-run, you're using the wrong tool.
- **14-section structure is a contract.** The HTML skill parses against these exact headers. Adding or renaming a section breaks the renderer. Changing content *within* a section is a prompt edit only.
- **Competitive Parity is a cross-cutting lens.** Items with a topical home (e.g., Monetization) keep that home and get a ⚔️ overlay. Pure parity items (like Plagiarism Detection) become their own theme. This is surfaced in both the LATER themes section and a dedicated strategic call-out.
- **Author rule: `Type=Feature` is reserved for `adnanwarsi`.** The skill flags violations so they get consciously promoted or downgraded. Do not silence this check — it's what keeps the roadmap from drifting into "every issue is a feature."
- **No fabrication.** `[ANNOUNCED]` tags come only from `references/announcements.md`. `[FEATURED]` comes only from `references/features_page.md` AND being released. The skill will not invent announcements that don't exist.

**The reference files are the human-maintained inputs:**

- `references/announcements.md` — every time a community.ta-39.com post ships for a roadmap item, add a line. Without this, the MD doesn't know to tag it `[ANNOUNCED]`.
- `references/features_page.md` — every time the marketing features page (www.ta-39.com/en/features) adds or removes a claim, update this. The "Marketing-vs-Ship Gap" table is meaningless without it.

Both files are plain markdown tables. Keep them tidy.

---

## The `ta39-roadmap-html` skill

Renders the MD into an executive dashboard.

**Trigger phrases:** "generate TA39 roadmap HTML", "regenerate roadmap dashboard", "rebuild the HTML", and — importantly — automatic handoff from the MD skill when the user says "update TA39 roadmap" with no qualifier.

**Key design decisions baked in:**

- **Self-contained HTML.** Tailwind via CDN, inline CSS vars for the theme palette, no external JS beyond the CDN. The file is meant to be opened directly or hosted on GitHub Pages without a build step.
- **Theme portfolio matrix.** The Now / Next / Later columns per theme are the dashboard's headline view. Themes come from the MD's LATER section headers plus any theme the renderer infers for NOW/NEXT items that don't have an explicit LATER row.
- **Parsing against section headers.** `render_html.py` uses regex on the 14 section headers. Keep them exact. If the MD skill changes a section title, change the regex here in the same commit.
- **No data fetching.** This skill is pure MD → HTML. It never talks to GitHub. That separation is intentional: if GitHub is unreachable, you can still re-render the dashboard from the last known MD.

---

## How to change the pipeline

**Small content tweak** (new risk, new strategic call-out, reword a section):
1. Edit `ta39-roadmap-md/SKILL.md` in this folder.
2. Copy the edit into the installed skill: `mnt/.claude/skills/ta39-roadmap-md/SKILL.md`.
3. Re-pack the `.skill` bundle (optional but recommended so fresh Cowork sessions get the new version).
4. Commit the change to this repo in the same PR.

**Renderer tweak** (new card element, new color, new theme handling):
1. Edit `ta39-roadmap-html/scripts/render_html.py` in this folder.
2. Copy into the installed skill: `mnt/.claude/skills/ta39-roadmap-html/scripts/render_html.py`.
3. Run the weekly task manually ("Run now") to verify the new render before Sunday.
4. Commit.

**New reference mapping** (new announcement, new features-page claim):
1. Add a line to the relevant `references/*.md`.
2. Copy to the installed skill.
3. Commit. The next weekly run will pick it up automatically.

**New section in the MD** (structural change):
1. Edit `ta39-roadmap-md/SKILL.md` to define the new section and its place in the 14-section ordering.
2. Edit `ta39-roadmap-html/scripts/render_html.py` to parse the new section and render it.
3. Both skills must land together. Do not merge one without the other.
4. Manually run the weekly task to verify.
5. Commit both skill changes + the regenerated MD + HTML.

---

## How to reinstall the skills in a fresh Cowork session

If someone new picks up this repo and needs to run the pipeline on their own machine:

1. Open Cowork with the `Product Roadmap Braintstorm` workspace folder selected (or any folder — they can move the skills later).
2. Drop the two `.skill` files from this folder into the session; Cowork installs them.
3. Put a classic GitHub PAT with `repo` + `project` scopes at `<workspace>/.secrets/github_pat`.
4. Recreate the scheduled task (`ta39-weekly-roadmap-refresh`) with the prompt from the repo root `README.md`'s "How the weekly refresh works" section.
5. Click "Run now" once to pre-approve Bash, network, and file writes. After that it's hands-off.

---

## What this folder is *not*

- **Not where the skills execute.** The weekly job runs skills from the Cowork skills directory (`mnt/.claude/skills/`), not from this repo. Editing files here without syncing to the installed location does nothing.
- **Not a Python package.** These scripts are intentionally stdlib-only and run directly via `python3`. No `setup.py`, no `requirements.txt`, no virtualenv.
- **Not versioned separately.** The skill version is the commit SHA of this folder. If you need a rollback, `git revert` the relevant commit.
