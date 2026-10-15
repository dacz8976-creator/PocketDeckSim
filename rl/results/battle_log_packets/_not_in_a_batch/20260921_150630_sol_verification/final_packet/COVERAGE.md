# Coverage Checklist: 20260921_150630000_iOS.MP4

## Full independent source review

- [x] Setup and visible opening state, 00:00.000-00:09.200
- [x] Turn 1, player, 00:09.200-00:37.800
- [x] Turn 2, opponent, 00:37.800-01:07.800
- [x] Turn 3, player, 01:07.800-01:40.800
- [x] Turn 4, opponent, 01:40.800-02:04.400
- [x] Turn 5, player, 02:04.400-02:59.000
- [x] Turn 6, opponent, 02:59.000-03:12.800
- [x] Turn 7, player, 03:12.800-04:06.800
- [x] Turn 8, opponent, 04:06.800-04:20.400
- [x] Turn 9, player, 04:20.400-04:50.200
- [x] Turn 10 and terminal result, 04:50.200-05:03.699

The verifier reviewed the complete timeline at coarse intervals and expanded every action window needed to reconcile setup, searches, hand/deck exchanges, Energy, healing, attacks, damage, knockouts, score, switching, Bench changes, and the terminal result. The retained set contains 104 full-resolution frames. This is not a claim that every decoded source frame was individually inspected.

## Required event audit

- **Deck searches and failed searches:** Turn 1 Poke Ball to Carvanha; Turn 3 Pokemon Communication exchanges Gyarados ex for Magikarp; Turn 4 Poke Ball to Hisuian Zorua; Turn 5 Cabbie no-target; Turn 8 Poke Ball to Caterpie; Turn 9 Poke Ball no-target.
- **Energy attachments and acceleration:** Opponent Grass Energy reconciled across Turns 2, 4, 6, and 8. Player Water Energy reconciled across Turns 3, 5, 7, and 9.
- **Return-to-hand and replay:** Lucky Ice Pop is the same physical card replayed after Heads. Turn 5 is Heads/Heads; Turn 7 is Heads/Tails.
- **Knockouts and score:** Magikarp KO and 0-1; Butterfree KO and 1-1; Gyarados KO and 1-2.
- **Switches, retreats, and Bench changes:** Mega Sharpedo ex promotion after Magikarp KO; Zoroark ex promotion after Butterfree KO; Turn 9 retreat to Gyarados; both player Bench Pokemon discarded by Wild Swing.
- **Terminal sequence:** Spiteful Illusion, Gyarados KO, second opponent point, empty player board, literal Defeat.

## Gemini corrections integrated

- Auto visibility does not prove Solo mode. Solo/PvP remains unknown.
- Turn 4 Poke Ball occurs before Professor's Research, and the Grass Energy is attached to Zorua, not Butterfree.
- Turn 5's manual attachment raises Magikarp to two Energy; Turbo Shark gives Carvanha its first.
- Turn 6 gives Zoroark ex its second Grass Energy.
- Turn 7 gives Gyarados its third Energy manually and its fourth through Turbo Shark; it never reaches five.
- Turn 8 includes Poke Ball, Caterpie search/Bench, and one attachment that raises Zoroark ex from two to three Energy.
- Turn 9 begins with Gyarados at four Energy and raises Carvanha from one to two before Wild Swing.

## Remaining uncertainty

No visible gameplay interval remains unreviewed. Match mode, hidden information, and the player's unspoken strategic intent remain explicitly unknown where the recording does not establish them.
