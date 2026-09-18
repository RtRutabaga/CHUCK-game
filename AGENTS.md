# AGENTS.md — CHUCK Development Rules

This repository is worked on by Sean, Claude Code, and Codex.

## Authority Order

When documents conflict, use this order:

1. Direct instruction from Sean in the current task.
2. `docs/development/CURRENT-PHASE.md` for current scope and acceptance criteria.
3. `docs/design/GAME-BIBLE.md` for the core game vision.
4. Topic-specific design supplements in `docs/design/`.
5. Architecture documentation describing the current codebase.
6. Campaign source material in `docs/source/campaigns/`.
7. Agent inference.

Campaign notes are source material, not automatic game requirements.

## Core Development Rules

- Work on one coherent feature or tightly related feature slice at a time.
- Keep the game runnable.
- Inspect the existing implementation before editing.
- Preserve working systems unless the current task requires changing them.
- Prefer modular, reusable systems over one-off hacks.
- Prefer data-driven content where repeated content is expected.
- Maintain stable interfaces between systems.
- Do not perform unrelated cleanup or broad rewrites.
- Do not add dependencies without explaining why they are needed.
- Do not silently change controls, scale, tone, art direction, or game rules.
- Do not invent missing creative decisions when they materially affect the game.
- Small technical implementation choices may be made autonomously when they preserve the documented vision.

## Chuck Rules That Must Not Drift

Chuck is approximately one foot tall. Chuck is a rat. Chuck wears an oversized purple open jacket. Chuck does not speak and has no internal monologue.

Chuck is calm, patient, fearless, compassionate, observant, and persistent.

Chuck is not a conventional hero and does not become increasingly powerful.

Chuck's small size is a gameplay and level-design rule, not a cosmetic trait.

Do not describe or implement Chuck as a giant rat relative to the game world. His D&D source stat block used the creature category “Giant Rat,” but the game’s authoritative scale is approximately one foot tall.

## Design Guardrails

Exploration is more important than combat. Environmental storytelling is preferred over exposition. Humor is deadpan and restrained. The world may be absurd; Chuck is not a cartoon character. The world should remain worth saving.

Impossible geography is not portal travel. Regions are internally believable; their connections are wrong.

Avoid traditional equipment progression, inventory-driven design, quest logs, rarity systems, stat screens, and unnecessary UI unless Sean explicitly changes the design.

## Agent Relay Workflow

Only one coding agent should make changes at a time.

Sessions can end without warning on a usage limit. The repository is the
handoff; chat is not. `docs/development/TWO-AGENT-GIT-WORKFLOW.md` covers
session sizing, committing at every green point, and picking up a dirty tree.

Before editing:

1. Read this file.
2. Read the **Baton** block at the top of `docs/development/HANDOFF.md`.
3. Read `docs/README.md`.
4. Read `docs/development/CURRENT-PHASE.md`.
5. Read the relevant design supplement.
6. Inspect the current code and recent Git history.
7. State the intended implementation boundary.

After editing:

1. Run the game or the most relevant available checks.
2. Verify the requested feature.
3. Review the diff for unrelated changes.
4. Update the Baton in `docs/development/HANDOFF.md`.
5. Commit the completed pass with a clear commit message.

Do not leave a session holding uncommitted work. Commit at every green
point rather than once at the end.

The next agent should begin from the repository state and Git history, not assumptions about the previous agent's chat.

## Stop Conditions

Stop and report instead of continuing when the task requires a major unjustified architecture rewrite, design documents materially conflict, a creative decision would alter the game's identity, the game cannot be returned to a runnable state, the task expands substantially beyond the active phase, or implementation would violate a phase scope restriction.

Do not solve scope problems by quietly building future phases.
