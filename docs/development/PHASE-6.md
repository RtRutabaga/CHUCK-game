# PHASE 6 --- THE JUNGLE TEMPLE

## Status

Phase 5 ends at the temple entrance.

Phase 6 is a full dungeon crawl through the temple interior and ends
with Chuck escaping onto a ship at sea. Phase 7 begins aboard that ship.

Implemented so far:

- Temple Map 1: reversible torch-lit entrance hall and first Ashtray.
- Temple Map 2: long, narrow torch-lit connector with five spike bands, five
  skeletons, repeated committed jumps, and one Ashtray.
- Temple Map 3: broad torch-lit chamber with twelve avoidable, durable
  skeletons, looping routes around monumental piers, and one Ashtray. Its
  onward boundary turns west into Temple Map 4.
- Temple Map 4: long, narrow west-running connector with eight staggered dart
  launchers, recurring wall torches, and one Ashtray. Its west boundary enters
  Temple Map 5.
- Temple Map 5: broad torch-lit snake chamber with twenty one-hit snakes,
  looping lanes around masonry piers, and one Ashtray. Its onward route turns
  south into Temple Map 6.
- Temple Map 6: very narrow torch-lit winding connector with eight one-tile
  Astral Sea fall cuts requiring committed jumps, one Ashtray, and an eastward
  boundary reserved for the next broad room.
- Every Temple Map 1-6 threshold now uses a narrowed three-tile opening and a
  reusable human-scale stone arch instead of repeated doorway bars.
- Temple Map 7: broad reversible shrine hall east of the Astral wind — twelve
  avoidable skeletons, alternating skull/serpent guardian monument rows, the
  full dressing and threshold kit, one Ashtray, and an inert north boundary
  reserved for Map 8.
- Temple Map 8: the gauntlet — a narrow L-shaped connector concentrating the
  established defenses (spike bands, dart lanes, Astral cells) with a
  monument pair, full kit, one Ashtray, and an inert west boundary reserved
  for Map 9 (the final-chamber approach).
- All six temple interiors carry mute procedural dressing in the game's
  established style-add-on language: coiled serpent idols, glyph stelae,
  terracotta urns, and fallen column drums, none of which change any route,
  count, or hazard.

------------------------------------------------------------------------

# Phase Goal

By the end of this phase the player should:

1.  Explore multiple interconnected temple maps.
2.  Navigate jumps, traps, and environmental hazards.
3.  Fight through skeleton-filled rooms.
4.  Clear a snake chamber.
5.  Reach the temple's final chamber.
6.  Survive a battle between three adventurers and a beholder.
7.  Be struck by a scripted Fireball.
8.  Cross a rubble map filled with Astral Sea hazards.
9.  Crawl through a narrow stone passage.
10. Emerge aboard a ship at sea.

------------------------------------------------------------------------

# 1. Temple Structure

The temple should consist of many connected interior maps rather than
one large floor.

Possible rooms include:

-   entrance halls
-   shrines
-   collapsed corridors
-   trap corridors
-   puzzle passages
-   snake chamber
-   rubble passages
-   final chamber

Maintain the established procedural pixel-art style.

Alternate broad/open rooms with long, narrow connector maps. Temple wall
torches should recur in every authored temple gameplay map. Do not arrange the
dungeon as one continuous northward line: vary the cardinal direction of
successive exits and connectors so the route turns through the structure.

------------------------------------------------------------------------

# 2. Gameplay Focus

Movement and hazard avoidance are the primary gameplay.

Jumping should be used frequently.

Temple hazards should include:

-   dart walls
-   spike pits
-   collapsing floors
-   jump gaps
-   moving hazards

Combat supports exploration rather than replacing it.

------------------------------------------------------------------------

# 3. Enemies

Primary enemy:

-   Skeletons (reuse the existing implementation)

Skeletons continue to be durable enemies.

## Snake Room

Create one dedicated snake chamber.

Snakes are intentionally one-hit enemies.

This briefly lets the player feel powerful before returning to the
temple's normal difficulty.

------------------------------------------------------------------------

# 4. Final Chamber

This room intentionally subverts expectations.

Chuck is not the hero.

He has wandered into someone else's climactic battle.

Present three adventurers:

-   male fighter
-   wizard
-   clearly female ranger

On entering, each delivers a short, non-interactive heroic dialogue line
about continuing the fight.

They battle:

-   a beholder
-   skeletons

The fighter occupies skeletons.

The ranger fires arrows.

The wizard casts spells.

The beholder attacks with eye rays.

All attacks are gameplay hazards for Chuck.

Chuck cannot meaningfully affect the outcome.

For a period of time there is no way forward.

The player's only objective is survival.

Eventually the wizard casts Fireball.

The explosion is scripted, reduces Chuck to roughly half Sanity, and
throws him into the rubble map.

------------------------------------------------------------------------

# 5. Rubble Map

Create a collapsed rubble map containing numerous Astral Sea hazard
blocks.

Reuse the established Astral Sea visual language and hazard behavior.

The only exit is a narrow crawlspace Chuck can fit through.

------------------------------------------------------------------------

# 6. Escape Cutscene

Show Chuck crawling through a tight stone passage.

A light appears ahead.

Chuck emerges into a wooden room.

A hole reveals the open sea.

He has unknowingly reached the deck of a ship.

End the phase here.

Gameplay aboard the ship belongs to Phase 7.

------------------------------------------------------------------------

# 7. Music

Three distinct tracks are required.

## Temple

Mysterious, ancient, and shamanic.

## Final Chamber

A bold heroic adventure theme.

This is the adventurers' boss battle, not Chuck's.

## Escape Cutscene

Brief, enchanting, and mysterious.

------------------------------------------------------------------------

# 8. Story Notes

Do not explain who the three adventurers are.

Do not explain the collided worlds.

The player only witnesses the encounter.

These heroes will return much later.

Eventually the player will discover they are among the people attempting
to repair the collided worlds, while Chuck remains a passerby.

Do not reveal that information yet.

------------------------------------------------------------------------

# 9. Out of Scope

Do not implement:

-   ship gameplay
-   sailing
-   explanation of the adventurers
-   explanation of the beholder
-   explanation of the collided worlds

The phase ends immediately after Chuck reaches the ship.

------------------------------------------------------------------------

# 10. Acceptance Criteria

-   [x] Multiple connected temple maps exist.
-   [ ] Skeletons are the primary enemy.
-   [x] Snakes are one-hit enemies.
-   [x] Jumping and hazards are central throughout the temple.
-   [x] Dart walls and spike pits are
    implemented.
-   [ ] The final chamber contains the fighter, wizard, ranger,
    beholder, and skeletons.
-   [x] Chuck cannot meaningfully influence the battle.
-   [x] Survival depends on hazard avoidance.
-   [x] The scripted Fireball transition works.
-   [x] The rubble map uses Astral Sea hazards.
-   [x] Chuck escapes through a narrow crawlspace.
-   [x] The cutscene ends aboard a ship at sea.
-   [ ] Temple, boss encounter, and cutscene each have distinct music.
-   [ ] Phase 7 begins aboard the ship.
