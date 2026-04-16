# Features Page Claims → Issue Mappings

This file tracks claims made on [www.ta-39.com/en/features](https://www.ta-39.com/en/features)
and the GitHub issues that back (or should back) them. It is the input for
the **Marketing-vs-Ship Gap** table in `TA39-Roadmap.md`.

The gap exists because marketing sometimes names capabilities that are not
fully in production. When the page overstates reality, the roadmap must
either pull work forward (if it's a real commitment) or soften the page
(if it's aspirational).

## Claim table

| Features-page claim | Anchor issue(s) | Typical reality |
|---|---|---|
| **"Revision Rounds"** | [#697](https://github.com/TA-39/frontend/issues/697), follow-on [#740](https://github.com/TA-39/frontend/issues/740) | #697 is the core. Once released, this claim is met. #740 adds the "Learning Loop" layer on top. |
| **"Handwritten Work Support"** | [#99](https://github.com/TA-39/graditron/issues/99) (Arabic HTR), plus any earlier baseline OCR issue | Ambiguous: the page may describe already-shipped baseline OCR, or may overstate current capability. Needs a 5-minute audit with marketing each run to confirm. |
| **"Canvas / Google Classroom breadth"** | [#378](https://github.com/TA-39/frontend/issues/378) (LTI, shipped), [#473](https://github.com/TA-39/frontend/issues/473) (Canvas Discussions, Backlog), [#226](https://github.com/TA-39/frontend/issues/226) (GC re-use, Backlog) | Partial. Core LTI submission is there; discussions and GC re-use are not. |
| **"Optimize Rubrics With AI"** | [#343](https://github.com/TA-39/frontend/issues/343) | Shipped (In Production & Done). Met. |
| **"Feedback Templates"** | [#344](https://github.com/TA-39/frontend/issues/344) | Shipped (In Production & Done). Met. |
| **"Assignment Exemplars"** | [#440](https://github.com/TA-39/frontend/issues/440) | Shipped. Met. |
| **"Teacher / Student / Context-Aware Copilot"** | [#384](https://github.com/TA-39/frontend/issues/384), [#385](https://github.com/TA-39/frontend/issues/385), [#366](https://github.com/TA-39/frontend/issues/366) | Shipped. Met. Next evolution is agentic (#547, #649) — Later. |

## How to write the Marketing-vs-Ship Gap section

For each claim with a real gap (anchor issue is not yet released):

1. State the claim.
2. State current reality, linking the anchor issue and noting its Status.
3. Rate risk as Low / Medium / High based on:
   - Low: claim is met, or follow-on enhancement is pipelined
   - Medium: claim partially met, core is shipped but a named sub-capability
     is missing
   - High: central claim is unshipped and visible to prospects

Always end the section with a **Tag application note** reminding the reader
that `[FEATURED]` is reserved for released items on the features page.
