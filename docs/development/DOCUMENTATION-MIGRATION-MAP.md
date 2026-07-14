# Documentation Migration Map

Use this repository structure:

```text
CHUCK/
├── AGENTS.md
├── docs/
│   ├── README.md
│   ├── design/
│   │   ├── GAME-BIBLE.md
│   │   ├── CHUCK-Game-Bible-Supplement-Geography.md
│   │   ├── CHUCK-Game-Bible-Supplement-Player-Progression.md
│   │   └── CHUCK-SOUNDTRACK-BIBLE.md
│   ├── development/
│   │   ├── CURRENT-PHASE.md
│   │   ├── HANDOFF.md
│   │   ├── DECISIONS.md
│   │   ├── TWO-AGENT-GIT-WORKFLOW.md
│   │   └── DOCUMENTATION-MIGRATION-MAP.md
│   └── source/
│       └── campaigns/
│           ├── Chuck-character-overview.txt
│           ├── Campaign-Notes-RIME-OF-THE-FROSTMAIDEN-TALES-OF-THE-ARCTIC-AVENGERS.txt
│           ├── Campaign-Notes-Storm-King's-Thunder.txt
│           ├── Campaign-Notes.txt
│           ├── Willie's-Campaign.txt
│           ├── CAMPAIGN-NOTES-BUHETIAN-DESERT.txt
│           ├── Tomb-of-Annihilation-Campaign-Notes.txt
│           ├── Augustus.txt
│           └── pasted.txt
```

Copy the existing supplements into `docs/design/` unchanged.

Copy campaign source files into `docs/source/campaigns/` unchanged.

Do not merge all campaign notes into the Game Bible.

If a Game Architecture Document already exists in the live repository, keep it and place it under `docs/development/` or another clearly named architecture location. Do not rewrite its description of the current codebase from planning documents alone. Architecture documentation must match the actual repository.
