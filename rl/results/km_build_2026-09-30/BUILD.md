Decision this informs: none on its own. This is the cloud's round for km re-issued on kta (`../trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, "Amendment 1 (Sept 30 …): km re-issued on kta", part (c), which scopes it; main 3aed736; Dustin's choice B, Sept 30). It covers the build, its tests, the identity checks with the counter tool's 8a, and the one code review. After this, the order is the amendment's (g): the laptop's identity games at B and its threshold preparation, then Dustin's separate go-ahead for the registered tables. No registered km game or table was played, no threshold was measured, and nothing here is a reading. **Build B = commit 1f6319e** (`1f6319e4b72e34a42d2d3c3ffc7cc9a09fdfa6f3`): ec7e1a8's `engine/` plus km's N2 in kta's clock, in `engine/src/players/` only. 9c11b30 (`../km_build_2026-09-29/`) stays implementation evidence only.

Seeds: identity on the table's deals (72,000,000 + pairing × 10,000 + i), the 17 new cells' and Scizor's (21,108,000,000 + …), B2e's and `l-charizardy`'s (21,106,000,000 + …) and the other second lists' (72,000,000 + …); even i puts the first-named deck in seat 0. The counter tool's traced test games use Claude diagnostic seeds 20,000,920,000 to 20,000,920,019 (kp3), as at 9c11b30. The km unit tests' random games use 20,000,000,400 and up.

# km on kta: build B (Sept 30)

## In plain words

- **km3 is now kta3 with one change.** kta3 is the adopted working pilot: kog plus kt's switch 1, the defender's damage cuts in the threat clock. km3 adds N2: each hit in that clock also includes the damage a Stadium in play adds, Training Area's +10 for a Stage 1 attacker and Arena of Antiquity's +20 for an [F] attacker hitting an ex. With neither Stadium in play, km3 plays exactly as kta3.
- **Where things stand** (`STATUS.txt` has a line per step):
  1. **Build:** done, B = 1f6319e.
  2. **Tests:** done. km's 14 tests pass, and the full suite passes: 1,991 passed, 0 failed.
  3. **Counter tool:** done, 8a at B. It is built from the unchanged source in a copy of B's `engine/`. Its five tests pass, and test 1's and test 3's outputs are byte-identical to 9c11b30's. 8a: kta3 680 of 680 and km3 80 of 80.
  4. **Identity:** done. Every check passes, with every game equal: 114,080 games through the scan plus the counter tool's 760, the amendment's 114,840. The table is below.
  5. **Code review:** done. No blocker and no should-fix, five notes (below).
- **For the laptop** (the amendment's (e) governs):
  - Build the programs from B's `engine/` by `git archive 1f6319e engine`, not from the branch head, and the counter tool (source `05d7ba41…`) as an example in a copy of it.
  - Programs built on the laptop will have their own sha256. What carries across machines is the commit, the tool's source and the games. The laptop's check is **agreement on the tested games**: its programs play the tested games as the committed references and this round's outputs have them. It is not a claim that the programs are identical, or about games not tested.
  - The km3 smoke at B, the laptop's km3 reference ((e) item 3), is `identity/1f6319e_km3_smoke_40.jsonl`, with the sha256 in `STATUS.txt`.
  - Test 1's and test 3's committed outputs are `tool_test1_stdout.txt`, `tool_test1_games.jsonl`, `tool_test3_trace_rows.jsonl` and `tool_test3_trace.tsv`, with their sha256 in `STATUS.txt`.

## What was built (`git diff ec7e1a8 1f6319e -- engine/ ':!engine/UPSTREAM.md'`)

- **The base.** `engine/src/players/` was set to ec7e1a8's first, as 9c11b30 set it to 233bced's. Every other file of `engine/` is ec7e1a8's, except the notes file `engine/UPSTREAM.md`, which no build reads (the amendment's (c) item 2). So kt, kta, ktb and ktc in B are ec7e1a8's kog-based presets, unchanged.
- **The flag, preset and code** (`value_functions.rs`, `players/mod.rs`):
  - `EvalFeatures` gets `stadium_bonus_in_clock`, false in `OFF`, `KQ`, `KD` and `KPR` (the presets that list every field) and so in every preset but `KM`.
  - `KM = EvalFeatures { stadium_bonus_in_clock: true, ..EvalFeatures::KTA }`.
  - km's value function is kta's call with `KM`.
  - `PlayerCode::KM`, its parser line before `k<N>`, and its own inner `get_player` arm are as at 9c11b30. The doc lines now say kta.
- **N2 in kta's clock.** This is the part the amendment leaves to the cloud, stated here.
  - **How the flag gets there.** ec7e1a8's `kt_clock` becomes `kt_clock_stadium`, with the flag as an 8th argument. `kt_clocks` passes `features.stadium_bonus_in_clock` to both of its calls: the bot's own survival clock and its clock on the opponent. `kt_clock` stays as a test-only wrapper (`#[cfg(test)]`) that passes `false`, so kt's tests call it as before and the release build has no unused function. Where the amendment points at `kt_clock` (`value_functions.rs:1685-1762` at ec7e1a8), B's code is `kt_clock_stadium`.
  - **Where the bonus goes.** After the threat is picked (still on unbonused damage), and only with the flag on and a Stadium in play, the threat's attacker's stage and types are read by `threat_attacker_stage_and_types`. That is the evolution form for the bot's own evolving threat, and board only for the opponent's. The threat's damage against each victim is then that damage plus `lasting_stadium_damage_bonus` for the victim's ex-ness. Both helpers are 9c11b30's, unchanged, so the 54-case pin carries over.
  - **The order, as `modify_damage` applies it** (`hooks/core.rs`): the Stadium bonus is added into the pre-Weakness damage, and the defender's reductions come off after Weakness, floored at 0. So in kta's clock the first hit is `(damage + bonus) − (permanent + temporary)` and every later hit `(damage + bonus) − permanent`, each floored at 0. kta's clock has no Weakness step, in kta or in km.
  - **With the flag off, or no damage Stadium in play,** the damage is the threat's own, and the arithmetic, types and casts are ec7e1a8's.
- **Not in B:** 9c11b30's change to kp's scan. km on kta doesn't use kp's clock, so B leaves the scan and `extract_features` as ec7e1a8 has them.

## Tests (all pass; `suite.log`)

All of section 4.1's tests are re-based to kta by the amendment's (c) items 3.1 and 3.2. They are in `value_functions.rs` (`mod km_tests`), `players/mod.rs` and `public_pricing_player.rs`, with numbers from `card.py`.

- **3.1, on kta's clock** (`clock()` is `kt_clock_stadium` with switch 1 on, as `kt_clocks` runs it):
  - **The pin**, unchanged: the function against `modify_damage`, 54 cases.
  - **The clock:** the 190-HP board (3 hits, 2 with Training Area or Arena; kta sees 3), the 180-HP board (2 either way), and the Kirlia board (6; 5 with Training Area; 6 with Arena). The boards carry no cut, so kta's clock gives kog's numbers, and km gives 9c11b30's.
  - **Both sides**, and **the benched threat**.
  - **The Riolu test**, kept as registered and read at the unit level: the candidates and the attacker lookup. Through the whole clock this board prices Riolu, not the form (the amendment's (f)).
  - **The full-clock Cubone/Marowak test:** 6 turns under kta; under km 5 with Training Area, 4 with Arena, 6 with Hiking Trail; 30 either way board only.
  - **Nothing to read:** km's clock equals kta's with no Stadium, Hiking Trail or Fragrant Forest.
  - **Played states:** km's value equals kta's bit for bit in setup and wherever neither damage Stadium is in play, and differs somewhere where one is (12 random-move games, seeds 20,000,000,400-402).
  - **The card-arithmetic diagnostic.**
  - **New: the pin where N2 meets switch 1** (`where_n2_meets_switch_1_a_hit_in_ktas_clock_is_what_modify_damage_deals`).
    - The cases are 3 Stadium cases × 3 attackers × 6 victims, 54 boards. The attackers are Mega Lucario ex (Stage 1 [F]), Kirlia (Stage 1 [P]) and Machop (Basic [F]).
    - The victims carry Heavy Helmet, Steel Apron, Metal Core Barrier, a −20 live through the threat's first attack turn, or a Tool plus the −20. They are an ex or not, and have no Weakness to [F] or [P].
    - km's first and later hits in kta's clock equal `modify_damage`'s damage for that active-to-active attack, on the board with every cut and with the lasting cuts only. kta's equal `modify_damage` on the same boards without the Stadium.
- **3.2, presets, value function, parser and wiring:**
  - `KM` with its flag cleared equals `KTA`, every field, compared as presets are compared. All 18 other presets have the flag off.
  - km's value with `KM`'s flag cleared equals kta's value function, bit for bit, on the played states.
  - `the_codes_are_kog_plus_their_switches` (KTA = KOG + switch 1, KOG as ec7e1a8's) is kept unchanged and passes.
  - **The parser:** `km3` and `KM5` parse; `km`, `kmx`, `km3x` and `km1a` don't; `kog3`, `kt3`, `kta3`, `ktb3`, `ktc3`, `koh3`, `kph3` and `k3` parse as before.
  - **Wiring through `get_player`, on 9c11b30's Machoke board:** km3 plays Arena and kta3 doesn't. With Hiking Trail instead, km3 equals kta3.
  - **Wiring through `get_player`, on a new switch-1 board:**
    - The board: Venusaur (150 HP left, Retreat 3) faces Mewtwo ex (50 a hit), with Heavy Helmet and Giant Cape in hand and one Tool slot.
    - kog3 plays the Cape: its clock sees the Cape's +20 HP (3 hits to 4) and not the Helmet's cut.
    - kta3 plays the Helmet: switch 1 counts the cut, 150 ÷ 30 is 5 hits.
    - km3 equals kta3. So `km3` is built on kta, not kog, and `kta3` from `get_player` plays switch 1.
- **Checked by planted faults, before B was committed.** The code was changed twice by hand and the tests run:
  - with the Stadium bonus added after the cuts instead of before, the new pin fails: Kirlia with Training Area against Metal Core Barrier gives the clock 10 where `modify_damage` gives 0;
  - with `KM` built on kog, the switch-1 wiring test fails: km3 plays Giant Cape.
  - The code was then restored byte for byte.
- **Full suite:** 1,991 passed, 0 failed. That is ec7e1a8's 1,977 (`../kt_kog_2026-09-28/README.md`) plus km's 14. No existing test's expected value was edited.
- **Fresh Stiffen counts:** deferred, as the amendment's (f) says. No km test reads Stiffen.

## The counter tool (8a at B)

The source is unchanged: `../tool_turn_effect_census_2026-09-25/tool_census.rs`, sha256 `05d7ba4183ce9e3098036de9acb5181ea71f7077ef9b3798ad4e5d165dc22365`. It is built as an example in a scratch copy of B's `engine/` (`git archive 1f6319e engine`; `check_tool.sh` checks the copy against B and the source's sha256), with the version before the Sept 29 round (816fd9c's, `a2510339…`) beside it for test 1.

| | sha256 |
|---|---|
| source | `05d7ba4183ce9e3098036de9acb5181ea71f7077ef9b3798ad4e5d165dc22365` |
| program, cloud build at B | `b48db2a89fd871b0d96c4de2090dd8a699aa515b378f51c5964a0edf1fe6947e` |
| old tool's program, for test 1 | `bf29c60f2eece878f879922fb4135d75faf7fe477dc4b0ad2018a8165cfb963c` |

**All pass** (`check_tool.sh`, `tool_check.py`, `tool_check.txt`):
1. **The old output, exactly.** kp3 on the table's first 20 deals of the 28 pairings (560 games): the old and new tools' stdout, stderr and games-out are byte-identical. Committed: `tool_test1_stdout.txt` (sha256 `a82786bb69fa10ca3bfba4c5854055911a280246440d9ab7b359319acb746997`) and `tool_test1_games.jsonl` (`057ae92e9a369d016bd10754313dd80f5eb7da1148bcdc79a1252cd642c67e0f`). **These equal 9c11b30's**, as expected: kp3 is untouched by B.
2. **The same games through the new options:**
   - games-out is byte-identical;
   - the card table is the same;
   - every row's fingerprint, seed and seats equal games-out's.
3. **Traced games against a recount from the trace.** kp3, Altaria v Lucario, seeds 20,000,920,000-019: 80 of 80 seat-cards agree for Arena of Antiquity and Training Area. Committed: `tool_test3_trace_rows.jsonl` (sha256 `fe983bab064437f5ea836ad43556c3896e6bbdf319eb44e74205729d265dd6b2`) and `tool_test3_trace.tsv` (`dee32d7fc8acd82f8dac23d1d3290140f483f27dd7289f61799f88d07840f285`). **Both equal 9c11b30's byte for byte.**
4. **`--first-deal`:** kta3 on deals 20-39 of the 17 cells gives 8a's rows for those deals exactly (340 rows, no counts).
5. **Refusals:** each of the six refused combinations exits with an error before any game.
- **Identity 8a** (move fingerprint, both decks, seed and seats; cell counts asserted; `--no-counts`, so no count was written or read):
  - the tool's kta3 on i < 40 of all 17 named cells: **680 of 680** deals equal `ec7e1a8_kta3_table.jsonl` (13 cells) and `ec7e1a8_kta3_new17.jsonl` (4 cells);
  - its km3 on pairings 0 and 2, i < 40: **80 of 80** equal item 7's smoke.
  - kog3's 680 is dropped, as the amendment says.

## The code review (the amendment's (c) item 3.5)

**Who and how.** One independent agent in this session did the review, read-only: git, file reads and grep, with no builds and no games. It covered B's diff against ec7e1a8, set against the amendment's (b), (c), (d) and (f). **It found no blocker and no should-fix.**

**What it checked in the code:**
- **Flag off (every code but km):** `kt_clock_stadium`'s arithmetic, casts, threat pick, cuts and bench loop are ec7e1a8's. The flag-off branch adds no work that changes anything, and kt's tests call the test-only wrapper unchanged.
- **Flag on:**
  - the threat is picked on unbonused damage;
  - the bonus is for the picked threat's attacker (its form through the same `evolution_targets` index, and board only for the opponent's side);
  - it uses each victim's own ex-ness, for the Active and the Bench;
  - it is combined as `modify_damage` does, bonus before the cuts and floored at 0;
  - no hidden information is read;
  - the two helpers are byte-identical to 9c11b30's.
- **The flag reaches both of `kt_clocks`' calls,** and only `KM` sets it.
- **The parser line, the variant and km's own inner `get_player` arm** are right.
- **Every test (c) 3.1 and 3.2 lists is present,** and no existing test's expected value was edited. The new pin and the switch-1 board would each fail on the faults they target.

**Its five notes, and what was done:**

| note | done |
|---|---|
| A. No test shows N2 reaching the bot's own survival clock (the opponent's threat) through `kt_clocks`: every test would pass if that call got `false`. | Checked without changing B. A diagnostic test was appended to a separate scratch copy of B's `engine/` and passes (`review_note_a_diagnostic.rs`). With Training Area in play, `kt_clocks` gives the bot's survival clock 2 under `KM` against 3 under `KTA`, and its clock on the opponent 2 against 3. Each equals `kt_clock_stadium` on its side. It is not one of B's tests: adding it would change B's commit, and the reviewer advised against reopening B for it. |
| B. The "flag cleared equals kta's value" check is true by construction once the preset test passes. | Kept, since (c) 3.2 asks for it. The game-level evidence that the flag-off path is kta's is identity items 1, 5 and 6 below. |
| C. No test pins a benched victim under N2, or the unbonused threat pick. | Noted. The code is right on both (the review read it), and the amendment requires neither. |
| D. BUILD.md must state the order, how the flag gets there, and that 9c11b30's scan change is not kept. | Stated above, in "What was built". |
| E. `threat.damage + bonus` is an unchecked u32 add. | Noted. It could overflow only if a damage estimate were near u32's maximum, which no attack's is, and `modify_damage` adds the same way. |

## Identity at B (the amendment's (c) item 4; `run_km.sh`, `identity.py`, `identity/identity_check.txt`)

All runs use the cloud's programs built from B (legality_scan sha256 `e72a18f50464c716f9477d2201033c5f11ae6270b90b63662b061f62b255d639`, deckgym `35b42fc3938ad6770b6b2a6f53830ae50d1005e244d444d1f87a425a9ce22d3b`), 4 threads, on the committed references. A game is equal when its moves, choices, openings, winner, points, seed and seats all are (and the deck files, where the reference has them). Every run's scan page must also be free of rule findings.

**Every check passes, with every game equal and every scan page free of rule findings.** No difference was found, so nothing stopped. That is 114,080 games through the scan, plus the counter tool's 760 (8a, above): 114,840, the amendment's count.

| item | run at B | reference | result |
|---|---|---|---|
| 1 | **kta3, all 500 table deals** | `../kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl` (the laptop's ec7e1a8 games) | 14,000 of 14,000 |
| 1 | **kta3, the 17 new cells, 500 deals** | `ec7e1a8_kta3_new17.jsonl` | 8,500 of 8,500 |
| 1 | k3, all 500 table deals | `../engine_switch_2026-09-28/pin_identity_k3_500.jsonl` | 14,000 of 14,000 |
| 1 | kp3, all 500 table deals | `pin_identity_kp3_500.jsonl` | 14,000 of 14,000 |
| 1 | kog3, all 500 table deals | `../koh_2026-09-28/bd2907f_kog3_500.jsonl`, and `../kog_composition_2026-09-27/table_kog3.jsonl` | 14,000 of 14,000 against each |
| 1 | kog3, the 17 new cells, 500 deals | `new17_kog3.jsonl` | 8,500 of 8,500 |
| 2 | kq3, all 500 table deals | `../kt_2026-09-26/identity/official_kq3_500.jsonl` | 14,000 of 14,000 |
| 2 | kd3, 40 table deals | `../rules09_fixes_2026-09-26/af8489f_kd3_40.jsonl` | 1,120 of 1,120 |
| 2 | kpr3, 40 table deals | `af8489f_kpr3_40.jsonl` | 1,120 of 1,120 |
| 3 | **kta3, B2e's 96 pairings, i < 40** | `ec7e1a8_b2e_kta3.jsonl` | 3,840 of 3,840 |
| 3 | **kta3, Scizor's 8 pairings, i < 40** | `ec7e1a8_scizor_kta3.jsonl` | 320 of 320 |
| 3 | **kta3, the four second lists, i < 40** | `ec7e1a8_var_{v-lucario_2,v-suicune_2,v-weezing_2,l-charizardy}_kta3.jsonl` | 280, 280, 280 and 320: 1,160 of 1,160 |
| 3 | kog3, B2e's 96 pairings, i < 40 | `../koh_2026-09-28/reading/b2e_kog3.jsonl` | 3,840 of 3,840 |
| 3 | kog3, Scizor's 8 pairings, i < 40 | `../koh_2026-09-28/laptop_runs/scizor_kog3.jsonl` | 320 of 320 |
| 3 | kog3, the four second lists, i < 40 | `laptop_runs/var_*_kog3.jsonl` | 280, 280, 280 and 320: 1,160 of 1,160 |
| 4 | `KM` with its flag cleared equals `KTA` | a test (`km_is_kta_plus_n2_and_nothing_else`) | passes |
| 5 | **km3 on the 15 table cells with neither the panel Altaria nor Lucario list, 500 deals** | `ec7e1a8_kta3_table.jsonl` | 7,500 of 7,500 |
| 5 | **km3 on the 13 new cells with neither, 500 deals** | `ec7e1a8_kta3_new17.jsonl` | 6,500 of 6,500 |
| 6 | kta3 at B, pairings 0 and 2, 40 deals | `ec7e1a8_kta3_table.jsonl` | 80 of 80 |
| 7 | km3 smoke, pairings 0, 2 and 19, 40 deals | none: a clean, complete run only; its games were not read. It is the laptop's km3 reference: `identity/1f6319e_km3_smoke_40.jsonl`, sha256 `55f7a5905acad7d9a9daabdf541c9aee258704c23712a1d2b8f8271e2e73d043` | 120 games, clean |
| 8 | the diff of `engine/` from ec7e1a8, `engine/UPSTREAM.md` aside | `engine/src/players/` only | yes |
| 8a | the counter tool (above) | the kta3 files and item 7's smoke | 680 of 680; 80 of 80 |

- **What these show:**
  - **kta3 at B plays exactly as kta played its tables.** Item 1 matches all 22,500 games, and item 3 all 5,320 at i < 40. This runs through B's changed `kt_clock_stadium` with N2's flag off.
  - **km3 with nothing for N2 to read plays kta3's games** (item 5). That includes the 464 development games in 13 of those 28 cells where kta3's moves differ from kog3's (the amendment's (b) item 6). So this is also game-level evidence that km3 is built on kta, switch 1 included.
  - **The older codes are unchanged:** k3, kp3, kog3, kq3, kd3 and kpr3.
- **What these license** (section 4.1, "Only an identity that covers those files licenses that reuse"):
  - The eight kta3 reference files of the amendment's (b) item 3 are kta3's games at B, the files km3 is read against.
  - The coverage files are covered at i < 40, as registered. The rest of each file is licensed by that rule, not by a game here, and the laptop's (e) adds i < 20 at its own build.
- **Agreement across machines.** Every kta3 reference was played by the laptop's ec7e1a8 programs (`924751ba…`, `40797636…`), and the cloud's build of B agrees with them on every tested game. That is agreement on the tested games, not a claim that any two programs are identical.
- **Run times are not a timing measure.** The counter tool's build and checks and a scratch diagnostic ran on the same machine at the same time. The timing pair is the laptop's.
- **A container restart** stopped the runner at about 03:21 UTC, during kta3's 500 table deals. The runner was restarted at 04:49 with the same program and calls. It skipped the finished items and re-checked them (they pass again, so `identity_check.txt` lists items 5 to 7 twice), then replayed kta3's table deals from the start (`STATUS.txt`, "RESUMED").

## Files

- `STATUS.txt`: one line per step, with every sha256.
- `suite.log`: the full suite at B.
- `run_km.sh`, `identity.py`, `identity/`: the identity runs (each `1f6319e_*.jsonl` with its scan page `.txt`) and `identity_check.txt`.
- `check_tool.sh`, `tool_check.py`, `tool_check.txt`: the counter tool's tests and 8a. Test 1's and 3's outputs are `tool_test1_stdout.txt`, `tool_test1_games.jsonl`, `tool_test3_trace_rows.jsonl` and `tool_test3_trace.tsv`. 8a's rows (no counts) are `identity/1f6319e_tool_kta3_km17_40.jsonl` and `identity/1f6319e_tool_km3_p02_40.jsonl`.
