Decision this informs: none on its own. This is the cloud's round for km re-issued on kta (`../trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`, "Amendment 1 (Sept 30 …): km re-issued on kta", part (c), which scopes it; main 3aed736; Dustin's choice B, Sept 30). It covers the build, its tests, the identity checks with the counter tool's 8a, and the one code review. After this, the order is the amendment's (g): the laptop's identity games at B and its threshold preparation, then Dustin's separate go-ahead for the registered tables. No registered km game or table was played, no threshold was measured, and nothing here is a reading. **Build B = commit 1f6319e** (`1f6319e4b72e34a42d2d3c3ffc7cc9a09fdfa6f3`): ec7e1a8's `engine/` plus km's N2 in kta's clock, in `engine/src/players/` only. 9c11b30 (`../km_build_2026-09-29/`) stays implementation evidence only.

Seeds: identity on the table's deals (72,000,000 + pairing × 10,000 + i), the 17 new cells' and Scizor's (21,108,000,000 + …), B2e's and `l-charizardy`'s (21,106,000,000 + …) and the other second lists' (72,000,000 + …); even i puts the first-named deck in seat 0. The counter tool's traced test games use Claude diagnostic seeds 20,000,920,000 to 20,000,920,019 (kp3), as at 9c11b30. The km unit tests' random games use 20,000,000,400 and up.

# km on kta: build B (Sept 30)

## In plain words

- **km3 is now kta3 with one change.** kta3 is the adopted working pilot: kog plus kt's switch 1, the defender's damage cuts in the threat clock. km3 adds N2: each hit in that clock also includes the damage a Stadium in play adds, Training Area's +10 for a Stage 1 attacker and Arena of Antiquity's +20 for an [F] attacker hitting an ex. With neither Stadium in play, km3 plays exactly as kta3.
- **Where things stand** (`STATUS.txt` has a line per step):
  1. **Build:** done, B = 1f6319e.
  2. **Tests:** done. km's 14 tests pass, and the full suite passes: 1,991 passed, 0 failed.
  3. **Counter tool:** STEP3.
  4. **Identity:** STEP4.
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

STEP3DETAIL

## The code review (the amendment's (c) item 3.5)

REVIEW

## Identity at B (the amendment's (c) item 4; `run_km.sh`, `identity.py`, `identity/identity_check.txt`)

IDENTITY

## Files

- `STATUS.txt`: one line per step, with every sha256.
- `suite.log`: the full suite at B.
- `run_km.sh`, `identity.py`, `identity/`: the identity runs (each `1f6319e_*.jsonl` with its scan page `.txt`) and `identity_check.txt`.
- `check_tool.sh`, `tool_check.py`, `tool_check.txt`: the counter tool's tests and 8a. Test 1's and 3's outputs are `tool_test1_stdout.txt`, `tool_test1_games.jsonl`, `tool_test3_trace_rows.jsonl` and `tool_test3_trace.tsv`. 8a's rows (no counts) are `identity/1f6319e_tool_kta3_km17_40.jsonl` and `identity/1f6319e_tool_km3_p02_40.jsonl`.
