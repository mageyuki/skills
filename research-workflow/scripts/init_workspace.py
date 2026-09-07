#!/usr/bin/env python3
"""Initialize or resume a stable research workspace below its resolved root."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


LIST_FIELDS = {"scope", "out_of_scope", "questions", "source_status", "artifacts"}
STRING_FIELDS = {
    "project_key",
    "topic_slug",
    "title",
    "status",
    "phase",
    "created_at",
    "updated_at",
    "goal",
    "current_question",
    "current_conclusion",
    "next_action",
}


def run_git(cwd: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def sanitize(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\.git$", "", value)
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-._")
    return value or "unknown"


def derive_project_key(cwd: Path) -> str:
    repo_root_raw = run_git(cwd, "rev-parse", "--show-toplevel")
    if not repo_root_raw:
        return "standalone"

    repo_root = Path(repo_root_raw)
    origin = run_git(repo_root, "remote", "get-url", "origin")
    if not origin:
        return f"local--{sanitize(repo_root.name)}"

    owner = ""
    repository = ""
    scp_match = re.match(r"^[^@]+@[^:]+:(.+?)/([^/]+?)(?:\.git)?$", origin)
    if scp_match:
        owner, repository = scp_match.groups()
    else:
        parsed = urlparse(origin)
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2:
            owner, repository = parts[-2], parts[-1]
        elif parts:
            repository = parts[-1]

    if owner and repository:
        return f"{sanitize(owner)}--{sanitize(repository)}"
    return f"local--{sanitize(repo_root.name)}"


def now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def resolve_within_root(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SystemExit(f"Refusing path outside research root: {resolved}") from exc
    return resolved


def validate_manifest(manifest: object) -> dict[str, object]:
    if not isinstance(manifest, dict):
        raise SystemExit("Invalid existing manifest: root must be a JSON object")

    required = {"schema_version"} | LIST_FIELDS | STRING_FIELDS
    for field in sorted(required):
        if field not in manifest:
            raise SystemExit(
                f"Invalid existing manifest: missing required field '{field}'"
            )

    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 2:
        raise SystemExit(
            "Invalid existing manifest: field 'schema_version' must be the integer 2"
        )
    for field in sorted(LIST_FIELDS):
        if not isinstance(manifest[field], list):
            raise SystemExit(
                f"Invalid existing manifest: field '{field}' must be a list"
            )
    for field in sorted(STRING_FIELDS):
        if not isinstance(manifest[field], str):
            raise SystemExit(
                f"Invalid existing manifest: field '{field}' must be a string"
            )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="Stable topic slug")
    parser.add_argument("--title", default="")
    parser.add_argument("--cwd", default=os.getcwd())
    parser.add_argument(
        "--root",
        default=os.environ.get("RESEARCH_HOME", str(Path.home() / ".research")),
    )
    parser.add_argument("--project-key")
    args = parser.parse_args()

    cwd = Path(args.cwd).expanduser().resolve()
    root = Path(args.root).expanduser().resolve()
    slug = sanitize(args.slug)
    key = sanitize(args.project_key) if args.project_key else derive_project_key(cwd)
    target = resolve_within_root(root / key / slug, root)
    stamp = now_iso()
    manifest_path = target / "manifest.json"
    resolve_within_root(manifest_path, root)
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SystemExit(
                "Invalid existing manifest: manifest.json must contain valid JSON"
            ) from exc
        manifest = validate_manifest(manifest)
        manifest["updated_at"] = stamp
    else:
        manifest = {
            "schema_version": 2,
            "project_key": key,
            "topic_slug": slug,
            "title": args.title,
            "status": "active",
            "phase": "orientation",
            "created_at": stamp,
            "updated_at": stamp,
            "goal": "",
            "scope": [],
            "out_of_scope": [],
            "current_question": "",
            "current_conclusion": "",
            "questions": [],
            "source_status": [],
            "artifacts": [
                {"path": "brief.md", "purpose": "Goal and scope", "updated_at": stamp},
                {"path": "state.md", "purpose": "Current research state", "updated_at": stamp},
                {"path": "sources.md", "purpose": "Evidence and freshness ledger", "updated_at": stamp},
                {"path": "assumptions.md", "purpose": "Assumption ledger", "updated_at": stamp},
                {"path": "changes.md", "purpose": "Append-only delta log", "updated_at": stamp},
            ],
            "next_action": "",
        }

    target.mkdir(parents=True, exist_ok=True)
    resolve_within_root(target / "research", root).mkdir(exist_ok=True)
    resolve_within_root(target / "runs", root).mkdir(exist_ok=True)

    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    files = {
        "brief.md": """# Research brief

## Goal

## Decision or deliverable

## Scope

## Out of scope

## Constraints

## Questions
""",
        "state.md": """# Research state

## Phase

orientation

## Current conclusion

## Current question

## Confirmed constraints

## Unresolved questions

## Stale, unavailable, or unauthenticated sources

## Next action
""",
        "sources.md": """# Sources

| ID | Source identity/location | Authority | Retrieved | Freshness window | Scope | Supports | Status | Last error |
|---|---|---|---|---|---|---|---|---|
""",
        "assumptions.md": """# Assumptions

| ID | Assumption | Reason | Confidence | Validation | Status |
|---|---|---|---|---|---|
""",
        "changes.md": f"""# Research changes

## {stamp} — orientation

- Evidence: workspace initialized
- Assumptions:
- Calculations:
- Source freshness:
- Conclusion:
- Open questions:
- Next action: define the goal and orientation questions
""",
    }

    created: list[str] = []
    for name, content in files.items():
        path = target / name
        resolve_within_root(path, root)
        if path.exists():
            continue
        path.write_text(content, encoding="utf-8")
        created.append(name)

    print(target)
    print(f"project_key={key}")
    print(f"topic_slug={slug}")
    print("created=" + (",".join(created) if created else "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
