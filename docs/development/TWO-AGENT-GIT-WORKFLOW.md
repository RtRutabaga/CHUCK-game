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

---

## Sessions End Without Warning

Both agents run on usage limits. A session can stop mid-sentence, with
work half-done and nothing committed. This has already happened to both
of them on this repository. Plan for it rather than hoping.

The rule that follows from it: **the repository is the handoff. Chat is
not.** An incoming agent must never need the outgoing agent's
conversation, because it may not exist any more and cannot be read
across models anyway.

### Never end holding uncommitted work

Commit at every green point, not at the end of the task. A slice that
produces four commits is better than one that produces one, because
three of them survive an interruption.

If a session is cut off with a dirty tree, the next agent's first job is
§ Reconciling A Dirty Tree below — not new work.

### Keep the baton current as you go

`HANDOFF.md` opens with a **Baton** block. Write it when you *start* a
task, not when you finish. Update it at each commit. It costs almost
nothing and it is the only thing that survives a hard stop.

The baton is overwritten every pass. It is not a log. The log is the
rest of the file.

---

## Session Size

Size a slice by its blast radius, not by how it sounds. "Remove the
Ashtray" is one idea and four hundred files; "add a save-code field" is
one idea and three. Only the second is a session.

Before starting, state:

- the files you expect to touch, roughly, and how many
- the commits the slice will break into
- what "done" looks like for each commit

**If the answer is more than about twenty files or more than about four
commits, it is not one session.** Split it, do the first part, and put
the rest in the baton as the next bounded task. Say you are splitting it
rather than quietly doing half.

Mechanical sweeps — a rename across the tree, a test rewrite, a marker
removal — are the usual offenders. They read as one decision and land as
hundreds of edits. Budget them as their own session, and commit the
sweep separately from the change that motivated it.

---

## Write Down What Was Expensive To Learn

If a fact cost real work to establish, it belongs in the repository
before the session ends, or the next agent pays for it again.

Put it in `DECISIONS.md` if it constrains future work. Put it in the
baton if it only matters to the next pass. Examples worth the line:

- a generator no longer reproducing its shipped map
- an asset budget, measured
- a test that is slow, flaky, or load-bearing in a surprising way
- an approach that was tried and abandoned, and why

"I measured it and it was fine" is worth writing down too. It stops the
next agent measuring it again.

---

## Reconciling A Dirty Tree

When `git status` is not clean at the start of a session, stop and work
out whose work it is before touching anything.

1. Read the baton. If it names the work in progress, follow it.
2. If the baton does not explain it, assume it is the other agent's
   unfinished pass. Do not build on top of it and do not commit it as
   part of something else.
3. Report what is there and ask, unless Sean has already said to take it
   over.

Finishing someone else's half-done pass without being asked is how two
agents produce one incoherent commit.

---

## Cheap Starts

An incoming agent should be able to begin from three things:

1. The **Baton** block at the top of `HANDOFF.md`.
2. `git log --oneline -5` and `git status`.
3. One named document, if the task needs one.

That is the target. If a task genuinely cannot be started from those,
the baton was not written well enough — say so, and fix the baton as
part of the pass.

Do not read the whole of `HANDOFF.md` to start a task. The passes below
the baton are history, kept for when something specific needs
explaining. Older history lives in `HANDOFF-ARCHIVE.md` and is not part
of a normal start.

## Handoff Rule

Record facts in the **Baton** block at the top of `HANDOFF.md`: branch, base
commit, what this pass is doing, what is committed so far, what is still
dirty, how it was verified, known issues, and the next bounded task.

Overwrite the baton; do not append to it. When a pass finishes, move its
summary down into the log below and leave the baton describing what comes
next.

## Git Rule

Commit after each completed, tested pass. Do not bundle unrelated changes.

Example commit messages:

- `feat: add Waterdeep guard interaction`
- `feat: add reusable tutorial proximity prompt`
- `feat: add sewer map transition`
- `feat: teach jump at astral gap`
- `feat: add rat scratch combat tutorial`
- `feat: return sewer exit to Waterdeep docks`
