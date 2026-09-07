# Artifact templates

Create only the artifacts required by the research question. `manifest.json` is always required.

## brief.md

```markdown
# Research brief

## Goal
## Decision or deliverable
## Scope
## Out of scope
## Constraints
## Questions
```

## state.md

```markdown
# Research state

## Phase
## Current conclusion
## Current question
## Confirmed constraints
## Unresolved questions
## Stale, unavailable, or unauthenticated sources
## Next action
```

## sources.md

```markdown
# Sources

| ID | Source identity/location | Authority | Retrieved | Freshness window | Scope | Supports | Status | Last error |
|---|---|---|---|---|---|---|---|---|
```

## assumptions.md

```markdown
# Assumptions

| ID | Assumption | Reason | Confidence | Validation | Status |
|---|---|---|---|---|---|
```

## changes.md

Append one entry after each research cycle.

```markdown
# Research changes

## YYYY-MM-DDTHH:MM:SSZ — <phase>

- Evidence:
- Assumptions:
- Calculations:
- Source freshness:
- Conclusion:
- Open questions:
- Next action:
```

Within a cycle, persist detailed evidence, assumptions, calculations, and conclusions first; update their compact `manifest.json` and `state.md` summaries second; append this change entry last. If records conflict, use original evidence, scope, and retrieval times to reconcile them, and leave unresolved discrepancies explicit.

When stopping, use the existing `state.md` sections to record the reason, unresolved questions, and decision impact; mirror those deltas in the final `changes.md` entry. Scope exhaustion can leave material questions unanswered. For an unauthenticated tenant source, retain last-known evidence under `Stale, unavailable, or unauthenticated sources` but do not describe it as current.

## facts.csv

```csv
id,category,item,value,unit,scope,region,source_id,retrieved_at,status,notes
```

## Reproducible calculations

Persist formulas and literal inputs in `calculate.py`, a spreadsheet-like table, or another rerunnable artifact. Record units, currency, region, billing tier, allowances, tax treatment, price date, and exchange-rate date when applicable. Save normalized outputs instead of relying on conversational arithmetic.

## findings.md

```markdown
# Findings

## Recommendation or conclusion
## Verified evidence
## Assumptions and inferences
## Alternatives and trade-offs
## Calculation summary and sensitivity
## Stale or unavailable evidence
## Residual uncertainty and open questions
```

Optional `research/<topic>.md` files hold bounded evidence for one question. Optional `runs/<timestamp>/` directories may hold minimized intermediate material that is not loaded by default.
