# Design Pressure Test 0.1.0 Evaluation Evidence

## Scope

This report compares the ten frozen pressure scenarios in a candidate-null baseline with the final 79-line candidate and records the focused case 04 wording experiment. It records evaluation evidence only; it makes no deployment, publication, release, or production-approval claim.

## Method

Each original scenario ran once in the candidate-null baseline and once against the final candidate. Generation and scoring used separate fresh isolated processes with the same fixed model configuration. Raw scores and diagnostic accepted statuses were recorded separately.

The focused case 04 experiment used five no-guidance controls, five runs with the original 77-line candidate, and five runs with the corrected 79-line candidate. Current-candidate composite validation covered all 15 current generation records: ten original scenarios plus five focused case 04 runs.

The baseline gate required substantive failure rather than absence of unknown labels. All ten baseline responses had a material focused-falsifier, consequence, report-completeness, or design/process-ownership failure.

## Artifact identity

| Artifact | SHA-256 | Note |
|---|---|---|
| Case fixture | `b4aa400aa785d947da321e997d58cf938ea48729fdb163f56d2dcf1d1d20b6ff` | Ten scenarios; unchanged throughout |
| Canonical rubric | `f1c15768e7bb2e856870f70ba131015578b22f06a5f943fb33bc34f855a02cdf` | Unchanged throughout |
| Original guided candidate | `0788da1823c8e20e302baff621d0398d6340589e0f61c0e761f3ff1fadc2bf6c` | 77 lines |
| Final candidate | `cfd9092034aedc44f2feec186ff1706d7b32541dd3cddd5c6963fed19a8ed0c6` | 79 lines; unchanged after final runs |

## Final comparison

| Case | Baseline | Final raw | Accepted status | Final outcome |
|---|---|---|---|---|
| `pressure-clear` | FAIL | PASS | PASS | CLEAR |
| `pressure-revision-required` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-blocked` | FAIL | PASS | PASS | BLOCKED |
| `pressure-explicit-low-risk` | FAIL | PASS | PASS | CLEAR |
| `pressure-architectural-trigger` | FAIL | PASS | PASS | BLOCKED |
| `pressure-high-risk-trigger` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-uncertain-trigger` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-no-spec-edit` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-no-self-approval` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-no-next-process` | FAIL | PASS | PASS | CLEAR |

The final original-scenario comparison is 10 baseline FAIL, 10 final raw PASS, and 10 accepted PASS.

## Outcome-form coverage

| Outcome | Count |
|---|---:|
| CLEAR | 3 |
| REVISION_REQUIRED | 5 |
| BLOCKED | 2 |

The final responses used all five canonical report fields with a focused challenge, falsifying observation, and consequence. They distinguished supplied evidence from inference and gaps, avoided redesign and self-approval, and did not choose the next process.

## Case 04 history and correction

The original 77-line guided case 04 response retains its raw PASS for provenance, but its accepted status remains FAIL because it elevated routine user-interface implementation checks to a material design blocker without supplied evidence of a specific design-changing risk. That result has not been overwritten or reclassified.

The focused experiment preserved the progression: all five controls returned future test plans; the original 77-line candidate produced three overblocking BLOCKED outcomes and two CLEAR outcomes; and the corrected 79-line candidate produced five bounded CLEAR outcomes, each raw and diagnostically accepted PASS.

The correction filters absent low-level implementation artifacts without weakening material requirements. Explicit safety, integrity, durability, migration, rollback, dependency, data-loss, and architectural evidence gaps still produced BLOCKED or REVISION_REQUIRED where appropriate. CLEAR remains bounded to the tested assumptions and is not production approval.

## Limits and status

The original scenarios have one final sample each (`n=1`); the focused case 04 variants have five samples each (`n=5`). These results provide no statistical guarantee, meta-test result, universal PASS claim, or assurance beyond the frozen scenarios, rubric, and candidate.

The task comparison is accepted. A committed scoped review and whole-project publication remain pending separate actions.
