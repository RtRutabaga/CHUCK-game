# Two-Agent Git Workflow

Claude Code and Codex work on the same repository as a relay team. They do not work simultaneously.

Git is the shared memory of implementation. Repository documentation is the shared memory of the game vision.

## Standard Cycle

1. Sean gives one agent a focused task.
2. The agent reads repo documentation and current Git state.
3. The agent implements one coherent pass.
4. The agent tests the result.
5. The agent updates `HANDOFF.md`.
6. The agent commits.
7. Sean playtests or reviews.
8. Sean gives feedback to the next agent.
9. The next agent reads the repository, recent commits, and handoff before editing.

## Suggested Role Bias

Claude Code is the default technical lead for architecture-heavy implementation and larger feature construction.

Codex is the default reviewer/fixer for inspecting implementation, debugging, targeted improvements, testing edge cases, tightening code boundaries, and clearly bounded follow-ups.

These are role biases, not permanent ownership boundaries. Sean may direct either agent.

## One Agent at a Time

Finish, test, update the handoff, and commit before switching agents.

## Task Size

Use one feature or vertical slice per task.

Good Phase 2 tasks include adding the Waterdeep guard interaction, reusable proximity prompts, sewer grate choice and transition, sewer map shell, jump tutorial obstacle, rat scratch tutorial, or sewer exit/Waterdeep return state.

Do not use vague tasks such as “Finish Phase 2 and improve anything else you notice.”

## Handoff Rule

Record facts: branch, latest relevant commit, completed task, files changed, systems changed, verification, known issues, and recommended next bounded task.

## Git Rule

Commit after each completed, tested pass. Do not bundle unrelated changes.

Example commit messages:

- `feat: add Waterdeep guard interaction`
- `feat: add reusable tutorial proximity prompt`
- `feat: add sewer map transition`
- `feat: teach jump at astral gap`
- `feat: add rat scratch combat tutorial`
- `feat: return sewer exit to Waterdeep docks`
