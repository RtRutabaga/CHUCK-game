# CHUCK Documentation Guide

The repository documentation is organized so Claude Code and Codex can work from the same source of truth.

## Read First

1. `../AGENTS.md`
2. `development/CURRENT-PHASE.md`
3. `design/GAME-BIBLE.md`

Phase 14 is complete. Phase 13 remains the completed Collided Desert traversal,
rift encounter, and return-to-Waterdeep contract. No Phase 15 scope document
exists yet.

Then read the topic-specific supplement relevant to the task.

## Documentation Roles

- `design/GAME-BIBLE.md`: core creative authority.
- `design/CHUCK-Game-Bible-Supplement-Geography.md`: impossible geography, regional integrity, map connections, transitions, and the Pantry Principle.
- `design/CHUCK-Game-Bible-Supplement-Player-Progression.md`: progression philosophy, genre subversion, minimal UI, lack of equipment progression, and Chuck logic.
- `design/CHUCK-SOUNDTRACK-BIBLE.md`: soundtrack identity, composition, synthesis, arrangement, motifs, and audio implementation direction.
- `development/PHASE-10.md`: completed Zephyros and city-arrival contract.
- `development/PHASE-11.md`: completed contract for the rainy city,
  urban sewer, daytime collision district, and Douglas fir handoff.
- `development/CURRENT-PHASE.md`: short pointer to the active implementation
  boundary and its authoritative phase contract.
- `development/PHASE-14.md`: active implementation contract for the Waterdeep
  finale, shared starting/ending city layout, and fountain plaza.
- `design/references/tahuya-cabin/`: Sean-authored layout and photographic
  references for Phase 12. The layout drawing governs spatial relationships;
  photographs govern structure, materials, palette, furniture, and scale.
- `development/WEB-BUILD.md`: contract for running the game in a browser
  and publishing it from GitHub Pages. A technical document, not a phase:
  it changes no game content and does not open Phase 15. Partly built;
  read its section 2 before touching the web work.
- `development/HANDOFF.md`: the relay note. Opens with a **Baton** block —
  the one thing to read to pick up work, and the one thing that survives a
  session ending on a usage limit. Recent passes follow it.
- `development/HANDOFF-ARCHIVE.md`: older passes, moved out of the read
  path. Not part of starting a task.
- `development/DECISIONS.md`: durable decisions future agents could otherwise reverse.
- `development/WEB-BUILD.md`: browser port contract and remaining verification;
  `../chuck/chuck/WEB-README.md`: local prototype build instructions.
- `source/campaigns/`: historical D&D source material.

Campaign files verify history, characters, objects, locations, and references. They do not override the Game Bible or active phase.

## Key Principle

Do not make every agent reread every campaign note before every coding task.

Read authoritative design docs first. Consult campaign sources when a task involves campaign history or a specific reference.
