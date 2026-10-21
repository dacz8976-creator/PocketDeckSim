# Release notes: main-4d48844, the official engine from Oct 21

**Adopted Oct 21, 2026, as a rules-correction update.** Dustin's words (to the coordinator, Oct 21, 2026, answering "adopt the engine now, with points 3-5 as recommended, and move the slow-report program after tonight's replay check passes?"; verbatim):
> Yes, I recommend that split. It addresses my remaining concerns.
> - Adopt the reviewed engine as a rules-correction update.
> - Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine.
> - Leave historical scoreboards and mixed-opponent comparisons alone. Revisit them only if a future decision relies on them.
> - Keep the bot's simplified hit-back evaluation listed as an unmeasured limitation.
>
> There's no need to add another benchmark or approval stage. The remaining work is the normal release verification and the already-planned slow-report check.

His decisions on the open points, as the coordinator recommended them: #385 stays as a rule (its card text says "during your turn"); no re-baselining (items 2 and 3 under "Tied to the OLD engine", the mixed kt/kta clause-(d) comparisons and scoreboard v3 with its thresholds and kta3's status, stay records of their old engines, revisited only if a future decision relies on them); the readings of his Oct 20 ruling listed next are kept. Still open: the holder-side boosts on a hit back (not named in the ruling). The bots' simplified evaluation of a hit back is an unmeasured limitation ("Known limits", item 4). The slow-report program moves only after its kx3 replay check passes; until then its reports name the old engine. The Growl rule's "+X" case is recorded (Oct 20, the Luxray/Espathra retry), and the engine matches it.

## Readings of his Oct 20 ruling applied to card text, not recorded (kept on Oct 21; he can still veto each)
His words: "The attack back is treated as an attack in every situation (weakness, attack blocking, bounded field) not like an ability. Abilities don't trigger heavy helmet, attacks do". Of the hit back's interactions, only Weakness (183108), Bounded Field (Boundedfield_hitback_test) and Heavy Helmet's cut (20261009_223237000) are recorded, and Rocky Helmet is the card the ruling names. These two follow from the ruling and each card's text and were never seen in a game:
1. **The Rough Skin-type Abilities answer a hit back.** Rough Skin, Counterattack, Steel Spikes and Automated Combat read "If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon"; the hit back counts as damage from an attack, so the Attacking Pokémon's Ability answers the holder with 20 (an Ability's damage, which ends the chain; tests pin both).
2. **Intimidating Fang cuts a hit back.** "As long as this Pokémon is in the Active Spot, attacks used by your opponent's Active Pokémon do −20 damage": the hit back is treated as the holder's attack, so a Luxray hit back takes 20 less, before Weakness, and a hit back cut to 0 does nothing.
On the same footing, with less at stake: Poison Barb and Poison Point poisoning the holder; Safeguard, Disguise and the Bench shields preventing it; the damage-cut Abilities and Tools other than Heavy Helmet. No listed deck reaches any of these except Rocky Helmet (t-blaziken) and Shuckle ex's Solid Shell (t-vespiquen) against brews 07 and 09. Each can be taken out with a small code change.

## What the adoption activates
- **The three programs** in `rl/engine-2026-10-21/` (`deckgym` 9ab0196d… blob, sha256 2d3709b272abf8a83431c3e72d59f9ff0e2c8ae3e60698f22a1ca79e65ab2085; `legality_scan` 2975381f33fdd7fc650f293f0dd254226cbb6e39527529fd123ffae897051b1a; `goldfish` db52d3de65ca2577aa39af7539635a1473d4f876842bd711131a3b2c7d797f31): the final build's tested bytes, the same git blobs as `rl/results/engine_candidate_2026-10-20/programs_final/`, mode 100755, never rebuilt.
- **The current-engine selector.** `project_manifest.json`'s `available_release` names them. `current_engine.py`, `decks/screen/floor.py` and `decks/screen/run_screen.py` read it, so the screen and the floor switch with the manifest. `make_predictions.py`'s `CURRENT_ENGINE` moves with it: floor pages made on `rl/engine-2026-10-21/deckgym` count as current, and no slow report does until the slow report's re-pin.
- **The slow-report program:** not moved by this commit. Per Dustin (Oct 21), the slow-report program moves only after its kx3 replay check passes. Until then the pinned program stays kx3 on main-c045ede's engine, every page names it in its headline ("kx3 (d513e37b, on main-c045ede)"; `rl/strength/README.md` says so too), and `make_predictions.py` counts no slow report as current. The re-pin is drafted on `laptop/new-slow-pin-2026-10-20`: the frozen kx3 players (`claude/playout-pilot` d513e37b) on this engine (`laptop/kx3-on-engine-candidate-2026-10-20` 87a7f340, engine tree 64de03e2), built with `rl/strength/build.sh` at STRENGTH_JOBS=2 (`/home/dacz8976/kx_r3/strength`, sha256 7d046b6f…; build record OK); self-checks equal to the pin's texts (km3 81b572198c04d5d1, kx3 31d638dbc818b0fa); its pin tests pass (`slow_pin/PIN_TESTS.txt` on that branch).

## Release identity
- Built from 4d4884492aa85496acf9bafdae18b22739f56647 (2026-10-21, 02:00-02:12 UTC); engine tree 46239c19. main's `engine/` after the adoption is that tree, byte for byte: no exception.
- The Oct 20 build (d9d2e704, deckgym 245e11e8…) is the final candidate without the hit back's change; it carried the Oct 20 pass and is the attribution build below.
- **Activation checks** (after the merge, in the repository root, on Linux):
  1. `cd rl/engine-2026-10-21 && sha256sum -c SHA256SUMS`: three OK lines.
  2. `git ls-tree HEAD rl/engine-2026-10-21/`: deckgym 9ab0196d…, legality_scan bac355c4…, goldfish c48e300d…, each 100755.
  3. `python3 current_engine.py`: prints this repository's `rl/engine-2026-10-21/deckgym` (it refuses a file whose hash is not the manifest's).
  4. The manifest's three sha256 equal `SHA256SUMS`.

## The floor re-check pages on the final build
| Piece (1,920 games; run_screen 3,840) | Recorded on main-c045ede | Oct 20 build (245e11e8) v recorded | Final build v recorded |
|---|---|---|---|
| B_D_victini-passive | clears the floor, 693 of 1,920 | SAME: clears the floor, 693 of 1,920 | SAME: clears the floor, 693 of 1,920 |
| A_brew-06 | fail, 125 of 1,920 | SAME: fail, 125 of 1,920 | SAME: fail, 125 of 1,920 |
| A_brew-06b | fail, 262 of 1,920 | SAME: fail, 262 of 1,920 | SAME: fail, 262 of 1,920 |
| A_control14_k3 | control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 | SAME: control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 | SAME: control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 |
| A_brew-05b | clears the floor, 577 of 1,920 | SAME: clears the floor, 577 of 1,920 | SAME: clears the floor, 577 of 1,920 |
| A_07 | clears the floor, 1,098 of 1,920 | SAME: clears the floor, 1,098 of 1,920 | SAME: clears the floor, 1,098 of 1,920 |
| A_run_screen | run_screen, 20 lines | SAME | SAME |
| B_12 | clears the floor, 635 of 1,920 | SAME: clears the floor, 635 of 1,920 | SAME: clears the floor, 635 of 1,920 |
| B_brew-07 | clears the floor, 1,168 of 1,920 | SAME: clears the floor, 1,168 of 1,920 | DIFFERS: clears the floor, 1,165 of 1,920 |
| B_brew-09 | clears the floor, 837 of 1,920 | SAME: clears the floor, 837 of 1,920 | DIFFERS: clears the floor, 824 of 1,920 |
| B_D_root | clears the floor, 693 of 1,920 | SAME: clears the floor, 693 of 1,920 | SAME: clears the floor, 693 of 1,920 |
| B_D_amended | clears the floor, 597 of 1,920 | SAME: clears the floor, 597 of 1,920 | SAME: clears the floor, 597 of 1,920 |

**Sort of the changes** (PLAN addendum: the Oct 20 build, without the hit back's change, is the attribution build):
- **(a) Rule fix, the hit back as attack damage:** brews 07 and 09 only, and only in their games against t-blaziken and t-vespiquen. t-blaziken holds 1 Rocky Helmet (A2 148), which now answers Mega Sableye ex's hit back with 20; t-vespiquen holds 2 Shuckle ex (A4 021), whose Solid Shell ("This Pokémon takes -20 damage from attacks") now cuts it. No other opponent list holds a card the change reads. Final build v the Oct 20 build, per opponent:
  - brew 07: t-blaziken 8 of 240 games differ (wins 143 → 140), t-vespiquen 12 of 240 (119 → 119); the other six opponents 0 of 240 each. Total 1,168 → 1,165 wins.
  - brew 09: t-blaziken 21 of 240 (137 → 131), t-vespiquen 43 of 240 (93 → 86); the other six 0 of 240 each. Total 837 → 824 wins.
  - Both verdicts are unchanged: each still clears the floor (bar: 419 wins or more of 1,920).
- **(b) Upstream change:** none on these pages. The Oct 20 build carries every upstream change and the Growl rule, and it equals the recorded pages on all 12 pieces.
- **(c) Unexplained:** none.

Record: `release/floor_recheck_final/` (the final build's pages and comparisons; `DIFF_BY_OPPONENT.txt`), `release/floor_recheck/` (the Oct 20 build's), `release/FLOOR_TABLE.md`.

## A sample of the Oct 20 pass's runs, replayed on the final build
| Run (replayed command) | Games or deals | v the recorded reference | v the Oct 20 build |
|---|---|---|---|
| `08a9b3a_10_cli_k3` | 240 | SAME: the summary lines equal (Player 0 won 150 (62.50%)) | SAME |
| `08a9b3a_10_cli_kp3` | 240 | SAME: the summary lines equal (Player 0 won 144 (60.00%)) | SAME |
| `08a9b3a_10_cli_kog3` | 240 | SAME: the summary lines equal (Player 0 won 149 (62.08%)) | SAME |
| `08a9b3a_10_cli_kta3` | 240 | SAME: the summary lines equal (Player 0 won 149 (62.08%)) | SAME |
| `08a9b3a_10_cli_km3` | 240 | SAME: the summary lines equal (Player 0 won 149 (62.08%)) | SAME |
| `08a9b3a_10_goldfish` | 0 | SAME: the page and the coverage file byte-equal | not compared (plays no games) |
| `08a9b3a_10_run_screen` | 3,840 | SAME: run_screen: 20 of 20 lines equal | SAME |
| `08a9b3a_8b_cloud_new_k3` | 240 | SAME: 0 differing deals of 240 | SAME (0 deals) |
| `08a9b3a_8b_cloud_new_km3` | 240 | SAME: 0 differing deals of 240 | SAME (0 deals) |
| `08a9b3a_dev_km3_new17` | 8,500 | DIFFERS: 7 differing deals of 8500 | SAME (0 deals) |
| `08a9b3a_table_k3` | 14,000 | SAME: 0 differing deals of 14000 | SAME (0 deals) |
| `08a9b3a_dev_km3_table` | 14,000 | SAME: 0 differing deals of 14000 | SAME (0 deals) |
| `08a9b3a_8_new_km3` | 16,000 | DIFFERS: 1 differing deals of 16000 | SAME (0 deals) |
| `08a9b3a_new17_k3` | 8,500 | DIFFERS: 8 differing deals of 8500 | SAME (0 deals) |
| `08a9b3a_cov_b2e_km3` | 48,000 | SAME: 0 differing deals of 48000 | SAME (0 deals) |

Against the recorded references only the Growl rule's known changes remain, the ones the Oct 20 pass attributed (RESULT.md): new17 pairing 21 (km3 7 deals, k3 8) and step 8's km3 carriers (1). Every run that plays games equals the Oct 20 build's games.

## Tied to the OLD engine (main-c045ede): not re-run, and not new-engine evidence
Old thresholds and summaries do not carry over. Each item stays a record of main-c045ede (or of an older engine):
1. **kx3 and its recorded games.** The slow-report pin (program 76df495b; laptop/kx3-on-rules2 cd20a97a, engine tree 4ebb30a9) until its re-pin; the 8 slow reports made on it (`rl/results/slow_reports/2026-10-12_*`, `2026-10-13_*`, `2026-10-14_*`; brews 07 and 09's rows against t-blaziken and t-vespiquen are among those the hit back's change can move) and the paired dry runs; `kx3_on_rules2_2026-10/` (its 202 + 202 replay games), `m64_on_rules2_2026-10/` and `pause_positions_kx3_2026-10/`. kx3's unchanged self-check digest is a 12-game check, not identity for those games.
2. **The mixed kt/kta clause-(d) tables (ec7e1a8):** `kt_tables_2026-09-28/ec7e1a8_d_*` and `ec7e1a8_mixed_*`, `kta_tables_2026-09-29/ec7e1a8_fresh_d_*` and `ec7e1a8_fresh_id_*_d_i20`. Not replayed. On the same deals #401 changed 15.7% of km3's and 15.5% of kta3's Rayquaza games, so these would very likely change. Dustin decided on Oct 21 to leave them alone, revisited only if a future decision relies on them.
3. **Scoreboard v3's frozen cells and thresholds, and kta3's status.** `scoreboard_v3_2026-09-27/frozen_cells.csv` (its altaria_greninja v hydreigon cell holds new17 pairing 21, where k3 changes 8 and kp3 7 of 500 games), RUN5's development real error (k3 15.3, kp3 15.5, kog3 14.0), kta3's "adopted, unconfirmed" status and km3's Stadium thresholds (`km_tables_2026-09-30/READING.md`). Dustin decided on Oct 21: no re-baselining; they stay main-c045ede's records, revisited only if a future decision relies on them. The would-be new references are the candidate's 7 game files in `games/new/`; their names keep the `08a9b3a_` prefix of the commands they replay, but the candidate played them.
4. **The ladder predictions** (`rl/results/ladder_validation/predictions/`, 8 files), never overwritten. After the pin `read_ladder.py` prints "NOT the current engine now" for them; new-engine predictions are new files, from new-engine pages and reports. Brews 07 and 09's predictions are built from rows the hit back's change can move.
5. **Exam run 1 and the frozen AI judge** (frozen-4, engine 70652fff; `weekly_review_2026-10-18/RUN1_OUTCOME.md`). A later run on this engine needs a new freeze (frozen-5).
6. **The Oct 12 floor re-check pages** (`floor_recheck_rules2_2026-10/`) and their runners. The final build's pages above are new records beside them, never replacements.
7. **Also on the old engine:** the deck journal's stored "current engine" flags (deck 01's two kx3/km3 entries mean "current when added"); the pg_pos position harnesses and the pause-game position lists (`next_pilot_2026-10/old_positions/`, `pause_games_new_2026-10-12/` and `-13/`; five positions from game 261005_183108000 hold Mega Sableye ex and Poison Barb at the list level); the setup tester's runs (labelled c045ede; probably unaffected, not checked); dated prose naming main-c045ede or `rl/engine-2026-10-12/` (history, left as is). One of those could mislead a reader, `deck_improvement/kingambit_2026-10-15/CHECK.md:359`, which said to use `rl/engine-2026-10-12/deckgym`; this commit points it to the program `current_engine.py` prints.

What carries over unchanged: every replayed row that came out equal.

## Known limits (items 1-3 are deferred to a later round and change no listed deck's games; item 4, the bots' evaluation of a hit back, is an unmeasured limitation)
From an independent read-only review of the hit back's change (no blocking defect found), re-checked against the code of 4d488449 on Oct 21. Line numbers are at 4d488449.
1. **Who caused a Knock Out, when the answer finishes the holder.** The Attacking Pokémon's Rocky Helmet or 20-damage Ability answers the hit back with plain damage (`engine/src/actions/apply_action_helpers.rs`:826-831), and the knockout pass then runs with the attack's reference, as an attack knockout (`attack_outcome.rs`:281 then :292, and the other callers). A holder that survives the attack and is knocked out only by the answer is therefore handled as "Knocked Out by damage from an attack", which the card text of these does not allow:
   - **Iris**: a Haxorus with Rocky Helmet gets Iris's extra point, 2 points instead of 1 (`apply_action_helpers.rs`:976-986). Example: an 80-HP Bristling Spikes Togedemaru takes Frenzied Blade's 70 and is left at 10; its 30 hits Haxorus back; Haxorus's Rocky Helmet answers 20 and knocks it out.
   - **The attacker's Lucky Mittens** draws (`engine/src/hooks/core.rs`:2786-2793), when the answer comes from a 20-damage Ability (Mittens takes the Tool slot Rocky Helmet would need). **Zoroark's Illusive Trickery and Garchomp's Mach Stealth** give their protection for the opponent's next turn when their Rocky Helmet makes the knockout (`core.rs`:2764-2784).
   - **The holder's Lucky Egg** draws to 5 (`core.rs`:2470-2476) and **its Rescue Scarf** returns it to the hand (`apply_action_helpers.rs`:1013-1019).
   - **Its owner's revenge attacks** get their bonus next turn (`apply_action_helpers.rs`:1029-1039: Marshadow, Oricorio, Chi-Yu, Tatsugiri, Bouffalant, Iron Leaves, Furfrou, Toxtricity, Lapras), and a Mega Sableye ex knocked out this way arms **Zarude's Dark Vengeance** +80 (:998-1008).
   - The bots' look-ahead repeats it (`engine/src/players/public_reply.rs`:564-565).
   - Reach: no listed deck shows a visible effect. Only brews 07 and 09 against t-blaziken (its Rocky Helmet answering Mega Sableye ex's Cursed Jewel) can mislabel a knockout, and none of those three lists holds a card that reads the label. Electrical Cord, Offload Pass, the Innards Out family and Hala would follow the same path, but no hit-back holder printed today can carry them into it.
   - The other way round (also deferred, `rules/09`): an Attacking Pokémon that the hit back knocks out gets none of its Lucky Egg or Rescue Scarf, though the Oct 20 ruling makes that knockout attack damage. Whether the holder's Lucky Mittens counts its hit back as an attack "used by" the holder is a rules point the ruling does not settle.
   - Older, not from this change: Electrical Cord on a Lightning Attacking Pokémon moves Energy when the defender's flat Rocky Helmet or Ability knocks it out (`core.rs`:2477-2482).
2. **Also not done for a hit back:** the Attacking Pokémon's coin-flip Abilities (Carefree Steps, Celestial Blessing, Guarded Grill, Securely Sheltered), Guts and Perish Body, Bouncy Body and Dark Pendant; a Benched receiver's Protective Poncho against the holder's Ability return damage (a gap from before). No listed deck reaches them.
3. **The switch:** `DECKGYM_FLAT_RETURN_DAMAGE` or `DECKGYM_ROUND2_OFF` turns all of the hit back's change off (Weakness, cuts, prevention, Disguise and the answer), not only its Weakness as before. Never set in a recorded run.
4. **The bots' evaluation of a hit back: an unmeasured limitation.** `engine/src/players/` is unchanged, so the bots' clock evaluation (`counter_cut` in `engine/src/players/value_functions.rs`, about line 1928: kt's switch 3, which kta and km3 read through kt's clock) still prices a hit back at its printed amount, as plain `get_counterattack_damage`: no Weakness, no cut, no prevention and no answer. Only the one-move look-ahead (`public_reply.rs`:564) plays the hit back out with the engine. The Weakness the engine has given a hit back since Oct 12 is not in that price either. How much this changes the bots' play, and the floor, screen and slow-report numbers in games with a hit-back holder (in the listed decks, Mega Sableye ex in brews 07 and 09; this release adds the gap against t-blaziken's Rocky Helmet and t-vespiquen's Solid Shell), has not been measured.

**To fix after the pin, tests only** (`engine/` stays as built here, tree 46239c19, until then; a later tests-only commit):
- `the_receivers_intimidating_fang_cuts_the_hit_back_before_weakness` (`core.rs`:3832-3839) never involves Weakness (Luxray is weak to Fighting; no hit-back holder is Fighting), so it cannot check the order its name claims: rename it, or give it a test-only receiver weak to the holder's type. It does check that Fang cuts the hit back and that a hit back cut to 0 sets off no Rocky Helmet. The engine's order (Fang, then Weakness) follows `rules/02` but has never been seen in a game.
- The Disguise unit test (`core.rs`:3865-3876) and the end-to-end tests in `engine/tests/rules_repair_hit_back_attack_damage.rs` read the switch's default instead of pinning it with `with_return_weakness`: under either variable the Disguise test and 7 of the 9 end-to-end tests would fail (counted by hand, not run). `weakness_first_then_the_attackers_cut` cannot catch a swapped order (+20 and -20 cancel; the order is checked by the Bounded Field test in `core.rs`), and `the_attackers_own_new_hit_back_does_not_answer` passes with the change on or off. The Oct 12 file `engine/tests/rules_repair_return_damage_weakness.rs` has the same unpinned pattern.
- Add ignored tests that record the known-wrong knockout credit above, so the later fix has a target.

## Checks of the adoption commit (a scratch worktree, before main moved; no engine run)
Run on Oct 21, before main moved, on 98c5d6ce: a build of this commit whose files differ from it only in this section (`git diff 98c5d6ce` against this commit lists only this file). With `release/tools/verify_draft.sh 98c5d6ce <scratch worktree> rl/engine-2026-10-21` (pass the engine folder: the script's default, `rl/engine-2026-10-20`, does not exist); Python tests only, no engine run:
- `cd rl/engine-2026-10-21 && sha256sum -c SHA256SUMS`: three OK lines; the three programs are mode 100755.
- `python3 current_engine.py`: prints the worktree's `rl/engine-2026-10-21/deckgym`, rc 0. The manifest's three sha256 equal `SHA256SUMS`; `historical_releases` ends with main-c045ede; `available_release` is main-4d48844 (source_commit 4d488449).
- `make_predictions.py --selftest`: SELF-TEST PASSED, 136 ok, 0 FAIL. `read_ladder.py --selftest`: SELF-TEST PASSED.
- `test_journal`: 61 tests, 1 failure, `PartB.test_the_first_fill_holds_the_proposals_and_withdrawn_lists` (22 != 12). It fails the same way on main before the adoption (d8e00a66), so it does not come from the adoption.
- `floor_recheck_rules2_2026-10/test_runners`: 55 OK. `panel_ladder_2026-09-26/test_calibration_safety`: 168 OK. CI: `test_run_screen_weights` 21 OK, `test_floor_pricing_pilot` 5 OK, `read_km.py --selftest` and `test_km_thresholds` give their known answers.
- Placeholders: none left.

Separately, in a worktree of the same commit, with KX_RUNS_DIR unset: `rl/strength`'s ten test modules (`/home/dacz8976/slowpin_run_tests.sh` and `test_slow_report_paired`; the slow report reads `rl/strength/README.md`, which this commit changes, and the pin itself is unchanged): all OK.

After the fast-forward, the same checks are run again on main; the results go to the agent mailbox (laptop-018).

## Left as is on purpose
- `engine/UPSTREAM.md` line 9 still says "NOT adopted" and lists upstream #367/#418 as deferred; both are out of date (this engine takes #367/#418). It stays as built (tree 46239c19) until a later commit. RUN5, this file and `rl/engine-2026-10-21/README.md` record the adoption.
- The Oct 20 build's programs (`programs/`), the U and V builds (local refs, not pushed) and the laptop's `pincand_work` stay until the slow report's re-pin is made (after its kx3 replay check passes).
