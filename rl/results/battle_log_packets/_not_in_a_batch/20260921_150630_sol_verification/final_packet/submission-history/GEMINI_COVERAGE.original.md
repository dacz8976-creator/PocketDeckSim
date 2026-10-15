# Coverage Ledger

## Turn and Phase Intervals

- **Setup Phase**: `00:00.000` - `00:09.200`
  - Active/Bench placements, initial hands, coin toss / going first determination, and "Ready? Go!" sequence.
- **Turn 1 (Player)**: `00:09.200` - `00:37.800`
  - Turn start, Wallace played to evolve Carvanha into Mega Sharpedo ex, Poké Ball played, Carvanha benched, turn end.
- **Turn 2 (Opponent)**: `00:37.800` - `01:07.800`
  - Quick Growth resolves evolving Caterpie to Metapod, Professor's Research, Klefki benched, Energy attached, Metapod attacks Magikarp with Ram (KO), point awarded, Mega Sharpedo ex promoted.
- **Turn 3 (Player)**: `01:07.800` - `01:40.800`
  - Professor's Research played, Pokémon Communication exchanges Gyarados ex for Magikarp, Magikarp benched, Energy attached, Mega Sharpedo ex attacks Metapod with Turbo Shark, accelerating Water Energy to Benched Magikarp.
- **Turn 4 (Opponent)**: `01:40.800` - `02:04.400`
  - Quick-Grow Extract evolves Metapod into Butterfree, Professor's Research played, Poké Ball played, Hisuian Zorua benched, Energy attached, Butterfree attacks with Sunny Wind (Mega Sharpedo ex takes 60 damage, Butterfree heals 20).
- **Turn 5 (Player)**: `02:04.400` - `02:59.000`
  - Lucky Ice Pop played twice with consecutive Heads flips to heal Mega Sharpedo ex, Cabbie played (whiffs/no valid Stadium targets), Water Energy attached to Magikarp, Turbo Shark attacks Butterfree, accelerating Energy to Magikarp.
- **Turn 6 (Opponent)**: `02:59.000` - `03:12.800`
  - Hisuian Zorua evolves into Hisuian Zoroark ex, Grass Energy attached, Butterfree attacks with Sunny Wind (Mega Sharpedo ex takes 60 damage, Butterfree heals 20).
- **Turn 7 (Player)**: `03:12.800` - `04:06.800`
  - Wallace played to evolve Magikarp into Gyarados, Lucky Ice Pop played twice (Heads then Tails), Energy attached to Gyarados, Turbo Shark Knocks Out Butterfree, Turbo Shark accelerates Energy to Gyarados, Opponent promotes Hisuian Zoroark ex.
- **Turn 8 (Opponent)**: `04:06.800` - `04:20.400`
  - Energy attached, Caterpie benched, Hisuian Zoroark ex attacks Mega Sharpedo ex with Spiteful Illusion for 140 damage (Mega Sharpedo ex left at 10 HP).
- **Turn 9 (Player)**: `04:20.400` - `04:50.200`
  - Poké Ball played (whiffs/no targets in deck), Mega Sharpedo ex retreats, Gyarados promoted, Water Energy attached to Carvanha, Gyarados attacks with Wild Swing discarding both Benched Pokémon (Carvanha and 10 HP Mega Sharpedo ex) for 100 damage to Hisuian Zoroark ex.
- **Turn 10 (Opponent) & Terminal Sequence**: `04:50.200` - `05:03.699`
  - Hisuian Zoroark ex attacks Gyarados with Spiteful Illusion for 140 damage (KO), awarding Opponent second point. With no remaining Pokémon on Player's field or Bench, game ends in Defeat screen.

## Verification Checklist

- [x] Initial board setup verified
- [x] All 10 turns and player switches tracked
- [x] All Card plays and failure prompts verified (Cabbie whiff, Poké Ball whiff)
- [x] All coin flips documented (Lucky Ice Pop: H, H, H, T)
- [x] Energy generation and Turbo Shark attachments tracked
- [x] Discard mechanics on Gyarados Wild Swing verified
- [x] Terminal condition (loss via total board wipe) verified

## Unresolved Intervals

- None observed. Full match continuity captured without missing frames or transitions.
