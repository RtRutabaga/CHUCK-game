# CHUCK

CHUCK is a pixel-art exploration game about a one-foot-tall rat crossing a
world whose regions have been joined together incorrectly.

He is calm, patient and fearless, he does not speak, and he never becomes
more powerful. The regions are each internally believable; it is their
connections that are wrong.

**The game is complete.** It can be played start to finish in a browser, on a
desktop, a phone, or an Xbox.

## Play it

| | |
|---|---|
| **Desktop and Xbox** | <https://rtrutabaga.github.io/CHUCK-game/> |
| **Phone** (touch controls) | <https://rtrutabaga.github.io/CHUCK-game/mobile/> |

The first visit downloads about 11 MB. On a phone, hold it in landscape; for a
full-screen game with no browser bars, use **Share → Add to Home Screen** and
launch it from that icon.

## Saving

There are no save files. **SAVE GAME gives you a twelve-character code**, and
**LOAD CODE** takes one back — on any machine, in any of the builds. A code is
the save; nothing is kept for you.

Codes are forgiving on the way in: lower case, missing dashes, and a letter O
where a zero belongs all work.

## Controls

| | Keyboard | Controller | Touch |
|---|---|---|---|
| Move | WASD / arrows | stick or d-pad | the pad, corners go diagonal |
| Talk / examine | E / Enter | B | INSPECT |
| Jump | Space | A | JUMP |
| Scratch | F | X | SCRATCH |
| Pause | Esc | Y | the pause button |

## Running from source

```bash
cd chuck/chuck
pip install -r requirements.txt
python main.py
```

The test suite is plain modules of `test_*` functions — there is no pytest and
none is wanted:

```bash
python tools/run_tests.py
```

It prints `modules: N of N` and then any failures. Read the module count, not
only the failure line: a module that fails to import contributes no tests, and
a green-looking run can be hiding one.

## Repository

- `chuck/chuck/` — the game: `src/`, `assets/`, `data/`, `tests/`, `tools/`
- `docs/design/` — the Game Bible and its supplements, the creative authority
- `docs/development/` — phase contracts, the agent handoff, the web build
- `AGENTS.md` — the rules this repository is worked on under

The browser build is produced by `chuck/chuck/tools/build_web.py` and published
by GitHub Actions on every push to `main`, to both URLs above.

---

This is unofficial Fan Content permitted under the Fan Content Policy. Not
approved/endorsed by Wizards. Portions of the materials used are property of
Wizards of the Coast. ©Wizards of the Coast LLC.
