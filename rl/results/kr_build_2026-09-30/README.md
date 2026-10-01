Decision this informs: none on its own. This is the cloud's build of TIMING.md's C2 (`../kn_build_2026-09-30/TIMING.md`) as `kr<N>`, with a one-sided diagnostic `kro<N>`.
- Dustin approved building it as the next candidate (the Fable coordinator via Dustin, Sept 30: "build only; the registration is the laptop's and Dustin's, after the rules switch pins").
- No table game, no identity replay, no merge.
- **The build** is two commits on `claude/pensive-ptolemy-spwc0b`. They touch `engine/src/players/` and one new test file, `engine/tests/kr_judged_turns_test.rs`:
  - `6a5f225`: the tests, on a scaffold whose C2 charge was still 0, so they failed first;
  - `7c882b5`: the rule.

Seeds: only Claude diagnostic seeds, and scratch decks or the floor's own deals.
- The unit tests' random games use 20,952,000,000 + 10 × pair + game, and their 200 deals 20,953,000,000 + i.
- The judged turns replay the floor's own games (seeds 7100 to 14600, as `floor.py` played them).
- The smoke repeats kn's smoke's seeds: 20,960,000,000 + 100,000 × deck + 10,000 × opponent + 5,000 × seat + game.

# kr: km + C2, a benched threat pays its Active's way out (Sept 30 – Oct 1)

## In plain words

- **What kr is.** km3, with one change to its clock (its estimate of how many turns each side needs to win). An attacker waiting on the Bench now has to pay for its way into the Active Spot: the Energy its side's Active still lacks to retreat. This applies to both sides; `kro` applies it to the opponent's attackers only.
  - Goo-zooka's +1 Retreat Cost counts only if it's still in effect on the turn that attacker would come in.
  - N1's flat term (kn) is off.
  - With C2 off, kr3 plays exactly as km3: checked move for move on 200 scratch deals.
- **What it fixes.** The tie is gone. kr3 doesn't play Goo-zooka at the first chance:
  - its median first play is turn 7, like km3's, against kn3's turn 2;
  - in the Grass Knot deck, 364 of its 388 plays come right before a Grass Knot, as km3's do (359 of 360). kn3's did so in only 120 of 677.
- **What it doesn't do.**
  - **It rarely plays Goo-zooka at all:** 1.6% of chances in the plain Goo-zooka deck, against km3's 0.1% and kn3's 86%.
  - **On the diagnosis's judged turns it plays only 1 of the 6 that TIMING.md predicted** (11602 turn 4), and correctly none of the 3 "no" turns. TIMING.md's reading was wrong for the other five. The reasons are in km's clock, not in C2's arithmetic:
    - the clock picks the readiest attacker as the threat, so an opponent's Active that can attack at all (Deino, Igglybuff, Chien-Pao ex) is the threat, and nothing on the Bench pays;
    - it can't see Energy from Abilities (Hydreigon's Roar in Unison) or the opponent's evolutions (Espeon);
    - it doesn't price the damaged Active that a raised cost strands.
- **Its footprint is large, as TIMING.md warned.** The control deck (no Goo-zooka, no Plaza) plays differently in 297 of 600 games under kr3, and 117 of 600 under kro3. So most of the reach is the bot's own half: C2 also changes how the bot values its own Bench.
- **In the smoke the wins are mixed and small** (paired deals, below). These are scratch decks; they describe these games, not strength.

## Names

- `kr<N>` (C2 on both sides) and `kro<N>` (the opponent's clock only, the diagnostic for attribution).
- No existing code starts with `kr`: the k-codes are `k`, `kp`, `kq`, `kd`, `kpr`, `kpf`, `kpg`, `kph`, `kpha`, `kphb`, `koa`, `kob`, `kor`, `kog`, `koh`, `kt`, `kta`, `ktb`, `ktc`, `km` and `kn`.
- `kro` is parsed before `kr`, and both before `k<N>`, which would reject them. `kor3` and `kn3` parse as before (the parser test).

## What was built (`git diff cae37a3 7c882b5 -- engine/`, less kn's lines; `value_functions.rs`, `mod.rs`, `public_pricing_player.rs`)

- **Flags and presets.**
  - `EvalFeatures` gets `retreat_opponent_threat` and `retreat_own_threat`. They are false in `OFF`, `KQ`, `KD` and `KPR`, so in every preset but the two new ones.
  - `KR = EvalFeatures { retreat_opponent_threat: true, retreat_own_threat: true, ..EvalFeatures::KM }`.
  - `KRO` is the same with the opponent's flag only.
  - N1's flag is off in both (`KM` has it off).
- **The clock.**
  - `kt_clock_stadium` becomes `kt_clock_c2` with a `retreat_in` parameter. `kt_clock_stadium` stays as a test-only wrapper with it off, so km's and kt's tests call it as before.
  - `kt_clocks` passes `retreat_opponent_threat` to the clock of how soon the opponent wins, and `retreat_own_threat` to the bot's own.
  - With `retreat_in` on, before the threat is picked, every benched candidate's missing Energy gets `benched_retreat_shortfall`. The Active's own candidates are unchanged.
- **`benched_retreat_shortfall`, C2 as TIMING.md states it:** `max(0, the Active's board Retreat Cost − the Energy attached to it)`.
  - **The cost** is the engine's own `get_board_retreat_cost_for_player`: Tools, Stadiums, Trap Territory, Villainous Delivery and the stored effects, but not this turn's discounts.
  - **Goo-zooka's timing.** A stored `IncreasedRetreatCost` counts only if it's live on the turn the threat would otherwise attack. That turn is `first_attack_turn_number` for the candidate's missing Energy plus the shortfall without such effects. An effect with d turns left is live through turn t + d, as switch 1 reads a temporary cut.
  - **How it's computed.** The cost is read from a copy of the Active whose stored effects are rebuilt without the expired ones. That copy also has its Special Conditions cleared, which the board cost doesn't read.
  - **Stated limit:** an Active that can't retreat at all (a Special Condition that blocks it, or `NoRetreat`) gets no charge, as today. A fossil's board cost is 0, so it gets none either.
- **`mod.rs`:** `PlayerCode::KR` and `KRO`, the parser lines, and their `get_player` arms with km's pilot (public pricing, depth N, no opponent ply).

## Tests (all pass at `7c882b5`)

| test | what it shows |
|---|---|
| `kr_and_kro_are_km_plus_c2_and_nothing_else` | `KR` and `KRO` with their flags cleared equal `KM`, every field; `KRO` is `KR` without the bot's own half; all 20 other presets have both flags off |
| `c2_pin_the_shortfall_is_the_engines_retreat_arithmetic` | on boards with Goo-zooka's effect, Peculiar Plaza on a [P] and a non-[P] Active, Trap Territory, Small Balloon, Inflatable Boat, Bombirdier, and the three combined, for every Energy count from 0 to cost + 1: C2's charge equals the fewest Energy the engine needs added to the Active before it offers a Retreat. An Asleep Active gets no Retreat from the engine and no charge from C2 |
| `c2_counts_a_raised_cost_only_while_it_is_live_when_the_threat_would_attack` | Goo-zooka's +1 (1 turn left) counts for a benched threat that would attack on the opponent's next turn and not for one that would attack two turns later. An effect with 3 turns left counts for that later one |
| `c2_moves_the_clock_only_where_a_benched_threat_waits` | Mewtwo ex waiting behind Dratini with 1 Energy: km's lead 1, kr's 2 with Goo-zooka's effect, unchanged without it or with Mewtwo ex in front. The bot's own side the same |
| `on_played_states_kr_and_kro_are_km_with_their_flags_cleared_and_differ_somewhere` | every position of 10 random games of the scratch pairs, both views: with the flags cleared, kr and kro are km bit for bit; in setup, kr = kro = km; both differ from km somewhere |
| `kr3_with_c2_off_equals_km3_move_for_move_on_200_scratch_deals` | kn's five scratch pairs, 40 deals each: km3 (as `deckgym simulate` builds it) and kr3 with C2 off play the same moves, choices and results in all 200. kr3 itself differs from km3 in at least one of the first 40 |
| `kr3_from_get_player_plays_goo_zooka_where_it_delays_their_benched_threat_and_not_otherwise` | the Mewtwo-ex-behind-Dratini board through `get_player`: kr3 and kro3 play Goo-zooka, km3 ends the turn; with Mewtwo ex in front, kr3 ends the turn |
| `kr_and_kro_parse_before_k_and_nothing_else_moves` | `kr3`, `KR5`, `kro3`, `KRO5` parse; `kr`, `krx`, `kr3x`, `kr1a`, `kro`, `krox`, `kro3x` don't; `km3`, `kn3`, `kor3`, `kog3`, `kt3`, `kta3`, `kph3`, `k3` as before |
| `kr3_on_the_ten_judged_goo_zooka_turns_plays_it_on_11602_only_and_km3_on_none` (`tests/kr_judged_turns_test.rs`) | the diagnosis's 10 judged turns, each reached by replaying its floor game with km3 (a guard checks the opponent's Active is the one the diagnosis recorded), then played by kr3 and by km3. **It pins what C2 does: kr3 plays Goo-zooka on 11602 turn 4 only; km3 on none.** TIMING.md's six-turn reading is recorded beside each case. The lists are embedded |

- **Tests first.** At `6a5f225` the presets, the parser and the C2-off identity passed. The pin, the liveness, the clock, the played-state difference, kr3-differs, the wiring and the judged turns failed.
- **Two tests were corrected after the rule went in. Neither is a rule change:**
  - **The pin's Goo-zooka effect now has 9 turns left.** With 1 turn left, a retreat that itself waits for attachments comes after the effect expires: that is the liveness test's subject, not the arithmetic's. With 0 Energy on the Active, C2 charged 2 where the engine's cost now is 3, and both are right.
  - **The judged-turns test was rewritten from TIMING.md's expectation (6 of 6) to the measured outcome (1 of 6),** with each miss's reason in its header (next section).
- **Planted faults** (`run_faults.sh`, `faults.log`; each file restored byte for byte):

  | fault | caught by |
  |---|---|
  | Goo-zooka's effect counts whatever its turns left | the liveness test |
  | the Active's own candidates charged too | the clock test |
  | each clock given the other side's flag | the wiring test (kro3) |
  | the 200-deal test's "C2 off" player with C2 on | that test |

- **The full suite:**
  - on this branch's engine at `7c882b5`: **2,031 passed, 0 failed** (`suite.log`). That is 2,022 (`../kn_build_2026-09-30/`) plus kr's 9, with no existing expected value edited.
  - on `d363ba8`'s `engine/` (the official engine's source) with `7c882b5`'s `players/` and the new test file: **2,011 passed, 0 failed** (`suite_d363ba8.log`). That is build B's 1,991 plus kn's 11 and kr's 9; the branch's extra 20 are the unmerged repair drafts' tests.
  - The repository's `decks/` was linked beside that copy, since several km and kt tests read `../decks/research/`. A first run without it failed 9 tests on exactly that missing folder, and nothing else.

## The judged turns: why C2 plays on one, not six

From the probe (`probe/`: a scratch program printing, at each of the deck's decisions where Goo-zooka is offered, kr's and km's root scores and the opponent's clock with C2 off and on; `probe_output.txt`):

| turn | TIMING.md read | kr3 | why |
|---|---|---|---|
| 11602 t4 | play | **plays** | After Sabrina, Butterfree (ready) waits behind Grovyle with 0 Energy. C2 charges it 1, and 2 with Goo-zooka (live next turn): their lead goes from 1 to 2, worth about 100. |
| 9102 t4 | play | holds | Hydreigon (1 short) behind Deino (0 Energy, cost 1). The clock already charges the retreat's attachment, so Hydreigon's turn is two turns away, after Goo-zooka expires. In the game Hydreigon's own Ability (Roar in Unison) gave it its Energy, which km's clock doesn't count. C2 also makes Deino (20 damage, 1 short) the clock's threat. |
| 12600 t4 | play | holds | Chien-Pao ex retreats for free (Inflatable Boat on a [W] Pokémon) and can attack now, so it is their threat. Goo-zooka's real value there was the damaged ex left in front (a knockout), which C2 doesn't price. |
| 9600 t3 | play | holds | Their Active Deino can attack now, so it is their threat. Bombirdier, which they retreated into, was still in their hand. |
| 8101 t3 | play | holds | After Sabrina, Torchic in front (1 short) attacks as soon as the benched Castform could. So whether Castform comes in or not, the clock's total is the same. |
| 7102 t2 | play | holds | Their Active Igglybuff can attack now, so it is their threat. Their real attacker, Espeon, comes by evolution, and the clock doesn't scan the opponent's evolutions (hidden cards). |
| 7100 t9, 8103 t4, 14600 t4 | hold | holds | as the diagnosis judged |
| 13600 t6 | (not read) | holds | — |

The common cause: km's clock picks the threat with the fewest missing Energy first. An opponent's Active that can attack at all, however weakly, is their threat. C2 charges only benched threats, so it acts only when the opponent's Active can't attack and a ready attacker waits behind it.

## The smoke (`smoke/`)

- **How.** kn's smoke as it was: its scratch decks, its program (`kn_smoke.rs`, used unchanged) and its seeds. There are three arms for the deck's pilot (km3, kr3, kro3), with km3 the opponent's in all of them.
- **The build:** `d363ba8`'s `engine/` with `7c882b5`'s `players/` (`scratch_engine_diff.txt`: only those three files and the example differ).
- kn3's columns are kn's smoke's.
- **The km3 arm equals kn's smoke's km3 games in all 2,400 deals,** fingerprint for fingerprint.

| deck (card) | opponent | km3 plays / chances | kr3 | kro3 | kn3 | kr3 games that differ | kro3 | kn3 |
|---|---|---|---|---|---|---|---|---|
| goo (Goo-zooka) | fire_balloon | 0 / 853 | 4 / 830 | 4 / 850 | 206 / 253 | 76 / 200 | 16 | 163 |
| goo | psychic | 3 / 846 | 18 / 832 | 21 / 823 | 228 / 255 | 129 | 80 | 178 |
| goo | water_boat | 0 / 988 | 19 / 908 | 22 / 933 | 248 / 284 | 141 | 112 | 173 |
| grass_goo (Goo-zooka) | fire_balloon | 72 / 636 | 75 / 637 | 75 / 637 | 199 / 241 | 31 | 28 | 155 |
| grass_goo | psychic | 123 / 675 | 135 / 669 | 135 / 667 | 229 / 251 | 62 | 56 | 155 |
| grass_goo | water_boat | 165 / 683 | 178 / 685 | 177 / 685 | 249 / 278 | 75 | 72 | 157 |
| plaza (Plaza) | fire_balloon | 166 / 173 | 163 / 197 | 166 / 173 | 166 / 173 | 78 | 14 | 0 |
| plaza | psychic | 176 / 176 | 176 / 221 | 175 / 182 | 116 / 397 | 88 | 34 | 124 |
| plaza | water_boat | 169 / 176 | 170 / 197 | 170 / 178 | 169 / 176 | 106 | 76 | 0 |
| psychic (Cyrus; control) | fire_balloon | 17 / 21 | 17 / 22 | 17 / 22 | 17 / 21 | 78 | 12 | 0 |
| psychic | psychic | 38 / 58 | 34 / 52 | 38 / 56 | 38 / 58 | 108 | 42 | 2 |
| psychic | water_boat | 83 / 92 | 72 / 79 | 85 / 94 | 83 / 92 | 111 | 63 | 0 |

**Per deck (600 games a code):**

| deck | km3 | kr3 | kro3 | kn3 | games that differ: kr3 / kro3 / kn3 |
|---|---|---|---|---|---|
| goo | 3 / 2,687 (0.1%) | 41 / 2,570 (1.6%) | 47 / 2,606 (1.8%) | 682 / 792 (86.1%) | 346 / 208 / 514 |
| grass_goo | 360 / 1,994 (18.1%) | 388 / 1,991 (19.5%) | 387 / 1,989 (19.5%) | 677 / 770 (87.9%) | 168 / 156 / 467 |
| plaza | 511 / 525 (97.3%) | 509 / 615 (82.8%) | 511 / 533 (95.9%) | 451 / 746 (60.5%) | 272 / 124 / 124 |
| psychic (control) | — | — | — | — | **297 / 117 / 2** |

**The timing:**
- median turn of the first Goo-zooka play: 7 for km3, kr3 and kro3 in the goo deck, and 8 in the Grass Knot deck. kn3's was 2 in both;
- plays on the game's first chance turn (goo deck): 2 for kr3 against kn3's 492;
- in the Grass Knot deck, plays just before a Grass Knot that turn: km3 359 of 360, kr3 364 of 388, kro3 363 of 387, kn3 120 of 677.

**Paired deals,** won with km3 only / won with the code only:

| deck | opponent | kr3 | kro3 | kn3 |
|---|---|---|---|---|
| goo | fire_balloon | 1 / 5 | 0 / 1 | 3 / 0 |
| goo | psychic | 6 / 13 | 4 / 7 | 1 / 4 |
| goo | water_boat | 28 / 15 | 10 / 8 | 8 / 4 |
| grass_goo | fire_balloon | 2 / 4 | 2 / 4 | 1 / 1 |
| grass_goo | psychic | 4 / 4 | 3 / 4 | 23 / 3 |
| grass_goo | water_boat | 5 / 7 | 5 / 6 | 17 / 3 |
| plaza | fire_balloon | 0 / 0 | 1 / 0 | 0 / 0 |
| plaza | psychic | 4 / 8 | 1 / 2 | 3 / 5 |
| plaza | water_boat | 7 / 3 | 6 / 2 | 0 / 0 |
| psychic | fire_balloon | 1 / 2 | 0 / 0 | 0 / 0 |
| psychic | psychic | 6 / 10 | 1 / 5 | 0 / 0 |
| psychic | water_boat | 12 / 8 | 7 / 3 | 0 / 0 |

These are scratch decks with 200 deals a row; they describe these games and are not a strength result.

## The expected footprint and the carrier

- **Footprint: large, on every list, not only lists with N1's cards.**
  - The smoke's control deck carries no Goo-zooka, Plaza or Trap Territory. It differs from km3 in 297 of 600 games under kr3 (49.5%), and in 117 of 600 under kro3 (19.5%).
  - The Goo-zooka and Plaza decks differ in 28% to 58% under kr3.
  - The reach comes from the clock's threat changing wherever a side's threat is benched behind an Active short of its retreat. That is common in early turns, on both sides, and the bot's own half is most of it.
  - **On the 45 cells, expect a footprint of the same order (tens of percent of games for kr3, perhaps a fifth for kro3), well above kn's.** It is not measured here (no table games). It has to be read by a full footprint route like kt's, and kro3 is the code that attributes the halves.
- **Carrier.**
  - For Goo-zooka: the Whimsicott ex Ariados list (`../b2e_card_check_2026-09-26/decks/h-whimsicott.txt`), and Dustin's decks 14 and 15.
  - The smoke's Grass Knot deck shows the carrier's pattern kept: Goo-zooka still before Grass Knot, a little more often (388 plays against 360).
  - In the plain Goo-zooka deck, and on the diagnosis's turns from decks 14 and 15, it plays rarely (1.6% of chances; 1 of 6 judged turns), for the reasons above.
  - So a carrier read would mostly measure C2's general clock change, not Goo-zooka.

## For the laptop, and the open points

- **Build:** `git archive d363ba8 engine` with `7c882b5`'s `engine/src/players/` (and `engine/tests/kr_judged_turns_test.rs` for the suite); `smoke/run_smoke.sh` does exactly this. Programs built there have their own sha256; what carries is the commit and the tests.
- **Two findings for whoever writes a registration:**
  1. **The judged-turns criterion (play on the 6) is not met:** 1 of 6. The misses come from km's clock (the readiest Active is the threat; Ability Energy and the opponent's evolutions are unseen; a stranded damaged Active is unpriced), not from C2's arithmetic. A rule that met it would have to change how the clock picks the threat, which is outside C2 as stated.
  2. **The footprint is large and mostly the bot's own half** (control deck 297 against 117 of 600). kro is the narrower variant if only the opponent's half is wanted.
- These are findings, not a verdict; registration and any choice between kr, kro or neither is the laptop's and Dustin's.

## Limits

- The smoke's decks exist only for this build; their wins describe these games only.
- The judged turns are 10 positions from two of Dustin's decks.
- The probe is a scratch program in a copy of `7c882b5`'s engine (`probe/kr_probe.rs`, `probe/probe_helpers.rs`, sha256 in `probe/kr_probe.sha256`); it is not in the repository's engine.
- C2 assumes one attachment a turn and no switching card in the hand, as the clock does. An Active that can't retreat at all is left as today.

## Files

- `README.md`: this note.
- `suite.log`, `suite_d363ba8.log`: the full suites.
- `run_faults.sh`, `faults.log`: the planted faults.
- `probe/`: `kr_probe.rs`, `probe_helpers.rs`, `kr_probe.sha256`, `probe_output.txt`.
- `smoke/`: `run_smoke.sh`, `smoke.py`, `smoke_output.txt`, `games.jsonl`, `kn_smoke.sha256`, `scratch_engine_diff.txt`. The decks and `kn_smoke.rs` are kn's, in `../kn_build_2026-09-30/smoke/`.
