# The laptop's second read of F1-F7 at R (Sept 30 evening)

**What was read:** R = 1abdbe8 on `sonnet/rules-fixes` (Sonnet, the author of F1-F7), against `PLAN.md`'s F-table.
- **How:** Opus subagents of the laptop session, reading only. Nothing was built, tested or played.
- **Verify pass:** each finding that wasn't a note got an attempt to refute it. One finding was refuted: "no coin probe for 8c" is out of date, because Sonnet's `coin_probe.rs` and `coin_lookahead.py` are on main at d010d2d.
- **Equivalence:** the reading extended to R, and compared row by row with Sonnet's, is `EQUIVALENCE_at_R_opus.md`. Every row holds at R. The two readings agree on every code hunk and differ only on side claims.

## Verdict: no code bug; four things to fix before sitting 1

**Engine side (F1-F4, F7): nothing blocks the build.**
- **F1 is correct.** kd now takes the heads cut off `hit(base)`'s result, after Weakness and the other reductions, as `modify_damage` does, and prices the coin on direct damage.
  - It changes no table game for any pilot. Only `EvalFeatures::KD` reaches `persistent_defender_damage`, and the changed arms need a coin-Ability victim (5 printings, none in any `decks/` list).
  - So kd3's identity gate should replay identically.
- **F2's text is accurate.**
- **F3 and F4 are sound guard tests.** Each would fail if what it guards were removed.
- **The suite at R:** 2,018 passed. That is 2,011 + F3 + F4 + F7's 5 tests.

**Confirmed findings, to fix before sitting 1:**

| # | Finding | Fix | Touches |
|---|---|---|---|
| 1 | **F7's Bastiodon numbers can't show "after Weakness".** Grimhound Flare does 80 per heads plus 20 Weakness against a 100 cut. For k = 1, 2, 3 the old raw cut and the new order both give 0/80/160 on heads, so the three coin tests pass at d4fbc2a too (repair A alone). They prove the defender's coin runs on the Keep/Reroll path, not the order. The two doc comments ("would leave 20", "would be 97.5") misdescribe the old engine. | Give the Keep case a +10 attacker bonus (for example Giovanni). k = 1 then loses 10 after Weakness against 0 with the raw cut. Or use a non-Mega Fire coin attacker under Bounded Field. At least correct the two comments. | `engine/tests/victini_victory_star_test.rs`, so a new R |
| 2 | **`offgate_discard_then_damage` can fire in table games.** EQUIVALENCE_sonnet.md:137 says it needs "cards no list has". But `decks/research/vespiquen.txt` (a table deck) and t-vespiquen hold Vespiquen ex with Basic [G] Bench Pokémon, and Chase Order's discard is chosen hundreds of times per table cell (`chase_order_2026-09-25/kp3_vespiquen.txt`). With no coin Active, the fall-through `ApplyDamage` (apply_attack_action.rs:321-325) comes at the next tick. | Correct the record. Have 7b and 7c require **both** off-gate counters above 0: the vespiquen cells for this one, the helpers for the other. | `EQUIVALENCE_sonnet.md`, `PLAN.md:111`, `sitting1.sh` |
| 3 | **That counter has never fired anywhere.** It read 0 in the coin smoke, and none of `counter_probe`'s cases reaches a `DiscardOwnBenchedThenDamage`. Its detection reads as correct, but step 7b's evidence for the B10 hunk rests on it. | Add `counter_probe` cases before the sitting: Vespiquen ex with a Benched Combee into a non-coin Active (expect 1, at the tick after the discard), and into a Meowth B2 124 Active (expect 0, with `coin_queued_offered` 1). | `smoke/rerun_R/counter_probe.rs` |
| 4 | **Each counter keeps only its first tick,** so "explained on the board" can rest on an early firing that changed nothing. `coin_queued_offered` fired in 13 of the coin smoke's 28 *unchanged* games. Victory Star games 3 and 5 pass on firings at ticks 27 and 22, while the build that changed them was at k−1 (69, 31). In step 8 most carrier games would fire early, so any later difference would pass. | Record every firing tick. Then 8c's `first_diff` requires a firing in the same turn as the first difference (or within the mover's search depth), and sends anything else to a trace. That changes the wording of PLAN.md:127, so it's the coordinator's call. | both `instrument_scan.py`, `first_diff.py`, `PLAN.md:127` |

**Notes (none blocks):**
- **Game 28 of the Victory Star smoke** holds by elimination only. Its one path runs through a Copycat draw, which kog3 samples once per node. Record it as the one candidate judgment call for Dustin, under PLAN.md:135.
- **`coin_queued_offered` isn't exact at the switch-in site** (apply_attack_action.rs:6565-6576). Simpler and exact: every `ApplyQueuedAttackDamage` that isn't AlsoChoiceBenchDamage comes from the coin branch, so drop the id test. That also removes its `COIN_IDS` dependence, which goes stale at B4b.
- **The coin counters miss the Victory Star Keep/Reroll path.** It's conservative and unreachable in the planned pairings. Fix: also match KeepAttackCoinResults and RerollAttackCoins.
- **`offgate_helper_choice` also counts the Chase Order fall-through,** and isn't split per helper or row.
- **The traces' forced-move differences** (n = 1) are labelled "lookahead", when they're board differences. Add a full-state hash per tick.
- **Stale comments:** core.rs:1597-1600 ("the coin flips for every hit") overstates it, since six sites, Wild Swing, the own-Bench form and a copied Chase Order still skip the coin. And core.rs:3176 still says "-100 from the damage before modifiers".

**Effect on the schedule:** finding 1 changes R, which needs a new suite run. Findings 2-4 change the counters and the sitting-1 runner's expectations. Sitting 1 doesn't start tonight. It waits for the new R and the counter fixes, then starts Oct 1 from 5 pm Central.
