# TA39 Product Roadmap

**Source:** GitHub Projects board [TA-39 Product Development (project #4)](https://github.com/orgs/TA-39/projects/4).
**Scope:** Every non-archived item with `Type = Feature` authored by `adnanwarsi`.
**Retrieved:** 2026-04-17 (fresh pull — 25 in-scope items, #343 Rubric UI joined after re-typing as Feature).
**Horizon:** Through Q3 2026.

The MD is the source of truth. The HTML dashboard (`TA39-Roadmap.html`) is a projection of it. If a row is missing a theme or a blurb, the dashboard is partial — fix it here.

---

## Public-surface tagging

- `[ANNOUNCED]` — there is a dedicated post on community.ta-39.com.
- `[FEATURED]` — the item is **released** AND named on www.ta-39.com/en/features. Pipeline items never carry `[FEATURED]`; that would be making a claim before a commitment.
- `[SILENT]` — released but neither announced nor featured. Hidden inventory.

Tags signal "what users have been told about." They are not a quality signal; they are a communications signal.

---

## Kanban Status Glossary

The status names on the board are not self-evident to a reader. Wire this into any stakeholder read.

| Status | Meaning | Position in flow |
|---|---|---|
| Backlog | Unprioritized, no commitment. | Later |
| Ready for Development | Groomed. Unstarted. Committed for the next open slot. | Next |
| In progress | Code is being written. | Now |
| In Review | PR open / code review. | Now |
| Testing in Production | Behind a flag, being validated live. **Treated as released.** | Released |
| In Production & Done | Shipped, flag removed. | Released |
| Archive | Out of scope. | Excluded |

Keep in mind: `Ready for Development` ≠ "about to ship." It means "the team could pick this up next." Readers mis-hear this constantly.

---

## Status Overview

| Bucket | Count |
|---|---|
| RELEASED | 10 |
| NOW | 2 |
| NEXT | 4 |
| BLOCKED | 0 |
| LATER | 9 |
| ARCHIVED (excluded) | 2 |
| **In-scope total** | **25** |

**Velocity context.** Ten releases are spread across 2025-Q1 through 2026-Q2. The cadence accelerated in 2026: #343 (Rubric UI Overhaul) on 2026-03-25, #344 (Feedback Templates) on 2026-03-29, #697 (Revision Rounds) on 2026-04-12. Three public launches in under three weeks is a new pace for the team and aligns with the sharper announcement cadence on community.ta-39.com.

Two active builds (#166 Arabic summaries, #596 Arabic NLP epic) concentrate risk in the Arabic / Multilingual theme. Both are in `In progress`; #596 is `XL` and is not a 6-week effort. If Arabic-market GTM has a target date, surface the dependency now.

---

## Marketing-vs-Ship Gap

What the public page claims, against what has actually shipped. This is the RFP-readiness view.

| Claim (on www.ta-39.com/en/features) | Anchor issue(s) | Reality today | Risk |
|---|---|---|---|
| Revision Rounds | [#697](https://github.com/TA-39/frontend/issues/697), [#740](https://github.com/TA-39/frontend/issues/740) | #697 `Testing in Production` (live as of 2026-04-12 and publicly launched). #740 "Learning Loop" evolution is `Ready for Development` — unstarted. | **Low** on the core claim; **Medium** if prospects expect the longitudinal loop. |
| Handwritten Work Support | [#99](https://github.com/TA-39/graditron/issues/99) (Arabic HTR), plus baseline OCR | Arabic HTR is `Ready for Development` — unstarted. Baseline English OCR ships today but the page wording is ambiguous. | **Medium** — needs a 5-minute copy audit with marketing each run. |
| Canvas / Google Classroom breadth | [#378](https://github.com/TA-39/frontend/issues/378), [#473](https://github.com/TA-39/frontend/issues/473), [#226](https://github.com/TA-39/frontend/issues/226) | LTI Google Doc submission shipped 2025-05-03. Canvas Discussions (#473) and GC re-use (#226) both Backlog. | **Medium** — the page implies parity, reality is partial. |
| Optimize Rubrics With AI | [#343](https://github.com/TA-39/frontend/issues/343) | Shipped 2026-03-25 & announced 2026-03-30. Met. | **Low** |
| Feedback Templates | [#344](https://github.com/TA-39/frontend/issues/344) | Shipped 2026-03-29. Met. | **Low** |
| Assignment Exemplars | [#440](https://github.com/TA-39/frontend/issues/440) | Shipped 2025-05-15. Met. | **Low** |
| Teacher / Student / Context-Aware Copilot | [#384](https://github.com/TA-39/frontend/issues/384), [#385](https://github.com/TA-39/frontend/issues/385), [#366](https://github.com/TA-39/frontend/issues/366) | Shipped. Met. Next evolution is agentic (#547, #649) — both `Later`. | **Low** on current claim. |

**Tag application note.** `[FEATURED]` is reserved for released items that also appear on the features page. Pipeline items never earn `[FEATURED]`, even if marketing has pre-named them. That is a commitment, not a claim.

---

## Announcement Cross-Reference

Every released item that has a dedicated community post. Two of the ten released items are `[SILENT]` and appear in the hidden-inventory section below.

| Issue | Title | Theme | Post | Announced | Released | Tags |
|---|---|---|---|---|---|---|
| [#697](https://github.com/TA-39/frontend/issues/697) | Revision-Aware Writing & Feedback Cycles | Teacher-in-the-loop intelligence | [Introducing Revision Rounds](https://community.ta-39.com/announcements/post/introducing-revision-rounds-making-student-revision-across-drafts-visible-jbYENcYH221JQqt) | 2026-04-14 | 2026-04-12 | [ANNOUNCED] [FEATURED] |
| [#344](https://github.com/TA-39/frontend/issues/344) | Feedback Template creation (Simplify) | Teacher-in-the-loop intelligence | [Build Feedback Templates More Easily](https://community.ta-39.com/announcements/post/you-can-now-build-feedback-templates-more-easily-in-ta39-toqLgjVRG53sHX8) | 2026-03-30 | 2026-03-29 | [ANNOUNCED] [FEATURED] |
| [#343](https://github.com/TA-39/frontend/issues/343) | Rubric UI and setup experience overhaul | Teacher-in-the-loop intelligence | [Optimize Rubrics With AI](https://community.ta-39.com/announcements/post/you-can-now-optimize-rubrics-with-ai-in-the-rubric-library-wUoDP62myFdyOId) | 2026-03-30 | 2026-03-25 | [ANNOUNCED] [FEATURED] |
| [#440](https://github.com/TA-39/frontend/issues/440) | Assignment Exemplars | Quality & evaluation stack | [Create Exemplars for Any Rubric](https://community.ta-39.com/announcements/post/you-can-now-create-exemplars-for-any-rubric----powered-by-ai-1S4jZwTapdze0XR) | 2025-05-15 | 2025-05-15 | [ANNOUNCED] [FEATURED] |
| [#384](https://github.com/TA-39/frontend/issues/384) | Teacher CoPilot | Agentic / Copilot evolution | [New TA39 Copilot](https://community.ta-39.com/announcements/post/new-ta39-copilot-transform-feedback-into-meaningful-conversations-t98LSruxg85pprV) | 2025-04-25 | 2025-04-23 | [ANNOUNCED] [FEATURED] |
| [#385](https://github.com/TA-39/frontend/issues/385) | Student CoPilot | Agentic / Copilot evolution | *same post as #384* | 2025-04-25 | 2025-04-24 | [ANNOUNCED] [FEATURED] |
| [#366](https://github.com/TA-39/frontend/issues/366) | Context-Aware Copilot Panels | Agentic / Copilot evolution | *same post as #384* | 2025-04-25 | 2025-08-23 | [ANNOUNCED] [FEATURED] |
| [#378](https://github.com/TA-39/frontend/issues/378) | Canvas Google Doc Submissions via LTI | Integrations & LMS breadth | [Google Docs Submission Support](https://community.ta-39.com/announcements/post/update-google-docs-submission-support-now-available-sHeucGoJSdE6sWM) | 2025-01-21 | 2025-05-03 | [ANNOUNCED] [FEATURED] |

**Note — Announced vs. Released.** These are often the same week, but not always. #366 was released months after its original post because the feature shipped incrementally. Carry both columns honestly so the team can see where we pre-announced, where we retroactively announced, and where shipping lagged.

**Orphaned announcement posts (no live `Type=Feature` issue).** On each refresh these should be either filed as issues or consciously ignored:

- [Organizing Assignments: Folders in TA39](https://community.ta-39.com/announcements/post/organizing-assignments-folders-in-ta39-5d8F8faYPAXjAQv) — no anchor feature issue.
- Rubric Converter Utility post.
- Trusted Apps Pledge post.

---

## RELEASED

All 10 released items. `Testing in Production` and `In Production & Done` both count — the flag distinction doesn't matter to a reader; both are live.

| # | Title | Theme | Repo | Priority | Size | Status | Tags |
|---|---|---|---|---|---|---|---|
| [#697](https://github.com/TA-39/frontend/issues/697) | Revision-Aware Writing & Feedback Cycles | Teacher-in-the-loop intelligence | frontend | High | L | Testing in Production | [ANNOUNCED] [FEATURED] |
| [#344](https://github.com/TA-39/frontend/issues/344) | Feedback Template creation (Simplify) | Teacher-in-the-loop intelligence | frontend | High | L | In Production & Done | [ANNOUNCED] [FEATURED] |
| [#343](https://github.com/TA-39/frontend/issues/343) | Rubric UI and setup experience overhaul | Teacher-in-the-loop intelligence | frontend | High | L | In Production & Done | [ANNOUNCED] [FEATURED] |
| [#440](https://github.com/TA-39/frontend/issues/440) | Assignment Exemplars Support | Quality & evaluation stack | frontend | High | L | In Production & Done | [ANNOUNCED] [FEATURED] |
| [#384](https://github.com/TA-39/frontend/issues/384) | Teacher CoPilot | Agentic / Copilot evolution | frontend | High | — | In Production & Done | [ANNOUNCED] [FEATURED] |
| [#385](https://github.com/TA-39/frontend/issues/385) | Student CoPilot | Agentic / Copilot evolution | frontend | High | — | In Production & Done | [ANNOUNCED] [FEATURED] |
| [#366](https://github.com/TA-39/frontend/issues/366) | Context-Aware Copilot Panels | Agentic / Copilot evolution | frontend | Critical | M | In Production & Done | [ANNOUNCED] [FEATURED] |
| [#378](https://github.com/TA-39/frontend/issues/378) | Canvas Google Doc Submissions via LTI | Integrations & LMS breadth | frontend | High | M | In Production & Done | [ANNOUNCED] [FEATURED] |
| [#188](https://github.com/TA-39/frontend/issues/188) | Update UI for New Class Analysis Report & Assignment Tabs | Platform & UX | frontend | High | S | In Production & Done | [SILENT] |
| [#532](https://github.com/TA-39/frontend/issues/532) | Internationalization — Multi Language Support for Frontend UI | Arabic / Multilingual | frontend | High | L | In Production & Done | [SILENT] |

---

## NOW

Active build or QA. Concentrated in Arabic — this is the big market bet in flight.

| Issue | Title | Theme | Status | Priority | Size | Repo | Tags |
|---|---|---|---|---|---|---|---|
| [#166](https://github.com/TA-39/api/issues/166) | Arabic Mode Summary Report Generation (RTL + Arabic Template) | Arabic / Multilingual | In progress | High | S | api | — |
| [#596](https://github.com/TA-39/frontend/issues/596) | [Stream 3][Epic] Arabic NLP Enablement for TA39 Feedback Platform | Arabic / Multilingual | In progress | High | XL | frontend | — |

**Ship-order read.** #166 is `S` — it should land weeks ahead of #596. That gives the Arabic market a shippable demo (RTL summary reports) while the NLP epic continues. #596 at `XL` is a quarter-scale investment; do not expect it to close in Q2 even if it keeps moving. Size the team's Arabic bandwidth accordingly.

---

## NEXT

`Ready for Development` — groomed, unstarted, committed to the next open slot.

| Issue | Title | Theme | Priority | Size | Tags | Q2 realism |
|---|---|---|---|---|---|---|
| [#99](https://github.com/TA-39/graditron/issues/99) | Arabic Handwriting Recognition (HTR) Capability | Arabic / Multilingual | High | XL | — | **Defer to Q3.** XL cold-start, cross-repo (graditron), stacks on the #596 NLP pipeline. Not a 6-week effort. |
| [#327](https://github.com/TA-39/frontend/issues/327) | Plagiarism Detection Integration | Competitive Parity | Medium | L | `Competitive Parity` label | **Must-start in Q2** if enterprise RFPs are a Q3 pipeline focus. L item, achievable if prioritized. |
| [#701](https://github.com/TA-39/frontend/issues/701) | Microsoft Teams LMS Integration | Integrations & LMS breadth | High | L | — | **Must-start in Q2.** L item, unblocks Teams-standardized schools (large GCC + US enterprise segment). |
| [#740](https://github.com/TA-39/frontend/issues/740) | Evolve Draft Revision Rounds into a "Learning Loop" System | Teacher-in-the-loop intelligence | High | L | — | **Q2 stretch / Q3 base.** Natural follow-on to #697 release. Features page already implies this exists. |

**Q2 realism summary.** Two of four NEXT items (#701, #327) are plausibly shippable in Q2 given sizes and priorities. #99 and #740 should be framed as Q3 realistically — don't commit them externally this quarter.

---

## LATER

Backlog, bucketed by theme. Themes with no LATER items (Arabic, Quality & evaluation, Platform & UX) are omitted here; they still appear in the theme-portfolio view.

### Theme 1 — Agentic / Copilot evolution

| Issue | Title | Priority | Size | Tags | Note |
|---|---|---|---|---|---|
| [#547](https://github.com/TA-39/frontend/issues/547) | Evolve TA39 Into an Agentic Instruction Platform | High | XL | — | The "north-star" agentic bet. High priority but XL means this is a 2026-H2 build at the earliest. |
| [#649](https://github.com/TA-39/frontend/issues/649) | TA39 Copilot — Conversational, Agentic Interface Embedded in Core UI | High | XL | — | The UI-level agentic surface. Pairs with #547 — ship together or sequence deliberately. |
| [#474](https://github.com/TA-39/frontend/issues/474) | Voice-Based Assignment Support: Audio Transcription, Language Detection | Medium | — | — | Voice as an input modality is a natural extension of the agentic platform; position as an agentic-era capability. |

### Theme 2 — Teacher-in-the-loop intelligence

| Issue | Title | Priority | Size | Tags | Note |
|---|---|---|---|---|---|
| [#331](https://github.com/TA-39/frontend/issues/331) | Teacher-Led Calibration for AI Feedback (Delta-Based Templates) | High | L | — | The "teach the system your voice" loop. High-priority, L-size — should be prioritized for pull-forward. |
| [#328](https://github.com/TA-39/frontend/issues/328) ⚔️ | Student-Teacher Interaction on Feedback & AI Score Disputes (HITL) | Medium | — | `Competitive Parity` label | Dispute flow is table-stakes in enterprise RFPs. Parity-driven but topical home is HITL. |
| [#113](https://github.com/TA-39/frontend/issues/113) ⚔️ | Iterative Feedback during Writing Process — Socratic Style | Medium | XL | `Competitive Parity` label | XL parity play. Distinct from #697 (Revision Rounds) — #113 is in-flight guidance; #697 is cross-draft arc. |

*⚔️ = also carries the GitHub `Competitive Parity` label.*

### Theme 3 — Integrations & LMS breadth

| Issue | Title | Priority | Size | Tags | Note |
|---|---|---|---|---|---|
| [#473](https://github.com/TA-39/frontend/issues/473) | Support Canvas Discussions as Source for TA39 Feedback | Medium | — | — | Expands Canvas surface beyond submissions. Features page already implies this is supported. |
| [#226](https://github.com/TA-39/frontend/issues/226) | Support for re-use in Google Classroom | Low | — | — | Low-priority but the features page names it. Either pull forward or soften the claim. |

### Theme 4 — Monetization

| Issue | Title | Priority | Size | Tags | Note |
|---|---|---|---|---|---|
| [#374](https://github.com/TA-39/frontend/issues/374) ⚔️ | Individual Paid User — Stripe Subscription & Feature Entitlements | Low | — | `Competitive Parity` label | **The entire monetization theme is one `Low` backlog item.** If self-serve revenue is a 2026 goal, this is mis-prioritized. If not, archive and stop carrying the noise. |

*⚔️ = also carries the GitHub `Competitive Parity` label.*

---

## Shipped but NOT publicly announced

Hidden inventory. Released, silent. These are the "pitch ammunition" bucket — retroactive announcements cost little and turn shipped work into renewed credibility.

| Issue | Title | Theme | Repo | Released | Status |
|---|---|---|---|---|---|
| [#188](https://github.com/TA-39/frontend/issues/188) | Update UI for New Class Analysis Report & Assignment Tabs | Platform & UX | frontend | 2025-02-02 | In Production & Done |
| [#532](https://github.com/TA-39/frontend/issues/532) | Internationalization — Multi Language Support for Frontend UI | Arabic / Multilingual | frontend | 2025-08-03 | In Production & Done |

**Recommended retroactive posts:**

1. **#532 Internationalization foundation** — this is the most strategic silent ship. It is the plumbing that makes the Arabic bet credible. Announcing it now frames the Arabic roadmap (#166, #596, #99) as a deliberate long-arc investment rather than a reactive feature drop.
2. **#188 Class Analysis UI refresh** — short post, visual before/after, re-establishes momentum on teacher-facing surfaces.

Two silent releases on a base of ten is a low ratio — the team is mostly announcing what it ships. Close the gap on these two and the communication story is clean.

---

## Risks & Dependencies

1. **Public-surface vs. shipped product.** Features-page claims for Canvas breadth and handwritten work outrun shipped reality (#473, #226, #99 all unstarted or backlog). RFPs will expose this. Either pull forward or edit the page.
2. **Arabic theme dependency chain.** #166 → #596 → #99 is a single chain of dependencies spread across three repos (api, frontend, graditron). If any link slows, the Arabic market launch slips. There is no in-flight Arabic work *outside* this chain — no redundancy.
3. **Monetization under-investment.** One `Low` priority backlog item (#374) is the entire self-serve revenue story. This is a portfolio-level gap, not an issue-level one.
4. **Missing Iteration/Sprint field population.** None of the in-scope items have an Iteration populated. This means sprint commitments live outside the board, and the board cannot serve as a sprint-planning artifact without fixing this.
5. **Cross-repo coordination is under-managed.** #596 (frontend) has implicit dependencies on #166 (api) and #99 (graditron). No explicit dependency link on the board. First slip will surface this.
6. **Quality & eval stack has aged out of the active roadmap.** The previous roadmap carried Sentinel/Eval Harness items; none are in-scope today. Either they're archived (in which case eval is running on vibes) or they belong on this board. Clarify.

---

## Strategic Call-outs

**(a) Teacher-in-the-loop is the differentiator, and shipping confirms it.**
#697 (Revision Rounds) and #344 (Feedback Templates) both shipped in the last six weeks. Both are teacher-in-the-loop features. #331 (Calibration) and #740 (Learning Loop) are the obvious next steps. This is the theme with real velocity — lean into it.

**(b) Agentic is the right long-arc bet and is correctly parked in Later.**
#547 and #649 are both XL and flagged as 2026-H2 work. That's honest sequencing: copilot (shipped) → agentic (next era). Don't let marketing collapse the two timelines.

**(c) Arabic is the largest uncommitted-risk cluster.**
Three items (#166 NOW, #596 NOW, #99 NEXT) plus a silent foundation (#532) add up to a multi-quarter, multi-repo investment. If there is an Arabic-market GTM date, surface the dependency chain on the board. If there isn't, consider sequencing #166 to ship standalone as a credible Arabic demo while #596 continues.

**(d) Monetization is the portfolio hole.**
Exactly one `Low` priority backlog item. If individual-user revenue is part of the 2026 story, #374 should move up and get sized. If not, say so out loud — the silence on this line is a leadership signal either way.

**(e) Hidden inventory is small and easy to close.**
Two silent releases. The 2026 cadence has been clean — most shipped work gets a post. Close #188 and #532 with retroactive posts and the communication loop is effectively complete.

**(f) Competitive Parity is a distinct lens — review the portfolio.**
Four items carry the `Competitive Parity` label:

- [#327](https://github.com/TA-39/frontend/issues/327) Plagiarism Detection — pure parity play, no topical home; theme = `Competitive Parity`.
- [#113](https://github.com/TA-39/frontend/issues/113) Socratic Feedback — topical (Teacher-in-loop) + parity overlay.
- [#328](https://github.com/TA-39/frontend/issues/328) HITL Disputes — topical (Teacher-in-loop) + parity overlay.
- [#374](https://github.com/TA-39/frontend/issues/374) Stripe Subscriptions — topical (Monetization) + parity overlay.

Three of the four are `Medium` or `Low`. Under-investing loses enterprise RFPs (plagiarism, disputes). Over-investing burns differentiation capacity. Leadership question: is parity a Q3 priority or a 2026-H2 priority? Right now the label is applied but the priorities don't reflect an answer.

---

## Changes vs. the board today

1. **Populate Iteration fields** on every NOW and NEXT item so the board becomes a sprint artifact.
2. **Link cross-repo dependencies** between #166 / #596 / #99 explicitly so a slip on one surfaces on the others.
3. **Reprioritize or retire #374** — force a decision on self-serve monetization.
4. **Set a Priority on #327** — Medium today, but if enterprise RFPs are the Q3 target, it should be High.
5. **File or close the orphan announcement posts** (Folders, Rubric Converter, Trusted Apps Pledge) — either they need feature issues or the posts should be archived from the announcements reference.
6. **Clarify the quality/eval stack.** If Sentinel / Eval Harness work still exists, add it back to project #4. If not, add a note so future roadmap reads don't ask.

---

## Appendix — Feature Blurbs

One-sentence human explanations of what each feature does. These are rendered under the title on the HTML dashboard cards. Keep them short (≤ 22 words) and say what users *get*, not how it's built. Issue numbers are the join key — the HTML renderer falls back to no-blurb gracefully when an entry is missing, and prints a stderr warning listing gaps so they're easy to backfill.

| # | Blurb |
|---|---|
| 99 | Handwritten-Arabic OCR so scanned handwritten work flows through the same feedback loop as typed submissions. |
| 113 | Socratic feedback during writing — TA39 asks guiding questions instead of grading completed work. |
| 166 | RTL summary reports in Arabic — the first real Arabic-market output teachers can hand to students. |
| 188 | Class-level analytics view so teachers can spot patterns across a whole class, not one paper at a time. |
| 226 | Re-use existing Google Classroom assignments inside TA39 so teachers don't rebuild content they've already posted. |
| 327 | Integrated plagiarism check on submissions — the enterprise-RFP parity item that unblocks procurement conversations. |
| 328 | A structured way for students to challenge AI feedback or scores with the teacher in the loop. |
| 331 | Teachers correct AI feedback with deltas — the system learns their voice without prompt-retraining. |
| 343 | Rebuilt rubric creation with AI-assisted criteria drafting so teachers optimize rubrics in minutes instead of hours. |
| 344 | One-click feedback templates let teachers capture how they give feedback and reuse it across assignments. |
| 366 | Copilot panels that adapt to where the user is in the product, so help shows up in context. |
| 374 | Self-serve Stripe subscription for individual teachers — the monetization path that doesn't require a school contract. |
| 378 | Students submit Google Docs straight through Canvas LTI without leaving the LMS workflow. |
| 384 | Conversational sidekick that turns rubric feedback into teacher-friendly next steps and talking points. |
| 385 | Student-facing copilot that explains feedback plainly and answers 'what do I do with this?' in the moment. |
| 440 | AI-generated student exemplars for any rubric show classes what each score level actually looks like. |
| 473 | Canvas discussion posts become a first-class submission surface — feedback on participation, not just essays. |
| 474 | Voice submissions — students record audio, TA39 transcribes, detects language, and runs the normal feedback loop. |
| 532 | Multi-language UI foundation — the scaffolding that lets the product ship Arabic and other locales. |
| 547 | The bet that TA39 becomes an agent that autonomously helps teachers plan, assign, and coach. |
| 596 | End-to-end Arabic NLP pipeline — OCR, tokenization, feedback — that makes TA39 feel native to Arabic-first classrooms. |
| 649 | Copilot embedded in the core UI as a conversational agent, replacing menus where an agent makes more sense. |
| 697 | Surfaces the arc of a student's drafts so teachers can see revision quality — not just the final version. |
| 701 | Microsoft Teams LTI support so schools standardized on Teams can adopt TA39 without switching LMSes. |
| 740 | Turns Revision Rounds into a longitudinal learning loop — tracks student growth patterns across many assignments. |

---

## Follow-ups I can generate on request

- **Exec version** — 1-page condensed roadmap for board/investors with bucket counts, marquee releases, and risks only.
- **Sprint plan** — honest 2-week cut from NOW + top NEXT items with capacity and carryover accounted for.
- **Competitive frame** — call-out (f) expanded into a battle-card / RFP-readiness view.
- **Refreshed xlsx tracker** — the 25-item list with bucket, status, priority, size, labels, and announcement-linkage columns.
- **Retroactive-announcement drafts** — community posts for #532 and #188 in TA39 voice.
