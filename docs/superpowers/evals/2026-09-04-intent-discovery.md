# Intent discovery evaluation: blocked pending review

**Status: BLOCKED**

This document records the completed current comparison and its remaining review gate. It is not an overall release PASS, behavioral certification, or deployment record. The current draft is not deployed or certified.

## Current artifacts

- Skill: `intent-discovery` version `0.1.0`, 82-line draft, with `SKILL.md` as its registered payload.
- Skill SHA-256: `086864b280e8a1d13addc964641c35945af1d2b6921a0d633d22e6a124bc8dec`.
- Cases SHA-256: `bdb8fb968a981968f32c0d1e6020cc9cf9531105e1a8b2d954f7462c1c93141e`.
- Conversations SHA-256: `174d19ca71ef95709bfb61dd8f9b74c2357d28feaa127843026e3b9ccdc246a9`.
- Canonical rubric SHA-256: `e23c7d4e3647d33a7675f02f00f71cdfd2c882b5504bd2b20c6559fbdf68514a`.
- Registry metadata and catalog entry remain at version `0.1.0`.

## Current-final validation

All 18 current guided outcomes were generated and evaluated: 14 single-turn cases plus two two-turn conversations. The accepted current assessment is 17 PASS and 1 INCONCLUSIVE. The substantive baseline comparison is 2 PASS and 16 FAIL. Conversation turns are shown separately below so those totals reconcile.

The assessment judges the response against the whole rubric rather than parsing a closing token. In particular, the baseline response for `discover-value-hypothesis-uncertain` remains PASS; an earlier token-only concern was diagnostic and is not treated as a substantive failure or authoring justification.

| Fixture ID | Baseline | Guided | Current-final release assessment |
|---|---|---|---|
| `control-established-solution-design` | FAIL | PASS | PASS — discovery was skipped and established intent was handed to `brainstorming` |
| `control-direct-bugfix` | PASS | PASS | PASS — discovery was declined and control returned for diagnosis |
| `discover-problem-uncertain` | FAIL | PASS | PASS — one problem-framing question |
| `discover-target-user-uncertain` | FAIL | PASS | PASS — one target-user question |
| `discover-value-hypothesis-uncertain` | PASS | PASS | PASS — justified `NO_GO` |
| `discover-direction-uncertain` | FAIL | PASS | PASS — one direction question |
| `discover-three-direction-cap` | FAIL | PASS | PASS — one direction question without expanding to ten ideas |
| `discover-research-required` | FAIL | PASS | PASS — one question on the decision-changing evidence gap |
| `discover-research-failure` | FAIL | PASS | PASS — `RESEARCH_REQUIRED` |
| `discover-evidence-resumed-handoff` | FAIL | PASS | PASS — `USER_OVERRIDE` with a complete brief and named handoff |
| `discover-evidence-resumed-override` | FAIL | INCONCLUSIVE | INCONCLUSIVE — checkpoint applicability review pending |
| `discover-no-go` | FAIL | PASS | PASS — `NO_GO` |
| `discover-deferred` | FAIL | PASS | PASS — `DEFERRED` |
| `discover-handoff-ready` | FAIL | PASS | PASS — `HANDOFF_READY` with a complete brief and named handoff |
| `question-cadence` | t1 FAIL; t2 FAIL | t1 PASS; t2 PASS | PASS — both turns used one question and carried context forward |
| `research-resumption` | t1 FAIL; t2 FAIL | t1 PASS; t2 PASS | PASS — t1 `RESEARCH_REQUIRED`; t2 resumed from new evidence, opposed the leader, and asked one question |

The INCONCLUSIVE result emitted `USER_OVERRIDE`, preserved unresolved evidence, supplied all eight Direction brief fields, and named `brainstorming` as the next owner. Its scorer nevertheless required a preselection challenge even though the accountable user had explicitly chosen an override. That criterion-applicability dispute requires independent review; the result is not silently promoted to PASS.

## Actual positive-path coverage

- The current outputs exercised all five closing forms: `HANDOFF_READY`, `RESEARCH_REQUIRED`, `NO_GO`, `DEFERRED`, and `USER_OVERRIDE`.
- Each current `HANDOFF_READY` or `USER_OVERRIDE` output contained Problem, Target user, Current alternatives, Value hypothesis, Evidence and assumptions, Chosen direction, Non-goals, and Open risks, followed by a handoff naming `brainstorming`.
- Cases `discover-evidence-resumed-handoff` and `discover-handoff-ready` used the clarified ongoing-discovery context. Conversation turn two used the corresponding arm's actual first assistant output rather than fabricated history.

## Prior diagnostic observations

These observations came from earlier revisions and are not promoted to current-final grades:

- A preceding guided revision produced 15 PASS, 1 FAIL, and 2 INCONCLUSIVE results. It was not a final release evaluation.
- Five control and five candidate wording samples were run. The `Current alternatives` field was correct in all five candidate outputs, but overall grades remained INCONCLUSIVE because the fixture was ambiguous.
- One earlier `discover-evidence-resumed-override` scoring attempt timed out, and one diagnosed retry succeeded. A later `discover-handoff-ready` score attempt and its single diagnosed retry both ended in operation errors.
- Earlier blocked batches and failed or unusable records remain provenance only; none was reused or relabeled as PASS.
- Scoring resumed after a local temporary-storage quota was cleared. The earlier service-only attribution is withdrawn, and no upstream outage is asserted.

The wording repeat was targeted and limited. It is not a statistical UX guarantee, and no inference is made for pressure scenarios that were not run against the current-final bytes.

## Scoped draft-review changes

- New entry now distinguishes non-product-intent work, established intent with only solution design remaining, and unresolved product intent. The first returns control without a terminal; only the second passes to `brainstorming`; the third enters discovery.
- A supplied in-progress discovery record is treated as ongoing context. A record showing that the focused checkpoint already survived can close when the terminal condition is met rather than bouncing merely because the four core inputs are established. The skill does not infer a record or consent.
- Registry privacy validation now has an integrated temporary-payload test, and conversation contract tests keep fixture prose solely in the TSV while checking IDs, shape, nonempty turns, and user-only role shape.

The complete current behavioral comparison followed these scoped changes. Deterministic checks still establish structure and privacy boundaries rather than behavioral correctness.

## Blocker and remaining release gate

The full 18-outcome comparison is complete. The behavioral release gate remains open only because the `discover-evidence-resumed-override` result needs independent review of whether the focused preselection checkpoint applies after an accountable user's explicit override. No skill, rubric, fixture, metadata, or infrastructure change is justified by that disputed score.

Until that review is resolved, status remains BLOCKED with 17 accepted current PASS results and 1 INCONCLUSIVE result. No overall release PASS, deployment, or certification is claimed.
