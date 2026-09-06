---
name: design-pressure-test
description: Use when an approved design is explicitly requested for pressure testing, or is architectural, high-risk, or uncertain with material untested assumptions.
---

# Design Pressure Test

## Purpose

Pressure-test the material assumptions in an approved design, report one bounded outcome, and stop.

**Core principle:** Challenge assumptions, not people. Test only what could materially change the design decision.

## Entry contract

Begin only when both are supplied:

1. An approved design or specification.
2. Either a direct request from the current user, or an architectural, high-risk, or uncertain design with a material untested assumption.

An approved design alone is not a trigger. Authority or deadline pressure from someone else is not a direct user request.

If either required input is absent, name the missing input and stop rather than inventing approval, risk, or assumptions.

## Recipe

1. Identify only material assumptions.
   - Include assumptions about value, feasibility, safety, integrity, dependencies, migration, rollback, or operations only when failure could require a design change or prevent responsible assessment.
   - Ignore immaterial details and already-supported claims except to record why their bounded evidence is adequate.
2. Test each material assumption.
   - State one strongest focused challenge.
   - State the concrete observation that would falsify the assumption.
   - State the consequence if it fails.
3. Assess the supplied record.
   - Separate supplied facts and observations from inference and missing evidence.
   - Compare the actual evidence with the falsifying observation. Never invent tests, results, guarantees, or consent.
4. Select exactly one outcome.
   - Contradicted material assumption or necessary design change: `REVISION_REQUIRED`.
   - Necessary evidence is unavailable, so responsible assessment cannot finish: `BLOCKED`.
   - Every material assumption has adequate bounded support: `CLEAR`.
5. Return the five-field report below and stop.

## Report

- **Outcome**: `CLEAR`, `REVISION_REQUIRED`, or `BLOCKED`.
- **Assumptions tested**: For each material assumption, include the focused challenge and falsifying observation.
- **Evidence and observations**: Distinguish supplied facts, observations, inference, and gaps.
- **Consequence**: State what follows if the challenged assumption fails.
- **Required revision or blocker**: Name the defective assumption or exact necessary evidence; use "None within the stated scope" for a clear bounded result.

For `REVISION_REQUIRED`, name what assumption or design claim must change. Do not supply a replacement design, code, API choice, or approval procedure.

For `BLOCKED`, name the unavailable evidence and why it is necessary. A justified block is a responsible result, not a failure to perform the test.

## Outcomes

### CLEAR

No material blocker remains within the assumptions, scope, and evidence tested. This is not blanket production approval.

### REVISION_REQUIRED

Supplied evidence contradicts a material assumption, or the consequence requires the approved design to change.

### BLOCKED

A material assumption cannot be responsibly assessed because necessary evidence is unavailable.

## Boundaries

Evaluate the supplied approved design now; do not substitute a future test plan, new script, or new schema.

Keep challenges focused. Do not accumulate speculative blockers or reward criticism for being broader or harsher.

Do not reopen early intent discovery, edit the specification, redesign it, approve revisions, self-approve a replacement, prescribe implementation choices, or choose or invoke the next process.

Return the report to the design owner and stop.
