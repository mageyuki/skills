---
name: intent-discovery
description: Use when any of the problem, target user, value hypothesis, or product direction is materially unresolved.
---

# Intent Discovery

## Overview

Discover a bounded, evidence-aware product direction before solution design.

**Core principle:** advance one decision at a time from supplied facts, explicit assumptions, and the user's judgment.

## Classify

Classify only at new entry. On later turns, or when an in-progress discovery record is supplied, resume its current step; newly supplied facts update the picture but do not restart classification. If the supplied record shows that the focused checkpoint already survived, close with `HANDOFF_READY` when its condition is met instead of bouncing merely because all four core inputs are now established. Do not invent a discovery record or user consent.

At new entry without such a record, build the current picture from the conversation: problem, target user, value hypothesis, and product direction. Current alternatives are today's incumbent tools or workarounds, not candidate product directions. Use supplied alternatives; do not invent them. Use current alternatives to test the value hypothesis.

- If the task is not a product-intent decision, such as a concrete defect with known expected behavior, say discovery does not apply and return control without a closing token.
- If all core inputs are established and only solution design remains, say discovery is not needed and pass the established intent to `brainstorming` without a closing token.
- If any core intent input is materially unresolved, continue discovery.
- The current user who is accountable for the decision may explicitly ask to continue discovery. Pressure attributed to a sponsor, manager, peer, or other third party does not make that choice for them.

## Ongoing turns

Use this shape while discovery remains open:

1. Carry forward the relevant fact or assumption already supplied.
2. State briefly which decision it affects.
3. Ask exactly one gentle, decision-relevant question, then wait.

Ground the question only in supplied facts. If the user has not said interviews, user contact, or a workaround exists, ask without presupposing any of them.

An unanswered question keeps discovery open; it is never a closing state. Do not replace the question with a feature proposal, pilot plan, or solution design.

## Discover

1. **Frame.** Resolve the highest-impact gap among problem, target user, current alternatives, and value hypothesis.
2. **Diverge.** When framing is sufficient, compare no more than three product directions. Keep them at outcome level, without solution details.
3. **Check evidence.** Separate supplied facts from assumptions. If an external fact could change the direction, use `research-workflow` only for that gap. Never invent evidence or consent.
4. **Resume.** When evidence arrives, continue from the existing context and resolve only the next material gap.
5. **Oppose, then select.** Immediately before selection, state the strongest focused reason the leading direction could be wrong and test it against the evidence. If user judgment is needed, ask that one question and wait. Select only after this checkpoint survives.

## Terminal states

Close only when one condition below is true. Emit exactly one closing token. For `HANDOFF_READY` and `USER_OVERRIDE`, the same response contains the token, the complete eight-field Direction brief, and a final handoff line naming `brainstorming` as the next owner.

### HANDOFF_READY

Evidence supports one direction and it survives the focused checkpoint. Emit `HANDOFF_READY`, provide the Direction brief, and pass it to `brainstorming` for design.

### RESEARCH_REQUIRED

A decision-changing fact is missing, or relevant research failed or is unavailable. Emit `RESEARCH_REQUIRED`, name the evidence gap, and stop without a Direction brief.

### NO_GO

Evidence leaves no candidate with a defensible value case. Emit `NO_GO`, summarize why, and stop without a Direction brief.

### DEFERRED

The current user deliberately pauses selection. Emit `DEFERRED`, preserve what would resume discovery, and stop without a Direction brief.

### USER_OVERRIDE

The accountable current user deliberately chooses progress despite unresolved evidence. Emit `USER_OVERRIDE`, preserve the gap, assumptions, and override, provide the Direction brief, and pass it to `brainstorming`. This is a direction choice, not an instruction to keep discovery open.

## Direction brief

Use this only for `HANDOFF_READY` or `USER_OVERRIDE`. Fill it from the conversation and research; distinguish evidence from assumptions. If material core context is still missing, stay ongoing and ask one question rather than inventing a field or closing blindly.

- **Problem:**
- **Target user:**
- **Current alternatives:**
- **Value hypothesis:**
- **Evidence and assumptions:**
- **Chosen direction:**
- **Non-goals:**
- **Open risks:**

Keep the chosen direction user-informed and product-level. `brainstorming` owns solution design and approval; this brief does not choose implementation, architecture, APIs, or dependencies.
