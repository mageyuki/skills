# Multi-Agent Skill Installation Design

**Status:** Approved in chat on 2026-09-04

## Goal

Extend the public README from OpenCode-only installation to accurate installation guidance for Claude Code, Codex, Gemini CLI, GitHub Copilot, Cursor, and official Grok Build, while preserving OpenCode's remote registry flow.

## Scope

- Keep the current OpenCode `skills.urls` installation unchanged.
- Document project-level and user-level installation for the six selected agents.
- Present Vercel Labs `skills` CLI as an optional shortcut, not an official vendor mechanism.
- Leave the current `research-workflow` payload and registry version unchanged.
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
2. Optional Vercel Labs CLI installation for all selected agents in the current project.
3. Native local installation table with project, user, and reload guidance.
4. Exact native clone-and-copy commands grouped by compatible directory.

The optional project command is:

```bash
npx skills add mageyuki/skills --skill research-workflow -a claude-code -a codex -a gemini-cli -a github-copilot -a cursor -a grok -y
```

The README will identify this as the Vercel Labs `skills` CLI and link to its documentation. It will not use `-g`, because the CLI's Codex user directory differs from Codex's first-party documentation. It will not use `--all`, because that would install to agents outside the selected scope.

The native fallback will clone the repository and copy the complete `research-workflow/` directory, not only `SKILL.md`, because the skill requires `scripts/` and `references/`. Copy commands will be grouped for Claude Code, the four agents using `.agents/skills/`, and Grok Build so no executable example silently chooses the wrong host directory.

```bash
git clone --depth 1 https://github.com/mageyuki/skills.git mageyuki-skills
```

## Skill Portability Decision

The Agent Skills specification supports this skill's relative `scripts/` and `references/` layout. An attempted behavioral evaluation did not load the candidate and therefore established neither a pass nor a skill failure. On 2026-09-04, the user chose README-only work rather than an unverified payload edit or an expansion into evaluation-infrastructure maintenance. Therefore `research-workflow/`, `index.json`, and registry tests remain unchanged.

## Verification

- Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`.
- Confirm that no skill payload or registry version changed.
- Check README commands, paths, product names, and official links against the persisted research ledger.
- Review each retained implementation task, then perform one final whole-change critical review.

## Failure Handling

- The optional CLI is never the only path; users without Node.js can use native directories.
- Do not claim a remote registry for agents other than OpenCode.
- Do not infer official Grok Build from the presence of `~/.grok`, because a community CLI uses the same directory name.
- Keep the Gemini CLI transition note out of the main procedure unless its official Skills documentation becomes unavailable; the current first-party page still documents Skills.

## Evidence Record

The complete source and freshness ledger is stored outside the repository below `$RESEARCH_HOME`. Material uncertainty remains around Gemini CLI's announced Antigravity transition and Grok Build's absence from the Agent Skills client showcase; both products nevertheless have live first-party Skills documentation as of 2026-09-04.
