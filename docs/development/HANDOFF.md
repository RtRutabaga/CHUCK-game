# Agent Handoff

<!-- Read the Baton. Do not read the rest of this file to start a task.
     Deeper history is in HANDOFF-ARCHIVE.md. See TWO-AGENT-GIT-WORKFLOW.md. -->

## Baton

**Claude, 2026-09-19: mobile save-code entry, and the phase sequence
closed.** A phone can now resume a game. Two independent ways in, and
`src/` is untouched by the second.

The shell one is the good one: the phone's *own* keyboard, raised by a
real HTML field in `/mobile/`, outside the iframe. SDL never sees a
keystroke, so there is no question about whether a synthesised key event
produces text on the Python side. The code goes in through the paste
door the load page already polls, and OS long-press-paste works for
free. Three methods on `tools/browser_clipboard.js` carry it:
`isPasteEnabled()` (the game's own signal, set when the load page opens
-- the shell reads it rather than tracking scenes), `offerPaste(text)`,
and `pastePending()`. That last one is a handshake, not decoration: the
game drains key events *before* it polls for a paste, so an Enter sent
in the same breath reaches a field that is still empty. The shell waits
for the code to be collected, then presses.

**Why not an on-screen keyboard in `title_scene`:** `src/` has no
pointer input at all -- nothing reads a mouse or a touch. Drawing one
would mean building that first, inverting two scale steps to hit-test,
and then either showing it to desktop players or giving the game a
"this is a phone" branch, which is the fork `/mobile/` exists to avoid.
Sean raised splitting into two pages/two builds, and it would have
answered the desktop objection cleanly; it was not needed, because the
phone's keyboard only exists for HTML inputs and the game is a canvas.
Putting entry in the shell is what makes the native keyboard reachable
at all.

The `src/` one is a four-line fallback: `K_UP`/`K_DOWN` now dial in
`CodeEntry.handle_event`. The dial was built for "a player without a
keyboard" but only a controller could reach it, because the load page
gates it on `using_controller` and the touch shell emulates a keyboard.
**Do not fix that by loosening the gate.** The dial reads actions;
`move_up` carries W and `interact` carries E, and W, S and E are all
letters in the save-code alphabet, so a keyboard player would find the W
in their code dialling and the E submitting. Hanging it off the arrow
keys, which produce no character, has no collision to have.
`test_code_entry.py` pins that reasoning so it does not get "simplified"
back.

`tests/test_mobile_code_entry.py` is the new seam test: it holds the
shell and the bridge to the same method names, exactly as
`test_mobile_touch_controls.py` holds the buttons to `KEY_BINDINGS`. A
rename in either file would break the phone silently. The touch-control
test caught the new Enter button unprompted, which is the seam working.

Checks: **193 of 193**, and the shell's JavaScript driven in a browser
against a stub exposing the real bridge -- the panel tracks the game's
signal, a typed code is collected before Enter arrives, lower case and
dashes pass through for `normalise`, refusals behave, and all eight
original buttons still dispatch.

**Copy out, not just paste in.** Saving on a phone reaches
`navigator.clipboard.writeText` inside the iframe, and the worry was
that the shell's buttons dispatch *synthetic* key events, which do not
normally carry the transient user activation the clipboard requires.
Measured inside the frame at the moment the game would copy: the event
is untrusted (`isTrusted: false`) but activation is present
(`userActivation.isActive: true`), because a real tap on the parent
propagates it to a same-origin frame. So the mechanism is sound. It
could not be proven end to end -- the browser pane denies clipboard
writes to the parent frame too, so its refusal says nothing about a
phone. The iframe now also states `allow="clipboard-read;
clipboard-write"`: a no-op where the default `self` allowlist already
covers it, insurance where a browser is stricter.

**The two pages now point at each other.** Nothing detects a device. The
desktop page carries a small link to `/mobile/` that removes itself
inside a frame, because `/mobile/` iframes that very page -- left alone
it would offer to nest another shell. A link rather than a redirect, at
Sean's call: user-agent sniffing would have to be right about the Xbox
browser. JUMP and INSPECT were swapped on the touch pad, also his call.

**Sean's phone pass, 2026-09-19.** He played on a phone and said the
mobile page works; whether that included a save-code resume specifically
was not confirmed, so do not record it as tested until he says so.
Outstanding from the same pass: **no audio on `/mobile/`**, while
**PC and Xbox audio have been working all along** -- so the browser
build's audio is fine and this is the shell, not the game.

Ruled out already: audio is built and shipped (`build_web.py` converts
every WAV master to OGG), `runtime.py`'s `audio_path` swaps the suffix
on emscripten so lookups resolve, and the default levels are 8 of 10,
not zero.

The live suspect is that **the iframe has never received a trusted user
gesture**. On PC and Xbox the player interacts with the game page
directly; in the shell every tap lands on the parent overlay and reaches
the game as a synthetic key event. Browsers unlock audio on a genuine
gesture. Two things were measured and neither settles it: a tap on a
shell button *does* give the iframe transient activation
(`userActivation.isActive` true) although the event is untrusted, so a
spec-compliant browser should allow `resume()`; but the browser pane
creates its AudioContext already `running`, so a phone's suspended state
could not be reproduced there. iOS Safari is stricter than the spec
about Web Audio unlock.

Diagnostics put to Sean, cheapest first: the iPhone silent switch (it
mutes Web Audio in Safari), and tapping the *middle* of the screen away
from any button -- the overlay is `pointer-events: none` there, so that
tap passes through to the iframe and is the one trusted gesture
available today. **If audio starts after that tap, the diagnosis is
confirmed** and the fix is an unlock bridge: a helper beside
`browser_clipboard.js` that tracks the AudioContext and exposes a
`resume`, which the shell calls from inside a real tap handler in the
parent. Deliberately not built yet -- not while the silent switch is
still a live explanation.

**The silent switch was the answer, and it is now handled.** iOS files a
page's sound as "ambient" by default, which is what silent mode is for;
music and video apps declare otherwise. `tools/browser_audio.js` now
sets `navigator.audioSession.type = "playback"` (Safari 16.4+), which
says this is the main content and stops the switch applying. It is
injected before the clipboard script because it must precede the audio
context the wasm build creates. The trade, accepted deliberately:
playback audio interrupts other apps rather than mixing under them, and
stops in the background.

**Full screen is two answers.** Safari on iPhone has no Fullscreen API,
so no button can hide the bars there -- do not add one and assume it
works. Where the API exists the shell has a button that also tries
`screen.orientation.lock`; where it does not, the button removes itself
and the panel shows the only iOS route, Share -> Add to Home Screen,
backed by `mobile/manifest.webmanifest` with display fullscreen and
landscape.

**Diagonals on the phone (224173a).** Sean could not move diagonally.
Four touch buttons never could: a pointer belongs to the element it
lands on until it lifts, so a thumb between up and left sent up alone.
Microsoft's touch guidance is explicit for a 2D game with eight
directions -- an 8-way d-pad, not a joystick, with multiple directions
active together -- so the pad is now read as one control. Angle from the
centre picks one of eight sectors past a dead zone, a diagonal holds
both arrows, and sliding re-reads the angle so a direction changes
without lifting. Cardinals get 50 degrees against the diagonals' 40,
because eight equal sectors make a clean "up" hard and menus want up.

That pass also fixed a lost-press bug in the pad *and* the plain
buttons: `setPointerCapture` throws once the pointer has gone, and it
ran before the press, so the throw ate the input. **Press first, follow
after** -- worth remembering for any control added later.

**COPY on the quit warning (01de8dc).** Shared with the save page
through `_copy_now`, so the two cannot drift. The confirm panel grew to
128px for the third option; those numbers are constants beside each
other so the fit test reads what the drawing uses. `test_pause_menu`
pressed confirm options by index and now finds them by name.

**The save-code panel is verified end to end against the real game.**
Sean opened the browser pane, the live build booted, and the whole chain
ran: the game's load page turned paste on, the shell's poll saw
`isPasteEnabled()`, the panel appeared, a typed code went through
`offerPaste` to `take_browser_paste`, and Enter resumed at temple_1 with
the 12 cigarettes the code carried. The touch wording was visible in the
same run -- "PAD UP / DOWN   INSPECT" on the title, "TYPE ABOVE, OR DIAL
WITH THE PAD." on the load page.

**Claude's browser pane cannot boot the wasm build at all while it is
hidden.** pygbag drives Python from `requestAnimationFrame`, and a
hidden document halts it: zero animation frames in three seconds,
measured, against 179 once the pane was open. The page sticks at
"Loading, please wait ...". `show_pane` has no browser pane, so **ask
Sean to open it** before attempting any in-game browser test.

**A habit worth keeping.** Three tests written this session passed
against deliberately broken code before they were fixed: a panel-overflow
check defeated by the font's descender rows, a d-pad seam check that hit
a KeyError first, and a W/S/E guard defeated because the next keystroke
overwrites the damage. Breaking the code on purpose and confirming the
test screams is the finish line, not writing the assertion.

**The game now names the controls a phone has (e9ac16d).** It was
telling touch players to press E, SPACE and ESC. `runtime.touch_host()`
reads the marker the shell already puts on the page it embeds,
`?mobile=1` -- the same one the desktop page reads to hide its link to
`/mobile/` -- and `prompts.py` gained touch as a third case beside
keyboard and controller, so the hints, title prompt, controls page and
menu footers all followed from one change. A controller still wins over
the shell.

**`touch_host()` is how a fork would start, so the rule is written into
it: wording only.** Which control a line of text names, nothing else. No
layout, scene, rule or control may depend on it -- that belongs in the
shell. Its docstring and `tests/test_touch_wording.py` both say so, and
a test pins the marker to the one the shell sends, so the game cannot
grow a second opinion about what a phone is.

**The settings wheel did nothing, and now does (169ae9d).** It widened
each `clamp()`'s bounds instead of scaling the result, and on a phone
the floor wins: measured at full stretch, the d-pad went 150px to 150px
and a button 52px to 52.5px. The pad was on a variable the slider never
touched; the round chips were hardcoded. One `--scale` now multiplies
every control size, kept in localStorage. Portrait gets a "turn
sideways" prompt rather than a 16:9 sliver, and the prototype note is
gone.

**Safari will not start the game until the page has had a real touch**
(121df58), and pygbag never says so: its only message element is the
"Loading" line, hidden by then. The game therefore sat on a black
screen waiting for a tap nobody knew to give. That was always true --
what made it visible was removing the "Landscape prototype" note, which
had been the only thing on screen and was standing in for a message
that never existed.

The shell shows "TAP TO PLAY" instead. **It must stay
`pointer-events:none`:** the tap has to pass through into the iframe,
because that is the frame Safari wants the gesture in, and a label that
caught it would leave the player tapping a black screen for ever. A
test fails if anyone makes it clickable. The listener that dismisses it
goes on the *iframe's* document -- the parent never sees a touch that
lands in there.

**iPhone Safari has no Fullscreen API**, and removing the button there
was wrong: it left a player looking at browser bars with nothing to
explain them. The button stays and opens the panel holding the Add to
Home Screen route, which is the only thing that works on iOS.

**A process rule, learned the hard way this session:** work that is
built and tested is not shipped. Say "pushed" or "live" only after the
push has happened *and* the deployed page has been fetched and checked.
Sean went to look at his phone for a fix that was still sitting
uncommitted, because it had been described as done.

**Not verified, and it needs a device:** copying a save code out, and
both halves of the above on an actual iPhone -- whether `audioSession`
really defeats the silent switch, and whether the home-screen launch
gives a chrome-free landscape game.
The native keyboard raising, iOS viewport reflow in landscape, and the
OS paste button are untested. `tests/test_browser_clipboard.js` was
extended but **did not run** -- there is no Node on this machine and
`run_tests.py` does not execute it. Someone with Node should run it
once.

**The phase sequence is closed** (e421c24), at Sean's instruction: the
main game is done, with the acknowledgment that he may change or add
things later. `CURRENT-PHASE.md` now says what may proceed without a
phase -- technical work, off the Baton -- and draws the line: a way to
type a save code on a phone is not game content, a region is.

**Next, in order:**

1. **A real phone pass on `/mobile/`**: resume a game from a save code,
   and check the keyboard in landscape. Everything above waits on it.
2. **A real play test on a real browser**, and **listen to the audio**.
   Both are blocked on a device that is not Claude's pane, which runs
   the wasm build at ~1.4 fps. `WEB-BUILD.md` sections 6 and 6b.

**Codex, 2026-09-19: browser save-code clipboard.** Sean confirmed the
Phlegethos transition works in another browser. Copy now settles its browser
Promise in JavaScript and polls a bounded status from Python, showing exactly
`Copied` on success instead of remaining at `Copying...`. Load Code enables a
native paste listener only while open; Ctrl/Cmd-V bypasses SDL's key capture,
and the field consumes and normalizes the pasted text. Clipboard read access
is limited to the user-initiated paste event. Desktop clipboard stays intact.
Checks: browser clipboard JS (success/denial/paste/lifecycle), 9 browser-runtime,
22 existing save-menu plus new paste-to-resume, and 25 code-entry tests pass.
The previous commit's content-versioned downloads and visible crash reports
are included in this publication. No actual Xbox clipboard test performed.

**Codex, 2026-09-19: Xbox still reports a blank Phlegethos handoff.**
Confirmed Pages run 35467546505 succeeded and fetched the live APK to verify
the captain-map guard really shipped. Full captain -> fall -> playable Hell
sequence now runs frame-by-frame in the regression test and passes locally.
No second gameplay exception reproduced; Xbox caching remains a hypothesis.
Build finalization now gives the APK a content-hashed filename, retaining the
legacy APK for old index pages. Browser Python crashes display their traceback
in a DOM panel after SDL shutdown, so Xbox can report a readable error.
Eight browser-runtime and twelve plank-procession tests pass. Actual Xbox
retest still needed; do not claim the remaining report resolved.

**Codex, 2026-09-19: Waterdeep southern wall.** The shared docks map now
uses the fountain plaza's solid castle-brick terrain across its southern
land edge (row 34, columns 20–55), including the southeast corner. Sea
remains sea. Opening, post-sewer, and finale use this same geometry.
Eight Waterdeep-return checks pass; opening and finale wall collision and
rendering checked directly. No mobile-shell files changed.

**Codex, 2026-09-19: Phlegethos handoff crash fixed.** Preserving story
flags exposed unconditional captain/plank reconstruction on every map once
`captain_confronted` was set. Restrict that reconstruction to
`ship_exterior_deck`. Reproduced the reported crash with actual completed-ship
flags; the expanded treasure-handoff test now loads, updates, and draws all
five destinations and passes. The 12 plank-procession checks also pass.
The mobile-work notes below remain applicable; this pass is on main.

**Branch** `main`, at the tip. Last full suite: **194 of 194** at
121df58.

**Live:** <https://rtrutabaga.github.io/CHUCK-game/> and the landscape
touch shell at `/mobile/`. Every push to `main` republishes both.

**Codex, before anything else:** your worktree at
`C:/Users/ashsm/.codex/worktrees/0b37/CHUCK-game` is still on 80c9749
holding the mobile-shell pass uncommitted. **That work is already in
main** (e9ee867), with two fixes on top: the controls were stacked in the
top-left, and the key events were dispatched at the iframe *window*,
where SDL does not listen -- it registers on the iframe's *document*.
Discard your copy and rebase; do not apply it again. Nothing was lost,
including your note that no real-iPhone pass had been done. It still has
not been.

**Desktop/Xbox fixes reach the phone for free**, and that is structural,
not a process: `/mobile/` iframes the same `index.html` from the same
`src/`. There are two seams, both names written twice and both able to
drift silently, and each has a test holding it shut:

- the touch shell names the keys its buttons press, a copy of
  `KEY_BINDINGS` in HTML -- `tests/test_mobile_touch_controls.py`, every
  button presses a bound key and every bound action has a button, so
  adding or rebinding an action on desktop fails the suite until the
  phone follows;
- the shell names the bridge methods it calls on `CHUCKClipboard` --
  `tests/test_mobile_code_entry.py`, so renaming one in
  `tools/browser_clipboard.js` cannot quietly stop the phone loading a
  save code.

Add a third seam and it needs a third test; that is the price of the
shell, and it is much cheaper than a fork. **Do not fork `src/` for
mobile;** see TWO-AGENT-GIT-WORKFLOW.md "There Is Only One CHUCK".

**Two rules earned this session, both now written down where they
belong:**

- Retiring a map's save slots: add them to
  `save_registry.RETIRED_ENTRIES` and repoint them at a surviving
  neighbour. Tombstone only when there is nowhere sensible left to land.
  Changing `FROZEN_ENTRY_DIGEST` is almost never the answer.
- Finding another agent's stranded work: `git worktree list` first, not
  `git status`. `TWO-AGENT-GIT-WORKFLOW.md` section "Work You Cannot
  See" has the recovery procedure, including `diff HEAD` rather than
  `diff`.

## Recent Passes

## Session of 2026-09-19 (Claude)

Moved down from the baton. Newest first.

- **Codex: your worktree copy has already landed (Claude, 2026-09-19).**
  `C:/Users/ashsm/.codex/worktrees/0b37/CHUCK-game` is still sitting on
  80c9749 with the mobile-shell pass uncommitted -- `tools/build_web.py`,
  `WEB-README.md` and a baton entry. That work shipped in e9ee867 with two
  fixes applied on top (the controls were stacked in the top-left, and the
  key events were dispatched at the iframe window where SDL does not
  listen). **Discard the worktree copy and rebase onto main; do not apply
  it again.** Nothing in it was lost: your baton note's substance is in the
  entry above, including the point that a real-iPhone pass had not been
  done -- it still has not, and that is Sean's next test.
  I left the worktree untouched rather than cleaning it, per the rule in
  TWO-AGENT-GIT-WORKFLOW.md § Work You Cannot See: it is yours, and it is
  a free backup until you say otherwise.
- **Mobile prototype, first phone build (Claude, 2026-09-19):** picked up
  Codex's touch-shell pass and shipped it. `tools/build_web.py` writes
  `build/web/mobile/index.html`, an iframe around the existing browser build
  with a landscape touch overlay (d-pad, JUMP/SCRATCH/INSPECT, pause, and a
  gear panel sizing the buttons). The existing Pages workflow uploads the
  whole `web` tree, so it publishes free at
  `https://rtrutabaga.github.io/CHUCK-game/mobile/`.
  Two things were fixed before it could work at all:
  - `#pad` and `#actions` are not `.touch`, so they were `position: static`
    and both stacked at the top-left with all three action buttons at one
    point. They now anchor to the bottom corners inside the safe-area insets.
  - The shell dispatched its synthetic `KeyboardEvent`s at the iframe's
    *window*. SDL registers `keydown`/`keyup` on the iframe's **document**
    (confirmed by reading `JSEvents.eventHandlers`), so nothing ever reached
    the game. It now dispatches on `contentDocument`, and each button carries
    an explicit `data-code`/`data-keycode` because SDL2 looks the scancode up
    from `code` -- `f` and `e` were sending `code:"f"`/`code:"e"` rather than
    `KeyF`/`KeyE`.
  Verified in-browser against the real buttons, not by hand-dispatching:
  arrows move the title cursor, INSPECT opens LOAD CODE, pause backs out.
  Same origin, so `contentDocument` stays reachable.
  **Known gap for the next pass:** LOAD CODE wants a typed twelve-character
  code and the shell offers no keyboard, so a phone can start a new game but
  cannot resume one. That is the first thing to solve -- either an on-screen
  code entry in the shell or touch-driven entry in `title_scene`.
  Sean is play-testing Waterdeep and the sewers on a phone; Codex owns the
  next mobile pass. Core game code is untouched by this commit.
- **Suite green again, 191 of 191 (Claude, 2026-09-19):** cleared the four
  failures reported above. Two were counts left stale by the tea-table cut
  and nothing more -- the bodies of both tests still passed. The mushroom
  registry is 9 maps, not 10; the Feywild arrival count is 24, not 26,
  because the tea table sat *between* Rootways and Needle Garden, so cutting
  it joined two links into one. Both numbers now carry the reason.
  `test_treasure_handoffs` was the only module importing `pytest`, which is
  not installed, so it had been silently import-failing since it was added.
  Rewritten in the plain style the other modules use -- same assertions, the
  `parametrize` became a loop over the five crossing cutscenes. That is why
  the module count went 190 -> 191.
  The registry failure was the one real decision. 75a70b7 did not merely
  delete the tea table: it repointed `feywild_5` and `feywild_5_return` onto
  the surviving neighbours, same arrival and facing, then set
  `runtime_entry=False`. So an existing code still resumes where the player
  left off, but nothing new is saved there -- a state the codebase had no
  word for, which is why the doors-only test failed. Both slots sit at index
  49 and 57 inside a fully frozen 147-entry prefix, so tombstoning them (the
  header's usual retirement) would have changed `FROZEN_ENTRY_DIGEST` *and*
  broken codes that presently work. Instead the state is named:
  `save_registry.RETIRED_ENTRIES`, listed explicitly rather than inferred
  from `runtime_entry`, since inferring it would let a development jump or
  cutscene handoff drift into `SAVE_ENTRIES` unnoticed. The frozen digest is
  untouched and no code in the wild changes meaning.
  Checked that the new exception narrows rather than masks: emptying the set
  brings the original failure back, and a retired slot pointed at an arrival
  that does not exist is caught by the new
  `test_every_retired_slot_still_lands_somewhere_real`.
  **If you retire a map, add its slots to `RETIRED_ENTRIES` and repoint them
  at a surviving neighbour.** Tombstone only when there is nowhere sensible
  left to land.
- **Next:** mobile save-code entry, still Codex's -- a phone can start a game
  but not resume one, because LOAD CODE wants twelve typed characters and the
  shell has no keyboard.


## Superseded Baton Entries

Passes that were left in the baton block rather than moved down when
they finished. Newest first.

- **NPC trailer revision (Codex, 2026-09-19):** added eight seconds of Chuck
  approaching the plaza blacksmith, interacting, reading "I don't shoe rats."
  and walking away. Dialogue stays visible 5.4 seconds. Trailer is now 46
  seconds; previous action footage and per-world audio preserved. Reviewed
  conversation frame and verified full export decode; same local MP4 path.
- **Action trailer revision (Codex, 2026-09-19):** recut to 38 seconds:
  grass destruction + cigarette pickup, sewer enemy scratch/defeat, Chult,
  urn shatter + carton collection, three spike-pit jumps, ship, Feywild, city.
  Actual game-state logs verify rewards, breakage and defeat; no gameplay
  rules changed. Local MP4 overwritten, per-area music retained, no added
  text, cabin or final encounter. Export verified by full decode.
- **Trailer revision (Codex, 2026-09-19):** per Sean, removed all added
  titles/cards and video fades. Export is now 44 seconds of gameplay with
  each scene's actual requested music and synchronized SFX. No continuous
  replacement soundtrack. Same local MP4 path; cabin/finale still excluded.
- **Trailer (Codex, 2026-09-19):** created a 49-second 1080p/30 MP4 at
  artifacts/trailer/CHUCK-gameplay-trailer.mp4 (local ignored artifact).
  tools/capture_trailer.py captures actual game-rendered frames with scripted
  movement, mixes frame-timed game SFX with fall_to_chult music, and encodes
  using optional local imageio-ffmpeg. Includes docks, Chult Falls, earlier
  temple battle, ship, Feywild and city; excludes cabin and final encounter.
  Gameplay code untouched. Capture setup and intermediates are ignored.
- **Final encounter music (Codex, 2026-09-18):** the 74-second trio cue
  was looping back to its sparse intro before the dragon's 82+ second entry.
  First dialogue now hands to desert_trio_pressure.wav, a developed-section
  loop with continuous pulse/kit, added timpani, snare pickups and brass
  through the ending. The existing dragon trigger still starts its boss cue.
  Source score and rendered WAV included; 22 music/encounter checks pass.
- **Final encounter respawn (Codex, 2026-09-18):** death now preserves the
  running trio encounter, army/siege/dragon, dialogue clock, terrain and music.
  Chuck returns at (32, 26), on protected ground beyond the west Sea's maximum
  advance, with full sanity. Collected cigarettes remain with the ongoing
  room. Other maps retain their existing reset behavior. All 34 focused final
  encounter tests pass, including repeated deaths after arena collapse and
  continued dialogue afterward.
- **Latest cut (Codex, 2026-09-18):** removed the giant tea-table map.
  Rootways now connects directly to Needle Garden in both directions using
  their existing arrival markers. Retired feywild_5 save-code slots stay
  reserved and load neighboring maps; no save registry IDs were renumbered.
  Removed the map generator and retired-map tests/dressing registrations.
- **Latest fixes (Codex, 2026-09-18):** extended the plaza smithy's west
  wing to the edge and north wall, sealing the reverse route into the guarded
  docks street while keeping southern exits open. Escape-to-ship and four
  later story cutscenes now pass existing progress flags to checkpoint loads
  so premium cartons survive. Verified five real cutscene handoffs, all plaza
  tests, and existing escape/river tests (27 passing checks total).
  Already-erased treasure flags need a player save-code repair; do not award
  optional treasure automatically to all players.
- **Correction (Codex, 2026-09-18):** Sean clarified that only the street
  north of the tavern is guarded (rows 1–7, including the previously missed
  row 7). East exits beside/south of the tavern reach the fountain plaza.
  Supersedes the full-edge block below. Controller A now jumps/backs out;
  B inspects, talks, and confirms. Y still pauses; View/Menu stay unbound.
  Verified all east exit rows in both eras; 13 plaza checks and 29
  controller/tutorial/checkpoint checks pass.
- **Publication follow-up (Codex, 2026-09-18):** the previous full dock
  boundary fix had never been committed/pushed after approval hit a usage
  limit. Verified every east exit row in both Waterdeep eras, including
  repeated updates on the exit; 32 focused tests pass. Publishing the pending
  guard fix together with the previously requested controller changes.
- **Latest pass (Codex, 2026-09-18):** reserved Xbox Menu/Start and
  View/Change View for Edge browser controls. In-game controller pause now uses
  the otherwise-unused Y button, with prompts and browser Gamepad fallback
  updated accordingly. Focused controller/tutorial checks pass (32).
- **Latest polish (Codex, 2026-09-18):** confirmed controller-aware text is
  shared by the title, Controls page, load/save footers, and tutorial hints,
  including browser Gamepad fallback input. The title's controller footer now
  explicitly reads ``D-PAD / STICK`` plus the controller-specific confirm
  button. Focused controller/title checks pass (18).
- **Latest pass (Codex, 2026-09-18):** browser SAVE GAME → COPY now uses
  ``navigator.clipboard.writeText`` instead of unavailable Pygame/SDL scrap.
  It reports ``Copied.`` on success and an honest permission fallback when a
  browser or device blocks clipboard access. Desktop copying is unchanged.
  The browser package builds and 54 focused save/code/browser tests pass.
- **Latest fix (Codex, 2026-09-18):** completed the Waterdeep guard boundary
  as specified. Every east-edge exit tile, including the lower opening, now
  gives ``Stick to the docks, rat.`` and holds Chuck on the docks after the
  dialogue closes, in both opening and finale states. The plaza remains
  available by checkpoint/code but not by walking from the docks. Focused
  Waterdeep checks pass (23).
- **Latest pass (Codex, 2026-09-18):** added a browser Gamepad API fallback
  for Xbox Edge, which can expose the controller to JavaScript while sending
  no SDL/Pygame events. Standard Xbox buttons, d-pad, and left stick now feed
  the same named actions as desktop controllers; Menu/View pause globally.
  The browser package builds successfully and the focused fallback/browser/
  checkpoint checks pass (25).
- **Latest pass (Claude Code, 2026-09-18):** finished Codex's dock pass.
  The tree is clean; `main` is pushed and Pages redeploys on push.
- **Branch / base:** `main`, base `9fc2c87`.
- **The bug in it was a decorator, not a design.** Codex's new
  `_dock_guard_boundary_hit` property was inserted directly above
  `_waterdeep_midday` and took its `@property` with it. `_waterdeep_midday`
  became a bound method, which is always truthy, so the docks were
  permanently in their returned-from-the-sewer state: `dock_worker`
  became `bobert_neighbour`, the lamps went out, the pier retinted. Four
  of the five failures were that one line.
- **The fifth was a real disagreement, resolved in Codex's favour.** The
  open tavern doorway art is 48px — three tiles — but only the centre
  tile was walkable, so Chuck caught solid facade inside the visible
  arch. `test_tilemap` asserted the sides stay solid "because Phase 2
  does not build an interior"; that reason is stale now the tavern
  interior exists, so the test was updated rather than the code.
- **Verified by behaviour, not just by tests:** walking the guarded
  upper-east edge gives "Stick to the docks, rat." and does not
  transition; the tavern threshold is three walkable tiles with solid
  facade either side and behind.
- **Suite:** 191 of 191.
- **Xbox, still open and the most useful next thing.** `?diagnostics=1`
  now logs the pad: `button N down | reached: <actions>`. Get that
  reading off the Xbox before any further controller fix. The title
  accepts `jump` as a confirm; if that is what Xbox sends, dialogue,
  the pause menu, the code field and talking in the world all need the
  same treatment — and the pause menu cannot copy it verbatim, because
  the east button is bound to both `jump` and `back` there.
- **Live:** `https://rtrutabaga.github.io/CHUCK-game/`.

---


## Latest Pass — Codex's Dock Pass, Finished (2026-09-18)

- Restored `@property` to `_waterdeep_midday`, which Codex's new
  boundary property had taken. That single line was four of the five
  failures: the docks had been stuck in their midday state.
- Kept the three-tile tavern threshold and updated the test that
  contradicted it, since the art is 48px and the stated reason for the
  old assertion no longer holds.
- Checked both behaviours in a running scene rather than trusting the
  suite: the guarded edge warns and holds, the doorway is walkable
  across its visible width and solid either side.

## Latest Pass — Xbox Confirm, and a Way to Stop Guessing (2026-09-18)

- Committed Codex's title fix: the title accepts `jump` as well as
  `interact`, so Edge on Xbox can confirm an option after moving with
  the d-pad.
- Added a gamepad reader to `?diagnostics=1`. It names the pad once and
  then reports every press as `button N down | reached: <actions>`,
  polled rather than hooked so it changes nothing about input handling.
  Four focused checks, including the Xbox case: a press that reaches
  nothing at all.
- Set aside an unfinished pass of Codex's that fails five tests, so the
  Xbox fix could ship on its own. It is back in the working tree.

## Latest Pass — Requested Gameplay Polish (2026-09-18)

- Added the opening Waterdeep pause-hint fallback and fixed numpad code input.
- Closed both old routes out of final Waterdeep, updated the sign and dock
  dialogue, and preserved the opening-era tavern/sewer behavior.
- Added the daytime arrival manhole through its generator, muted cabin seating
  examinations, and shortened the collided-desert banner examination.
- Focused regression modules and map regeneration checks pass.

## Latest Pass — The Code Is The Only Save (2026-09-18)

- Removed CONTINUE from the title and the local save file from the game.
  `SaveSystem`, `save2.json` and `default_save_path` are gone; `save.py`
  keeps `SaveRecord` alone. `write_save` became `save_here`, which banks
  the point and returns the record rather than writing anything.
- `settings.json` was deriving its path from the save file's and would
  have vanished with it. It has its own `default_settings_path()` now,
  pointing at the same place, so existing settings are kept.
- The test suite's save/relaunch round trips go through a code. Sanity
  assertions after a resume became `SANITY_START`: a code has no room
  for sanity, so the old assertions described the impossible.

## Latest Pass — Codes Become The Only Save (2026-09-18)

- Sean decided to drop CONTINUE and the local save file entirely, leaving
  the twelve-character code as the whole save system. Recorded in
  `DECISIONS.md`, with `SAVE_CODES.md` §7 and `WEB-BUILD.md` §4.1 marked.
- QUIT TO TITLE now shows the code before asking, since with no CONTINUE
  it is the only thing that survives leaving. Read-only. The no-code case
  (mid-cutscene) says so plainly. Both layouts checked by rendering them.
- The removal itself was deliberately not started: ~37 test files touch
  the file-save path, past the session-size line in the workflow doc.

## Latest Pass — Pages Blockers Answered (2026-09-18)

- Committed Codex's browser timing reporter, which its session had written
  and described in the handoff but not committed. Verified first: 3
  diagnostics checks, 6 browser-runtime checks, full suite 190 of 190.
- Served the existing local build and inspected the running context. Pygbag
  0.9.3 needs no cross-origin isolation for this game, so GitHub Pages can
  host it; `index.html` carries no absolute asset paths, so the
  `/CHUCK-game/` subpath is fine.
- Recorded that the runtime comes from a third-party CDN at play time, and
  that Claude's browser pane is unusable for timing or play-testing.
- No game code changed in this pass beyond committing Codex's.

## Latest Pass — Browser Traversal Diagnostics (2026-09-18)

- Added opt-in `?diagnostics=1` console timing samples with FPS, p95 frame
  time, and worst frame time. Hidden-tab time and scene/map changes reset the
  sample so reports do not hide stalls.
- Verified title, opening cutscene, and `waterdeep_docks` in the browser at
  approximately 60 FPS; observed p95 frame times of 17.3–17.6 ms and maxima
  below 21.5 ms in the measured samples.
- Added focused tests for timing behavior and rebuilt the browser preview.

## Latest Pass — Browser Audio Buffer (2026-09-18)

- Added browser-only buffering headroom for reported walking audio glitches.
- Desktop audio, cues and playback rules unchanged. 16 focused checks and
  both platform startup assertions pass; web build succeeds.
- Audible result awaits Sean's test in a fresh preview tab.

## Latest Pass — Browser Cutscene and Canvas Fix (2026-09-18)

- Explicitly stop the previous browser music stream before replacement,
  avoiding the hang at the opening cutscene's early music cue.
- Fixed SDL framebuffer and CSS 16:9 letterboxing; browser fullscreen stays
  with browser chrome. Build/serve both apply the presentation override.
- Live title -> full opening -> docks verified, plus movement/jump/pause
  and tall-window proportions. 71 relevant regression checks pass.
- Preview rebuilt; desktop behavior and authored content retained.

## Latest Pass — Local Browser Build Foundation (2026-09-17)

- Reconciled Codex's interrupted prototype per Claude's WEB-BUILD contract;
  committed runtime/build foundation as `c54100a`.
- Browser title launch verified; gameplay verification stopped when browser
  tooling became unavailable. Added console traceback reporting for resumption.
- Desktop checks: 1,291 across 189 modules; isolated save-path rerun required
  for one module. Build archive is 11.1 MB, plus separately fetched runtime.
- No content, controls, save format, desktop audio masters or publishing changes.

## Latest Pass — Broken Daytime Street Ends (2026-09-17)

- Branch: `save-codes`; base commit: `9edf766`.
- Replaced thin unbuilt wall caps at daytime street ends with Astral Sea:
  Day 1's north side street, Day 2's north/east streets (including Sean's
  screenshot), and Day 3's capped street/sidewalk/alley edges. Genuine
  authored building masses and the sidewalk exits remain intact.
- `finish_day_buildings` finds shallow boundary caps using the generators'
  original unbuilt-wall vocabulary, runs the existing terrace pass, then
  removes only those caps. This preserves surrounding building art seeds
  and never treats an authored building as an unfinished street end.
- Removed Day 4's isolated southern road, crossings and lower protrusion.
  A shorter paved footway with concrete edging still joins the west/east
  routes; its puddle and street furniture remain on surviving pavement.
  Updated its material validator to require the absence of stray roadway.
- All six day generators validate. All 49 checks across 11 focused modules
  pass: street ends, furnishing/parity, street furniture, sidewalk travel,
  park/Examine, and each daytime map. Native views of the road ends and the
  former southern stub were inspected. Days 5/6's shipped maps are unchanged.

## Latest Pass — Daytime Shops and Municipal Plaza (2026-09-17)

- Branch: `save-codes`; base commit: `634ede6`.
- Added twelve signless storefronts to suitable building fronts in Days
  1, 2, 3, 4 and 6 (3/2/3/3/1). Day 5 remains a building-free overpass.
  They reuse the night shops' dimensions and window vocabulary with an
  overcast daytime palette and unlettered canvas valances. Doors answer
  exactly `it's closed`; existing night signs/assets are unchanged.
- Day 1's open plaza beside the avenue now has one animated low concrete
  fountain, four park benches, four planted tubs, and a newspaper box.
  The fountain's five-by-two-tile collision follows the bowl; a clear
  pedestrian ring surrounds it. The plaza/side-street connection, pickups,
  puddles, patrol routes, and onward sidewalk exit remain accessible.
- New props have restrained Examine lines in `data/dialogue/examine.json`.
  Sprites come from `generate_city_furnishing.py`; placement is generated
  by `dress_day_storefronts` and `dress_day_park` in the shared city helpers.
  Map glyphs U+E180–U+E187 identify these props and the fountain's solid base.
- All 101 checks across 14 relevant modules pass, including actual Examine
  actions at every new object, storefront wall footprints, fountain
  collision/walkability, sidewalk exits, generator parity, the six day-map
  suites, and existing night storefronts. Native park and shop views were
  rendered and inspected. No save, progression, or transition changes.

## Latest Pass — Day-City Sidewalk Connections (2026-09-17)

- Branch: `save-codes`; base commit: `dcabdfe`.
- Removed Day 1's one-column building seam between the plaza and the north
  side street (column 53, rows 14–28), replacing it with continuous sidewalk.
- Day 1's east connection now occupies the northern sidewalk's full width.
  Day 2's south connection moves to the eastern sidewalk. Day 3's northern
  entrance has a three-column footway beside a slightly narrower building;
  its southern exit moves to the western sidewalk. Day 5's two connections
  move from traffic lanes to widened ends of the western footway.
- Day 4's already-paved north/east connections now cover their whole footway
  widths; Day 6's northern pavement entrance is five tiles wide. The roads
  beside relocated exits in Days 1–3 visibly end in Astral terrain.
- Shared furnishing helpers accept protected approach cells, used only by
  these six day-map generators, so lamps, bins, benches and signs cannot
  obstruct the exit mouths. All six shipped maps were regenerated and
  validated; named arrivals and stable checkpoint IDs are preserved.
- Corrected Day 4 → 5 arrival facing to south and Day 5 → 4 to west, matching
  the destination footways (including the Day 4 return checkpoint).
- New regression coverage checks clear pavement behind every threshold
  cell, actual travel through every cell, safe pavement arrivals, facing,
  no immediate bounce, and removal of the Day 1 seam. Also ran all six day
  map suites, city furnishing/edge checks, transitions, checkpoints and
  save registry checks. Native views of all ten connection mouths and the
  repaired plaza were rendered and inspected.

## Latest Pass — Sewer Jump Mercy (2026-09-17)

- Branch: `save-codes`; base commit: `98ab2fe`.
- Sean requested a nearby retry for the difficult Astral jump course shown
  in his screenshot. That course is `modern_city_sewer_2` in the repository
  (not the crocodile hall named `modern_city_sewer_3`).
- Deaths within course columns 10–24, rows 45–54 now return Chuck to the
  center of dry tile (12, 42), below the green sludge and before the first
  jump. The normal fall, quiet fade, enemy reset, Sanity refill, cigarette
  rollback, and death count continue unchanged.
- Mercy destinations are authored in `src/systems/respawn.py`. WorldScene
  selects a destination per death; it never moves the entrance checkpoint
  or changes a save record, registry, code, or progression flag. Deaths
  elsewhere still return to the entrance, even after a local retry.
- Regression coverage drives actual falls at every gap in the course,
  repeated retries, safe footing, unchanged entrance identity, and a later
  non-course death. The neighboring sewer, checkpoint, menu/save, hazard,
  and death-count checks were also run. The actual retry frame was rendered
  and visually inspected at native resolution.

## Latest Pass — City Storefronts (2026-09-17)

- Branch: `save-codes`; base commit: `ac5fa4d`.
- Sean requested ground-level shop graphics matching the existing city neon,
  with every door closed and answering exactly `it's closed` on Examine.
- All twelve signed locations across the six night-city maps now have a
  three-tile-wide frontage: a bottle-window bar, a cafe under OPEN, or a
  stocked convenience store under 24H. Each has inset glazing, a closed
  human-scale door, a latch, and a flush pavement threshold. Only the neon
  animates; the frontage stays still.
- Uses the existing neon prop anchors and animation registry. The generator
  now renders complete fronts into those assets, and the props reuse the
  existing `closed_door` dialogue. No map regeneration, collision, route,
  progression, save-system, or daytime-city changes.
- Validation: 98 checks across 12 focused modules passed (storefronts,
  furnishing, Examine, props, dialogue, tilemap, and all six night-city maps).
  The storefront checks exercise the actual Examine action at all twelve
  doors and verify the sprite footprint remains within solid building tiles.
  All twelve locations were rendered and visually inspected at 320x180.
- Work boundary remains scenery polish within existing maps. Phase 15 has
  no contract. Older notes below predate Claude's save-code work; consult
  `chuck/chuck/PROJECT_STATUS.md` and `SAVE_CODES.md` for the current save
  system. Ashtrays no longer exist.
