# mageyuki skills

## Overview

This repository is a public OpenCode-compatible registry of portable skills maintained by mageyuki. The registry root is served directly, with each skill directory acting as both reviewed source and downloadable payload.

## Install

Add the raw registry root to your OpenCode configuration:

```jsonc
{
  "skills": {
    "urls": [
      "https://raw.githubusercontent.com/mageyuki/skills/main/"
    ]
  }
}
```

Fully quit and restart OpenCode after changing its configuration.

## Available skills

| Skill | Version | Purpose |
|---|---:|---|
| `research-workflow` | `0.1.0` | Durable, evidence-first workflows for multi-source research, comparisons, estimates, architecture research, incidents, and refreshes. |

## Updates and versions

The `main` branch is the latest channel. Every change to a skill payload must bump that skill's semantic version in `index.json`, because OpenCode uses the version to decide when to refresh its cache. Reviewed release tags preserve immutable source revisions.

After bootstrap, publish an update by pushing a reviewed commit to a temporary candidate branch, waiting for the `validate` status on that exact SHA, and then fast-forwarding `main` to the same SHA without merge or rebase.

## Adding a skill

Add a skill in its own directory with a `SKILL.md`, list every payload file in `index.json`, assign an initial semantic version, add focused tests, and add a catalog entry above. Removing or renaming a skill requires an explicit migration note.

## Availability

OpenCode needs network access to fetch the registry index at startup. If the registry is unavailable, OpenCode does not enumerate a stale remote-skill cache; consumers should treat the skill as unavailable and retry after service is restored.

## Security

Skills are executable instructions that can direct tool use. Review a skill before enabling it and report unsafe instructions or path-handling vulnerabilities as described in [SECURITY.md](SECURITY.md).

## License

This repository is licensed under the [MIT License](LICENSE).
