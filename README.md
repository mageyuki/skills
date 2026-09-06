# mageyuki skills

## Overview

This repository is a public Agent Skills-compatible collection maintained by mageyuki. OpenCode can consume it as a remote registry; other supported agents can install the same skill directories locally.

## Install

### Install one skill with the CLI

The third-party [Vercel Labs `skills` CLI](https://github.com/vercel-labs/skills/blob/main/README.md) can install one registered skill at a time. Choose the command for the skill you want; do not run all three unless you want all three skills:

```bash
npx skills add mageyuki/skills --skill research-workflow
npx skills add mageyuki/skills --skill intent-discovery
npx skills add mageyuki/skills --skill design-pressure-test
```

`--skill` selects one registered skill. The CLI can prompt for the target agent, or you can specify one with `-a`:

```bash
npx skills add mageyuki/skills --skill intent-discovery -a opencode
```

Installation defaults to the current project. Add `-g` for a user-wide installation. Do not combine a local CLI installation with remote registration of the same skill below.

Selecting a skill does not install workflows it references. `intent-discovery` calls `research-workflow` when research is needed and hands off to a separately supplied `brainstorming` skill; install those separately when needed. This repository does not supply `brainstorming`.

### OpenCode: register all listed skills remotely

As an alternative to selecting individual local copies with `--skill`, add the raw registry root to your OpenCode configuration. This registers every skill listed in this repository's remote index; it does not perform `--skill` selection:

```jsonc
{
  "skills": {
    "urls": [
      "https://raw.githubusercontent.com/mageyuki/skills/main/"
    ]
  }
}
```

Do not combine this with local copies of the same skills. Fully quit and restart OpenCode after changing its configuration.

### Native install for Claude Code, Codex, Gemini CLI, GitHub Copilot, Cursor, and Grok Build

Clone the repository and copy the complete skill directory so its `scripts/` and `references/` remain available:

```bash
git clone --depth 1 https://github.com/mageyuki/skills.git mageyuki-skills
skill=intent-discovery
```

The other valid values are `research-workflow` and `design-pressure-test`. In the same shell, the selected `skill` value applies to whichever one agent-group pair you run below.

| Agent | Project directory | User directory | Reload or check |
|---|---|---|---|
| [Claude Code](https://code.claude.com/docs/en/skills) | `.claude/skills/` | `~/.claude/skills/` | Changes are watched; restart only if the directory was created after startup. |
| [Codex](https://developers.openai.com/codex/build-skills) | `.agents/skills/` | `~/.agents/skills/` | Restart if the skill does not appear. |
| [Gemini CLI](https://geminicli.com/docs/cli/skills/) | `.agents/skills/` | `~/.agents/skills/` | Run `/skills reload`. |
| [GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | `.agents/skills/` | `~/.agents/skills/` | CLI: run `/skills reload`; cloud agent: commit the project skill. |
| [Cursor](https://cursor.com/docs/context/skills) | `.agents/skills/` | `~/.agents/skills/` | Restart Cursor if the skill is not discovered. |
| [Grok Build](https://docs.x.ai/build/features/skills-plugins-marketplaces) | `.grok/skills/` | `~/.grok/skills/` | Run `grok inspect`; disk changes reload automatically. |

For a project installation, run only the pair for your agent group:

```bash
# Claude Code
mkdir -p .claude/skills
cp -R "mageyuki-skills/$skill" .claude/skills/

# Codex, Gemini CLI, GitHub Copilot, or Cursor
mkdir -p .agents/skills
cp -R "mageyuki-skills/$skill" .agents/skills/

# Grok Build
mkdir -p .grok/skills
cp -R "mageyuki-skills/$skill" .grok/skills/
```

For a user installation, run only the pair for your agent group:

```bash
# Claude Code
mkdir -p "$HOME/.claude/skills"
cp -R "mageyuki-skills/$skill" "$HOME/.claude/skills/"

# Codex, Gemini CLI, GitHub Copilot, or Cursor
mkdir -p "$HOME/.agents/skills"
cp -R "mageyuki-skills/$skill" "$HOME/.agents/skills/"

# Grok Build
mkdir -p "$HOME/.grok/skills"
cp -R "mageyuki-skills/$skill" "$HOME/.grok/skills/"
```

`Grok Build` means the official xAI `grok` coding agent from [x.ai/cli](https://x.ai/cli/).

## Available skills

| Skill | Version | Purpose |
|---|---:|---|
| `research-workflow` | `0.1.0` | Durable, evidence-first workflows for multi-source research, comparisons, estimates, architecture research, incidents, and refreshes. |
| `intent-discovery` | `0.1.0` | Gentle, evidence-aware discovery when product intent remains materially unresolved. |
| `design-pressure-test` | `0.1.0` | Focused adversarial testing of material assumptions in an approved design when explicitly requested or risk-triggered. |

## Updates and versions

The `main` branch is the latest channel. Every change to a skill payload must bump that skill's semantic version in `index.json`, because OpenCode uses the version to decide when to refresh its cache. Reviewed release tags preserve immutable source revisions.

Local installations are updated with `npx skills update` when installed by the optional CLI, or by pulling the source clone and copying the skill directory again.

After bootstrap, publish an update by pushing a reviewed commit to a temporary candidate branch, waiting for the `validate` status on that exact SHA, and then fast-forwarding `main` to the same SHA without merge or rebase.

## Adding a skill

Add a skill in its own directory with a `SKILL.md`, list every payload file in `index.json`, assign an initial semantic version, add focused tests, and add a catalog entry above. Removing or renaming a skill requires an explicit migration note.

## Availability

OpenCode needs network access to fetch the registry index at startup. If the registry is unavailable, OpenCode does not enumerate a stale remote-skill cache; consumers should treat the skill as unavailable and retry after service is restored. Local agent installations continue using their installed copy until explicitly updated.

## Security

Skills are executable instructions that can direct tool use. Review a skill before enabling it and report unsafe instructions or path-handling vulnerabilities as described in [SECURITY.md](SECURITY.md).

## License

This repository is licensed under the [MIT License](LICENSE).
