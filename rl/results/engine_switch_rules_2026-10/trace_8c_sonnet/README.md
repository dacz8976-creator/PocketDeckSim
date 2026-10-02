# Step 8c, the second independent run (Sonnet, on the laptop's cores)

**Result: STOP. 7 of the 3,813 changed games are UNEXPLAINED under the tightened rule** (`UNEXPLAINED.md`). The 63 step-8b rows agree row for row with the cloud's classification (`compare_8b.txt`).

Decision this informs: PLAN.md step 8c (the trace gate before the rules switch). Candidate: R = `f8cfa9c` (engine tree 38af8b0, the candidate 5a18d31's engine); old = main `d363ba8` (engine tree 9c84fef). Input: `handoff_8c.tsv` (blob a76266b, main 78e51e8; 3,750 step-8 rows + 63 step-8b rows, every one `moves_differ = yes`). Run on the laptop's cores after SITTING 2 DONE (02:27:30 UTC), 12 jobs at nice 19, about 35 minutes including the builds.

## Result

| group | step 8 | step 8b | total |
|---|---|---|---|
| on the board (a reach counter fired at a tick at or before k in k's turn, or at the cause tick) | 2,364 | 50 | 2,414 |
| lookahead, both halves hold (code gate + a probe finding it within the bot's 3 plies at tick k) | 1,378 | 13 | 1,391 |
| needs a judgment (queued choice only at the leaf, ply 3, in a mixed frame) | 1 | 0 | 1 |
| **unexplained** | **7** | 0 | **7** |
| all | 3,750 | 63 | 3,813 |

- Kinds of first difference: state 2,406; lookahead 1,405; length (one game a prefix of the other) 2.
- 306 step-8 rows have no reach counter anywhere (handoff_8c.md); none of them is unexplained: 305 are lookahead with both halves, 1 needs a judgment.
- **CONDITION 3** (`full_prevention_only = yes`): 297 rows (296 step 8 + 1 step 8b) = 296 lookahead with both halves + 1 needs a judgment. They are listed one by one, each with its probe result, in `condition3.tsv`. The one needing a judgment is also a CONDITION 3 row (see `judgment.md`).
- Golden probes (on-board games: the probe must find the gate where the counter fired) 0 mismatches; negative controls (unchanged games: the probes must find nothing) 0 failures; every trace's move fingerprint equals the row's old_moves / new_moves (3,813 of 3,813).
- 8b cross-check: `compare_8b.txt`, all 63 games agree with `early_warning_8b/classify_output.txt` at 3a107f4 on tick, kind, turn and verdict.

## The 7 unexplained games (`diag7.txt` has each one's row, first difference, choices and extra tick)

| game | kind | what it is |
|---|---|---|
| k3 p4 i7, km3 p4 i7, km3 p4 i360 (garchomp_meowth v t-sceptile) | lookahead, tick 95 / 84 / 57 | after Land Crush knocks out the active Pokémon, the owner's Promote differs (idx 3 v 2, or 2 v 3); no reach counter at or before k; both probes find nothing at k |
| km3 p1 i399 (garchomp_meowth v t-blaziken) | lookahead, tick 81 | the same Promote difference |
| km3 p21 i310 (hisuian_goodra v t-suicune) | lookahead, tick 87 | the same, after Heavy Impact |
| k3 p31 i81, km3 p31 i12 (houndoom_victini v t-weezing) | length (72 v 73 ticks, 48 v 49) | R's game has one extra tick: the Victory Star offer (KeepAttackCoinResults / RerollAttackCoins) after Grimhound Flare with a Confused attacker; the old game ends on the attack tick. `vs_confused_choice_offered/_chosen` fire exactly at that extra tick. The rule marks every prefix difference UNEXPLAINED (PLAN.md:136), so they stay in the count. |

**Taken apart in `UNEXPLAINED_ANALYSIS.md`.** In short: the five lookahead games and the judgment game (km3 p4 i106) have one cause, shown by experiment: R's search prices a candidate through a queued coin-target damage frame (repair B(a)) that the old engine's plain `ApplyDamage` frame left unpriced at the end of the search, and R with only that queued form reverted for that one decision gives the old engine's scores and choice in all six. `coin_probe` cannot see it (it stops at the turn boundary, and counts free frames as plies). The two prefix games are repair A on the board (the extra tick is the Victory Star offer; the counters fire on it). I have not reclassified any game; the verdicts here are the rule's.

## Method

`classify_8c.py` generalises the cloud's `classify_8b.py` to every pairing of the hand-off. For every row it checks each deck file's git blob id against the row's, traces old and R with `vs_trace` (state hash per tick) in chunks of 20 deals, finds the first differing tick with `tightened_rule.first_difference`, reads the row's exact counters with `tightened_rule.counter_hits` (module from f8cfa9c, the accepted Oct 1 reading), runs `vs_probe` (A) and `coin_probe` (B, test-utils build) at tick k on every lookahead-only game with the row's bot, and runs golden probes and negative controls. `run_8c.sh` does the fresh builds (old d363ba8, R f8cfa9c; sources touched so cargo cannot reuse a stale library; their own target dirs) and then the classifier and `compare_8b.py`.

Programs (sha256, from `builds.txt`; both builds were run twice and came out identical):
- `bin_old_vs_trace` 36e0a9995dbf38a00830241e271a19a0738202ddfd40567dc4f4a2c1420a206e (d363ba8)
- `bin_new_vs_trace` dd53b54e10746545bd25b684bc37bc9a86de71e20994f6a1c5334bcd29a5d418 (f8cfa9c)
- `bin_new_vs_probe` 098091454a1ab20860ebcc5f93f8f3cd2e3c981747628c41dba0a5756a00252b (f8cfa9c)
- `bin_probe_coin_probe` 5fe442a11ec3dee154fd4f8881d371599b315920557713bf226c1f01a685d33b (f8cfa9c)

Inputs (sha256 of the files as extracted, in `builds.txt`): `handoff_8c.tsv` 55bf7e80…4110, `tightened_rule.py` 13c4d7a8…56ca. The 8b rows' own deck lists are `scratch_8b/` on main (a first attempt of this run died because the root lacked them; run_8c.sh now extracts them).

Files: `verdicts.tsv` (one line per game), `report.txt` (one line each, with the probe results), `condition3.tsv`, `judgment.md`, `UNEXPLAINED.md`, `summary.json`, `classify_output.txt`, `compare_8b.txt`, `builds.txt`, `diag7.py` / `diag7.txt` (the 7 in detail), `UNEXPLAINED_ANALYSIS.md` and the score-dump files (`dumps_summary.txt`, `dumps/`, `diag7b.txt`, `diag_prefix.txt`, `dg_patch.py`, `dg_repatch.sh`, `score_dump.rs`, `run_dumps.py`, `diag7b.py`, `diag_prefix.py`, `dump_programs.txt`).

Reproduce: `bash run_8c.sh <work dir> 12` from a checkout that has d363ba8, f8cfa9c and origin/main.
