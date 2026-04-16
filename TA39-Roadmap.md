# TA39 Product Roadmap

**Source:** GitHub Projects board `TA-39 / Product Development` (project #4), live pull via GraphQL.
**Scope:** 36 in-scope `Type=Feature` issues (2 archived excluded). Author rule: `Type=Feature` reserved for the product lead (`adnanwarsi`); exceptions are flagged.
**Retrieved:** 2026-04-16
**Horizon:** Now (active) → Next (Q2 2026) → Later (2H 2026 and beyond)

This is the source of truth. It carries the analytical lens leadership uses to read the board — not a dump of the issues. Where the board is ambiguous (missing priority, missing size, stale status), the gap is called out explicitly.

---

## Public-surface tagging rules

Two public surfaces are tracked: the community announcements feed (community.ta-39.com) and the marketing features page (www.ta-39.com/en/features). They produce two tags used throughout this document:

- **`[ANNOUNCED]`** — a dedicated community.ta-39.com post exists for the item.
- **`[FEATURED]`** — the item is released (`Testing in Production` OR `In Production & Done`) **AND** named on the features page. Pipeline items never carry `[FEATURED]`, even if they appear on the features page — that is a commitment, not a claim.

Together these tags signal *things users have already been told about*. They dictate which regressions are customer-visible and which releases deserve a retroactive post.

---

## Kanban Status Glossary

Reader confusion is concentrated here — `Ready for Development` sounds imminent but is an unstarted state, and `Testing in Production` sounds risky but means released. Internalize this table before reading the bucket sections.

| Status | Meaning | Position in flow | Bucket |
|---|---|---|---|
| Backlog | Filed, triaged, not yet pulled forward | 0 — idea / later work | LATER |
| Blocked / Information Needed | Cannot progress — missing dep, spec, decision | 0 — stalled | LATER (held) |
| Ready for Development | Spec is ready. No code yet. | 1 — unstarted, queued | NEXT |
| In progress | Actively being built | 2 — active | NOW |
| Ready for Testing (Staging) | Dev complete, in staging / QA | 3 — active QA | NOW |
| Testing in Production | Released to production under observation | 4 — released | RELEASED |
| In Production & Done | Released, validated, closed | 5 — released, stable | RELEASED |
| Archive | Out of scope for roadmap | — | excluded |

Anything past Ready-for-Development is "in flight." Anything at or before is "not yet started."

---

## Status Overview

| Bucket | Count | Meaning |
|---|---|---|
| RELEASED | 13 | In production or released-under-observation |
| NOW | 3 | Active build or QA |
| NEXT | 4 | Ready-for-Development — specs complete, unstarted |
| BLOCKED | 0 | (Blocked items are folded into LATER as "held") |
| LATER | 16 | Backlog + held (Blocked/Information Needed) |
| ARCHIVED | 2 | Excluded from all lists |
| **In-scope total** | **36** | |

**Velocity context.** 13 released features against 16 LATER items and 4 NEXT items is a reasonable shipped-to-pipeline ratio for a team this size. The concentration of shipped work in frontend (11 of 13) reflects that the team can move frontend inventory quickly; graditron and Sentinel move slower, and the evaluation-harness LATER pile shows it. The realistic Q2 ship list from NOW+NEXT is 3–4 items — #596 Arabic NLP is an XL epic that will bleed into Q3, and #99 HTR is another XL that won't start-and-ship in six weeks.

---

## Marketing-vs-Ship Gap

The www.ta-39.com/en/features page makes seven named claims. Five are met, one is partial, one is ambiguous and needs a marketing audit.

| Features-page claim | Anchor issue(s) | Current reality | Risk |
|---|---|---|---|
| Revision Rounds | [#697](https://github.com/TA-39/frontend/issues/697) core; [#740](https://github.com/TA-39/frontend/issues/740) learning-loop follow-on | #697 is **Testing in Production** — released under observation. Claim met. #740 is Ready-for-Dev. | Low |
| Handwritten Work Support | [#99](https://github.com/TA-39/graditron/issues/99) Arabic HTR | Ambiguous. #99 is Ready-for-Development (unstarted). Page may be describing pre-existing baseline OCR or overstating. Needs a 5-min audit with marketing. | Medium |
| Canvas / Google Classroom breadth | [#378](https://github.com/TA-39/frontend/issues/378) LTI shipped; [#473](https://github.com/TA-39/frontend/issues/473) Canvas Discussions Backlog; [#226](https://github.com/TA-39/frontend/issues/226) GC re-use Backlog | Partial. Core LTI submission shipped. Canvas Discussions and Google Classroom re-use both sit in Backlog — GC re-use is Low priority. | Medium |
| Optimize Rubrics With AI | [#343](https://github.com/TA-39/frontend/issues/343) | Shipped (In Production & Done). Met. | Low |
| Feedback Templates | [#344](https://github.com/TA-39/frontend/issues/344) | Shipped. Met. | Low |
| Assignment Exemplars | [#440](https://github.com/TA-39/frontend/issues/440) | Shipped. Met. | Low |
| Teacher / Student / Context-Aware Copilot | [#384](https://github.com/TA-39/frontend/issues/384), [#385](https://github.com/TA-39/frontend/issues/385), [#366](https://github.com/TA-39/frontend/issues/366) | Shipped. Met. Agentic evolution ([#547](https://github.com/TA-39/frontend/issues/547), [#649](https://github.com/TA-39/frontend/issues/649)) sits in Later. | Low |

**Tag application note.** `[FEATURED]` is reserved for released items named on the features page. Pipeline items that appear on the page — explicitly or implicitly — do not get the tag; they are commitments, not claims.

---

## Announcement Cross-Reference

Items with a dedicated community.ta-39.com post. `[ANNOUNCED]` is applied where a post exists; `[FEATURED]` is added only for released items also on the features page.

| Issue | Title | Theme | Post | Date | Tags |
|---|---|---|---|---|---|
| [#697](https://github.com/TA-39/frontend/issues/697) | Revision-Aware Writing & Feedback Cycles | Teacher-in-the-loop intelligence | [Introducing Revision Rounds](https://community.ta-39.com/announcements/post/introducing-revision-rounds-making-student-revision-across-drafts-visible-jbYENcYH221JQqt) | 2026-04-14 | `[ANNOUNCED][FEATURED]` |
| [#343](https://github.com/TA-39/frontend/issues/343) | Rubric UI and setup experience overhaul | Teacher-in-the-loop intelligence | [Optimize Rubrics With AI](https://community.ta-39.com/announcements/post/you-can-now-optimize-rubrics-with-ai-in-the-rubric-library-wUoDP62myFdyOId) | 2026-03-30 | `[ANNOUNCED][FEATURED]` |
| [#344](https://github.com/TA-39/frontend/issues/344) | Feedback Template creation (Simplify) | Teacher-in-the-loop intelligence | [Build Feedback Templates More Easily](https://community.ta-39.com/announcements/post/you-can-now-build-feedback-templates-more-easily-in-ta39-toqLgjVRG53sHX8) | 2026-03-30 | `[ANNOUNCED][FEATURED]` |
| [#440](https://github.com/TA-39/frontend/issues/440) | Assignment Exemplars Support | Teacher-in-the-loop intelligence | [Create Exemplars for Any Rubric](https://community.ta-39.com/announcements/post/you-can-now-create-exemplars-for-any-rubric----powered-by-ai-1S4jZwTapdze0XR) | 2025-05-15 | `[ANNOUNCED][FEATURED]` |
| [#384](https://github.com/TA-39/frontend/issues/384) | Teacher CoPilot | Agentic / Copilot evolution | [New TA39 Copilot](https://community.ta-39.com/announcements/post/new-ta39-copilot-transform-feedback-into-meaningful-conversations-t98LSruxg85pprV) | 2025-04-25 | `[ANNOUNCED][FEATURED]` |
| [#385](https://github.com/TA-39/frontend/issues/385) | Student CoPilot | Agentic / Copilot evolution | *same post as #384* | 2025-04-25 | `[ANNOUNCED][FEATURED]` |
| [#366](https://github.com/TA-39/frontend/issues/366) | Context-Aware Copilot Panels | Agentic / Copilot evolution | *same post as #384* | 2025-04-25 | `[ANNOUNCED][FEATURED]` |
| [#378](https://github.com/TA-39/frontend/issues/378) | Canvas Google Doc Submissions via LTI | Integrations & LMS breadth | [Google Docs Submission Support](https://community.ta-39.com/announcements/post/update-google-docs-submission-support-now-available-sHeucGoJSdE6sWM) | 2025-01-21 | `[ANNOUNCED][FEATURED]` |

**Orphaned announcement posts** (exist on community.ta-39.com but no mapped `Type=Feature` issue):

- [Organizing Assignments: Folders in TA39](https://community.ta-39.com/announcements/post/organizing-assignments-folders-in-ta39-5d8F8faYPAXjAQv)
- Rubric Converter Utility post
- Trusted Apps Pledge post

Either file the backing issue or keep them off the roadmap accounting. The Revision Rounds post also covered `#768 CR8`, which is in Archive and therefore excluded from this document.

---

## NOW — active build or QA (3)

| Issue | Title | Theme | Status | Priority | Size | Repo | Tags |
|---|---|---|---|---|---|---|---|
| [#6](https://github.com/TA-39/Sentinel/issues/6) | Sentinel — Baseline Evaluation Setup | Quality & evaluation stack | Ready for Testing (Staging) | High | M | Sentinel | — |
| [#166](https://github.com/TA-39/api/issues/166) | Arabic Mode Summary Report Generation (RTL + Arabic Template) | Arabic / Multilingual | In progress | High | S | api | — |
| [#596](https://github.com/TA-39/frontend/issues/596) | [Stream 3][Epic] Arabic NLP Enablement for TA39 Feedback Platform | Arabic / Multilingual | In progress | High | XL | frontend | — |

**Ship-order read.** Near-term ship order is #6 → #166 → #596. #6 is already in staging and is the quickest to flip to released. #166 is an S in active build — days of work, not weeks, assuming the Arabic template is stable. #596 is an XL epic and is the real Q2–Q3 story: it is the enabling platform for the Arabic market, and it will not flip on one date; expect incremental releases under observation.

**Recently promoted NOW → RELEASED.** [#697 Revision-Aware Writing & Feedback Cycles](https://github.com/TA-39/frontend/issues/697) is now `Testing in Production` — released under observation, aligned with the April 14 community announcement. Treat this as the most recent marquee ship.

---

## NEXT — Ready for Development (4)

These have specs but no code. All are sized or should be. The Q2-realism column is an honest call, not a target.

| Issue | Title | Theme | Priority | Size | Tags | Q2 realism |
|---|---|---|---|---|---|---|
| [#99](https://github.com/TA-39/graditron/issues/99) | Arabic Handwriting Recognition (HTR) Capability | Arabic / Multilingual | High | XL | — | Defer to Q3. XL from a cold start will not ship in 6 weeks; stitches into #596 Arabic NLP stack. |
| [#327](https://github.com/TA-39/frontend/issues/327) | Plagiarism Detection Integration | Competitive Parity | Medium | L | ⚔️ `Competitive Parity` label | Must-start if parity is an active enterprise blocker; otherwise Defer to Q3. L from a cold start = ~Q3 ship. |
| [#701](https://github.com/TA-39/frontend/issues/701) | Microsoft Teams LMS Integration | Integrations & LMS breadth | High | L | — | Must-start. High priority + Teams is a real enterprise LMS wedge. Plan a phased ship — LTI parity first. |
| [#740](https://github.com/TA-39/frontend/issues/740) | Evolve Draft Revision Rounds into a "Learning Loop" System | Teacher-in-the-loop intelligence | High | L | — | Must-start. Rides the #697 launch momentum and converts released capability into sticky behavior. |

**L/XL realism.** L from a cold start lands late Q2 / early Q3. XL from a cold start lands mid–late Q3. The pipeline should not be read as "4 ships in Q2." The credible Q2 ship list is: finish #596 first-slice, complete #166, release #6 from staging, plus 1–2 L items from NEXT (#701 and #740 are the most plausible).

---

## LATER — by theme (16)

Organized by the five themes the team plans against. `Competitive Parity` is treated as a cross-cutting lens (Section 12, strategic call-out f). Items that are pure parity plays with no topical home sit in their own theme; items with a topical home keep it and get a ⚔️ overlay.

### Theme 1 — Agentic / Copilot evolution (3)

The bet the company is making about what the product becomes next. These are XL and long-dated by design — right-sized as Later, not a timing failure.

| Issue | Title | Priority | Size |
|---|---|---|---|
| [#547](https://github.com/TA-39/frontend/issues/547) | Evolve TA39 Into an Agentic Instruction Platform | High | XL |
| [#649](https://github.com/TA-39/frontend/issues/649) | TA39 Copilot — Conversational, Agentic Interface Embedded in Core UI | High | XL |
| [#474](https://github.com/TA-39/frontend/issues/474) | Voice-Based Assignment Support: Audio Transcription, Language Detection, and Feedback | Medium | — |

### Theme 2 — Teacher-in-the-loop intelligence (3)

Converts feedback from a one-shot output into a teacher-tunable system. Direct enterprise value — schools will pay for the ability to steer and override AI.

| Issue | Title | Priority | Size | Tags |
|---|---|---|---|---|
| [#328](https://github.com/TA-39/frontend/issues/328) | Student-Teacher Interaction on Feedback & AI Score Disputes (HITL) | Medium | — | ⚔️ |
| [#331](https://github.com/TA-39/frontend/issues/331) | Teacher-Led Calibration for AI Feedback (Delta-Based Template Refinement) | High | L | — |
| [#113](https://github.com/TA-39/frontend/issues/113) | Iterative Feedback during Writing Process — Socratic Style | Medium | XL | *author violation: duhajar* |

*⚔️ = also carries the GitHub `Competitive Parity` label.*

### Theme 3 — Quality & evaluation stack (7) — *dependency risk concentrated here*

All High priority or no-priority-set. Half are Blocked. This is the theme most at risk of quietly slipping a full quarter because nothing is forcing it forward.

| Issue | Title | Priority | Size | Status |
|---|---|---|---|---|
| [#7](https://github.com/TA-39/Sentinel/issues/7) | Sentinel Manager UI | High | M | Blocked / Information Needed |
| [#14](https://github.com/TA-39/graditron/issues/14) | [Evaluation Harness] Multi-Metric Framework for Prompt Version Comparison | High | XL | Blocked / Information Needed |
| [#19](https://github.com/TA-39/graditron/issues/19) | [Evaluation Harness] M2 — Observability | *not set* | M | Backlog |
| [#21](https://github.com/TA-39/graditron/issues/21) | [Evaluation Harness] M3 — Quality Gates | *not set* | — | Backlog |
| [#22](https://github.com/TA-39/graditron/issues/22) | [Evaluation Harness] M4 — Governance | *not set* | — | Backlog |
| [#29](https://github.com/TA-39/graditron/issues/29) | [Stream 2] Two-Stage Feedback and Evaluation Architecture | High | L | Blocked / Information Needed |
| [#35](https://github.com/TA-39/graditron/issues/35) | Confidence Scoring & LLM vs. Programmatic Responsibilities | Medium | M | Backlog |

Three "Blocked/Information Needed" items with High priority is a concentrated unblock exercise, not seven unrelated problems.

### Theme 4 — Integrations & LMS breadth (2)

Both Backlog. Canvas Discussions is the larger surface-area win; Google Classroom re-use is the marketed-first-class capability that the roadmap treats as Low.

| Issue | Title | Priority | Size |
|---|---|---|---|
| [#473](https://github.com/TA-39/frontend/issues/473) | Support Canvas Discussions as Source for TA39 Feedback Generation | Medium | — |
| [#226](https://github.com/TA-39/frontend/issues/226) | User Requirement — support for re-use in Google Classroom | Low | — |

### Theme 5 — Monetization (1) — *under-weighted*

One issue. Low priority. Backlog. If individual-user revenue matters in 2026, this is mis-prioritized. If it doesn't, archive it and stop carrying the noise.

| Issue | Title | Priority | Size | Tags |
|---|---|---|---|---|
| [#374](https://github.com/TA-39/frontend/issues/374) | Individual Paid User — Stripe Subscription and Feature Access Control | Low | — | ⚔️ |

*⚔️ = also carries the GitHub `Competitive Parity` label.*

### Cross-cutting: Competitive Parity portfolio

Three items carry the `Competitive Parity` label across the three themes above:

| Issue | Title | Home theme | Bucket |
|---|---|---|---|
| [#327](https://github.com/TA-39/frontend/issues/327) | Plagiarism Detection Integration | *standalone parity play* | NEXT |
| [#328](https://github.com/TA-39/frontend/issues/328) | Student-Teacher Interaction on Feedback & AI Score Disputes | Teacher-in-the-loop (Theme 2) | LATER |
| [#374](https://github.com/TA-39/frontend/issues/374) | Individual Paid User Stripe Subscription | Monetization (Theme 5) | LATER |

#327 is the only pure parity play — no topical home. #328 and #374 are topical items carrying a parity overlay; the label there is a signal to enterprise-RFP reviewers, not a standalone theme.

---

## Shipped but NOT publicly announced — hidden inventory (5)

Released features with no dedicated community post and no features-page mention. This is pitch ammunition the world cannot see.

| Issue | Title | Theme | Repo | Status |
|---|---|---|---|---|
| [#20](https://github.com/TA-39/graditron/issues/20) | [Evaluation Harness] M1 — Foundations | Quality & evaluation stack | graditron | In Production & Done |
| [#188](https://github.com/TA-39/frontend/issues/188) | Update UI for New Class Analysis Report and Assignment Tabs | Teacher-in-the-loop intelligence | frontend | In Production & Done |
| [#297](https://github.com/TA-39/frontend/issues/297) | Render Markdown Properly in Text Pane | Platform & UX | frontend | In Production & Done |
| [#532](https://github.com/TA-39/frontend/issues/532) | Internationalization — Multi-Language Support for Frontend UI | Arabic / Multilingual | frontend | In Production & Done |
| [#720](https://github.com/TA-39/frontend/issues/720) | UI Refresh — Revolt Design Implementation | Platform & UX | frontend | In Production & Done |

**Recommended retroactive posts (top 3):**

1. **#532 Internationalization** — this is the single most important untold story. Multi-language UI is the foundational proof point for the Arabic-market strategy; not talking about it forfeits a differentiator.
2. **#720 UI Refresh (Revolt Design)** — a full UI refresh is inherently announceable; prospective users judge on first impression, and a design overhaul is the canonical "we are investing in the product" signal.
3. **#188 Class Analysis Report** — class-level analytics is a teacher-buyer feature. Shipping it silently leaves the page selling rubrics and copilots when the newer class-analytics story is also available.

The Eval Harness M1 (#20) is engineering infrastructure — fine to leave unannounced. Markdown rendering (#297) is a polish ship — fine.

---

## Risks & Dependencies

1. **Public-surface vs. shipped product.** The Handwritten Work claim on the features page is backed by an unstarted XL issue (#99). Until #99 starts, either the page is describing something else (baseline OCR) that should be disambiguated, or the page is overstating reality. Audit with marketing this week.
2. **Blocked High-priority concentration in the quality/eval stack.** #7, #14, and #29 are all High, all Blocked. Until the unblock owner identifies the missing information, velocity in Theme 3 is zero. This is the single largest slip risk in the roadmap — it is silent and has no shipping date to miss.
3. **Cross-repo dependencies on Arabic NLP.** #596 (frontend), #166 (api), and #99 (graditron) are a single enablement story split across three repos. A delay in any one stalls the observable customer impact. Track as one epic, not three lines.
4. **Missing Iteration / Sprint field population.** Every single in-scope item has `iteration=""`. The board cannot report burndown or show commitment-vs-delivery without an iteration cadence set. Either start populating Iteration or drop the expectation that the board itself is the sprint artifact.
5. **Author-rule violation.** [#113 Iterative Feedback — Socratic Style](https://github.com/TA-39/frontend/issues/113) is `Type=Feature` but authored by `duhajar`, not `adnanwarsi`. Either promote it (product lead owns it now) or downgrade to a Task — the current state muddies the "features map to product-lead intent" contract.
6. **No-priority evaluation items.** #19, #21, #22 (Eval Harness M2/M3/M4) all have Priority unset. The Eval Harness is how the team proves quality to enterprise; unprioritized in the tracker means unprioritized in practice.

---

## Strategic Call-outs

**(a) Agentic is the right "Later" bet.** #547 and #649 are both XL and both deferred. That is correct — the market is not yet ready, and shipping agentic-instruction before the Eval Harness (Theme 3) produces reputational risk. Keep them Later, keep them sized, revisit at end-Q2.

**(b) Monetization is underweighted.** [#374](https://github.com/TA-39/frontend/issues/374) is the only monetization issue, Low priority, Backlog. If individual-user revenue is part of the 2026 plan, this is mis-prioritized. If it is not, archive it. Carrying a Low-priority Backlog as the sum of monetization investment is a bad signal to anyone reading the board.

**(c) Eval Harness M2 / M3 / M4 have no Priority set.** #19, #21, #22. This is the stack that converts prompt-engineering wins into auditable, enterprise-grade quality. Leaving it unprioritized is the roadmap equivalent of saying the team does not know when quality graduates from "we check" to "we can show you." Set a priority this sprint.

**(d) Google Classroom re-use is Low Backlog but marketed first-class.** [#226](https://github.com/TA-39/frontend/issues/226) is Low priority while the features page names "Canvas / Google Classroom breadth" as a top claim. Either ship it or soften the page.

**(e) Hidden inventory = pitch ammunition.** 5 shipped features have no public post. #532 (Internationalization) is the most valuable missing story by a wide margin — it is the foundation the Arabic push rests on. #720 (UI Refresh) and #188 (Class Analysis) are the next two.

**(f) Competitive Parity is a distinct lens.** Three items carry the label:

- [#327](https://github.com/TA-39/frontend/issues/327) Plagiarism Detection — **pure parity play, no topical home**. NEXT.
- [#328](https://github.com/TA-39/frontend/issues/328) Student-Teacher HITL — parity overlay on Teacher-in-the-loop (Theme 2). LATER.
- [#374](https://github.com/TA-39/frontend/issues/374) Stripe individual subscriptions — parity overlay on Monetization (Theme 5). LATER.

Framed as a portfolio question for leadership: three is a thin parity bench. Under-investing loses enterprise RFPs where procurement checklists demand feature-check parity before TA39's differentiators get evaluated. Over-investing burns capacity that should be going into the Arabic market push, the Eval Harness, and the agentic evolution. The current mix (one NEXT parity play + two LATER overlays) is defensible if enterprise motion is Q3+; it is insufficient if a parity-sensitive deal is closing this quarter.

---

## Changes vs. the board today

Concrete actions the product lead should take after reading this:

1. **Retag #113** as either a lead-owned Feature (confirm and re-author) or a Task (correct the Type). Today it is neither.
2. **Set Priority on #19, #21, #22** (Eval Harness M2/M3/M4). Even "Medium" is better than unset.
3. **Populate the Iteration field** on #6, #166, #596, #701, #740 at minimum. Without it, sprint-level reporting is fiction.
4. **Audit the Handwritten Work claim** on the features page with marketing. Either link the page to the baseline OCR capability (if that is what's shipped), or commit #99 to a start date and land it in-quarter.
5. **Promote or archive #374.** Low + Backlog + Monetization is the worst of all worlds.
6. **File backing issues** for the three orphaned community posts (Folders, Rubric Converter, Trusted Apps Pledge), or move them out of the announcement canon.

---

## Follow-ups I can generate on request

- **Exec version** — 1-page condensed roadmap for board/investors with bucket counts, marquee releases, and risks only.
- **Sprint plan** — honest 2-week cut from NOW + top NEXT items with capacity and carryover accounted for.
- **Competitive frame** — the `Competitive Parity` analysis (call-out f) expanded into a battle-card / RFP-readiness view.
- **Refreshed xlsx tracker** — the full 36-item list with bucket, status, priority, size, labels, and announcement-linkage columns.
- **Retroactive announcement drafts** — community posts for #532 Internationalization, #720 UI Refresh, and #188 Class Analysis.
- **Quarterly theme review** — a Theme 1–5 deep read with bets, ship probabilities, and rebalancing recommendations.
