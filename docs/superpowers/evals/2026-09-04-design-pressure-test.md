# Design Pressure Test 0.1.0 Evaluation Evidence

## Scope

This report compares the same ten frozen pressure scenarios without and with the candidate guidance. It records evaluation evidence only; it makes no deployment, publication, release, or production-approval claim.

## Method

Each original scenario ran once in the candidate-null baseline and once against the current candidate. Generation and scoring used separate fresh isolated processes with the same fixed model configuration. The independent score assessed the actual response against the source scenario and canonical rubric.

The baseline gate required substantive failure rather than absence of unknown labels. All ten baseline responses had a material focused-falsifier, consequence, report-completeness, or design/process-ownership failure.

## Frozen artifacts

| Artifact | SHA-256 | Note |
|---|---|---|
| Case fixture | `b4aa400aa785d947da321e997d58cf938ea48729fdb163f56d2dcf1d1d20b6ff` | Ten scenarios |
| Canonical rubric | `f1c15768e7bb2e856870f70ba131015578b22f06a5f943fb33bc34f855a02cdf` | Unchanged across baseline and current runs |
| Candidate payload | `0788da1823c8e20e302baff621d0398d6340589e0f61c0e761f3ff1fadc2bf6c` | 77 lines |

## Results

`Raw current` preserves the independent score. `Accepted status` records the subsequent evidence assessment without rewriting that score.

| Case | Baseline | Raw current | Accepted status | Current outcome |
|---|---|---|---|---|
| `pressure-clear` | FAIL | PASS | PASS | CLEAR |
| `pressure-revision-required` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-blocked` | FAIL | PASS | PASS | BLOCKED |
| `pressure-explicit-low-risk` | FAIL | PASS | REVIEW_PENDING | BLOCKED |
| `pressure-architectural-trigger` | FAIL | PASS | PASS | BLOCKED |
| `pressure-high-risk-trigger` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-uncertain-trigger` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-no-spec-edit` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-no-self-approval` | FAIL | PASS | PASS | REVISION_REQUIRED |
| `pressure-no-next-process` | FAIL | PASS | PASS | CLEAR |

Raw current scoring is 10 PASS. Accepted status is 9 PASS and 1 REVIEW_PENDING.

## Outcome-form coverage

| Outcome | Count |
|---|---:|
| CLEAR | 2 |
| REVISION_REQUIRED | 5 |
| BLOCKED | 3 |

The current responses used all five canonical report fields and included a focused challenge, falsifying observation, and consequence. They distinguished supplied evidence from inference and gaps, avoided redesign and self-approval, and did not choose the next process. CLEAR remained bounded to the tested assumptions and was not presented as production approval. A justified BLOCKED was scored as valid product behavior.

## Baseline observations

The baseline commonly identified relevant evidence but omitted a concrete falsifying observation or consequence, proceeded despite contradiction, returned a future test plan, or crossed into migration tactics, replacement design, approval procedure, or next-process direction. Individual baseline scoring and diagnostic differences on case 07 ownership and case 09 falsification remain disclosed; other substantive failures independently support both baseline FAIL results.

## Pending review

The raw scorer marked `pressure-explicit-low-risk` PASS after it returned BLOCKED for missing functional proof around recent-first ordering and reset behavior. Review is still needed to decide whether those assumptions were material to the supplied low-risk design or whether the challenge exceeded the requested scope. The raw PASS is preserved and is not converted to FAIL while that question remains open.

## Limits

This is one sample per original case (`n=1`). There were no blind repetitions, so these results provide no statistical guarantee. No guided wording problem was identified, and variance was not assessed; blanket five-run repetition was therefore not triggered. The case 04 scope question awaits review rather than being classified as a wording failure.

No micro-test, refactor run, or meta-test was performed or is claimed. Overall review, deployment, publication, and release decisions remain pending.
