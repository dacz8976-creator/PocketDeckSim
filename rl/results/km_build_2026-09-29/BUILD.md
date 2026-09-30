Decision this informs: none on its own. This is the cloud's one round for km (`../trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, registered Sept 29, main 55e5d95; its top block governs): the build, the tests, the counter tool's extension to all 17 named cells with its check, the identity checks and the one code review. After this, the order is section 4.0's "Gate and order": Dustin's word on the build, then the laptop. No registered km game was played, M1's and M2's thresholds were not measured, and nothing here is a reading. Build commit **9c11b30**: the official engine's code (233bced's `engine/`) plus km in `engine/src/players/` only.

Seeds: identity on the table's deals (72,000,000 + pairing × 10,000 + i), the 17 new cells' (21,108,000,000 + pairing × 10,000 + i), B2e's (21,106,000,000 + …) and the second lists' own; even i puts the first-named deck in seat 0. The counter tool's traced test games use Claude diagnostic seeds 20,000,920,000 to 20,000,920,019 (kp3, Altaria v Lucario). The km unit tests' random games use 20,000,000,400 and up.

# km: the build (Sept 29)

## In plain words

- **km3 is kog3 with one change.** When it counts how many turns the opponent needs to win (and how many it needs itself), each hit now includes the damage a Stadium in play adds: Training Area's +10 for a Stage 1 attacker, Arena of Antiquity's +20 for an [F] attacker hitting an ex. Nothing else changed. With neither Stadium in play, km3 plays exactly as kog3.
- **Where things stand** (`STATUS.txt` has a line per step):
  1. **Build:** done, commit 9c11b30. It changes three files in `engine/src/players/` and nothing else in `engine/`. The programs for every game here are built from it.
  2. **Tests:** done. km's 11 tests at 9c11b30 pass, and the full suite passes: 1,986 passed, 0 failed.
     - The code review added a 12th test, test code only, in commit fb825d1.
     - A scan built from fb825d1 replays identity items 6 and 7 (160 games) byte for byte, so 9c11b30 stays the build.
  3. **Counter tool:** done. It now plays all 17 named cells, including the Rayquaza and Altaria/Greninja lists on their own seed base. It has a first-deal option and writes one row per game with each seat's counts. Its five tests and its identity check (8a) pass. Without the new options it prints exactly what the old tool printed, byte for byte.
  4. **Identity:** done. Every check passes, with every game equal: 86,220 games at the build plus the counter tool's 760. The table is below.
  5. **Code review:** done. It found no blocker. Its findings and what was done are below.
- **Three things the laptop should know before it builds this commit:**
  - **The program hashes will not match across machines.** A Rust build embeds its build paths and a hash of every source file, so the laptop's programs built from 9c11b30 will have different sha256s from the cloud's below. This already happened with kt: the same commit ec7e1a8 gave the cloud's scan e19703b1… and the laptop's 924751ba…, and both played every game identically. What does carry across is the commit, the counter tool's source sha256 (below), and the games. The laptop's own identity games at 9c11b30 equal to these (or to the same reference files) show the two builds are the same.
  - **Build 9c11b30, not the branch head.** Later commits on the branch add a test and notes only, but any source edit changes a Rust program's hash. So build the programs from 9c11b30's `engine/`, and the counter tool as an example in a copy of it, as done here.
  - **This build has the official engine's kt codes, not kt on kog.** km sits on 233bced's `engine/` exactly, so `engine/src/players/` was set back to 233bced's before km was added. The kt presets on kog from ec7e1a8 (kt's and kta's build) are therefore not in 9c11b30. kta keeps playing from ec7e1a8, and nothing here touches it.
- **One extra game, noted for completeness.** Before the identity runs I ran the scan once as `km3` on one deal (pairing 2, deal 0) to check that it accepts the code. That deal is part of item 7's smoke. Its result was not used.

## What was built (`git diff 233bced 9c11b30 -- engine/`)

- **The flag and preset** (`value_functions.rs`):
  - `EvalFeatures` gets `stadium_bonus_in_clock: bool` (`:388`). It is false in `OFF`, `KQ`, `KD` and `KPR`, the four presets that list every field.
  - `const KM = EvalFeatures { stadium_bonus_in_clock: true, ..EvalFeatures::KOG }` (`:478`).
  - The value function `public_clock_effect_km_value_function` sits beside kog's (`:318`). It is kog's call with `EvalFeatures::KM`.
- **The hook** (`value_functions.rs`):
  - `extract_features` gets one more argument, the flag (`:866`), and passes it to the clock. Both of `parametric_value_function_ex6`'s calls pass `features.stadium_bonus_in_clock`.
  - The damage-aware clock and its scan each get a `_stadium` version that takes the flag (`:1142`, `:1248`). The old functions, `calculate_turns_until_opponent_wins_projected` and `turns_until_opponent_wins_scan_projected`, are now thin wrappers that pass `false`. So no existing call site changed, and every test that calls them positionally runs the same code as before.
  - In the scan, after the threat is picked (`:1280-1291`): only when the flag is on **and** a Stadium is in play, it reads the threat's attacker's stage and types. Each hit on a victim is then the threat's damage plus `lasting_stadium_damage_bonus(stage, types, victim is ex)`. Otherwise a hit is the threat's damage, as before. The bonus goes into the two victim loops (the Active, then the safest remaining Pokémon); kq's own branch is untouched.
  - `lasting_stadium_damage_bonus` (`:1366`) returns 0 at once with no Stadium in play. Otherwise it adds the engine's own `stadiums::get_training_area_damage_bonus` (by stage) and the largest `stadiums::get_arena_of_antiquity_damage_bonus` over the attacker's types (against an ex). Its doc comment points at `hooks::modify_damage`, which it mirrors. No comment was added on the `core.rs` side, since that would touch a rules file.
  - `threat_attacker_stage_and_types` (`:1382`) returns the threat's Pokémon's stage and types. When the threat is an evolution form, it returns the evolved card's. Forms are only scanned for the bot's own threats, so no hidden zone of the opponent is read.
- **The code** (`players/mod.rs`):
  - `PlayerCode::KM { max_depth }` (`:200`).
  - The parser line, before `k<N>` (`:280`).
  - The `get_player` arm, with its own inner arm to km's value function (`:675`, `:690`). This avoids the or-pattern trap that section 4.1's wiring test guards against.
- **Floating point.** A hit was `max_damage`, and is now `max_damage + bonus as f64`. With a bonus of 0 the sum is the same number, so km equals kog bit for bit wherever neither Stadium applies. Identity 5 tests this in games.

## Tests (all pass; `suite.log`)

In `value_functions.rs`, `mod km_tests`, and in `players/mod.rs` and `public_pricing_player.rs`. Numbers were taken from `card.py`.

- **The pin** (`the_bonus_is_what_modify_damage_adds_for_an_active_to_active_attack`):
  - The cases: {no Stadium, Training Area, Arena} × attackers at Stage 0, 1 and 2 in [F], [R] and [P] (Machop line, Charmander line, Ralts line) × a target that is an ex (Mega Rayquaza ex) or not (Dratini). That is 54 cases.
  - In each, the new function equals `modify_damage` at base 50 with the Stadium minus without it.
  - Nine cases are nonzero: Training Area's three Stage 1s against both targets, and Arena's three [F] attackers against the ex.
- **The clock** (`a_stadium_bonus_that_saves_a_hit_shortens_the_clock_by_one_turn`):
  - Mega Lucario ex with [F][F] (Fighting Pulse 90) against a 190-HP Mega Lucario ex: 3 hits, and 2 with Training Area or with Arena. kog sees 3 either way.
  - Against 180 HP: 2 hits in every case.
  - Kirlia ([P], Stage 1, Smack 30) against Mega Rayquaza ex (180): 6 hits, 5 with Training Area, 6 with Arena.
- **Both sides** (`the_same_stadium_shortens_the_other_sides_clock_by_the_same_rule`): the same boards with the roles swapped give 3 → 2.
- **Benched threat** (`a_benched_stage_1_threat_gets_the_bonus`): Bonsly in front, and Mega Lucario ex with [F][F] benched. The threat is the benched Mega: 3 hits, 2 with Training Area.
- **Evolving threat** (`an_evolving_threat_is_priced_as_its_evolved_form_and_the_opponents_forms_are_not_scanned`):
  - Riolu with Mega Lucario ex in the bot's own hand. The evolved form's candidates read as Stage 1 [F], so they get Training Area +10 and Arena +20. Riolu's own read as Stage 0, so they get Arena only.
  - Read as the opponent's threat (board only), no form is scanned.
  - This test is at the unit level (the candidates and the attacker lookup). Through the whole clock, this board prices Riolu, not the form: each evolution step counts as one missing Energy, so Riolu's own attack is always at least one Energy closer than the Mega's Fighting Pulse. So the registered Riolu case can't be shown through the clock. The code review pointed this out.
- **Evolving threat through the whole clock** (`an_evolving_threat_that_the_clock_picks_is_priced_as_its_evolved_form`; added after the review, commit fb825d1, test code only):
  - The board: Cubone (Basic [F], only Growl, no damage) with [F] attached, Marowak (Stage 1 [F], Bone Beatdown 40) in the bot's hand, against Mega Rayquaza ex (180).
  - The clock picks the Marowak form: 1 turn for the evolution step, then 40 a hit, so 6 turns.
  - With Training Area it is 5. That +10 comes from the form's Stage 1; Cubone, at Stage 0, would get none.
  - With Arena it is 4, and with Hiking Trail 6. kog sees 6 in every case.
  - Board only (the opponent's view) there is no form and no damaging attack, so the clock is 30 either way.
- **Nothing to read** (`with_nothing_to_read_kms_clock_is_kogs`): with no Stadium, Hiking Trail or Fragrant Forest, km's clock equals kog's on the boards above.
- **Flag-off identity, bitwise** (`km_is_kog_plus_n2_and_nothing_else`): `KM` with its flag cleared equals `KOG`, and every other preset has the flag off.
- **Played states** (`on_played_states_km_is_kog_wherever_no_damage_stadium_is_in_play`):
  - The positions: every position of 12 random-move games (Altaria v Lucario, Lucario v Blaziken, Altaria v Suicune, Lucario v Altaria, 3 each; seeds 20,000,000,400-402), from each player's own view.
  - km's value equals kog's, bit for bit, in setup and wherever neither Training Area nor Arena is in play.
  - Where one is in play, km differs from kog at some position, so the test also sees the switch act.
- **Wiring** (`km3_from_get_player_plays_arena_where_n2_saves_a_hit_and_otherwise_plays_as_kog3`, `public_pricing_player.rs`):
  - The board: a Machoke that can't attack faces Mega Lucario ex with [F][F]. Arena of Antiquity is in the bot's hand, and no Zone Energy is available.
  - km3 from `get_player` plays Arena, and kog3 doesn't.
  - With Hiking Trail in hand instead, the two decide the same.
- **Parser** (`km_parses_before_k_and_nothing_else_moves`): `km3` and `KM5` parse; `km`, `kmx`, `km3x` and `km1a` are rejected; the other codes parse as before.
- **Diagnostic** (open question 13; `diagnostic_the_card_term_rewards_x_speed_before_copycat_and_a_play_under_hiking_trail_by_one`):
  - X Speed then Copycat, against Copycat alone, with no Trail: the card term differs by exactly +1.
  - With Hiking Trail in play and a hand under 3, playing any card is +1.
- **Full suite:** at 9c11b30, 1,986 passed, 0 failed (`suite.log`). That is 233bced's 1,975 plus km's 11. No existing test's expected value was edited. At fb825d1, with the review's added test: 1,987 passed, 0 failed (`suite_fb825d1.log`).

## The counter tool (step 3; identity 8a)

`../tool_turn_effect_census_2026-09-25/tool_census.rs`, extended. It is built as an example in a scratch copy of 9c11b30's `engine/` (`git archive`), so the build's diff stays `players/` only.

| | sha256 |
|---|---|
| **source (this round, after the review)** | `05d7ba4183ce9e3098036de9acb5181ea71f7077ef9b3798ad4e5d165dc22365` |
| **program, cloud build** (in a copy of 9c11b30's `engine/`) | `883426520104f9f834d88c0e3344e9568b6247a1558f44d90ecaedf77d7039e4` |
| first source, before the review (history; its checks passed too) | `b3eb7684cecd5dcbd4e24f3f532d701a145ca4fcfebe9624c4f1835cd2b2eecc` |
| first program (history) | `69d98fcb23cb5a5b23724eceb97cc2ff74b049975c4a126e4e2b7e164a2788e4` |
| old source (816fd9c's, the one main has and the laptop's kt counters used) | `a2510339e5867b171f22832dc1f31072494fe4667b862b36c92c263c39f01759` |
| old program, cloud build, for test 1 | `8d4f103cc54e415d1667e7f0e1dbb8a9f1f24eb4672b5ae79690d0576e689a32` |

**What it adds** (the file's header has the details):
- **`--cells km17`:** the 17 named cells.
  - The 13 table cells (pairings 0-6, 8, 13 and 18-21) are on 72,000,000 with the `decks/research` lists.
  - `new_decks.tsv` pairings 8, 9, 16 and 17 are on 21,108,000,000 with that file's lists: Rayquaza v Lucario, Rayquaza v Altaria, Altaria/Greninja v Lucario and Altaria/Greninja v Altaria.
  - Each cell's deck names are checked against the registration's list.
- **`--pairs`, `--root`, `--seed-base`:** read a pairings file as legality_scan does.
- **`--pairings`:** keeps the listed cells in their own order. Pairing 8 exists in both the table and `new_decks.tsv`, so `table:8` and `new_decks.tsv:8` pick one; a bare `8` keeps both.
- **`--first-deal`:** deal i starts at the given number.
- **`--rows-out`:** one row per game. Each row has the cell (source, pairing, decks a and b with their files), i, seed, first seat, each seat's deck and bot, and the move fingerprint (legality_scan's `moves`). Per seat and card it also has the turns offered, the turns played, and the targets. The cards counted:
  - the old ones (Tools, Field Blower, Stiffen);
  - every Stadium, X Speed, Team Rocket's Boss and Copycat;
  - Field Blower's targets, including the Stadium;
  - each X Speed play, with whether Hiking Trail was in play and whether the seat retreated later that turn.
- **`--no-counts`:** rows without any count, and no printed table. Used for identity checks on gating deals.
- **`--trace-out`:** every decision, with the watched cards offered and the move chosen.
- **The counting rule is the old one:** a turn is offered when the card is among the owner's legal moves at some decision of that turn, and played when it is played that turn.
- **Refused** (legality_scan refuses the same kinds of thing):
  - `--seed-base` with `--cells km17`, whose seed bases are the registration's. So a run meant as a diagnostic can't land on gating deals;
  - `--cells` with `--pairs`, `--decks` with `--pairs`, and `--root` in table mode;
  - `--trace-out` with `--no-counts`, since a trace carries the counts;
  - deals past a pairing's 10,000-seed block;
  - a pairings file with a pairing listed twice or a short row.
  - These came from the code review.
- **Usage for the threshold sample** (the laptop's step; not run here):
  - The sample is deals 200-299 of the 14 gating cells: M1's nine (table 2, 8, 13, 18, 19, 20 and 21; `new_decks.tsv` 8 and 16) and M2's five (table 0, 1, 3 and 4; `new_decks.tsv` 9).
  - So: `--cells km17 --pairings table:0,table:1,table:2,table:3,table:4,table:8,table:13,table:18,table:19,table:20,table:21,new_decks.tsv:8,new_decks.tsv:9,new_decks.tsv:16 --first-deal 200 --games 100 --bot kog3 --rows-out <file>`, and the same with `km3`. That is 1,400 games for each pilot.
  - A bare `--cells km17` would play all 17 cells.
  - Each row carries what the registration's deal-by-deal check of a measuring run reads: the move fingerprint (`moves`), both decks (`a`, `b`, `a_file`, `b_file`), `seed`, `first_seat` and `seat_decks`, keyed by `source`, `pairing` and `i`. (`tool_check.py rows` checks deals from 0 only. It was written for identity 8a, not for the sample.)

**Tests and identity 8a** (`check_tool.sh`, `tool_check.py`, `tool_check.txt`). All pass with the revised program, the one in bold above. The first program passed tests 1 to 4 and 8a as well, before the review.
1. **The old output, exactly.**
   - kp3 on the table's first 20 deals of the 28 pairings (560 games), with the same default arguments for the old and new tools.
   - stdout, stderr and `--games-out` are byte-identical. stdout sha256 is `a82786bb…`, games-out `057ae92e…`.
   - kp3's counts on these deals were already public (`kp3_census.txt`, 100 deals).
2. **The same games through the new options.** With `--seed-base 72000000` and `--rows-out`:
   - games-out is byte-identical;
   - the card table is the same;
   - every row's fingerprint, seed and seats equal games-out's.
3. **Traced games against a count from the trace.**
   - kp3 on Altaria v Lucario, on diagnostic seeds 20,000,920,000-019 (the lists that carry Training Area and Arena).
   - For each game, seat and card, the rows' offered and played turns for Arena of Antiquity and Training Area equal a recount from the move trace: 80 of 80.
   - The trace lists every Trainer the owner could play at each decision, watched or not. So the recount decides for itself which moves are the card.
   - Arena of Antiquity is played in 7 games and Training Area in 9.
   - `tool_check.txt` prints one game per card line by line, to count by hand:
     - Training Area, i 1 seat 1: offered on turns 2, 4, 6 and 8, played on 8, so (4, 1);
     - Arena, i 4 seat 1: offered on turns 2, 8, 10 and 12, played on 12, so (4, 1).
   - The first program's first run of this test failed on the check script's own pattern, not the tool. The trace prints a Trainer as `B2 153 Training Area`, and the script looked for `name: "…"`. It was fixed and rerun, and every run is recorded.
4. **`--first-deal`.** kog3 with `--first-deal 20 --games 20` on the 17 cells gives identity 8a's rows for deals 20-39 exactly (340 rows, no counts).
5. **Refusals.** These combinations each exit with an error before any game, with no games file written:
   - `--seed-base` with `--cells km17`;
   - `--cells` with `--pairs`;
   - `--decks` with `--pairs`;
   - `--root` in table mode;
   - `--trace-out` with `--no-counts`;
   - deals past a pairing's 10,000 seeds.
- **Identity 8a:**
  - The tool's kog3 on i < 40 of all 17 cells: **680 of 680** deals equal `table_kog3.jsonl` (13 cells) and `new17_kog3.jsonl` (4 cells). The check covers the move fingerprint, both decks (names, plus files where the reference has them), seed and seats.
  - Its km3 on pairings 0 and 2, i < 40: **80 of 80** equal item 7's smoke in the same way.
  - The check asserts the number of cells (17, and 2), so a dropped cell would fail.
  - No count was written or read for these games (`--no-counts`).

## The code review (section 4.0: the cloud's one review)

**Who and how.** An independent agent in this session did the review, read-only: git and file reads only, no builds and no games. It covered 9c11b30's diff against the registration's section 2 (N2) and section 4.1, and the counter tool with its checks against step 3 and identity 8a.

**What it checked in the code, with no blocker found:**
- km equals kog bit for bit when neither Stadium applies. The bonus is looked up only with the flag on and a Stadium in play, and `+ 0.0` leaves the number unchanged.
- The call sites are right: `extract_features` has its only two callers, and the wrappers pass `false`.
- The bonus mirrors `modify_damage` (`hooks/core.rs:1999-2009`): the same functions, the most over dual types, and the target's `is_ex()`.
- The side and the attacker are right, including an evolution form.
- No hidden information is read. Forms are scanned only for the bot's own threats.
- The parser order is right.
- With no new options, the counter tool behaves exactly as before. Its seats, seeds and deck files match legality_scan, and its km17 cells match the registration.

The one place km's bonus differs from `modify_damage` is also noted: every hit is treated as landing on the Active. This is the registration's stated simplification (section 2, "Intended simplifications").

**Its findings, and what was done:**

| finding | severity | done |
|---|---|---|
| The Riolu test never runs the evolution-form branch through the clock (Riolu always has one fewer missing Energy than the form) | note | Added the whole-clock Cubone/Marowak test (above; fb825d1, test code only). The registered Riolu case itself can't be shown through the clock, as the Riolu bullet above says. |
| A doc comment in `players/mod.rs`'s tests landed on the km parser test | note | Moved back (fb825d1) |
| The tool silently ignored `--seed-base` under `--cells km17` (a "diagnostic" could play gating deals and write their counts), and `--decks` under `--pairs` | should-fix | Both refused now |
| BUILD.md's sample command played all 17 cells, not the 14 gating cells | should-fix | Corrected (above) |
| `tool_check.py rows` took its cells from the rows, so a dropped cell would pass | note | It now asserts the count (17, or 2) |
| Test 3's recount leaned on the tool's own choice of which moves are the card | note | The trace now lists every Trainer the owner could play, so the recount is independent |
| No guard on deals past 10,000; duplicate or short rows in a pairings file; `--trace-out` with `--no-counts`; a misleading error for `--cells` with `--pairs` | note | All refused now |
| `tool_check.py` can't check a measuring run's kog3 arm deal by deal (it starts at deal 0 and refuses rows with counts) | note | Stated above. The laptop's reading check needs its own script. |
| Registration 4.0 step 4 has the laptop check the programs' sha256 against BUILD.md, which can't match across machines | process | For the laptop and Dustin: see "In plain words". The source sha256s and the commit do carry across, and the laptop's identity games show the builds agree. |

The tool was rebuilt after these changes. Every tool test and identity 8a were rerun with the revised program; the results are below. The first program's results stay in `STATUS.txt` and `tool_check.txt` as history.

## Identity (section 4.1; `run_km.sh`, `identity.py`, `identity/identity_check.txt`)

All runs use the cloud's programs built from 9c11b30 (legality_scan sha256 `e8f72631f812871f529dd8374610032acea03d1ddfe0d106ff0cd0725ccefdd5`, deckgym `fcbcdba4968b38f806904e602b3c2999271297390fb5e03a0c88ec1cc89c2e3b`), 4 threads. A game is equal when its moves, choices, openings, winner, points, seed and seats all are (and the deck files, where the reference has them). Every run's scan page must also be free of rule findings. The run times in `STATUS.txt` are not a timing measure: the counter tool's build and checks ran on the same machine at the same time. The timing gate is the laptop's.

**Every check passes, with every game equal and every scan page free of rule findings.** No difference was found, so nothing stopped. That is 86,220 games through the scan, or 86,980 with identity 8a's 760 (the registration's row 1 count), from 18:38 to 00:07 UTC.

| item | run at 9c11b30 | reference | result |
|---|---|---|---|
| 1 | k3, all 500 table deals | `../engine_switch_2026-09-28/pin_identity_k3_500.jsonl` (the pin's frozen table) | 14,000 of 14,000 |
| 1 | kp3, all 500 table deals | `../engine_switch_2026-09-28/pin_identity_kp3_500.jsonl` | 14,000 of 14,000 |
| 1 | kog3, all 500 table deals | `../koh_2026-09-28/bd2907f_kog3_500.jsonl`, and `../kog_composition_2026-09-27/table_kog3.jsonl` | 14,000 of 14,000 against each |
| 1 | kog3, the 17 new cells, 500 deals | `../kog_composition_2026-09-27/new17_kog3.jsonl` | 8,500 of 8,500 |
| 2 | kq3, all 500 table deals | `../kt_2026-09-26/identity/official_kq3_500.jsonl` | 14,000 of 14,000 |
| 2 | kd3, 40 table deals | `../rules09_fixes_2026-09-26/af8489f_kd3_40.jsonl` | 1,120 of 1,120 |
| 2 | kpr3, 40 table deals | `../rules09_fixes_2026-09-26/af8489f_kpr3_40.jsonl` | 1,120 of 1,120 |
| 3 | kog3, B2e's 96 pairings, i < 40 | `../koh_2026-09-28/reading/b2e_kog3.jsonl` | 3,840 of 3,840 |
| 3 | kog3, Scizor's 8 pairings, i < 40 | `../koh_2026-09-28/laptop_runs/scizor_kog3.jsonl` | 320 of 320 |
| 3 | kog3, second list v-lucario_2, i < 40 | `../koh_2026-09-28/laptop_runs/var_v-lucario_2_kog3.jsonl` | 280 of 280 |
| 3 | kog3, second list v-suicune_2, i < 40 | `…/var_v-suicune_2_kog3.jsonl` | 280 of 280 |
| 3 | kog3, second list v-weezing_2, i < 40 | `…/var_v-weezing_2_kog3.jsonl` | 280 of 280 |
| 3 | kog3, second list l-charizardy, i < 40 | `…/var_l-charizardy_kog3.jsonl` | 320 of 320 |
| 4 | `KM` with its flag off equals `KOG` | a test (`km_is_kog_plus_n2_and_nothing_else`) | passes |
| 5 | km3 on the 15 table cells with neither the panel Altaria nor Lucario list, 500 deals | `table_kog3.jsonl` | 7,500 of 7,500 |
| 5 | km3 on the 13 new cells with neither, 500 deals | `new17_kog3.jsonl` | 6,500 of 6,500 |
| 6 | kog3, pairings 0 and 2, 40 deals | `table_kog3.jsonl` | 80 of 80 |
| 7 | km3 smoke, pairings 0 and 2, 40 deals | none: a clean, complete run only; its games were not read | 80 games, clean |
| 8 | the diff of `engine/` from 233bced | `engine/src/players/` only | yes |
| 8a | the counter tool (above) | `table_kog3`, `new17_kog3`, item 7's smoke | 680 of 680; 80 of 80 |

- **What these license** (section 4.1, "Only an identity that covers those files licenses that reuse"):
  - The stored kog3 files the reading pairs km3 against, `table_kog3.jsonl` and `new17_kog3.jsonl`, are kog3's games at this build.
  - So are the coverage baselines at i < 40: B2e's `reading/b2e_kog3.jsonl` (on this branch; not on main), and on main `laptop_runs/scizor_kog3.jsonl` and the four `var_*_kog3.jsonl`.
  - These are the baseline files, named before the first km game as section 5 asks.
- **The table's 28 cells without either damage Stadium:** there km3 played every game exactly as kog3 did (item 5). Section 7 predicts the same.
- **Item 3 does not re-play every deal:** only i < 40 of each pairing, as registered. The rest of each baseline file is licensed by the rule, not by a game here.


## Files

- `STATUS.txt`: one line per step, with the sha256s.
- `suite.log`, `suite_fb825d1.log`: the full suite at 9c11b30 and at fb825d1.
- `run_km.sh`, `identity.py`, `identity/`: the identity runs (each `9c11b30_*.jsonl` with its scan page `.txt`) and `identity_check.txt`.
- `check_tool.sh`, `tool_check.py`, `tool_check.txt`: the counter tool's tests and identity 8a.
- `identity/9c11b30_tool_kog3_km17_40.jsonl`, `identity/9c11b30_tool_km3_p02_40.jsonl`: 8a's rows (no counts).
- `tool_test3_trace_rows.jsonl`, `tool_test3_trace.tsv`: test 3's diagnostic games.
