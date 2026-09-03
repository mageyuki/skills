---
name: research-workflow
description: Use when a question needs iterative multi-source research, cost estimation, SaaS or product comparison, architecture research, incident investigation, source freshness tracking, or a repeated evidence refresh.
---

# Research Workflow

## Overview

Iterative research uses a durable workspace as the system of record; conversation is temporary.

**Core principle:** initialize manifest-first state, orient cheaply, deepen only identified gaps, and synthesize from persisted evidence.

## Choose the mode

| Request | Mode |
|---|---|
| One supplied URL summary | Direct work |
| One local function explanation | Direct work |
| One known configuration answer | Direct work |
| One deterministic calculation | Direct work |
| One exact mechanical edit | Direct work |
| Multi-source comparison, uncertain estimate, architecture or incident investigation, or evidence refresh | Iterative research |

## Manifest-first recipe

1. **Locate or initialize.** Reuse the stable topic workspace; if absent, initialize before deep retrieval.
   Use the `Base directory for this skill` reported by the skill loader. Resolve
   `scripts/init_workspace.py` below that directory, then invoke it with Python 3
   and the stable topic slug. Never guess a config, cache, or home-directory path.
2. **Define the brief.** Record goal, decision, scope, exclusions, constraints, and 3–7 questions.
3. **Orientation.** Make 2–4 high-yield repository/task and primary-documentation reads. Record knowns, gaps, stale evidence, and next action.
4. **Deepen selectively.** Investigate one gap using the narrowest authoritative source. Keep retrieval bounded by tenant, project, region, dates, fields, pages, and result count. Update source identity, authority, retrieval time, freshness, claims, and errors.
5. **Persist the contract.** Separate evidence, inference, assumptions, reproducible calculations, conclusions, and open questions. Store numerical formulas and inputs in a rerunnable artifact.
6. **Synthesize from artifacts.** Re-read state and evidence, reconcile conflicts, state sensitivity and uncertainty, then update manifest and change log.
7. **Refresh by delta.** Resume the workspace, revalidate stale material, preserve last-known values after failures, and report only evidence, assumption, calculation, freshness, conclusion, and open-question deltas.

## Boundaries

- Write only below `$RESEARCH_HOME` or its `~/.research` fallback. Read repository/task sources and explicitly declared external sources.
- Never write credentials, raw secret state, unnecessary personal data, or unbounded payloads; minimize sensitive fields.
- Tenant facts require authenticated evidence. On failure, mark `unauthenticated` and stop that branch; never substitute public or stale data.
- External publication, mutation, or synchronization requires explicit authorization and confirmed success.

## Quick reference

| Need | Artifact/action |
|---|---|
| Current machine state | `manifest.json` (schema version 2) |
| Conclusion and next action | `state.md` |
| Evidence and freshness | `sources.md` |
| Assumptions and confidence | `assumptions.md` |
| Cycle deltas | `changes.md` |
| Detailed forms | [Artifact templates](references/artifact-templates.md) |
| Fields and update rules | [Manifest schema](references/manifest-schema.md) |
| Source choice | [Source priority](references/source-priority.md) |

## Example

For a SaaS cost comparison, initialize `monitoring-cost`, orient with current pricing and limits, record region/currency/date assumptions, calculate annual totals from persisted inputs, deepen billing or residency gaps, and report the recommendation plus uncertainty.

## Common mistakes

- Searching before creating or resuming the manifest.
- Substituting polished prose for persisted evidence.
- Retrieving without a recorded gap or bound.
- Mixing facts, assumptions, and calculations.
- Repeating a full refresh instead of its delta.
