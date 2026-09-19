# Two-Agent Git Workflow

Claude Code and Codex work on the same repository as a relay team. They do not work simultaneously.

Git is the shared memory of implementation. Repository documentation is the shared memory of the game vision.

## Standard Cycle

1. Sean gives one agent a focused task.
2. The agent reads the baton, `git worktree list`, and current Git state.
3. The agent implements one coherent pass.
4. The agent tests the result.
5. The agent updates `HANDOFF.md`.
6. The agent commits.
7. Sean playtests or reviews.
8. Sean gives feedback to the next agent.
9. The next agent reads the repository, recent commits, and handoff before editing.

This is the cycle when it completes. It frequently does not: Sean
switches agents when one runs out of usage, which lands mid-pass, at no
particular step, with no warning to either of them. Everything below is
written for that case rather than this one.

## Suggested Role Bias

Claude Code is the default technical lead for architecture-heavy implementation and larger feature construction.

Codex is the default reviewer/fixer for inspecting implementation, debugging, targeted improvements, testing edge cases, tightening code boundaries, and clearly bounded follow-ups.

These are role biases, not permanent ownership boundaries. Sean may direct either agent.

## One Agent at a Time

Only one agent edits the repository at a time. Where you can, finish,
test, update the baton and commit before the handover.

Where you cannot — and a usage limit gives no say in the matter — the
handover happens anyway, at whatever point you had reached. That is not
a failure of discipline, it is the normal case. The discipline is making
that moment survivable: commit at every green point, keep the baton
written ahead of the work rather than behind it, and assume every
sentence you are part-way through is one you will not finish.

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

A task is one feature or one vertical slice. "Finish Phase 2 and
improve anything else you notice" is not a task; it is a way of finding
out later that two agents improved the same thing differently.

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

## Work You Cannot See

`git status` in this repository does not show everything an agent has
done. Codex works in a **linked worktree**, not in the main checkout:

    C:/Users/ashsm/.codex/worktrees/<id>/CHUCK-game

When a Codex session stops mid-pass, the main tree stays perfectly clean
and the half-finished work is invisible to anyone standing in it. This
has already stranded two passes on this repository, and a clean
`git status` is exactly what makes it convincing.

So the first command of a session is not `git status`:

```bash
git worktree list
```

Every linked worktree it prints is somewhere work can be hiding. Check
each one that is not the main checkout, without leaving the main
checkout:

```bash
git -C <worktree path> status --short
git -C <worktree path> log --oneline -3
```

A dirty worktree is an unfinished pass. Read the baton, then the two
sections below.

### Taking work out of another agent's worktree

Do not edit in it and do not commit from it. It may be mid-thought, and
it is not yours. Lift the change out as a patch and apply it in the main
checkout:

```bash
git -C <worktree path> diff HEAD > pass.patch
git apply --check pass.patch && git apply pass.patch
```

`diff HEAD`, not plain `diff`: a bare `git diff` shows only unstaged
changes, so anything the other agent had staged goes silently missing
and you recover half a pass believing you have all of it. Untracked
files are in neither — check `git -C <worktree path> status --short` for
`??` lines and copy those across by hand.

`--check` first, always. Compare base commits before you start
(`git -C <worktree path> rev-parse HEAD`): a worktree sitting on an
older commit may not apply cleanly, and a half-applied patch is worse
than no patch.

Then leave the worktree exactly as you found it. It still holds the
original, which is a free backup until its owner returns, and tidying
someone else's checkout is not yours to do. Say in the baton that the
work has landed and name the commit, so the returning agent discards its
copy instead of applying it twice.

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

## Inheriting A Half-Finished Pass

The temptation is to read the diff, agree with it, and build on top.

**Run the full suite before you add anything to it.** Once your changes
are mixed with theirs, no failure can be attributed to either. A suite
run costs minutes; a misattributed failure costs a session. This has
already happened here: an incoming pass added a `@property` immediately
above an existing one and silently stole its decorator, turning a
property into an always-truthy bound method and breaking four unrelated
tests. It was cheap to find only because the suite was run first.

Then read the whole diff against `HEAD`, not only the parts you expect:

```bash
git diff HEAD
```

Sweeps and generated edits over-reach in ways that look fine where you
are looking — a regex that appends a stray paren to three unrelated
statements, a test rewrite that drops a block of dialogue nobody meant
to touch. The full diff is the only place that shows up.

When a test fails against an inherited pass, decide which of the two is
wrong before you fix either. Sometimes the pass is right and the test is
stale — the tavern threshold moved because the art is genuinely three
tiles wide. Say which it was in the commit message.

---

## Cutting Content Stales The Tests That Count It

Removing a map, a route or an NPC is never only the removal. Somewhere a
test asserts a total about a registry the thing was in, and that total
will still be yesterday's number tomorrow.

After any cut, search the suite for the counts before committing —
totals, lengths, and any registry the cut thing belonged to. Removing
the Feywild tea table left three behind: a mushroom-map count, an
arrival count, and a save slot whose map no longer existed. They stayed
red across several later commits because nobody looked and nobody wrote
the suite result down.

Fix the counts in the same commit as the cut, and say in a comment *why*
the number moved. "Nine, not ten: the tea table was cut" saves the next
person from re-deriving it, and from assuming the number is arbitrary.

A cut that retires a save slot has a further rule of its own, because
the slot is part of the wire format. See `src/systems/save_registry.py`.

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

**State the suite result as a number, every time.** "191 of 191", or
"190 of 191, `test_treasure_handoffs` failing, pre-existing, not mine".
"Tests pass" is not a handoff. A suite goes red one commit at a time,
and when nobody writes the count down, several passes land on top of a
failure before anyone notices whose it was — which is how four failures
accumulated here unremarked.

If you did not run it, write *that*. An honest "not run" costs the next
agent one command. A confident "verified" that was not costs them the
afternoon, and costs Sean the trust that makes the relay work at all.

Overwrite the baton; do not append to it. When a pass finishes, move its
summary down into the log below and leave the baton describing what comes
next.

## Git Rule

Commit after each completed, tested pass. Do not bundle unrelated changes.

Subjects are plain imperative sentences about the game, not tagged
conventional-commit lines. Match what is already in `git log`:

- `Complete guarded Waterdeep north boundary`
- `Remove Feywild tea table and connect Rootways to Needle Garden`
- `Make the code the only save`
- `Preserve final encounter progress when Chuck respawns`

The body is where a pass earns its keep. Say what was wrong, what you
changed, and — most valuable of all — what you considered and rejected,
because that is the part the next agent cannot reconstruct from the
diff.

---

## Sean's Machine

Facts that are not in the code and cost something to rediscover:

- The web build needs Python 3.12 via `chuck/chuck/.venv-web`, not the
  3.14 that runs the suite. `WEB-README.md` has the commands.
- Sean often has a preview server running on port 8000 and a browser tab
  open on it. **Check for one before starting your own**, and do not
  kill stray `http.server` processes to tidy up — that takes his live
  preview down without warning. It has happened.
- Preview at `127.0.0.1`, never `localhost`: pygbag treats `localhost`
  as a dev host and behaves differently.
