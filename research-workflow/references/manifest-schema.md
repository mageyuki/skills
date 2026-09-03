# Manifest schema

`manifest.json` is the compact machine-readable state for one stable research topic. Detailed evidence belongs in the artifact files.

## Required fields (schema version 2)

```json
{
  "schema_version": 2,
  "project_key": "",
  "topic_slug": "",
  "title": "",
  "status": "active",
  "phase": "orientation",
  "created_at": "",
  "updated_at": "",
  "goal": "",
  "scope": [],
  "out_of_scope": [],
  "current_question": "",
  "current_conclusion": "",
  "questions": [],
  "source_status": [],
  "artifacts": [],
  "next_action": ""
}
```

Use ISO-8601 UTC timestamps. Use empty strings or arrays for unknown values and record the gap as an open question; do not invent a value.

## Question entry

```json
{
  "id": "Q1",
  "question": "",
  "priority": "high",
  "status": "open",
  "answer_summary": "",
  "evidence_ids": []
}
```

Question status is `open`, `investigating`, `answered`, `blocked`, or `not_needed`.

## Source status entry

```json
{
  "id": "S1",
  "name": "",
  "location": "",
  "authority": "first-party",
  "retrieved_at": "",
  "freshness_window": "",
  "scope": "",
  "supports": [],
  "status": "fresh",
  "last_error": ""
}
```

Source status is:

- `fresh`: retrieved within the relevant freshness window;
- `stale`: last-known evidence could not be refreshed;
- `unavailable`: the source could not be reached;
- `unauthenticated`: required authentication is absent or expired;
- `superseded`: newer authoritative evidence replaced it.

## Artifact entry

```json
{
  "path": "facts.csv",
  "purpose": "Normalized pricing inputs",
  "updated_at": ""
}
```

## Update rules

- Preserve stable question and source IDs.
- Update entries instead of duplicating them.
- Never erase a last-known value solely because refresh failed.
- Mark replaced evidence superseded rather than deleting its history.
- Update `updated_at`, current state, source status, artifacts, and next action after each cycle.
- Keep detailed facts, assumptions, calculations, and deltas in their dedicated artifacts.
