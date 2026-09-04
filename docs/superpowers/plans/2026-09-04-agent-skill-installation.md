# Multi-Agent Skill Installation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add sourced installation instructions for Claude Code, Codex, Gemini CLI, GitHub Copilot, Cursor, and official Grok Build without changing the existing skill payload.

**Architecture:** Keep OpenCode's native remote registry as the first install path. Add one optional cross-agent installer command and one dependency-free native copy flow backed by a compact table of recommended project/user directories and reload checks.

**Tech Stack:** Markdown, Git, existing Python `unittest` registry checks

**Spec:** `docs/superpowers/specs/2026-09-04-agent-skill-installation-design.md`

## Global Constraints

- Document exactly Claude Code, Codex, Gemini CLI, GitHub Copilot, Cursor, and official xAI Grok Build in the new local-install section.
- Keep the existing OpenCode `skills.urls` JSON and restart instruction unchanged.
- Treat Vercel Labs `skills` CLI as optional and third-party; native directories must remain a complete fallback.
- Do not mention Devin, Windsurf, community `grok-cli`, Grok Chat, or the Grok API in the README install procedures.
- Do not modify `research-workflow/`, `index.json`, or registry behavior; the evaluator did not establish a skill failure.
- Do not add dependencies, installers, helper scripts, or speculative compatibility layers.
- Keep README prose in English to match the repository.

---

### Task 1: Document Multi-Agent Installation

**Files:**
- Modify: `README.md:3-21`
- Modify: `README.md:29-41`

**Interfaces:**
- Consumes: the existing OpenCode registry URL, the `research-workflow/` directory layout, and the approved first-party path matrix in the spec.
- Produces: one public README install contract that works without the optional CLI and does not alter skill payload/version semantics.

- [ ] **Step 1: Confirm the current documentation gap**

Use a repository content search for `Claude Code`, `Grok Build`, and `npx skills add` in `README.md`.

Expected: no matches. The existing OpenCode remote registry block must be present.

- [ ] **Step 2: Replace the overview and install section with the approved structure**

Use this content, preserving the existing registry URL exactly:

````markdown
## Overview

This repository is a public Agent Skills-compatible collection maintained by mageyuki. OpenCode can consume it as a remote registry; other supported agents can install the same skill directories locally.

## Install

### OpenCode

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

### Claude Code, Codex, Gemini CLI, GitHub Copilot, Cursor, and Grok Build

#### Optional installer

The third-party [Vercel Labs `skills` CLI](https://skills.sh/docs/cli) can install `research-workflow` for all six agents in the current project:

```bash
npx skills add mageyuki/skills --skill research-workflow -a claude-code -a codex -a gemini-cli -a github-copilot -a cursor -a grok -y
```

#### Native install

Clone the repository and copy the complete skill directory so its `scripts/` and `references/` remain available:

```bash
git clone --depth 1 https://github.com/mageyuki/skills.git mageyuki-skills
```

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
cp -R mageyuki-skills/research-workflow .claude/skills/

# Codex, Gemini CLI, GitHub Copilot, or Cursor
mkdir -p .agents/skills
cp -R mageyuki-skills/research-workflow .agents/skills/

# Grok Build
mkdir -p .grok/skills
cp -R mageyuki-skills/research-workflow .grok/skills/
```

For a user installation, run only the pair for your agent group:

```bash
# Claude Code
mkdir -p "$HOME/.claude/skills"
cp -R mageyuki-skills/research-workflow "$HOME/.claude/skills/"

# Codex, Gemini CLI, GitHub Copilot, or Cursor
mkdir -p "$HOME/.agents/skills"
cp -R mageyuki-skills/research-workflow "$HOME/.agents/skills/"

# Grok Build
mkdir -p "$HOME/.grok/skills"
cp -R mageyuki-skills/research-workflow "$HOME/.grok/skills/"
```

`Grok Build` means the official xAI `grok` coding agent from [x.ai/cli](https://x.ai/cli/).
````

- [ ] **Step 3: Clarify local update and availability behavior**

In `Updates and versions`, keep the current OpenCode version-cache paragraph and add:

```markdown
Local installations are updated with `npx skills update` when installed by the optional CLI, or by pulling the source clone and copying the skill directory again.
```

Replace `Availability` with:

```markdown
## Availability

OpenCode needs network access to fetch the registry index at startup. If the registry is unavailable, OpenCode does not enumerate a stale remote-skill cache; consumers should treat the skill as unavailable and retry after service is restored. Local agent installations continue using their installed copy until explicitly updated.
```

- [ ] **Step 4: Verify the documentation contract**

Search `README.md` and require all of these literal values:

```text
Claude Code
Codex
Gemini CLI
GitHub Copilot
Cursor
Grok Build
.claude/skills/
.agents/skills/
.grok/skills/
~/.claude/skills/
~/.agents/skills/
~/.grok/skills/
-a claude-code
-a codex
-a gemini-cli
-a github-copilot
-a cursor
-a grok
https://code.claude.com/docs/en/skills
https://developers.openai.com/codex/build-skills
https://geminicli.com/docs/cli/skills/
https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
https://cursor.com/docs/context/skills
https://docs.x.ai/build/features/skills-plugins-marketplaces
```

Confirm `README.md` contains none of `Devin`, `Windsurf`, `grok-cli`, `Grok Chat`, or `Grok API`. Confirm the OpenCode raw URL is unchanged. Run `git status --short` and `git diff --name-only a6c06ce`; neither output may show a path below `research-workflow/` or `index.json`.

- [ ] **Step 5: Run repository verification**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
git diff --check
```

Expected: 31 tests run, the externally configured registry test may skip, all executed tests pass, and `git diff --check` prints nothing.

- [ ] **Step 6: Prepare the exact retained diff**

Inspect `git status`, `git diff`, and recent commits. Stage only:

```text
README.md
```

Do not commit without explicit user authorization. When authorized, use commit message `docs: add multi-agent skill installation`.
