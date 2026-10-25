# Exam v2, part 2: labels (written 2026-10-25)

All 52 points in positions.json (13 games, 3 decks) are labelled in `labels.json`. Each key is Dustin's recorded move (`his_move`, copied exactly). Section 3 (segments, scope, replay checks) is left to the assembly.

## Counts by answer kind

| Deck | prepare | attack now | sacrifice | abandon | total |
|---|---|---|---|---|---|
| v2deck_9633a01781 (Dragon: Goomy/Goodra, Dratini line) | 4 | 0 | 0 | 0 | 4 |
| v2deck_5309993874 (Darkness: Mega Sableye ex, Hoopa ex) | 4 | 5 | 0 | 0 | 9 |
| v2deck_4fa967805c (Water: Mega Sharpedo ex, Wailord) | 17 | 19 | 3 | 0 | 39 |
| **All** | **25** | **24** | **3** | **0** | **52** |

Acceptable alternatives are listed at 10 points, one line each: 030939-t2, 031141-t3, 031716-t11, 204724-t2, 212621-t3, 212621-t11, 212621-t13, 213653-t9, 221937-t2 and 224410-t1. The other 42 points have none. Two more alternatives are pending only (see below).

## Questions for Dustin (2 of the 6 allowed)

1. **LAD-20261021_020916000_SR-t9**: In the Igri$ game (20261021_020916), turn 9, you used Cyrus to pull up the 10-HP Flutter Mane and knock it out. Would knocking out the Active 40-HP Carbink with Cursed Jewel instead (keeping Cyrus) have been an equally good play?
   Pending line: `Attach:1Darkness@1 zone`, `Attack:Cursed Jewel`.
2. **LAD-20261021_031141000_SR-t7**: In the えのき game (20261021_031141), turn 7, you put Water on Baltoy and retreated your 80-HP Mega Sharpedo ex instead of attaching to it and using Turbo Shark to knock out the 70-HP Vespiquen ex for 2 points. Was retreating your intended best play, or should the Turbo Shark knockout also count as a good answer (or as the better one)?
   Pending line: `Attach:1Water@0 zone`, `Attack:Turbo Shark`.

## Deck kinds (only the decks in DECK_KINDS_FOR.txt)

- v2deck_4fa967805c: evolution and setup, Bench preparation, sacrifice and recovery, fast pressure.
- v2deck_5309993874: control and combinations, evolution and setup.

## Conventions and things the assembly should know

- **Changing only the order of actions.** Per section 2, a line is a set of actions, so lines that only reorder the key's actions are not listed. The assembly's draw-first rule already covers Research and Poké Ball. Wallace isn't on that list, so where an action before Wallace could just as well come after it, I listed that order as an alternative (221937-t2, 224410-t1).
- **Bench slots.** Benching the same card in another empty slot (for example `Place:Goomy@3` instead of `@2`) is not listed. If the replay doesn't treat that as the same position, this has to be handled in matching.
- **Wallace target labels.** When only one Pokémon can be targeted, the engine's label has no arguments (`ChooseRandomEvolutionTarget`), as in 224410-t1 and 213653-t9. So the alternatives at 030939-t2 (no Poké Ball, so the Active Carvanha is the only target) and 221937-t2 (Wallace before the second Carvanha is benched) use the bare label. The replay check should confirm this.
- **Poké Ball / Wallace that visibly can't find anything** (212621-t11: no Basics left in the deck; 213653-t9: both Mega Sharpedo ex already out of the deck). For both I listed the same turn without the dead card as acceptable.
- **Board notes from the positions file.** 224410 t9-t13 note a Water left on the benched Mega Sharpedo ex after a retreat that costs 0. It doesn't change any label.
- **Nothing was left unlabelled.** No point was dropped. All first actions of the listed and pending lines are in that point's legal list. Later steps weren't checked with a tool (I had none), so the assembly's replay check should confirm them.
