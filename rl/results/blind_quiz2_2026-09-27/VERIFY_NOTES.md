# Quiz 3 verification (Sept 27, 2026)

**Verdict: pass, with three small notes and one caveat.** I did not build quiz 3; I checked it with my own scripts, not `build3.py`. Nothing in this folder except this file, and nothing in `quiz-2026-09-25` or the repo, was changed.

## How I checked

- **Replays:** both games for all 10 seeds (20 games, not just 5), with `rl/engine-2026-09-27/deckgym`. Its sha256 (27626eb5…7bf7931) equals `project_manifest.json`'s `available_release`.
- **Seats:** from each seed's own `selected.json` record (the deck named in DIAGNOSIS section 5), with legality_scan's rule (seed = 72,000,000 + pairing × 10,000 + i, first_seat = i % 2, kpf3 on the diagnosed deck only).
- **Dump comparison:** every ply against its DUMP2 line. I compared the turn, the player to move, the actor, and both boards: Energy Zone, discard Energy, hand size, points, and each Pokémon's name, HP, conditions and Energy. For the action I compared its kind only, not the full text.
- **First difference:** my own code finds it. I then compared the state there with `positions3.json` field by field: points, both Active and Bench spots, HP, Energy, Tools, deck and discard counts, the Energy Zone, your hand, the opponent's hand size, your decklist's "left" counts, the Supporter and retreat flags, and the Stadium.
- **Options:** grouped with my own "same move" rule. Bench spots count as the same when everything visible about them is equal. I also re-checked every merge on all hidden engine fields.
- **Re-render:** I rendered each position from my own replays with a scratch copy of `describe.py` (same SHA-256 as quiz 1's and this folder's). All 10 came out identical to `positions3.json`.
- **Scripts:** `verify3.py`, `verify3b.py` and `verify3c.py`, with output in `verify3_out.txt` and `verify3b_out.txt`. They are in the session scratchpad (`C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad`), not here.

## Pass/fail

| # | Check | Result |
|---|---|---|
| 1 | Replays reproduce the table games | **PASS**, all 20. Every baseline matches every `dump_base.txt` copy of its seed. Each kpf game matches exactly one `dump_kpf.txt` copy: 72050131 (Altaria) is copy 1 (line 21027), 72200103 is copy 2 (line 51610) and 72050138 is copy 2 (line 23256), as DIAGNOSIS says. |
| 2 | Results | **PASS.** Winner seat, points and final turn equal `table_kp3.jsonl` and `mixed_table_kpf3_<config>.jsonl` for all 20 games. The diagnosed deck's score change equals `selected.json` in all 10: nine −1, and Q09 +1. |
| 3 | First difference | **PASS**, all 10. It is a choice with identical states and moves before it, by the diagnosed deck's seat, at DIAGNOSIS's turn, with the same legal moves in both games. The plies are 15, 28, 13, 15, 13, 25, 27, 17, 16 and 26, equal to `ply_index` in the answer key. |
| 4 | Page state = true game state | **PASS**, all 10. Hand, boards, Energy, Tools, HP, points, Energy Zone, deck and discard, and decklist counts all match. |
| 5 | Answer key = replays | **PASS**, all 10. `kp3_keys` and `kpf_keys` contain the indices of each bot's actual move. Both option texts are the options those moves fall under. The written whole turns match the replayed turns move for move. Results, final points and final turns all match. |
| 6 | Options: full legal list, both bots' moves present | **PASS.** There are 77 options for 83 legal moves, and every legal move is behind exactly one option. The six merges are three exact duplicates (Q01 Mega Lucario ex, Q05 Fragrant Forest, Q06 X Speed) and three identical spots (Q04 Swablu to Bench 1 or 2, and Q10's Shuckle ex on Bench 1 or 3, for attach and for retreat). None of them differs in any hidden engine field. The two bots are on different options in all 10. |
| 7 | Blindness | **PASS.** Option fields are only key, group and text. The options follow the fixed group order (Attack, Trainers, Stadium, Energy, Pokémon, Retreat, End turn). There is no seed or 72xxxxxx number, no bot name, and no result, win, loss, "worse" or "better". The opponent shows hand size only, and its Energy Zone shows Next only. No card that is only in the opponent's hand or deck is named. The only hit, "Lucario" in Q06, is part of the Mega Lucario ex on the board. See note 4 on option order. |
| 8 | `quiz.html` can load `positions3.json` | **PASS.** The top-level fields are exactly quiz 1's, and the nested shape is the same. The one new path, a Tool on a Benched Pokémon (Q10), uses the same code as the Active. The page reads the documents in a `positions` collection, sorted by `order`, as `write_seed.py` did. See note 3. |
| 9 | Dustin's three rules answers | **PASS.** Rainbow Cave (answer 1), Garganacl's Blessed Salt (answer 2) and Professor Sada / Ancient Pokémon (answer 3) are in none of the 20 games' decks, and no Pokémon is Poisoned in any of them. |
| 10 | `quiz-2026-09-25` untouched | **PASS.** Its newest file is still GRADING_NOTES.md (Sept 26), and it has no `__pycache__`. `quizlib.py` here differs from quiz 1's only in ENGINE and the docstring. |

## Compared with DIAGNOSIS section 5

The builder's list of differences is accurate. I confirmed each one against the replays:
- **Q05:** there is no Shuckle ex in hand. The hand is Field Blower, X Speed, Leaf Cape and two Fragrant Forest. In both games Fragrant Forest's random pick gave Shuckle ex.
- **Q09:** kp3 plays Protective Poncho first.
- **Q03:** the opponent's Heatmor holds a Rocky Helmet.
- **Q04:** kpf also benches the second Swablu.
- **Q02:** both bots play Research.
- **Q06:** both bots bench Teal Mask Ogerpon ex from Fragrant Forest.
- **Q10:** there are two Leaf Capes. DIAGNOSIS's 160 and 170 HP already include them.

Q01, Q07 and Q08 match as written.

Two notes DIAGNOSIS marks "for the record" also check out:
- **Q02:** in kpf's game, Mega Lucario ex was at 100 of 190 at the start of Lucario's next turn, so it had taken 90.
- **Q07:** kp3 moved Darkrai up on turn 6, and its Torchic went down on turn 5, against turn 6 in kpf's game.

One small correction to BUILD_NOTES: it lists "Combee is 40/50" as missing from DIAGNOSIS. DIAGNOSIS does give 40 HP; it only leaves out that Combee is damaged.

## Notes (none blocks the quiz)

1. **Q01's grading note overstates the first tap.** The answer key says evolving on the Bench points to kp3's plan. But Bonsly retreats for free, so evolving on the Bench and then retreating into Mega Lucario ex ends on kpf's board. Q01 needs the plan too. The "first tap can't tell" list should be Q01-Q07 and Q09; only Q08 and Q10 are settled by the first tap.
2. **Q05 caveat.** The fork DIAGNOSIS cares about comes after a random pick: Shuckle ex attacking after X Speed and a retreat, or Combee attacking. The deck holds four Basic Grass (Combee, Shuckle ex ×2, Teal Mask Ogerpon ex), so Shuckle ex is a 50% pick. Dustin's answer tests fix A only if his plan says what he'd do when the Forest gives Shuckle ex. If his plan doesn't say, ask him that one question in chat after he answers. Don't add it to the page.
3. **Publish as a new artifact.** Quiz 3's ids Q01-Q10 are the same as quiz 1's, and quiz 1's store already holds Dustin's answers under those ids. Loaded into quiz 1's artifact, the page would show them as answered and mix the two quizzes.
4. **Option order is fixed, not a leak.** kp3's option sits above kpf's in 9 of 10, because Retreat comes near the bottom and kpf's move is a retreat in 7 of 10. The page never says which options the bots chose, so a reader can't use this.
5. **Minor rules oddity, Q04.** The Altaria player is offered "Use the Stadium Fragrant Forest" though Altaria has no Basic Grass Pokémon. Neither bot chose it. Whether Pocket lets you tap it there is unchecked.
