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

Never infer current tenant state from public documentation. If authenticated tenant evidence cannot be refreshed, preserve its last-known value, mark it stale or unauthenticated, identify affected conclusions, and stop that research branch.

## Bounded retrieval

Before retrieval, state the question or falsifiable hypothesis. Request only the required tenant, project, environment, region, date range, fields, page size, and total result count. Prefer aggregates and summaries over raw streams. Stop when authoritative sources converge, remaining uncertainty is bounded, more detail cannot change the decision, or the agreed scope is exhausted.

Keep credentials, tokens, unnecessary personal data, and raw secret-bearing payloads out of artifacts. External create, update, delete, publish, deploy, or synchronization actions require explicit user authorization and confirmation of success.
