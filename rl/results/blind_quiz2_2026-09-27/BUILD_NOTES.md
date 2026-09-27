# Quiz 3 build notes (Sept 27, 2026)

The second blind quiz holds the ten positions from the kpf veto diagnosis (`rl/results/kpf_2026-09-26/diagnosis/DIAGNOSIS.md`, section 5), in that section's order as Q01-Q10. Everything is in this private folder, and nothing was written to the repo or to `quiz-2026-09-25` (its newest file is still from Sept 26).

## Files

| file | what |
|---|---|
| `positions3.json` | What the page loads: a list of 10 display models, the same format as quiz 1's `positions_final.json` (version 2, with the decklist). Ids are Q01-Q10 with order 1-10. There are no seeds, bot names, results or hints. |
| `answer_key3.json` | Private. For each Q: seed, deck, config, pairing, deal, seats and players for both games. Also kp3's and kpf's option keys (every key equal to each bot's first move), both first-move texts, each bot's whole turn in plain words (replayed), both results with final points and turns, a `decision` field for grading, and DIAGNOSIS.md's board, choices and "decides" note. |
| `candidates3.jsonl` | Private. For each position: the engine state, the legal moves, both choices, both results and the history. |
| `build3.py`, `build3.sh`, `build3.log` | The build and every check. Run `wsl -e bash build3.sh`. The log is the full output of the last run. |
| `describe.py` | A verbatim copy of quiz 1's (same SHA-256, 62945E4E…). |
| `quizlib.py` | A copy of quiz 1's with one change: `ENGINE` points to the official Sept 27 engine. |

## What was done

- **Engine:** `rl/engine-2026-09-27/deckgym`. Its sha256, 27626eb5…7bf7931, equals project_manifest.json's `available_release` (main-83e17ae). The DUMP2 traces came from legality_scan built from the same commit, plus a watch-only print hook.
- **Seats:** taken from each seed's own selected.json record (deck and config) and legality_scan's `play_one`. seed = 72,000,000 + pairing × 10,000 + i, and first_seat = i % 2. For three seeds, selected.json has one record per deck. The diagnosed deck named in DIAGNOSIS.md picks the record: 72050131 is Altaria (first), and 72200103 and 72050138 are Vespiquen (second).

| Q | seed | turn | diagnosed deck (config) | seat 0 | seat 1 | kpf game players |
|---|---|---|---|---|---|---|
| Q01 | 72130094 | 3 | Lucario (second) | hydreigon | lucario | kp3,kpf3 |
| Q02 | 72190009 | 4 | Lucario (first) | suicune | lucario | kp3,kpf3 |
| Q03 | 72080079 | 2 | Lucario (second) | lucario | blaziken | kpf3,kp3 |
| Q04 | 72050131 | 2 | Altaria (first) | vespiquen | altaria | kp3,kpf3 |
| Q05 | 72160098 | 2 | Vespiquen (second) | hydreigon | vespiquen | kp3,kpf3 |
| Q06 | 72200103 | 4 | Vespiquen (second) | vespiquen | lucario | kpf3,kp3 |
| Q07 | 72000056 | 4 | Altaria (first) | altaria | blaziken | kpf3,kp3 |
| Q08 | 72010118 | 3 | Altaria (first) | altaria | hydreigon | kpf3,kp3 |
| Q09 | 72020118 | 2 | Lucario (second) | altaria | lucario | kp3,kpf3 |
| Q10 | 72050138 | 3 | Vespiquen (second) | altaria | vespiquen | kp3,kpf3 |

Each position was built in four steps:
1. Play the baseline game (kp3,kp3) and the kpf game with `deckgym simulate --seed <seed> --data-output`.
2. Compare both games with the dumps and the table rows.
3. Find the first differing choice with `quizlib.first_diff`.
4. Render the position with `describe.render_full`, the same call quiz 1 used, and pick each bot's option with `describe.option_for`.

The log and the "this turn so far" lines come from the baseline game's earlier moves. They are the same in both games, because first_diff requires equal states and equal choices before the difference.

## Checks and results (all passed; `build3.log`)

1. **deckgym simulate reproduces the scan's games: yes, all 20.**
   - Each game was compared ply by ply with the DUMP2 lines for its seed:
     - tick, turn and player to move;
     - the actor;
     - the chosen action, as Rust's `{:?}` text cut to 160 characters, exactly as the dump prints it;
     - both seats' boards: the Energy Zone (current and next), the discard Energy count, hand size, points, and every Pokémon's name, HP, conditions and Energy.
   - Every baseline game equals its dump_base.txt trace, with the same number of lines as plies (1,016 lines in all). For 72050131, 72200103 and 72050138, dump_base.txt holds two copies, one per config's run, and the baseline equals both.
   - Every kpf game equals exactly one dump_kpf.txt copy, and it is the expected one. On the three two-copy seeds, the runs came in config order: 72050131's Altaria game is copy 1, and 72200103's and 72050138's Vespiquen games are copy 2. This agrees with DIAGNOSIS.md's line numbers.
2. **Results match the table:** winner seat, points by seat, final turn and bots all equal the rows in `reading/table_kp3.jsonl` and `reading/mixed_table_kpf3_<config>.jsonl`, for all 20 games. The diagnosed deck's score change (kpf minus baseline) equals selected.json's `change` in all 10: nine are −1 and 72020118 is +1.
3. **First difference:** in all 10 it is a choice (equal states before it), made by the diagnosed deck's seat, at the turn DIAGNOSIS.md names. Both games offer exactly the same legal moves there. The two dumps also first differ at the same tick.
4. **The bots' moves are different options:** in all 10, even after identical Bench spots are merged.
5. **First moves:** each bot's first move is checked against a fixed list in build3.py, so the answer key can't drift silently. kp3 / kpf:
   - Q01: evolve on the Bench / retreat
   - Q02: Professor's Research / retreat
   - Q03: attach F to the Benched Riolu / retreat
   - Q04: bench Swablu / retreat
   - Q05: Leaf Cape / Fragrant Forest
   - Q06: evolve on the Bench / retreat
   - Q07: attach P to the Benched Darkrai / retreat
   - Q08: attach P to Swablu / attach P to the Active Darkrai
   - Q09: Protective Poncho / attach F to Riolu
   - Q10: retreat into Shuckle ex / retreat into Vespiquen ex
6. **The full legal move list:** 77 options for 83 legal moves. Every legal move is behind exactly one option. Six moves were merged into others:
   - 3 duplicate engine moves (two copies of a card in hand): Q01's Mega Lucario ex, Q05's Fragrant Forest and Q06's X Speed;
   - 3 identical-spot merges: Q04's Swablu to Bench 1 or 2, and Q10's identical Benched Shuckle ex (Bench 1 or 3), for both the attach and the retreat.
   No merged spot differs in any hidden engine field. Option order is `describe.build_options`' order, which never sees the bots' choices.
7. **Leak test** (build_final.py's, adapted to 10 positions):
   - top-level, opponent-side and option fields are exactly quiz 1's;
   - the opponent shows hand size only, and it is correct;
   - the opponent's Energy Zone shows only Next;
   - no seed, no 72xxxxxx number, no bot names (k3, kp3, kpf, any kp?3), and no result, outcome, winner, choice, state, hands, decks, cards, pairing, config or answer-key fields;
   - no opponent hand card and no deck-only card named anywhere;
   - the opponent's deck name appears only inside card names the player has seen;
   - the own decklist has only the player's own cards, 20 in all, with 'left' equal to the deck;
   - every option key is a legal move. **Passed.**
8. **Blind re-render:** each position was rendered again with both bots' choices and results removed from its data, and the output was identical. The page data doesn't depend on which bot did what. **Passed.**
9. **Negative checks:** 180 planted leaks across the 10 positions (18 kinds), and all 180 were caught. The kinds:
   - seed as the id or in the text;
   - a bot key field, or a bot name in an option;
   - a result field;
   - the opponent's hand shown, or its size wrong;
   - an option dropped or the options reordered;
   - the opponent's deck name in the matchup or the situation;
   - a planted, opponent-only or wrongly counted decklist row;
   - an opponent hand card in the log;
   - a deck-only card in "can't play".
10. **describe.py's own self-test**, run on the 10 positions. In its labels, "k3" means kp3 and "kp3" means kpf. 0 problems:
    - legal moves and options match one to one;
    - the Retreat Cost model agrees with the engine in all 10;
    - 33 hand cards were checked for playability against the engine;
    - both seats' cards come from their deck lists;
    - the log's between-turn damage and knockouts are all explained;
    - planted leaks are caught, and unknown move kinds raise.

## Where the positions differ from DIAGNOSIS.md's descriptions

Board, opponent and both choices were compared with section 5 by reading the rendered positions and the replayed turns.

- **Q05 (72160098) differs most.**
  - DIAGNOSIS gives the hand as "Shuckle ex, X Speed, Leaf Cape, Fragrant Forest, Field Blower". The real hand is Field Blower, X Speed, Leaf Cape and two Fragrant Forest. **There is no Shuckle ex in hand.**
  - In both games Shuckle ex came from using Fragrant Forest (a random Basic Grass from the deck) and was then benched.
  - Also missing from DIAGNOSIS:
    - Combee is 40/50.
    - The opponent's Mega Absol ex holds Deceptive Needle, and both bots play Field Blower on it.
    - Both bots play Leaf Cape on Combee and Fragrant Forest.
  - The first differing tap is only an order: Leaf Cape (kp3) or Fragrant Forest (kpf). The fork DIAGNOSIS describes (Shuckle ex after X Speed with Triple Slap, or Combee with Reckless Charge) comes after the random pick. Grade this one on the plan (answer key `decision`).
  - The dumps show hand size only, which is probably where the guess came from (DIAGNOSIS caveat 5).
- **Q09 (72020118):**
  - kp3's first move is Protective Poncho on the Active Riolu, then F to the Benched Hitmonlee.
  - kpf attaches F to Riolu, retreats into Hitmonlee, then puts Poncho on Hitmonlee.
  - DIAGNOSIS leaves Poncho out. The first taps are Poncho (kp3) or attach to Riolu (kpf).
- **Q03 (72080079):**
  - The opponent's Heatmor holds a Rocky Helmet (not mentioned). It did 20 to the attacker in both games: Bonsly in kp3's, Riolu in kpf's.
  - Riolu was benched earlier this turn with Poké Ball, which the page shows as already done.
- **Q04 (72050131):**
  - "Two Swablu in hand or on the Bench" means one on Bench 3 (benched this turn after Professor's Research) and one in hand.
  - kpf also benches the second Swablu after retreating; DIAGNOSIS doesn't say so.
  - The opponent's Fragrant Forest is in play.
  - kp3's Sleepy Lullaby did 0 damage because of Shuckle ex's Solid Shell (−20).
- **Q02 (72190009):** both bots play Professor's Research and bench a second Riolu. kpf plays Research after retreating. DIAGNOSIS lists Research only for kp3.
- **Q06 (72200103):** after the fork, both bots use Fragrant Forest and bench Teal Mask Ogerpon ex (not mentioned).
- **Q10 (72050138):**
  - Teal Mask Ogerpon ex and Vespiquen ex each hold a Leaf Cape (not mentioned).
  - kp3's retreat goes to the Shuckle ex on Bench 3. The option reads "a Benched Shuckle ex (Bench 1 or 3)", because the two are identical.
- **Q01, Q07 and Q08** match DIAGNOSIS as written.
  - Q01's order: kp3 plays evolve, Research, attach, Teary Attack. kpf plays retreat, Research, evolve, attach.
  - Q07's kp3 line: Bad Dreams from both Darkrai did 40 to the sleeping Torchic at the end of the turn.

## Grading notes

- In several positions the first tap alone can't tell the two plans apart, because one bot's first move also starts the other's plan in a different order. This happens in Q02, Q03, Q04, Q05, Q06, Q07 and Q09.
- Each answer key entry has a `decision` field that says what to compare, the same way quiz 1's did. Grade on it, and read the written plan. The page already requires a plan for any move that doesn't attack or end the turn.
- All 10 positions come from games where the two bots' results differ, by selection. Nine are "worse for kpf" and Q09 is the one "better" game.

## Not done

- No artifact was published or changed.
- `quiz.html` was not copied or edited. It would load `positions3.json` as one document per position in its `positions` collection, the way quiz 1's `write_seed.py` did.
- Dustin's three rules answers relayed with this task (turn energy, Poison and healing at 0 HP, and the Energy attach onto Ancient Pokémon) touch none of these ten positions. No Poison, healing or Ancient Pokémon appears in them.
