# Scoped test inventory

Use this reference only for the inventory/pruning scope the user authorized.
Do not infer a subsystem sweep from an ordinary feature or review request.

1. Identify the baseline, affected tests, production owners/callers and contracts.
   Run relevant available baseline checks; record failures or inability to run.
2. Read the candidate assertions and overlapping evidence. Decide retain, repair,
   consolidate or delete by actual detectable failure, not test names/counts.
   Group cases sharing a contract; no per-declaration ledger is required.
3. Before removal, identify the remaining owner and useful assertions to preserve.
   Keep uncertain candidates with an evidence gap. Transfer meaningful protection
   before deleting redundant proof; policy prose checks do not prove agent behavior.
   Check that no helper, export or fixture used only by the removed tests is left
   orphaned, and clean it up in the same batch.
4. Edit only within the approved scope and run the necessary affected checks.
   An intentional mutation can resolve uncertain detection ability; it is not a
   mandatory stage for every inventory. If used, save/restore exact current bytes,
   check restoration and rerun; never leave a deliberate defect behind.
5. Return the contract-to-coverage mapping, actual results and material limits in
   the existing report. Use the final review the project or host already requires,
   with findings judged for fact/impact/scope. No zero-findings or separate
   audit-review loop. Baseline failures do not authorize unrelated repairs.

Complete when the scoped decisions have evidence and the retained contracts are
covered. Disclose unresolved limits instead of claiming unsupported preservation.

Criteria adapted from OpenClaw at 3195fba90643c3897c538f2f6891c405331bee9c:
[campaign](https://github.com/openclaw/openclaw/blob/3195fba90643c3897c538f2f6891c405331bee9c/.agents/skills/test-audit/CAMPAIGN.md) and
[audit reference](https://github.com/openclaw/openclaw/blob/3195fba90643c3897c538f2f6891c405331bee9c/.agents/skills/test-audit/references/audit.md).
