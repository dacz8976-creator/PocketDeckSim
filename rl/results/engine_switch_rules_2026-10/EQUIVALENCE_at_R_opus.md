# Equivalence at R: the Opus reading extended to R, and Opus vs Sonnet row by row

This was a reading only. Nothing was built, run or played. Everything was checked after `git fetch` on these commits:
- **R** = 1abdbe8f, on origin/sonnet/rules-fixes. The branch tip, b3e6eae, adds only `EQUIVALENCE_sonnet.md`.
- **EQUIVALENCE_opus.md** was read from origin/main (c39e786). It reads the engine at c9df626.
- **EQUIVALENCE_sonnet.md** was read at b3e6eae.

Line numbers are at R unless marked "old" (4690810) or "c9".

## Verdict

- **Every row of EQUIVALENCE_opus.md still holds at R.** Between c9df626 and R, `engine/` changes in only 4 files:
  - `src/card_validation.rs` (F2);
  - `src/hooks/core.rs` (F1);
  - `tests/b4a_attack_batch2_test.rs` (F4 0311971, F7 893f9d6);
  - `tests/victini_victory_star_test.rs` (F3 c476556, F7 893f9d6).
- **Untouched from c9df626 to R:** `apply_action.rs`, `apply_attack_action.rs` and `attack_outcome.rs`. So rows B1-B15, B17 and A1-A4 carry over with the same line numbers.
- **B16 holds.** No F1 hunk is inside `modify_damage`; its lines only move up 9.
- **Diff checks:**
  - `engine/` is byte-identical from 893f9d6 to R (the diff stat is empty).
  - `players/` and `Cargo.lock` don't change from 4690810 to R (the diff stat is empty).
- **F1 is kd-only.** Without a coin-Ability PokÃ©mon in play it gives the same results as before.
- **The two readings agree on the equivalence verdict of every code hunk.** Neither reader misses a code hunk.
- **What the readings disagree on is side claims, not equivalence:**
  - D1: both readers overstate the reach of B15 (rows 5-6). This has a cheap remedy.
  - D2-D5: Sonnet slips. Opus is right on each.
  - D7: Sonnet's row 13 is not independent of Opus.
  - D8: a reach note on l-sharpedo.
- **Nothing here triggers the stop rule.**

## 1. EQUIVALENCE_opus.md extended to R

| Opus row | Touched at R by | Holds at R | Re-cite at R / note |
|---|---|---|---|
| Â§1 root fact (`HEADS_COIN_CUTS` empty off the gate) | none | yes | attack_outcome.rs unchanged: static at 37, early return 46-48, writes 53 and 57, the 5 calls 215/716/810/920/1004, the 7 `vec![]` 103-170 and 578, extend 663-668 |
| B1-B11, B17 | none | yes | same lines as c9 |
| B12-B15 | none | yes | same lines as c9 |
| B16 `modify_damage` | F1 is in the same file, but no hunk falls inside `modify_damage` (fn at core.rs:1814) | yes | read at 2056-2060, debug at 2061-2063, `.saturating_sub(heads_coin_cut)` at 2069 (c9: 2065-2069, 2078) |
| Comment-only core.rs:1394-1398 | none (F1's hunks are below it) | yes | same lines |
| Â§4 A1-A4 and the gate | none: F3, F4 and F7 are tests only | yes | gate at apply_action.rs:193; A's functions at apply_attack_action.rs:117, 136, 152 |
| Â§6 and Â§7 notes | none | yes | |
| Â§8 F1 | F1 | yes | see below |
| Â§8 F2 | F2 | yes, with one addition | see below |
| Â§8 F3, F4, F7 | tests only, no fix landed | yes | F4's test is in b4a_attack_batch2_test.rs, not the Victini file. No test file is new. |
| Â§8 F5, F6 | `rl/results/` only, no hook in `engine/` | yes | Â§8's hook-site conditions are moot |

**F1** (fix 160a9d4, tests 8e0622a). The changes:
- The `use` list drops `attacks::Mechanic` and `EFFECT_MECHANIC_MAP`. Nothing else in core.rs uses either, so no name resolves differently.
- Doc comments are updated.
- The `engine_flips_coin` local is deleted (old 1657-1667). It was a pure `EFFECT_MECHANIC_MAP.get` read, used only in the two match guards.
- The two coin arms lose their guard. The Reduce arm now prices heads as `first.saturating_sub(amount)`, after the whole pipeline, instead of `hit(base - amount)`.
- Two test asserts change.

**Is F1 on the table path for any pilot but kd? No.**
- The only production caller is players/value_functions.rs:1655 (`KdPricer::hits`).
- That is reached through `KdPricer::price` and `kd_turns_to_win` (1419), which is called only at 1221, under `if defender_modifiers` (1220).
- `defender_modifiers: true` appears only in `EvalFeatures::KD` (428). No constant is built from KD, and `..EvalFeatures::KD` occurs nowhere.
- `EvalFeatures::KD` is used only by `public_clock_effect_kd_value_function` (220-231), and players/mod.rs:649 wires that to KD.
- It is false for km (KTA plus N2), kta, kog, k, kp, kq and kpr.

**For kd with no coin-Ability PokÃ©mon in play, the results are identical:**
- **Victims are always in play.** They are victim_owner's Active (`maybe_get_active`, 1441) and Bench (`enumerate_bench_pokemon`, 1437).
- **The changed arms (core.rs:1724, 1728) need a coin Ability on the victim itself.** They match only when `ability_effect` is `CoinFlipToPreventIncomingDamage` or `CoinFlipToReduceIncomingDamage`.
  - `ability_effect` is the victim's own in-play Ability effect (1637-1642), and None under `skip_target_effects`.
  - Those two effects come only from the five printings: A2 114, B3b 050, A4 080, B2 124 and B2 204.
- **Every other victim takes the `_` arm (1736-1739), which is unchanged.** `hit(base_damage)` is still called once. The deleted local had no side effect and fed nothing else.
- **The attacker's own Ability never matters here.** The attacker `form` may be an evolution target taken from the deck (`kd_attacker`, 1555-1560), but the arms never read the attacker's Ability.
- **So kd3's identity gate (step 7, 1,120 games) should replay identical.**
- **What kd prices differently on the gate:**
  - Bastiodon or Goodra as the victim, under any attack: the cut now comes after Weakness and the other reductions.
  - Meowth or Togekiss as the victim, under DirectDamage, DirectDamageAndSelfCardEffect or DirectDamageIfDamaged: the coin is now priced.
  - Meowth or Togekiss under any other attack is priced as before.

**F2** holds.
- The text is at card_validation.rs:97. The card's status stays RulesUnverified, because `card_validation.rs:80` checks only that the list isn't empty.
- **Addition:** besides cli_preflight.rs:60 and examples/goldfish.rs:214, `src/bin/card_status.rs:44,108` also prints the text. It is not one of step 5's programs.
- Step 10's byte-equal checks hold, because no list there holds Victini.
- The `houndoom_victini` carrier's preflight and `--coverage` text will differ by this line. That is F2's text, not a game difference.

## 2. Opus vs Sonnet, hunk by hunk (`git diff 4690810 R -- engine/src/`)

| Hunk (at R) | Opus | Sonnet | Both verdicts | Agree? |
|---|---|---|---|---|
| `HEADS_COIN_CUTS`, `with_heads_coin_cuts`, `heads_coin_cut` (attack_outcome.rs:31-73) | B13 + Â§1 | 1 | `f()` off the gate | yes (D5 line slips) |
| The field plus its 7 `vec![]` (93, 103-170, 578) | B12 | 2 | invisible | yes (D4 wording) |
| `resolved_heads_coin_cuts` (176-182) | B12 | 3 | pure | yes |
| `into_mutation`'s wrap (207-226) | B14 | 4 | `f()` | verdict yes; Sonnet's "only hunk every attack runs" is wrong (D2) |
| Guts, point-denial and Perish Body wraps (716, 810, 920) | B15 | 5 | `f()` | verdict yes; reach overstated by both (D1) |
| `expected_damage_to` wrap (1004) | B15 | 6 | no production caller | yes |
| `modify_damage` (core.rs:2055-2069) | B16 | 7 | `- 0` | yes |
| Saturation doc comment (core.rs:1394-1398) | comment-only | 8 | code unchanged | yes. Sonnet adds that the unchanged bound stays valid under the new order. I checked this and it is right. |
| Tests (attack_outcome.rs 1253-, core.rs tests, test files) | test-only | 9 | not in the programs | yes |
| The split's `retain` (621-677) | B17 (Â§3) | 10 | not reached on the table; full prevention identical | yes (D6: different on-gate corners, both right) |
| The split's doc comment (612-620) | comment-only | not named | â€” | Sonnet omits it (comment only) |
| `coin_damage_prevention` and its call site (apply_attack_action.rs:247-253, 264-273) | B1 | 11 | token for token | yes |
| `queued_attack_damage_choice` (281-304) | B2 | 12 | the old literal | yes |
| `discard_then_damage_choice` and `chase_order_attack` (311-343) | B10 | 13 | the old literal | yes (D7: not independent) |
| `apply_discard_own_benched_then_damage` (apply_action.rs:1284-1308) | B10 | 22 | same frame | yes |
| `direct_damage`, `direct_damage_and_self_card_effect`, `push_direct_damage_choices` (2873-2920) | B3 | 14 | old literal | yes |
| `direct_damage_if_damaged` (2943-2966) | B4 | 15 | old literal | yes |
| `discard_all_energy_of_type_then_damage_any_opponent_pokemon` (2968-3002) | B5 | 16 | old literal | yes |
| `self_discard_energy_then_damage_any_opponent_pokemon` (3934-3959) | B6 | 17 | old literal | yes |
| `optional_discard_benched_basic_for_extra_damage` (4418-4455) | B9 | 18 | old literal | yes |
| `damage_to_any_opponent_per_target_energy` (4578-4595) | B7 | 19 | old literal | yes |
| `switch_in_opponent_benched_then_damage` (6537-6590) | B8 | 20 | old literal | yes |
| The dispatch passes `attack` to 8 mechanics (805, 839, 845, 902, 955, 1092, 1272, 1616) | B11 | 21 | clone only | yes |
| `has_unverified_attacker_coin_gate` doc (apply_attack_action.rs:92-95) | comment-only + Â§4 | not named | â€” | Sonnet omits it (comment only) |
| A1 (apply_action.rs:195-215) | A1 | Â§5 | behind the gate at 193 | yes |
| A2 (290-311) | A2 | Â§5 | behind the gate | yes |
| A3 `forecast_victory_star_choice` (fn at 319, hunk 362-384) | A3 | Â§5 | only while `pending_attack_coin_choice` is set (269) | yes |
| A4: the three functions (apply_attack_action.rs:117, 136, 152) | A4 | Â§5 | called only from A1-A3 | yes |
| card_validation.rs:97 (F2) | Â§8 F2 | Â§6 only, no Â§2 row | text only | verdict yes; reasoning differs (D3) |
| core.rs `use` list, `persistent_defender_damage` and its docs (F1) | Â§8 F1 | 23 + Â§6 | kd only | yes |

**What only one reader covers (checked; all correct):**
- **Only Sonnet: the census in its Â§1.** The old `apply_attack_action.rs` builds `ApplyDamage { attacking_ref: (action.actor, 0), .. }` at 9 places:
  - 7 are rewritten: old 2773, 2813, 2846, 3798, 4279, 4425 and 6402.
  - 2 are untouched: `also_choice_own_pokemon_damage` (old 6163) and `shuffle_opponent_tools_into_deck_before_damage` (old 8275, production code placed after the test modules).
  - B removes 8 literals (7 here plus 1 in apply_action.rs) and adds 2.
- **Only Opus:**
  - B11's Victory Star callers.
  - A with a Victini but no Confusion: `confusion_first` is false, so the old condition at 206 applies.
  - Â§6's correction of the bots' special case.
  - Â§7's notes.

## 3. Disagreements, and which is right (each read in the code)

**D1. The reach of B15 (Sonnet's rows 5-6). Both readers are wrong in the same way.**
- **The claims:**
  - Opus Â§5.2: "Rows B1 and B12-B16 need no counter: they run in every attack that deals damage."
  - Sonnet Â§4: "Rows 1 to 7 run on every attack â€¦ no counter is needed."
- **What the code does:**
  - The three live wraps run only past early returns that need a Guts, point-denial or Perish Body PokÃ©mon in the defending side's play (apply_attack_action.rs:366, 398, 428).
  - `expected_damage_to` never runs in a program: its only caller is `expected_damage_to_opponent_active`, which only tests call.
  - Each reader states these gates in its own row, so each contradicts itself.
- **Equivalence is unaffected:** with empty cuts the wrap is `f()`.
- **The correct wording:** "B1, B12, B13, B14 and B16 run in every attack that deals damage. B15 runs only with a Guts, point-denial or Perish Body PokÃ©mon in the defending side's play. `expected_damage_to` never runs."
- **Where B15 is reached:**
  - No list on the 28 cells (the C(8,2) pairings of the 8 t- lists, confirmed from `table_k3.jsonl`) holds Ursaluna, Conkeldurr, Dusknoir, Glimmora or Galarian Cursola.
  - Dustin's deck 01 holds 2 Glimmora B3a 045. Its Ability, Shattering Crystal, maps to `CoinFlipToDenyKnockoutPoints`.
  - So the point-denial wrap (attack_outcome.rs:810) runs on every attack into deck 01 while a Glimmora is in play.
  - Deck 01's floor page is committed: `rl/results/floor_dustin_2026-09-30/01-muk-glimmora-kingambit-regigigas_games.jsonl`.
- **Suggestion (the coordinator's call):** add that page to step 7c's plain replay. It is 1,920 games and takes minutes. Guts and Perish Body then rest on the reading and the tests, as Beast Wall did.

**D2. Sonnet's row 4: "This is the only hunk every attack of every table game runs." Wrong.**
- Every attack's forecast reaches `apply_defender_attack_modifiers` (185, 194, 205). That runs B1, which Sonnet calls row 11.
- Row 2's `vec![]` runs for every outcome built.
- Row 7 runs in every `modify_damage`.
- Row 4 itself runs only when `resolved` isn't empty (attack_outcome.rs:208).
- Opus's B1 ("runs on every attack") is right. No verdict changes.

**D3. F2's text. Opus is right.**
- Sonnet Â§6 says "Nothing reads the text". That is true only of tests.
- Programs print it: cli_preflight.rs:60, examples/goldfish.rs:214 and src/bin/card_status.rs:44,108. Opus missed card_status.
- No game is affected, and the status is unchanged.

**D4. Sonnet's row 2: the field "is read in â€¦ `split_with_damage_prevention`". Opus is right.**
- The split writes the field (`extend`, 663-668).
- Opus Â§1 says "the only write to the field is the extend". Wording only.

**D5. Sonnet's line slips. No verdict effect.**
- Row 1: the replace is at 57, not 55. The early return is at 46-48, not 45-48.
- Row 2: line 81 is the `#[derive(Clone)]`; the field is at 93.
- Row 5: it names only Ursaluna for Guts. Conkeldurr A3 096 has Guts too.
- Opus's numbers are at c9. At R only core.rs moves: up 9 below about line 1660.

**D6. Not a disagreement. Different on-gate corners of the split, and both are right.**
- **Sonnet's row 10:** an amount-0 entry at a finite-cut slot is now kept, and "carries no damage". This is fully harmless:
  - a flipping slot always also has an entry above 0 (634);
  - `handle_damage_only` merges entries per target (apply_action_helpers.rs:545-548).
- **Opus Â§7.3:** an entry that the cut takes to 0 is now kept, so the retaliation frame and the knockout pass run.

**D7. Process: Sonnet's row 13 is not independent of Opus.**
- Sonnet says it did not read EQUIVALENCE_opus.md before writing its Â§2. But its row 13's bold sentence carries Opus Â§6 items 2-3, and so do its Â§4 ("Added on the laptop Opus's point, Oct 1") and Â§7 ("the laptop Opus's second point").
- So B10 (Sonnet's rows 13 and 22) has one independent reader, not two.
- I re-checked it myself:
  - The fall-through literal (apply_attack_action.rs:321-325) equals old apply_action.rs:1253-1260, field for field.
  - `chase_order_attack` is called only inside `if coin_target` (316-320).
- It holds.

**D8. Reach: l-sharpedo is not in 7b's watch run.**
- Sonnet Â§6 (F5 table) says `offgate_discard_then_damage` reads above 0 in "the table run (t-vespiquen, l-sharpedo)".
- l-sharpedo is a ladder-panel list (`decks/screen/panel_ladder_2026-09-26/`), not one of the 28 cells that 7b's watch run plays.
- On 7b, only t-vespiquen's Chase Order with the discard can fire it. Wild Swing's fall-through reaches the watch build only in 8b (l-sharpedo v `meowth_carefree`).
- Opus Â§6.2 names only t-vespiquen, which is right.

## Files
- Written: `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\wf_rsr\equiv_at_R.md`.
- The scratch extracts it was read from are in `...\wf_rsr\equivalence-at-R\`.
