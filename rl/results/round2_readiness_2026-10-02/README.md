# Round-2 readiness (the cloud, Oct 2)

Three short jobs to make the round-2 package (everything `claude/coin-prevention-round2` adds to the official engine: the
later coin round, the card-text job and its follow-up) ready for the next rules switch. There were no table games and no
`players/` change.

## 1. Which lists and pairings the package can change

Inputs: main at 7c1b62f, with all 68 deck lists under `decks/` (`drafts_2026-10-01/` included; the other 15 `.txt` files there are
coverage and check pages), plus the 14 lists outside `decks/` that the pairing files name (B2e, and the carriers and scratch
lists of steps 8 and 8b). The card sets come from the card text in `engine/database.json`. `inventory.py` builds them and
`inventory_output.txt` prints every printing. A pairing is **expected to change** when a repaired mechanic can act in its games.
"Can act" does not mean it will: a game changes only if the cards meet in play. A pairing not listed cannot change through the
package.

Which lists hold the cards:

| Mechanic | Lists |
|---|---|
| Wild Swing (Gyarados) v a coin Ability | `l-sharpedo` (2 Gyarados A4 045). Four carriers supply the coin Ability. |
| Wellspring Dance, Tornado Shot, Double Splash, Triple Bombardment, second punch, Mischievous Ring, Litter | none |
| Will with a Confused attacker | Users: brew-01, brew-04, Dustin's 10. Twelve lists supply the Confusion (Weezing lists, Meowstic lists, brew-04, Dustin's 10, two scratch lists). |
| Victory Star with a block coin | none (draft D holds Victini, but no list holds a block-coin attack) |
| Will with a block coin | none |
| coin Abilities on your own Pokémon; the opponent's Active in an own-Bench choice; a copied discard attack | none |
| Trap Territory, two Ariados | Dustin's 12 and B2e's `h-whimsicott`. Both are one-sided: every pairing of these lists can change. |
| Luxury Coin on the opponent's Stadium | none (no Gholdengo list meets Mesagoza or Arcade) |
| a Fossil under an Item lock | none |
| Guts on your own Pokémon (E1) | none |
| Perish Body on a plain queued hit (E2) | none (no list holds Galarian Cursola) |

The pairings expected to change:

| Set | Expected to change | Which |
|---|---|---|
| Table, 28 cells (research lists) | 0 | |
| New 17 cells (scoreboard v3) | 0 | |
| B2e, 96 | 16 | `h-whimsicott` and Dustin's 12, each v all 8 panel lists (Trap Territory) |
| Carriers, steps 8 and 8b, 36 | 1 | `l-sharpedo` v `meowth_carefree` (Wild Swing) |
| Dustin's decks v the panel, step 7c, 32 | 0 | (it holds Dustin's 02, 06, 08 and 14) |
| Screen and floor (60 lists x 8 panel lists) | 11 | Dustin's 12 v all 8 (Trap Territory; floor page on record); brew-01, brew-04 and Dustin's 10 (floor page on record) v `t-weezing` (Will with a Confused attacker) |

So the switch costs 17 named pairings: 16 B2e and 1 carrier. The table and scoreboard v3 don't move. The screen and floor have
11 pairings over 4 lists. Two of those lists have floor pages that would need rerunning: Dustin's 10 (one pairing) and Dustin's
12 (all eight).

The amended draft D (one Mega Houndoom ex) doesn't change this. D holds no Will. Its Victini changes only against a block-coin
attacker, and no list holds one. Draft D's Victini against a Confused attacker is the official engine's Victory Star repair,
not the round-2 package.
