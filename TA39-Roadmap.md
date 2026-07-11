# TA39 Product Roadmap

**Source of truth:** GitHub Projects board [TA-39 Product Development (#4)](https://github.com/orgs/TA-39/projects/4)
**Scope:** 25 in-scope `Type=Feature` items (author rule: `Type=Feature` is reserved for the product lead `adnanwarsi`; exceptions flagged).
**Retrieved:** 2026-07-11 (live GraphQL pull via `fetch_board.py`).
**Horizon:** Released inventory → Now (in build/QA) → Next (ready, unstarted) → Later (backlog, theme-organized).

Bucket counts this pull: **RELEASED 11 · NOW 1 · NEXT 5 · BLOCKED 0 · LATER 8** (3 archived, excluded).

> **Change since last pull (2026-07-10):** [#596 Arabic NLP Enablement](https://github.com/TA-39/frontend/issues/596) was **closed as "not planned / superseded"** and removed from the board. It was **not dropped** — the Arabic NLP capability is effectively delivered through graditron's grading-pipeline modernization: [graditron #96](https://github.com/TA-39/graditron/issues/96) ("Arabic Grading Quality Experiments: Fanar/GPT routing and Arabic flow comparison," closed 2026-07-09) under the open epic [graditron #123](https://github.com/TA-39/graditron/issues/123). The old frontend-centric epic (fixed B1→B2→B3 design) was retired because that routed architecture replaced it. Because graditron #96/#123 are not `Type=Feature` on board #4, this roadmap can no longer see the Arabic NLP work even though it's effectively done. It was the Arabic theme's only NOW item. See NOW, Risk 2, and Call-out (g).

---

## Public-surface tagging rules

Two tags mark work that **users have already been told about** — they signal exposure, not internal status.

- **`[ANNOUNCED]`** — the item has a dedicated post on community.ta-39.com (see Announcement Cross-Reference). Applies regardless of ship state.
- **`[FEATURED]`** — the item is **released** (`Testing in Production` or `In Production & Done`) **AND** named on [www.ta-39.com/en/features](https://www.ta-39.com/en/features). Pipeline items never carry `[FEATURED]` even when the features page names them — that is a commitment, not a claim.
- **`[SILENT]`** — released but neither announced nor on the features page. This is the hidden inventory (see Section 11).

---

## Kanban Status Glossary

The board's status names do not map to intuition. Read this before reading the tables — in particular, `Ready for Development` means **unstarted**, and `Testing in Production` / `In Production & Done` mean **released**.

| Status | Meaning | Position in flow | Bucket |
|---|---|---|---|
| Backlog | Parked; not scheduled | Pre-flow | LATER |
| Blocked / Information Needed | Stalled awaiting a decision or input | Pre-flow | BLOCKED |
| Ready for Development | Groomed but **not started** | Start of flow | NEXT |
| In progress | Actively being built | Mid-flow | NOW |
| Development Complete | Code done, pre-QA | Mid-flow | NOW |
| Ready for Testing (Staging) | Queued for staging QA | Mid-flow | NOW |
| Testing in Staging | In staging QA | Mid-flow | NOW |
| Testing Pre-Production | Pre-prod validation | Late-flow | NOW |
| Testing Result Discussion | Reviewing QA outcomes | Late-flow | NOW |
| Testing in Production | **Released**, validating live | End of flow | RELEASED |
| In Production & Done | **Released**, closed | End of flow | RELEASED |
| Archive | Out of scope | — | ARCHIVED |

> **Reader trap:** stakeholders routinely misread `Ready for Development` as "about to ship." It is the opposite end of the pipeline from shipped. Every NEXT item below is a cold start.

---

## Status Overview

| Bucket | Count | What it contains |
|---|---|---|
| RELEASED | 11 | Live in production. |
| NOW | 1 | Active build/QA. |
| NEXT | 5 | Groomed, unstarted (`Ready for Development`). |
| BLOCKED | 0 | Nothing formally blocked this pull. |
| LATER | 8 | Backlog, organized by theme below. |
| **In-scope total** | **25** | (+3 archived, excluded.) |

### Theme portfolio scorecard

Each in-scope item carries exactly one theme (strongest topical home). ⚔️ = also carries the GitHub `Competitive Parity` label but sits under a topical theme.

| Theme | Released | Now | Next | Later | Total |
|---|---|---|---|---|---|
| Agentic / Copilot evolution | 3 | 0 | 1 | 1 | 5 |
| Teacher-in-the-loop intelligence | 1 | 0 | 1 | 3 | 5 |
| Quality & evaluation stack | 1 | 0 | 0 | 0 | 1 |
| Arabic / Multilingual | 2 | 0 | 1 | 0 | 3 |
| Integrations & LMS breadth | 1 | 0 | 1 | 2 | 4 |
| Monetization | 0 | 0 | 0 | 1 | 1 |
| Competitive Parity | 0 | 0 | 1 | 0 | 1 |
| Platform & UX | 3 | 1 | 0 | 1 | 5 |

### Velocity context

Released dates cluster in two waves. The **Copilot wave** (Apr–Aug 2025: #384, #385, #366, #378, #440, #532, #188) established the assistant surface and i18n plumbing. The **authoring/revision wave** (Mar–Apr 2026: #343, #344, #697) rebuilt rubric, template, and revision workflows. Most recent: **#166 Arabic Mode Summary Report closed today (2026-07-10)** — freshly promoted from build to RELEASED and not yet announced.

Throughput is real but lumpy — the pipeline is front-loaded with released Copilot/authoring work and now **critically thin in NOW (a single item)** after #596 left the board. The NEXT queue is heavy on L/XL cold starts, so near-term ship velocity depends entirely on when those get pulled into build. Note that real Arabic-NLP delivery is happening *off* this board (graditron #96/#123), so the board understates actual engineering activity.

---

## Marketing-vs-Ship Gap

One row per features-page claim. Reality sourced from the live board; risk rated per the reference rubric.

| Features-page claim | Anchor issue(s) & status | Reality | Risk |
|---|---|---|---|
| **Revision Rounds** | [#697](https://github.com/TA-39/frontend/issues/697) *In Production & Done*; follow-on [#740](https://github.com/TA-39/frontend/issues/740) *Ready for Development* | Core claim is **met** — revision cycles are live. #740 ("Learning Loop") is a pipelined enhancement, not a gap. | **Low** |
| **Handwritten Work Support** | [#99](https://github.com/TA-39/graditron/issues/99) Arabic HTR — *Ready for Development* (unstarted) | Arabic HTR is **not shipped**. Page may lean on earlier baseline OCR; if it implies Arabic handwriting today, it overstates. Needs a 5-minute audit with marketing. | **High** |
| **Canvas / Google Classroom breadth** | [#378](https://github.com/TA-39/frontend/issues/378) LTI *Done*; [#473](https://github.com/TA-39/frontend/issues/473) Canvas Discussions *Backlog*; [#226](https://github.com/TA-39/frontend/issues/226) GC re-use *Backlog* | **Partial.** Core Canvas LTI submission is live; Discussions-as-source and Google Classroom re-use are backlog. | **Medium** |
| **Optimize Rubrics With AI** | [#343](https://github.com/TA-39/frontend/issues/343) *In Production & Done* | Shipped. Met. | **Low** |
| **Feedback Templates** | [#344](https://github.com/TA-39/frontend/issues/344) *In Production & Done* | Shipped. Met. | **Low** |
| **Assignment Exemplars** | [#440](https://github.com/TA-39/frontend/issues/440) *In Production & Done* | Shipped. Met. | **Low** |
| **Teacher / Student / Context-Aware Copilot** | [#384](https://github.com/TA-39/frontend/issues/384), [#385](https://github.com/TA-39/frontend/issues/385), [#366](https://github.com/TA-39/frontend/issues/366) — all *Done* | Shipped. Met. Next evolution is agentic (#547, #649) — Later. | **Low** |

**Tag application note:** `[FEATURED]` is reserved for **released** items on the features page. Handwritten Work Support (#99) is on the page but unshipped — it carries no `[FEATURED]` tag and must not, because the page is making a commitment there, not a claim about live capability.

---

## Announcement Cross-Reference

Items with a dedicated community.ta-39.com post. `Announced` = post date. `Released` = production date (`closed_at` on the GitHub issue). These differ — we carry both.

| Issue | Title | Theme | Post | Announced | Released | Tags |
|---|---|---|---|---|---|---|
| [#697](https://github.com/TA-39/frontend/issues/697) | Revision-Aware Writing & Feedback Cycles | Teacher-in-the-loop intelligence | [Introducing Revision Rounds](https://community.ta-39.com/announcements/post/introducing-revision-rounds-making-student-revision-across-drafts-visible-jbYENcYH221JQqt) | 2026-04-14 | 2026-04-12 | `[ANNOUNCED]` `[FEATURED]` |
| [#343](https://github.com/TA-39/frontend/issues/343) | Rubric UI and setup experience overhaul | Platform & UX | [Optimize Rubrics With AI](https://community.ta-39.com/announcements/post/you-can-now-optimize-rubrics-with-ai-in-the-rubric-library-wUoDP62myFdyOId) | 2026-03-30 | 2026-03-25 | `[ANNOUNCED]` `[FEATURED]` |
| [#344](https://github.com/TA-39/frontend/issues/344) | Feedback Template creation (Simplify) | Platform & UX | [Build Feedback Templates More Easily](https://community.ta-39.com/announcements/post/you-can-now-build-feedback-templates-more-easily-in-ta39-toqLgjVRG53sHX8) | 2026-03-30 | 2026-03-29 | `[ANNOUNCED]` `[FEATURED]` |
| [#440](https://github.com/TA-39/frontend/issues/440) | Assignment Exemplars Support | Quality & evaluation stack | [Create Exemplars for Any Rubric](https://community.ta-39.com/announcements/post/you-can-now-create-exemplars-for-any-rubric----powered-by-ai-1S4jZwTapdze0XR) | 2025-05-15 | 2025-05-15 | `[ANNOUNCED]` `[FEATURED]` |
| [#384](https://github.com/TA-39/frontend/issues/384) | Teacher CoPilot | Agentic / Copilot evolution | [New TA39 Copilot](https://community.ta-39.com/announcements/post/new-ta39-copilot-transform-feedback-into-meaningful-conversations-t98LSruxg85pprV) | 2025-04-25 | 2025-04-23 | `[ANNOUNCED]` `[FEATURED]` |
| [#385](https://github.com/TA-39/frontend/issues/385) | Student CoPilot | Agentic / Copilot evolution | *same post as #384* | 2025-04-25 | 2025-04-24 | `[ANNOUNCED]` `[FEATURED]` |
| [#366](https://github.com/TA-39/frontend/issues/366) | Context-Aware Copilot Panels | Agentic / Copilot evolution | *same post as #384* | 2025-04-25 | 2025-08-23 | `[ANNOUNCED]` `[FEATURED]` |
| [#378](https://github.com/TA-39/frontend/issues/378) | Canvas Google Doc Submissions via LTI | Integrations & LMS breadth | [Google Docs Submission Support](https://community.ta-39.com/announcements/post/update-google-docs-submission-support-now-available-sHeucGoJSdE6sWM) | 2025-01-21 | 2025-05-03 | `[ANNOUNCED]` `[FEATURED]` |

> **Note on #366:** announced 2025-04-25 as part of the Copilot post but not closed in production until 2025-08-23 — a ~4-month announce-to-release gap. The other Copilot items (#384/#385) shipped within days of the post. Worth understanding why #366 lagged before we repeat the pattern.
>
> **Orphaned posts to resolve** (posts live, no in-scope `Type=Feature` issue): *Organizing Assignments: Folders in TA39*, *Rubric Converter Utility*, *Trusted Apps Pledge*. Either file issues or leave them off the roadmap deliberately. The Revision Rounds post also covered `#768 CR8`, which is archived (out of scope).

---

## RELEASED

Full released inventory (bucket = RELEASED). `[SILENT]` rows are the hidden inventory surfaced in Section 11.

| # | Title | Theme | Repo | Priority | Size | Status | Tags |
|---|---|---|---|---|---|---|---|
| [#166](https://github.com/TA-39/api/issues/166) | Arabic Mode Summary Report Generation (RTL + Arabic Template) | Arabic / Multilingual | api | High | M | In Production & Done | `[SILENT]` |
| [#188](https://github.com/TA-39/frontend/issues/188) | Update UI for New Class Analysis Report and Assignment Tabs | Platform & UX | frontend | High | S | In Production & Done | `[SILENT]` |
| [#343](https://github.com/TA-39/frontend/issues/343) | Rubric UI and setup experience overhaul | Platform & UX | frontend | High | L | In Production & Done | `[ANNOUNCED]` `[FEATURED]` |
| [#344](https://github.com/TA-39/frontend/issues/344) | Feedback Template creation (Simplify) | Platform & UX | frontend | High | L | In Production & Done | `[ANNOUNCED]` `[FEATURED]` |
| [#366](https://github.com/TA-39/frontend/issues/366) | Context-Aware Copilot Panels for Students and Teachers | Agentic / Copilot evolution | frontend | Critical | M | In Production & Done | `[ANNOUNCED]` `[FEATURED]` |
| [#378](https://github.com/TA-39/frontend/issues/378) | Canvas Google Doc Submissions via LTI | Integrations & LMS breadth | frontend | High | M | In Production & Done | `[ANNOUNCED]` `[FEATURED]` |
| [#384](https://github.com/TA-39/frontend/issues/384) | Teacher CoPilot | Agentic / Copilot evolution | frontend | High | — | In Production & Done | `[ANNOUNCED]` `[FEATURED]` |
| [#385](https://github.com/TA-39/frontend/issues/385) | Student CoPilot | Agentic / Copilot evolution | frontend | High | — | In Production & Done | `[ANNOUNCED]` `[FEATURED]` |
| [#440](https://github.com/TA-39/frontend/issues/440) | Assignment Exemplars Support — generate, use, fine-tune | Quality & evaluation stack | frontend | High | L | In Production & Done | `[ANNOUNCED]` `[FEATURED]` |
| [#532](https://github.com/TA-39/frontend/issues/532) | Internationalization — Multi-Language Support for Frontend UI | Arabic / Multilingual | frontend | High | L | In Production & Done | `[SILENT]` |
| [#697](https://github.com/TA-39/frontend/issues/697) | Revision-Aware Writing & Feedback Cycles (Teacher-Controlled Drafts) | Teacher-in-the-loop intelligence | frontend | High | L | In Production & Done | `[ANNOUNCED]` `[FEATURED]` |

**Shipped-but-NOT-announced (silent):** #166, #188, #532 — see Section 11 for retroactive-post recommendations.

---

## NOW

Active build or QA (bucket = NOW).

| Issue | Title | Theme | Status | Priority | Size | Repo | Tags |
|---|---|---|---|---|---|---|---|
| [#3](https://github.com/TA-39/website/issues/3) | TA39 Onboarding & Training | Platform & UX | In progress | High | XL | website | — |

**Ship-order read:** After #596 left the board, exactly **one** feature is in active build — [#3](https://github.com/TA-39/website/issues/3) Onboarding & Training, a High-priority XL still `In progress` (early-to-mid build), so not imminent. And #3 is adoption infrastructure, not product capability: the board currently shows **zero product-capability features in flight**. That's a real coverage gap against five groomed NEXT items waiting to be pulled.

**But the board understates reality.** The Arabic NLP engine — the strategic work #596 used to represent — is being delivered in graditron (#96 closed 2026-07-09, under the open modernization epic #123). Because those aren't `Type=Feature` on board #4, they don't appear in NOW. Real capability work is happening; this roadmap just can't see it. That's a tracking gap (Risk 2), not an idle-team gap.

**Left NOW since last pull:** [#596](https://github.com/TA-39/frontend/issues/596) closed as *not planned / superseded* (2026-07-11) — effectively delivered via graditron, not abandoned. [#166](https://github.com/TA-39/api/issues/166) (closed 2026-07-10) is now firmly RELEASED — live, and still silent (unannounced).

---

## NEXT

`Ready for Development` — **groomed but unstarted**. Q2 realism rates whether a cold start can plausibly ship this quarter given size/priority.

| Issue | Title | Theme | Priority | Size | Tags | Q2 realism |
|---|---|---|---|---|---|---|
| [#547](https://github.com/TA-39/frontend/issues/547) | Evolve TA39 Into an Agentic Instruction Platform | Agentic / Copilot evolution | High | XL | — | **Defer** — XL cold start; won't ship in ~6 weeks. Strategic, needs a real slot. |
| [#99](https://github.com/TA-39/graditron/issues/99) | Arabic Handwriting Recognition (HTR) Capability | Arabic / Multilingual | Medium | XL | Sanctioned OCR program | **Defer to Q3** — XL cold start. This *is* the "new product/technical program" #596's closing note said Arabic OCR would require: OCR was intentionally left unsupported under the routed NLP architecture, and #99 is the deliberate successor effort. Legitimately scoped — just size-and-sequence it as the new program it is. |
| [#327](https://github.com/TA-39/frontend/issues/327) | Plagiarism Detection Integration | Competitive Parity | Medium | L | `` `Competitive Parity` label `` (parity play) | **Defer** — L cold start; parity, not differentiation. Schedule deliberately. |
| [#701](https://github.com/TA-39/frontend/issues/701) | Microsoft Teams LMS Integration | Integrations & LMS breadth | Medium | L | — | **Defer to Q3** — L; enterprise reach but not this quarter from cold. |
| [#740](https://github.com/TA-39/frontend/issues/740) | Evolve Draft Revision Rounds into a "Learning Loop" System | Teacher-in-the-loop intelligence | Medium | L | Builds on shipped #697 | **Must-start candidate** — L, but rides live #697 foundation; best odds of a Q2 ship if picked first. |

**Realism note:** every NEXT item is L or XL. From a cold start, none of the XLs (#547, #99) ships in a ~6-week window, and the Ls (#327, #701, #740) ship only if pulled immediately and staffed. #740 is the highest-leverage near-term pick — it extends a released feature rather than starting greenfield. If Q2 needs a visible win, start #740.

---

## LATER

Backlog, organized by theme. Only themes with LATER items appear here; the rest are in the scorecard above. ⚔️ = also carries the GitHub `Competitive Parity` label.

### Theme 1 — Agentic / Copilot evolution

| Issue | Title | Priority | Size |
|---|---|---|---|
| [#649](https://github.com/TA-39/frontend/issues/649) | TA39 Copilot — Conversational, Agentic Interface Embedded in Core UI | High | XL |

The agentic north star. Correctly parked in Later — it's an XL that depends on the released Copilot surface maturing and on #547 (the agentic-platform groundwork in NEXT) landing first. High priority signals intent; the sequencing (#547 → #649) is right.

### Theme 2 — Teacher-in-the-loop intelligence

| Issue | Title | Priority | Size | |
|---|---|---|---|---|
| [#331](https://github.com/TA-39/frontend/issues/331) | Teacher-Led Calibration for AI Feedback (Delta-Based Template Refinement) | High | L | |
| [#328](https://github.com/TA-39/frontend/issues/328) | Student-Teacher Interaction on Feedback & AI Score Disputes (Human-in-the-Loop) | Medium | — | ⚔️ |
| [#113](https://github.com/TA-39/frontend/issues/113) | Iterative Feedback during Writing Process — Socratic Style | Medium | XL | ⚔️ |

This is the deepest Later theme and the most strategically coherent — teacher control is TA39's core promise. #331 (High) is the standout: teacher-led calibration is the mechanism that makes "you review, adapt, and decide" real, and it's unprioritized-into-backlog rather than pulled forward. #113 is XL **and** authored by `duhajar`, not the product lead — see author-rule flag in Risks.

*⚔️ = also carries the GitHub `Competitive Parity` label.*

### Theme 3 — Integrations & LMS breadth

| Issue | Title | Priority | Size |
|---|---|---|---|
| [#473](https://github.com/TA-39/frontend/issues/473) | Support Canvas Discussions as Source for TA39 Feedback Generation | Medium | — |
| [#226](https://github.com/TA-39/frontend/issues/226) | User Requirement — support for re-use in Google Classroom | Low | — |

Both back the "Canvas / Google Classroom breadth" features-page claim (Section 5). #226 is **Low** priority yet Google Classroom is marketed as first-class — mis-alignment called out in Strategic Call-outs (d). Neither is sized.

### Theme 4 — Monetization

| Issue | Title | Priority | Size | |
|---|---|---|---|---|
| [#374](https://github.com/TA-39/frontend/issues/374) | Individual Paid User — Stripe Subscription & Feature Access Control | Low | — | ⚔️ |

The **only** monetization item on the entire board, and it's Low/Backlog/unsized. If individual-user revenue matters in 2026, this is mis-prioritized. See Call-out (b).

*⚔️ = also carries the GitHub `Competitive Parity` label.*

### Theme 5 — Platform & UX

| Issue | Title | Priority | Size |
|---|---|---|---|
| [#474](https://github.com/TA-39/frontend/issues/474) | Voice-Based Assignment Support: Audio Transcription, Language Detection, Feedback | Medium | — |

Parked under Platform for lack of a cleaner home, but #474 is really a **new submission modality** (audio), not UX polish — closer in ambition to Arabic HTR (#99) than to a design refresh. If voice submissions become a market ask, it deserves a topical theme and a size. Unsized today.

---

## Shipped but NOT publicly announced

The hidden inventory — released, but no community post and not on the features page (`[SILENT]` in RELEASED). This is pitch ammunition sitting unused.

| Issue | Title | Theme | Repo | Released | Status |
|---|---|---|---|---|---|
| [#166](https://github.com/TA-39/api/issues/166) | Arabic Mode Summary Report Generation (RTL + Arabic Template) | Arabic / Multilingual | api | 2026-07-10 | In Production & Done |
| [#532](https://github.com/TA-39/frontend/issues/532) | Internationalization — Multi-Language Support for Frontend UI | Arabic / Multilingual | frontend | 2025-08-03 | In Production & Done |
| [#188](https://github.com/TA-39/frontend/issues/188) | Update UI for New Class Analysis Report and Assignment Tabs | Platform & UX | frontend | 2025-02-02 | In Production & Done |

**Recommended retroactive posts (top 3 — and there are exactly 3):**

1. **#166 Arabic Mode Summary Report** — shipped *today*, and it's the visible payoff of the MENA/GCC bet: full Arabic RTL summary reports. Strongest story, freshest, zero coverage. Announce it.
2. **#532 Internationalization** — the multilingual foundation that makes #166 and the whole Arabic push possible. A "TA39 now speaks your language" post frames the market position. Nearly a year live and silent.
3. **#188 Class Analysis Report & Assignment Tabs UI** — less strategic, but a concrete usability win teachers would recognize. Lightweight post.

Two of the three silent items are Arabic/Multilingual — the exact theme we're betting the market on, and the exact theme with zero announcements. That's the biggest self-inflicted comms gap on the board.

---

## Risks & Dependencies

1. **Public surface vs. shipped product (the marketing gap).** "Handwritten Work Support" is on the features page, but Arabic HTR (#99) is `Ready for Development` (unstarted). If prospects read that as live Arabic handwriting capability, we're overstating. **High** risk — audit with marketing this week and either soften the page or pull #99 forward.
2. **The Arabic NLP engine is delivered but invisible to this roadmap.** The strategic Arabic NLP work moved from feature-epic #596 (now closed/superseded) to graditron's grading-pipeline modernization ([#96](https://github.com/TA-39/graditron/issues/96), closed 2026-07-09, under open epic [#123](https://github.com/TA-39/graditron/issues/123)). That's good — it shipped. But because those aren't `Type=Feature` on board #4, the roadmap can't see the single most strategic capability the company is building; when #596 left the board, the Arabic theme's NOW column went to zero even though Arabic engineering did not stop. (For the record, [#99 Arabic HTR](https://github.com/TA-39/graditron/issues/99) in NEXT is *not* a contradiction with #596's "Arabic OCR intentionally unsupported" note — #99 is precisely the new OCR program that note said would be required. It's coherent, not stale.) The real risk is visibility: elevate the graditron Arabic work onto board #4 so leadership isn't reading a board that understates the company's biggest bet.
3. **Cross-repo dependency concentration.** Arabic capability now spans `graditron` (NLP routing #96/#123, HTR #99), `api` (#166 summary reports, shipped), and `frontend` (i18n #532, shipped). Coordination cost is real and there's no single owning repo or feature-board epic that captures the whole Arabic program — assign one owner with visibility across all three, and get the live graditron work represented on board #4 so leadership can see it.
4. **Teacher-in-the-loop is deep in backlog while it's the core promise.** The theme with the most Later items (#331, #328, #113) includes the mechanism (#331 calibration, High) that makes "you review and decide" literally true. It's unprioritized into backlog rather than staged. Strategic under-investment risk.
5. **Iteration/Sprint field is 100% unpopulated** — 26 of 26 items have no Iteration value. The board can't express *when* anything lands, only *which bucket*. Any date-based commitment is currently guesswork. Populate Iteration on at least all NOW and NEXT items.
6. **Author-rule violation.** [#113](https://github.com/TA-39/frontend/issues/113) is `Type=Feature` but authored by `duhajar`, not the product lead `adnanwarsi`. Either the lead consciously elevated it (then re-assign/confirm) or it's mis-typed and should be a task. Resolve so `Type=Feature` stays a trustworthy signal.
7. **NOW pipeline is down to a single item — and it's not product capability.** Only [#3](https://github.com/TA-39/website/issues/3) (Onboarding & Training) is in active build on the board, against five groomed NEXT items. Zero product-capability features are in flight per the board. If #3 stalls, board-visible shipping velocity is zero. (Real graditron work continues off-board — Risk 2 — but that doesn't help the roadmap-visible pipeline leadership reviews.)

---

## Strategic Call-outs

**(a) Agentic is the right "Later" bet.** #547 (NEXT) → #649 (Later) sequences the agentic evolution correctly on top of a released, proven Copilot surface (#384/#385/#366). Don't rush #649 ahead of #547; don't let it drift indefinitely either — it's the differentiation story for 2026.

**(b) Monetization is underweighted.** [#374](https://github.com/TA-39/frontend/issues/374) is the *only* monetization item on the board — Low priority, Backlog, unsized. If individual-user revenue matters in 2026, this is mis-prioritized; size it and lift it. If it doesn't, archive it and stop carrying the noise. Either way, "one Low-priority Stripe ticket" is not a monetization strategy.

**(c) Quality & evaluation stack is nearly invisible.** Only one item maps to this theme (#440 Exemplars, released) and there is **no** Eval Harness / Sentinel / scoring-confidence work anywhere in NOW/NEXT/LATER. For a product whose value is feedback quality, having no live evaluation-infrastructure investment on the roadmap is a gap. If eval work exists off-board, get it on-board.

**(d) Google Classroom re-use is Low/Backlog but marketed as first-class.** [#226](https://github.com/TA-39/frontend/issues/226) is Low priority and unsized, yet "Canvas / Google Classroom breadth" is a headline features-page claim. Align priority with the public promise, or adjust the promise.

**(e) Hidden inventory = pitch ammunition.** Three released features (#166, #532, #188) have zero public coverage — and two of them are the Arabic/Multilingual work we're betting the market on. Announcing #166 and #532 costs a day of writing and directly reinforces the MENA positioning. Highest-ROI comms move available.

**(f) Competitive Parity is a distinct lens.** Four items carry the `Competitive Parity` label:
- **Pure parity play (own theme):** [#327](https://github.com/TA-39/frontend/issues/327) Plagiarism Detection (NEXT) — no topical home; exists to match competitors.
- **Topical items with a parity overlay (⚔️):** [#328](https://github.com/TA-39/frontend/issues/328) Score Disputes / HITL (Teacher-in-loop), [#113](https://github.com/TA-39/frontend/issues/113) Socratic iterative feedback (Teacher-in-loop), [#374](https://github.com/TA-39/frontend/issues/374) Stripe subscriptions (Monetization).

Portfolio question for leadership: three of the four parity items sit in backlog. Under-investing in parity loses enterprise RFPs (plagiarism detection is table stakes in procurement); over-investing burns capacity we need for differentiation (agentic, teacher-in-the-loop, Arabic). Decide the parity budget explicitly rather than letting it default to "backlog forever."

**(g) The roadmap has an Arabic-shaped blind spot.** The most strategic capability the company is building — the Arabic NLP engine — is *effectively delivered* (graditron [#96](https://github.com/TA-39/graditron/issues/96), closed 2026-07-09, under open epic [#123](https://github.com/TA-39/graditron/issues/123)), yet it's invisible on board #4 because the work lives in non-`Type=Feature` graditron issues. When #596 closed this week, the Arabic theme's NOW column went to zero even though Arabic engineering did not stop. This is a governance problem, not a delivery problem: leadership reviewing this board would conclude Arabic investment paused, which is the opposite of what happened. Fix by elevating a roadmap-level `Type=Feature` epic that represents the graditron Arabic program, so the board reflects reality. Until then, read the Arabic theme's board numbers with this footnote attached.

---

## Changes vs. the board today

Concrete actions to reconcile the board with reality:

1. **Elevate a `Type=Feature` epic for the graditron Arabic NLP program** (represents #96/#123) so board #4 stops hiding the company's most strategic capability (Risk 2, Call-out g).
2. **Size and sequence [#99](https://github.com/TA-39/graditron/issues/99) as the sanctioned Arabic-OCR program.** It's the deliberate successor #596's ledger called for — give it an explicit program scope and a target horizon rather than leaving an XL sitting undated in NEXT.
3. **Re-type or confirm #113** — resolve the `duhajar` author-rule violation (elevate deliberately or convert to a task).
2. **Populate Iteration on all NOW + NEXT items** (7 items) so the board can express timing, not just bucket.
3. **Set a Size on unsized items** — #384, #385 (released, retroactive), and backlog items #328, #374, #473, #226, #474 all lack Size, blocking any capacity planning.
4. **Re-prioritize #226** (Google Classroom) up from Low, or soften the features-page claim — pick one.
5. **Re-prioritize / size #374** (Monetization) per Call-out (b), or archive it.
6. **Audit "Handwritten Work Support" claim** against #99's unstarted status with marketing (Risk 1).
7. **File issues (or explicitly drop)** the three orphaned announcement posts: Folders, Rubric Converter, Trusted Apps Pledge.
8. **Draft retroactive announcements** for #166 and #532 (Call-out e / Section 11).
9. **Assign a cross-repo owner** for the Arabic program spanning graditron (#96/#123/#99), api (#166), and frontend (#532) (Risk 3).

---

## Appendix — Feature Blurbs

One-sentence, plain-English explanation per feature (what users get).

| # | Blurb |
|---|---|
| 3 | Guided onboarding and training so new teachers reach productive use of TA39 quickly. |
| 99 | Handwritten-Arabic OCR so scanned Arabic work flows through the same feedback loop as typed submissions. |
| 113 | Socratic, in-the-moment prompts that guide students while they write instead of only after. |
| 166 | Full Arabic, right-to-left summary reports generated from an Arabic-native template. |
| 188 | Refreshed UI for the class analysis report and assignment tabs, easier to scan and navigate. |
| 226 | Reuse existing TA39 assignments and setup inside Google Classroom without rebuilding them. |
| 327 | Built-in plagiarism checking on submissions, surfaced alongside feedback. |
| 328 | A structured way for students to raise disputes and for teachers to override AI scores. |
| 331 | Teachers calibrate the AI by editing sample feedback; the system learns the delta and matches their style. |
| 343 | Rebuilt rubric creation and setup, with AI help to optimize rubrics in the library. |
| 344 | A simpler flow for building reusable feedback templates. |
| 366 | Context-aware Copilot panels that turn feedback into a two-way dialogue for students and teachers. |
| 374 | Individual paid subscriptions via Stripe, with feature access tied to entitlement. |
| 378 | Accept Google Doc submissions through Canvas via LTI, no manual export needed. |
| 384 | A teacher-side Copilot that turns feedback into guided conversations. |
| 385 | A student-side Copilot that helps students understand and act on their feedback. |
| 440 | Generate, apply, and fine-tune exemplar answers for any rubric to ground AI feedback. |
| 473 | Use Canvas Discussions posts as a source for TA39 feedback generation. |
| 474 | Accept audio assignment submissions with transcription, language detection, and spoken-work feedback. |
| 532 | A fully translatable frontend UI, the foundation for delivering TA39 in multiple languages. |
| 547 | Evolve TA39 from a feedback generator into an agentic assistant that acts on the teacher's behalf. |
| 649 | A conversational, agentic Copilot embedded directly in the core UI. |
| 697 | Teacher-controlled draft rounds that make student revision across drafts visible and reviewable. |
| 701 | Microsoft Teams integration so Teams-based classes can use TA39 in their LMS. |
| 740 | Extends revision rounds into a learning-loop system that tracks growth across drafts over time. |

---

## Follow-ups I can generate on request

- **Executive one-pager** — the board distilled to bets, gaps, and the three decisions leadership must make (monetization, parity budget, Arabic ownership).
- **Q2/Q3 sprint plan** — sequenced from NEXT (#740 first) with Iteration assignments filled in.
- **Competitive frame** — map the four parity items against named competitors and RFP checklists.
- **Comms plan** — drafts for the retroactive announcements (#166, #532) and the #366 announce-to-release retrospective.
- **Refreshed xlsx tracker** — the full board as a filterable spreadsheet with theme, bucket, size, and Iteration columns.
- **Marketing-page reconciliation** — a redline of www.ta-39.com/en/features against shipped reality (fixes the Handwritten Work Support overstatement).
