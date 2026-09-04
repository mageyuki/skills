# Multi-Agent Skill Installation Design

**Status:** Approved in chat on 2026-09-04

## Goal

Extend the public README from OpenCode-only installation to accurate installation guidance for Claude Code, Codex, Gemini CLI, GitHub Copilot, Cursor, and official Grok Build, while preserving OpenCode's remote registry flow.

## Scope

- Keep the current OpenCode `skills.urls` installation unchanged.
- Document project-level and user-level installation for the six selected agents.
- Present Vercel Labs `skills` CLI as an optional shortcut, not an official vendor mechanism.
- Verify whether the current `research-workflow` skill wording is portable before changing its payload.
- Link claims to first-party product documentation.

## Exclusions

- Devin and Windsurf, by user choice.
- Community projects named `grok-cli`.
- Grok Chat and the Grok API, which do not load coding-agent skills.
- Generic instruction files, MCP configuration, marketplaces, and organization-wide deployment.

## Research Findings

All selected coding agents have first-party `SKILL.md` support. OpenCode is the only selected agent with a native remote URL registry matching this repository. The other agents load local skill directories.

| Agent | Recommended project directory | Recommended user directory | First-party source |
|---|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Codex | `.agents/skills/` | `~/.agents/skills/` | [Codex skills](https://developers.openai.com/codex/build-skills) |
| Gemini CLI | `.agents/skills/` | `~/.agents/skills/` | [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) |
| GitHub Copilot | `.agents/skills/` | `~/.agents/skills/` | [Copilot agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| Cursor | `.agents/skills/` | `~/.agents/skills/` | [Cursor skills](https://cursor.com/docs/context/skills) |
| Grok Build | `.grok/skills/` | `~/.grok/skills/` | [Grok Build skills](https://docs.x.ai/build/features/skills-plugins-marketplaces) |

Gemini CLI, Copilot, Cursor, and Grok Build document additional compatible directories. The README will lead with one recommended directory per scope to avoid presenting equivalent choices as separate procedures.

Grok means the official xAI Grok Build CLI/TUI installed from `x.ai/cli`. It does not mean Grok Chat, the Grok API, or the unrelated `superagent-ai/grok-cli` project.

## README Design

The `Install` section will use this order:

1. OpenCode remote registry configuration and restart instruction.
2. Optional Vercel Labs CLI installation for all selected local agents.
3. Native local installation table with project, user, and reload guidance.
4. One shared clone-and-copy procedure for users who do not use the optional CLI.

The optional project command is:

```bash
npx skills add mageyuki/skills --skill research-workflow -a claude-code -a codex -a gemini-cli -a github-copilot -a cursor -a grok -y
```

The user-level form adds `-g`. The README will identify this as the Vercel Labs `skills` CLI and link to its documentation. It will not use `--all`, because that would install to agents outside the selected scope.

The native fallback will clone the repository and copy the complete `research-workflow/` directory, not only `SKILL.md`, because the skill requires `scripts/` and `references/`:

```bash
git clone --depth 1 https://github.com/mageyuki/skills.git mageyuki-skills
mkdir -p <skills-directory>
cp -R mageyuki-skills/research-workflow <skills-directory>/
```

The table will make clear that `<skills-directory>` is the parent directory shown for the selected agent and scope.

## Skill Portability Decision

The current skill says to use the exact phrase `Base directory for this skill` reported by the loader. That phrase is OpenCode-specific, while the Agent Skills specification describes supporting files relative to the skill root.

Before editing the payload, run reference-skill application scenarios against the current text:

1. The host supplies a concrete skill directory without OpenCode's phrase. The agent must resolve `scripts/init_workspace.py` below it.
2. The host supplies only the loaded `SKILL.md` path. The agent must derive the sibling `scripts/` path.
3. The host exposes no skill location. The agent must report the missing location rather than guess a config, cache, or home path.

If the current wording passes all scenarios, leave the skill payload and `index.json` unchanged. If a scenario fails because of the OpenCode-specific phrase, replace it with loader-neutral guidance to resolve `scripts/init_workspace.py` relative to this skill's directory. A payload edit requires a semantic version bump from `0.1.0` to `0.1.1`.

## Verification

- Record baseline scenario outputs before any skill edit.
- If edited, rerun the same scenarios with the modified skill and record the changed behavior.
- Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`.
- Run registry validation against the pre-change commit so a payload edit without a version bump fails.
- Check README commands, paths, product names, and official links against the persisted research ledger.
- Review each retained implementation task, then perform one final whole-change critical review.

## Failure Handling

- The optional CLI is never the only path; users without Node.js can use native directories.
- Do not claim a remote registry for agents other than OpenCode.
- Do not infer official Grok Build from the presence of `~/.grok`, because a community CLI uses the same directory name.
- Keep the Gemini CLI transition note out of the main procedure unless its official Skills documentation becomes unavailable; the current first-party page still documents Skills.

## Evidence Record

The complete source and freshness ledger is stored outside the repository below `$RESEARCH_HOME`. Material uncertainty remains around Gemini CLI's announced Antigravity transition and Grok Build's absence from the Agent Skills client showcase; both products nevertheless have live first-party Skills documentation as of 2026-09-04.
