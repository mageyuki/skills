# Source priority and retrieval bounds

Choose the most specific authoritative source capable of answering the current recorded gap.

| Need | Preferred source | Fallback |
|---|---|---|
| Repository behavior | Checked-out implementation and repository documentation | Repository history at a declared revision |
| Product behavior, API, or syntax | Current versioned first-party specification | Official release notes or vendor documentation |
| Architecture limits and service guarantees | First-party architecture, quota, and service-level documentation | Clearly labeled authoritative support material |
| Tenant configuration, telemetry, or inventory | Authenticated tenant-specific read source | User-provided current export |
| Pricing | Current first-party pricing page or API | Current first-party quote with its effective date |
| Background or independent context | Primary publication or standards body | Clearly labeled secondary source |

## Source record

For every material source, record:

- stable ID, name, URL/repository path/integration identity, and authority;
- retrieval time, applicable freshness window, and `fresh`, `stale`, `unavailable`, `unauthenticated`, or `superseded` status;
- tenant, project, environment, region, version, and date scope;
- supported claims and the last retrieval error, when present.

Never infer current tenant state from public documentation. If required authentication is absent or expired, preserve the last-known evidence, mark it unauthenticated, identify affected conclusions, and stop that research branch. Never present the retained value as current or substitute public data for tenant state.

## Bounded retrieval

Before retrieval, state the question or falsifiable hypothesis. Request only the required tenant, project, environment, region, date range, fields, page size, and total result count. Prefer aggregates and summaries over raw streams.

## Stopping criteria

- **Sufficient evidence:** stop when authoritative sources converge and residual uncertainty cannot change the decision.
- **Scope exhausted:** stop at the agreed boundary, but keep material unanswered questions and their decision impact explicit; exhaustion does not mean every question is answered.
- **Authentication unavailable:** stop the affected tenant branch and follow the preservation rules above.

Record the stop reason, unresolved questions, and decision impact in the existing `state.md` sections and final `changes.md` entry.

Keep credentials, tokens, unnecessary personal data, and raw secret-bearing payloads out of artifacts. External create, update, delete, publish, deploy, or synchronization actions require explicit user authorization and confirmation of success.
