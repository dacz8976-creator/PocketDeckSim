# The hand-off for step 8c: the changed games of rules switch 2 (steps 7c, 8b, 8 and 9's named rows)

Rebuilt by sitting2.sh (`sitting2_check.py handoff`) at every checkpoint from the per-scan-set rows (`handoff_<set>_<bot>.tsv`); every changed game is a row of `handoff_8c.tsv`. Nothing here is a verdict: 8c decides each row by the rule below (PLAN.md step 8c: (a) coin_probe v2, (b) the classifier, (e) the revert check, then hand traces for whatever the rule can't settle).

**CONDITION 3 (the Oct 1 ruling, carried by Dustin's yes to question 1, PLAN.md section 6's precedents and section 9, question 1: a changed game where only round 2's off-gate counters fired): 111 games (changed, an off-gate counter fired, no reach2 counter); each needs a trace meeting both halves in 8c; a pin-gate item, never a stop here.**

## Totals

Every changed game needs its first difference placed (tick k, its turn, the cause tick), not only the rows with no reach2 counter.

| step | bot | changed games | with different moves | reach | offgate_only (CONDITION 3) | other_only | none |
|---|---|---:|---:|---:|---:|---:|---:|
| 8b | km3 | 45 | 45 | 43 | 2 | 0 | 0 |
| 8b | k3 | 44 | 44 | 43 | 0 | 0 | 1 |
| 9 | km3 | 1044 | 1042 | 935 | 109 | 0 | 0 |

Changed games in which each reach2 counter fired (anywhere in the game; 8c places it against the first difference):

| step | bot | coin_queued_by_attack | coin_plain_damage_by_attack | coin_plain_damage_chosen | perish_plain_hit_offered | perish_plain_hit_chosen | coin_own_side_split | guts_own_side_split | will_confused_attack | will_block_coin_attack | vs_block_coin_built | vs_block_coin_choice_offered | trap_territory_offer_changed | trap_territory_outcome_changed | luxury_coin_opp_stadium | fossil_item_lock | attack_return_weakness |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 8b | km3 | 34 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 6 | 0 | 2 | 0 | 0 | 1 |
| 8b | k3 | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 6 | 2 | 0 | 0 | 0 | 4 |
| 9 | km3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 521 | 763 | 0 | 0 | 0 |

## The engines

- **old**: the official engine, main-8626a35 (`8626a35`; engine/ tree 38af8b0), the pinned programs
  `rl/engine-2026-10-02/` (legality_scan sha256 978912748c83fd6c8ee8e3e966c9a6b95c9fdf1eb9d500c7367b2c1463e71699). Where the old side is reused (step 8's carriers, pairings 0-31, and
  8b's pairings 32-35): Oct 1's recorded new-engine games (`rl/results/engine_switch_rules_2026-10/5a18d31_8_new_*.jsonl`, `5a18d31_8b_new_*.jsonl`;
  `reuse.tsv`), played by that same program on the same seeds (PLAN.md section 3, the real cost). Step 9's old side: km3's B2e reference
  (`km_tables_2026-09-30/1f6319e_b2e_km3.jsonl`), which the first switch's step 9 found equal to this engine's games.
- **new**: the candidate 08a9b3ae607c904e7df9f6e999d3f830eccc930f (main c4f27f2 + P c7a25df; engine/ = P's tree 70652ff), built by sitting 1:
  `programs.sha256` (the plain legality_scan) and `watch.sha256` (the watch build: the Victory Star script and the coin
  script at P, so the counters of `counters.tsv`).

## The tools (`tools_8c.tsv`, each at its own commit, blob-checked by sitting2.sh at its start)

| role | commit:path | blob |
|---|---|---|
| classifier | `486e146f:rl/results/engine_switch_rules2_2026-10/tools_8c/tightened_rule.py` | `6b6a83649f4299af974c1b8a0dc4900b3e27f011` |
| classifier_tests | `486e146f:rl/results/engine_switch_rules2_2026-10/tools_8c/test_tightened_rule.py` | `9f27a30cd80d5f70d140c078961e9d23ac16f2c6` |
| classify_8c | `486e146f:rl/results/engine_switch_rules2_2026-10/tools_8c/classify_8c.py` | `b344367d5f85fa7512274edc7d85d9926c48eff0` |
| coin_lookahead | `486e146f:rl/results/engine_switch_rules2_2026-10/tools_8c/coin_lookahead.py` | `76de39128667a03d72a6a9ca3aa155e3cc175f16` |
| classify_8b | `31380294:rl/results/engine_switch_rules2_2026-10/early_warning_8b/classify_8b.py` | `18a7cc14f846455d832699a93eb3f518b91f9ee8` |
| probe | `31380294:rl/results/round2_readiness_2026-10-02/coin_probe_v2.rs` | `318578349f3e138ccac2e23a32f413d5948ce5ff` |
| tracer | `31380294:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs` | `3fbc20d27e656d7134666bb54d0cbfdc8458fa51` |
| revert_check | `31380294:rl/results/coin_prevention_round2_2026-10-01/revert_switches/run_revert_gates.sh` | `0c7c2b90ed2614d96e92591c4285700de77f324b` |
| revert_score_dump | `31380294:rl/results/coin_prevention_round2_2026-10-01/revert_switches/score_dump_round2.rs` | `b2553655013be462be11de81d87126af6592593d` |
| revert_8c | `486e146f:rl/results/engine_switch_rules2_2026-10/tools_8c/revert_8c.py` | `efe9887443497b1e3d07653d0b73755216c7453d` |
| revert_8c_tests | `486e146f:rl/results/engine_switch_rules2_2026-10/tools_8c/test_revert_8c.py` | `6d18e2fbb3e6dc50e47fbe8e9d92db81f3d8214b` |
| handoff_adapter | `486e146f:rl/results/engine_switch_rules2_2026-10/tools_8c/handoff_for_classify.py` | `cf8dcfb4729210525734ce167de6d7051f8d54ef` |
| handoff_adapter_tests | `486e146f:rl/results/engine_switch_rules2_2026-10/tools_8c/test_handoff_for_classify.py` | `85912c6f43bbfb3c46bc66fdce733971452d9e0f` |

- **Pass each row's own bot** (its `bot` column: km3 or k3). The tracer and the probes default to kog3: a trace
  or probe under the default bot is another game.
- **Each row's deal:** its pairs file and seed block (the table below); seed = block + pairing x 10,000 + i; even i puts
  the held list in seat 0; the same bot in both seats.
- **Check each trace's move fingerprint** against the row's old_moves (the old engine's trace) and new_moves (the
  candidate's) before reading anything else from it: a trace that does not reproduce its game explains nothing.
- **Rows with moves_differ = no** (the games differ only in points, winner or another field, with the same moves): look at
  their state hashes and final boards; a prefix game is judged like any other board difference (PLAN.md section 6, change 2).

## The pairs files and seed blocks

| step | pairings | pairs file | seed block |
|---|---|---|---:|
| 7c | 0-23 (the hand-off holds deck 10 v t-weezing, pairing 7) | `rl/results/engine_switch_rules2_2026-10/pairs_7c2.tsv` | 23,300,000,000 |
| 8b | 32-37 (the cloud's rows; 32-35 Oct 1's scratch rows) | `rl/results/engine_switch_rules2_2026-10/pairs_8b_cloud.tsv` | 23,100,000,000 |
| 8b | 40-46 | `rl/results/engine_switch_rules2_2026-10/pairs_8b2.tsv` | 23,300,000,000 |
| 8 | 0-31 (Oct 1's carriers) | `rl/results/engine_switch_rules_2026-10/pairs_8.tsv` | 23,100,000,000 |
| 8 | 60-62 (the Will rows) | `rl/results/engine_switch_rules2_2026-10/pairs_will.tsv` | 23,300,000,000 |
| 9 | 32-39 and 80-87 (B2e's named rows) | `rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv` | 21,106,000,000 |

## The revert switches (counters.tsv; P's `engine/src/actions/apply_action_helpers.rs`)

Each gate is on by default (the new rule); its environment variable (`=1` or `true`) turns it off for the whole process, and off is the official engine at that gate. A switch set joined by "+" is set together: the seven sites' old damage needs G1 (`DECKGYM_NO_PLAIN_HIT_COIN`) off too (the G2 comment). `DECKGYM_ROUND2_OFF` turns every gate off together. Never set one in a recorded run: sitting2.sh refuses to start while any `DECKGYM_*` variable is set.

| mechanic | reach2 counters | switch |
|---|---|---|
| sites | coin_queued_by_attack | `DECKGYM_PLAIN_QUEUED_SITES+DECKGYM_NO_PLAIN_HIT_COIN` |
| plain_hit | coin_plain_damage_by_attack, coin_plain_damage_chosen | `DECKGYM_NO_PLAIN_HIT_COIN` |
| perish | perish_plain_hit_offered, perish_plain_hit_chosen | `DECKGYM_NO_PERISH_ON_QUEUED_HIT` |
| own_side_coin | coin_own_side_split | `DECKGYM_NO_OWN_SIDE_COIN` |
| own_side_guts | guts_own_side_split | `DECKGYM_NO_OWN_SIDE_GUTS` |
| will | will_confused_attack, will_block_coin_attack | `DECKGYM_WILL_SKIPS_GATE_COINS` |
| vs_block | vs_block_coin_built, vs_block_coin_choice_offered | `DECKGYM_NO_VICTORY_STAR_AFTER_BLOCK_COIN` |
| trap | trap_territory_offer_changed, trap_territory_outcome_changed | `DECKGYM_TRAP_TERRITORY_ONCE` |
| luxury | luxury_coin_opp_stadium | `DECKGYM_LUXURY_COIN_ANY_STADIUM` |
| fossil_lock | fossil_item_lock | `DECKGYM_FOSSIL_UNDER_ITEM_LOCK` |
| return | attack_return_weakness | `DECKGYM_FLAT_RETURN_DAMAGE` |

## The files

The rows: `handoff_8c.tsv` (columns: step, bot, pairing, i, seed, held_file, held_blob, panel_file, panel_blob, old_moves, new_moves, moves_differ, differing_fields, old_winner, new_winner, old_points, new_points, category, reach2_counters, offgate2_counters, round1_counters, superset_counters, revert_switches). reach2_counters, offgate2_counters, round1_counters and superset_counters are compact JSON with every firing tick of each counter that fired (keyed counters as {key: [ticks]}; `coin_queued_by_attack (round-1 keys)` holds the first round's sites); revert_switches names the switches of the fired reach2 counters' gates. The games and references (sha256):

- `engine_switch_rules2_2026-10/08a9b3a_7c2_old_km3.jsonl`: 1440 games, sha256 b42f773628cbfd13759c0bc5ebcfeb7f8350edb3e39ddd8ed78672163b5b2d45
- `engine_switch_rules2_2026-10/08a9b3a_7c2_watch_km3.jsonl`: 1440 games, sha256 22392a271aca15d3af5b7a1cb50ba049dedec80a56ae9a236f164a60dea21406
- `engine_switch_rules2_2026-10/08a9b3a_8b_cloud_old_km3.jsonl`: 80 games, sha256 065b334b47eeb79c0630c6992bc38f78b518f991845ca28b2d15c8c25eea0a78
- `engine_switch_rules2_2026-10/08a9b3a_8b_cloud_new_km3.jsonl`: 240 games, sha256 d2f6a03f18ce2f4ac23cb5d3c3103d56c269355f4cd3ce1ca78e8886463344c5
- `engine_switch_rules2_2026-10/08a9b3a_8b_cloud_watch_km3.jsonl`: 240 games, sha256 3e63f8e9fb8db3980c75fb900ed1cb96bfa57f7d1850d33fbb26c34995acaee6
- `engine_switch_rules2_2026-10/08a9b3a_8b_new2_old_km3.jsonl`: 280 games, sha256 cdb75cc55d3d9a28a0fc6869d3231fc5345d24a6eee7fd64ef0cec26e43ce4f0
- `engine_switch_rules2_2026-10/08a9b3a_8b_new2_new_km3.jsonl`: 280 games, sha256 5b385f8a89eea71cd121a9a870d3fcc6405a04506e09cf22fe20cfda8bcdf629
- `engine_switch_rules2_2026-10/08a9b3a_8b_new2_watch_km3.jsonl`: 280 games, sha256 53f82d2de2e5e30acf3a240c1a32f52874a29b99d7a903aa252510b91b5b74e6
- `engine_switch_rules2_2026-10/08a9b3a_8b_cloud_old_k3.jsonl`: 80 games, sha256 edf02fd5355d8e788c4f2aa1954208be40f3a4dc1397e668625d51b1915b83da
- `engine_switch_rules2_2026-10/08a9b3a_8b_cloud_new_k3.jsonl`: 240 games, sha256 9501a40197b7d673f4fad14c5c67c847eb5b30fc305925a9f2905d52730e1441
- `engine_switch_rules2_2026-10/08a9b3a_8b_cloud_watch_k3.jsonl`: 240 games, sha256 9c4ece33e0326c8d44f77c0e126f508ca7f9e077cc420a9d3d754ad8c809c6eb
- `engine_switch_rules2_2026-10/08a9b3a_8b_new2_old_k3.jsonl`: 280 games, sha256 5644fe9f0274af2f55453855184c5a79ca8f18d4d17a130930e103ee51910396
- `engine_switch_rules2_2026-10/08a9b3a_8b_new2_new_k3.jsonl`: 280 games, sha256 a489361a8697fd805ae49a617b58589ff59c31340d38146cacaf4011e0a52738
- `engine_switch_rules2_2026-10/08a9b3a_8b_new2_watch_k3.jsonl`: 280 games, sha256 2e2ccc8a32bf2bdc9935b7dc42bba7a37cb50b0345efdd97e22e742d2c0b0698
- `engine_switch_rules2_2026-10/08a9b3a_8_new_km3.jsonl`: 16000 games, sha256 22ac692917ecbd0cc0f29b05165cb68a49ea58854d0cd4b05d8a59485f508f71
- `engine_switch_rules2_2026-10/08a9b3a_8_watch_km3.jsonl`: 16000 games, sha256 adbc4df46783418a0fc9bac2942740826952ad059354b42f58cfba61c9f18061
- `engine_switch_rules2_2026-10/08a9b3a_8_will_old_km3.jsonl`: 1500 games, sha256 64ef9e482034118bb1686d2f703de69a5f04078f3a524b50c897380bc7fc33a1
- `engine_switch_rules2_2026-10/08a9b3a_8_will_new_km3.jsonl`: 1500 games, sha256 64ef9e482034118bb1686d2f703de69a5f04078f3a524b50c897380bc7fc33a1
- `engine_switch_rules2_2026-10/08a9b3a_8_will_watch_km3.jsonl`: 1500 games, sha256 887f87d53eb7a8811b808210847f2530517045472a7d29c80f1acd7cee6b28fe
- `engine_switch_rules2_2026-10/08a9b3a_8_new_k3.jsonl`: 8000 games, sha256 64dc6dcc38711279ab5332850d388a0d7840f85e8de1875c99a43bc8b7cc68b3
- `engine_switch_rules2_2026-10/08a9b3a_8_watch_k3.jsonl`: 8000 games, sha256 7ac23c23d5304071548f41f1f30519e4b352347e7398419c482f55b8738d16ac
- `engine_switch_rules2_2026-10/08a9b3a_8_will_old_k3.jsonl`: 750 games, sha256 a6b99d059067906f10b292217abf27ff1dff78875b92bd5140de2895e1363b2d
- `engine_switch_rules2_2026-10/08a9b3a_8_will_new_k3.jsonl`: 750 games, sha256 a6b99d059067906f10b292217abf27ff1dff78875b92bd5140de2895e1363b2d
- `engine_switch_rules2_2026-10/08a9b3a_8_will_watch_k3.jsonl`: 750 games, sha256 0b7f8ca7cb42a5d6d6e9b31fc145a3b599eee9d089b1361277537ef8e6355cf2
- `engine_switch_rules2_2026-10/08a9b3a_cov_b2e_km3.jsonl`: 48000 games, sha256 84247fb4a3a2ed69aa6c9c5622b34b488422d544b7a7b02b704882f70081eca1
- `engine_switch_rules2_2026-10/08a9b3a_9_watch_b2e_km3.jsonl`: 8000 games, sha256 fec6a5b8d43b9bb80a9a4cd6d199e678fd137881059c7d5e80b21d3631ef4905
- `engine_switch_rules_2026-10/5a18d31_8_new_km3.jsonl`: 16000 games, sha256 22ac692917ecbd0cc0f29b05165cb68a49ea58854d0cd4b05d8a59485f508f71
- `engine_switch_rules_2026-10/5a18d31_8_new_k3.jsonl`: 8000 games, sha256 64dc6dcc38711279ab5332850d388a0d7840f85e8de1875c99a43bc8b7cc68b3
- `engine_switch_rules_2026-10/5a18d31_8b_new_km3.jsonl`: 160 games, sha256 bf5405377a887ac9afb379b1a45573647720c07928ea989b1d56698c07577eff
- `engine_switch_rules_2026-10/5a18d31_8b_new_k3.jsonl`: 160 games, sha256 2d4ad0b4fa2d500b3c220c64cdacbfe967259250268da9fbe1721036442b65ec
- `km_tables_2026-09-30/1f6319e_b2e_km3.jsonl`: 48000 games, sha256 fa6fcaf5a4d219a1b4a9ad4ddd4cb0dbb83bc8498481c9ee69390dbfad863b63

## The rule

PLAN.md section 6, the mechanic check: the last plan's mechanic check, with three changes.
1. **The reach counters** are round 2's exact counters (`counters.tsv`, role reach2: 16 counters, section 0 (c)'s
   `attack_return_weakness` included); `coin_queued_by_attack` counts only ROUND2_QUEUED's attacks
   (Double Splash, Double-Punching Family, Litter, Mischievous Ring, Tornado Shot, Triple Bombardment, Wellspring Dance, Wild Swing). The supersets (`trap_territory_two_in_play`, `coin_defender_attack`, `vs_confused_attack`) and round 1's counters
   never count. A changed game is ON THE BOARD only when such a counter fired at or before the first differing tick k, in
   k's turn or at the cause tick; a firing after k, or in an earlier turn other than the cause tick, explains nothing.
2. **A prefix game** (one game longer or shorter than the other) is judged like any other board difference (precondition
   b): an exact counter at the extra tick, or nothing.
3. **IN LOOKAHEAD** (the same state and offered moves, a different choice) needs both halves: the code gate, and coin_probe
   v2 finding the gate's condition inside the bots' search at k; and the revert check: turning that gate off (its switch set
   below, alone: one name, or the names joined by "+" set together, as the seven sites need G1 off too; and
   `DECKGYM_ROUND2_OFF` for every gate together) must bring back the old engine's choice and scores. A game meeting the
   first two but failing the revert check is a stop.
Anything else is UNEXPLAINED: a stop, and it comes to Dustin first. A trace that needs a judgment call doesn't stop the
replays, but the pin waits for Dustin's word on it (PLAN.md section 6). Precedents (game 28, the 8 of `8c_DECISION.md`)
were that switch's own exceptions: a similar game this time is a new judgment call (PLAN.md section 6, precedents).
The categories above are the runner's sorting, not verdicts: reach (a reach2 counter fired somewhere in the game; 8c still
places it against k), offgate_only (CONDITION 3 (the Oct 1 ruling, carried by Dustin's yes to question 1, PLAN.md section 6's precedents and section 9, question 1: a changed game where only round 2's off-gate counters fired)), other_only, none. None of them stopped the runner; 8c decides every row.
