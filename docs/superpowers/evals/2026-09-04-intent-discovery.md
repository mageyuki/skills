# Intent discovery evaluation: task comparison accepted

**Status: TASK COMPARISON ACCEPTED — PUBLICATION PENDING**

This document records the accepted current task comparison. It is not evidence that whole-project publication, final registry deployment, or certification is complete.

## Current artifacts

- Skill: `intent-discovery` version `0.1.0`, 82-line draft, with `SKILL.md` as its registered payload.
- Skill SHA-256: `086864b280e8a1d13addc964641c35945af1d2b6921a0d633d22e6a124bc8dec`.
- Cases SHA-256: `bdb8fb968a981968f32c0d1e6020cc9cf9531105e1a8b2d954f7462c1c93141e`.
- Conversations SHA-256: `174d19ca71ef95709bfb61dd8f9b74c2357d28feaa127843026e3b9ccdc246a9`.
- Canonical rubric SHA-256: `e23c7d4e3647d33a7675f02f00f71cdfd2c882b5504bd2b20c6559fbdf68514a`.
- Registry metadata and catalog entry remain at version `0.1.0`.

## Current task comparison

All 18 current guided outcomes were generated and evaluated: 14 single-turn cases plus two two-turn conversations. The accepted current assessment is 18 PASS: 17 directly accepted PASS results plus 1 review-adjudicated PASS. This is not a claim that all 18 raw scorer records were PASS. Conversation turns are shown separately below so those totals reconcile.

The accepted baseline aggregate is 1 PASS, 16 FAIL, and 1 DISPUTED. `discover-value-hypothesis-uncertain` is DISPUTED because an earlier record has an overall PASS while the latest record has a criterion FAIL. The later failure is not characterized as token-only, neither record is overwritten, and the variance is not additional authoring justification. The other 16 baseline failures are substantive.

| Fixture ID | Baseline | Raw guided record | Accepted task assessment |
|---|---|---|---|
| `control-established-solution-design` | FAIL | PASS | PASS — discovery was skipped and established intent was handed to `brainstorming` |
| `control-direct-bugfix` | PASS | PASS | PASS — discovery was declined and control returned for diagnosis |
| `discover-problem-uncertain` | FAIL | PASS | PASS — one problem-framing question |
| `discover-target-user-uncertain` | FAIL | PASS | PASS — one target-user question |
| `discover-value-hypothesis-uncertain` | DISPUTED — earlier overall PASS; later criterion FAIL | PASS | PASS — justified `NO_GO` |
| `discover-direction-uncertain` | FAIL | PASS | PASS — one direction question |
| `discover-three-direction-cap` | FAIL | PASS | PASS — one direction question without expanding to ten ideas |
| `discover-research-required` | FAIL | PASS | PASS — one question on the decision-changing evidence gap |
| `discover-research-failure` | FAIL | PASS | PASS — `RESEARCH_REQUIRED` |
| `discover-evidence-resumed-handoff` | FAIL | PASS | PASS — `USER_OVERRIDE` with a complete brief and named handoff |
| `discover-evidence-resumed-override` | FAIL | Evidence/convergence FAIL — no preselection challenge | PASS — review-adjudicated `USER_OVERRIDE` |
| `discover-no-go` | FAIL | PASS | PASS — `NO_GO` |
| `discover-deferred` | FAIL | PASS | PASS — `DEFERRED` |
| `discover-handoff-ready` | FAIL | PASS | PASS — `HANDOFF_READY` with a complete brief and named handoff |
| `question-cadence` | t1 FAIL; t2 FAIL | t1 PASS; t2 PASS | PASS — both turns used one question and carried context forward |
| `research-resumption` | t1 FAIL; t2 FAIL | t1 PASS; t2 PASS | PASS — t1 `RESEARCH_REQUIRED`; t2 resumed from new evidence, opposed the leader, and asked one question |

## Review adjudication

The raw case 11 record retains an Evidence/convergence FAIL because no preselection challenge was present. Scoped review accepted the behavior because the accountable user had already chosen: the assistant did not make a new selection, but recorded `USER_OVERRIDE`, preserved the unresolved gaps, supplied all eight Direction brief fields, and named `brainstorming` as the next owner. The accepted PASS does not rewrite the raw criterion result, and neither the skill nor rubric changed for this adjudication.

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

## Publication state

The task comparison is accepted with 18 current PASS outcomes: 17 directly accepted and 1 accepted through scoped review. Prior variance and ambiguous checks remain qualified diagnostic observations rather than statistical certification.

Whole-project integration and publication remain pending. No final registry publication, deployment, or certification is claimed.
