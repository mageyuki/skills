# Intent discovery evaluation: blocked work in progress

**Status: BLOCKED**

This document preserves incomplete evaluation work. It is not a release PASS, behavioral certification, or deployment record. The current draft is not deployed or certified, and no current-final behavioral PASS is claimed.

## Current artifacts

- Skill: `intent-discovery` version `0.1.0`, 82-line draft, with `SKILL.md` as its registered payload.
- Skill SHA-256: `086864b280e8a1d13addc964641c35945af1d2b6921a0d633d22e6a124bc8dec`.
- Cases SHA-256: `bdb8fb968a981968f32c0d1e6020cc9cf9531105e1a8b2d954f7462c1c93141e`.
- Conversations SHA-256: `174d19ca71ef95709bfb61dd8f9b74c2357d28feaa127843026e3b9ccdc246a9`.
- Canonical rubric SHA-256: `e23c7d4e3647d33a7675f02f00f71cdfd2c882b5504bd2b20c6559fbdf68514a`.
- Registry metadata and catalog entry remain at version `0.1.0`.

## Current-final validation

Prior-variant grades are not carried forward to the current-final bytes. `NOT_RUN` means no usable current-final result exists.

| Fixture ID | Baseline | Guided | Current-final release assessment |
|---|---|---|---|
| `control-established-solution-design` | NOT_RUN | NOT_RUN | NOT_RUN |
| `control-direct-bugfix` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-problem-uncertain` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-target-user-uncertain` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-value-hypothesis-uncertain` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-direction-uncertain` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-three-direction-cap` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-research-required` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-research-failure` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-evidence-resumed-handoff` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-evidence-resumed-override` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-no-go` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-deferred` | NOT_RUN | NOT_RUN | NOT_RUN |
| `discover-handoff-ready` | INCONCLUSIVE — operation error | NOT_RUN | NOT_RUN |
| `question-cadence` | NOT_RUN | NOT_RUN | NOT_RUN |
| `research-resumption` | NOT_RUN | NOT_RUN | NOT_RUN |

For the clarified `discover-handoff-ready` fixture, baseline generation succeeded, but scoring failed with an operation error on the first attempt and on one diagnosed manual retry. This is `INCONCLUSIVE`, not a product PASS or FAIL. No final guided run exists for that fixture. No fresh baseline or guided run exists for the latest `discover-evidence-resumed-handoff` fixture.

## Prior diagnostic observations

These observations came from earlier revisions and are not promoted to current-final grades:

- Unguided rubric-v2 scoring produced 2 PASS and 16 FAIL results.
- A preceding guided revision produced 15 PASS, 1 FAIL, and 2 INCONCLUSIVE results. It was not a final release evaluation.
- Five control and five candidate wording samples were run. The `Current alternatives` field was correct in all five candidate outputs, but overall grades remained INCONCLUSIVE because the fixture was ambiguous.
- Cases `discover-evidence-resumed-handoff` and `discover-handoff-ready` were later clarified. The latest comparison is incomplete.
- Real multi-turn history was tested on earlier revisions; the current-final rerun remains pending.
- One earlier `discover-evidence-resumed-override` scoring attempt timed out, and one diagnosed retry succeeded. A later `discover-handoff-ready` score attempt and its single diagnosed retry both ended in operation errors.

The wording repeat was targeted and limited. It is not a statistical UX guarantee, and no inference is made for pressure scenarios that were not run against the current-final bytes.

## Scoped draft-review changes

- New entry now distinguishes non-product-intent work, established intent with only solution design remaining, and unresolved product intent. The first returns control without a terminal; only the second passes to `brainstorming`; the third enters discovery.
- A supplied in-progress discovery record is treated as ongoing context. A record showing that the focused checkpoint already survived can close when the terminal condition is met rather than bouncing merely because the four core inputs are established. The skill does not infer a record or consent.
- Registry privacy validation now has an integrated temporary-payload test, and conversation contract tests keep fixture prose solely in the TSV while checking IDs, shape, nonempty turns, and user-only role shape.

No external behavioral rerun followed these scoped changes. Status remains BLOCKED, and the deterministic checks do not establish behavioral correctness.

## Blocker and remaining release gate

External scoring is persistently blocked, so further external scoring work has stopped. No infrastructure, skill, rubric, fixture, or metadata change is justified by that external failure.

The behavioral release gate remains open. Current-final baseline and guided validation must be completed for every fixture before any release PASS, deployment, or certification claim. This work-in-progress report exists only to preserve the state of the evaluation while that work is externally blocked.
