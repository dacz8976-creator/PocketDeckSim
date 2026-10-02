# Step 8c: the revert check over every lookahead-kind game (Sonnet, Oct 1)

Decision this informs: whether the one switch found in `UNEXPLAINED_ANALYSIS.md` (the queued coin-target damage form, repair B(a)) is what decides **every** lookahead difference of step 8c, or whether other mechanisms hide in the 1,391 "lookahead, both halves hold" games. Verdicts in `verdicts.tsv` are unchanged.

## Result

**All 1,395 lookahead-kind games that have a repair B card in play reproduce the old engine on R-revert, at the first differing tick: the same chosen move and the same score for every candidate. None fails.** The other 10 lookahead-kind games are repair A (Victory Star) games, where R-revert is not the right switch and does not reproduce, as expected.

| group | games | R-revert reproduces the old choice | and every candidate's old score |
|---|---|---|---|
| all lookahead-kind games | 1,405 (1,391 step 8 + 14 step 8b) | 1,395 | 1,395 |
| a coin-Ability Pokémon on the board at the first differing tick (repair B in play) | **1,395** | **1,395** | **1,395** |
| no coin-Ability Pokémon on the board (the repair A games) | 10 | 0 (expected) | 0 |

- The 1,395 by verdict: 1,382 "lookahead, both halves hold"; 7 "on the board" (counter `coin_cut_recorded` at or before k); 5 UNEXPLAINED; 1 NEEDS A JUDGMENT. By step: 1,387 step 8, 8 step 8b. By bot: km3 906, k3 489.
- In **1,126** of the 1,395, the instrumented search also entered a pure queued attack-damage frame at a coin-Ability target (`PGGATE`); the old engine entered none (0 of 1,395). The other **269** reproduce on R-revert without a pure frame in R's search; for these the same switch acts through a mixed frame (the queued choice applied as a ply, as in the judgment game km3 p4 i106). I did not break the 269 down further.
- Every one of the 1,405 replays reproduces the first difference: the old program's choice at tick k differs from R's (1,405 of 1,405). So the instrumented programs follow the same games as the traces, and the check is on the first differing decision of each game, not a stand-in.
- The 10 repair A games (no coin-Ability Pokémon on the board; Victini / Houndoom decks, pairings 31 and 32): step 8 k3 p31 i121; km3 p31 i121, i379, i459; step 8b k3 p32 i6, i38; km3 p32 i6 (tick 28, on the board by `vs_confusion_first_built`), i12, i26, i38. Nine are "lookahead, both halves hold" through `vs_probe` finding the Confusion-first branch inside the search at tick k (built 0, 1 or 2); the tenth is on the board by that counter. Old and R choose different moves there (old: Evolve, Attach, Poké Ball, Sabrina, Copycat, Retreat...; R: Place Victini, Hiking Trail, UseStadium, Attack...); both choices for each are in `rc_aonly.txt`. A revert for repair A was not asked for and was not built.

## The finite-cut cases: R-revert is the right and sufficient revert

Repair B(a) has two parts that reach the bot: (1) the queued coin-target form (`queued_attack_damage_choice`, a snipe or switched-in target now queued as `ApplyQueuedAttackDamage`) and (2) the finite cut (Guarded Grill -100, Securely Sheltered -80) coming off after Weakness instead of before the modifiers (`split_with_damage_prevention`, `heads_coin_cuts`, `modify_damage` step 4). R-revert is (1) only. To see whether (2) is needed, I built VAR2: R with (2) also switchable back to the old order (`PG_CUT_BEFORE`: the cut comes off the raw damage as in d363ba8), and ran every lookahead-kind game whose decks hold Bastiodon (A2 114) or Hisuian Goodra (B3b 050):

| revert at the first differing decision | games reproduced (choice and every candidate score) |
|---|---|
| (1) queued form only (= R-revert) | **323 of 323** |
| (2) cut order only | 0 of 323 |
| (1) + (2) | 323 of 323 |

- 323 games (k3 pairings 17, 19, 20, 21, 22 and km3 17, 19, 20, 21, 22), a finite-cut Pokémon on the board at k in all 323; by verdict 315 "lookahead, both halves hold", 7 "on the board", 1 UNEXPLAINED (km3 p21 i310).
- No game needs the second revert: none where (1) fails and (1) + (2) reproduces. The cut-after-Weakness order never decides a first differing choice in this set; (1) alone does.

## What this does and does not show

- **Shows:** at the first differing tick of every lookahead-kind game with a repair B card in play, the queued coin-target form is sufficient for the difference: switch only that form back, for that one decision, and the old engine's choice and scores return. The 5 unexplained and the judgment game are not special: they are 6 of 1,395 with one cause.
- **Does not show:** that `coin_probe` finds the gate (it cannot, for decisions on the opponent's turn; see `UNEXPLAINED_ANALYSIS.md`); anything about later ticks of a game, or the games whose first difference is a state or length difference; the repair A games (10 here), which would need their own revert.
- "Repair B in play" is the check's own definition: a coin-Ability Pokémon (A2 114, B3b 050, A4 080, B2 124, B2 204) in play on either side at tick k. All 1,395 meet it; the other 10 are the repair A games.
- The revert applies to one decision only: the game is replayed with R as it is up to tick k (the states are identical to old's there), and the environment variable is set for that decision's search; what the search forecasts through `queued_attack_damage_choice` then takes the old form. Print-only patches and the switches are in scratch copies; nothing in `engine/` changed.

## Files and programs

`revert_check.tsv` (one line per game: the three choices, reproduced, scores equal, gate counts, coin Pokémon on the board), `revert_check_cut.tsv` (the 323), `rc_analysis1.txt`, `rc_analysis_cut.txt`, `rc_aonly.txt`; scripts `revert_check.py`, `rc_cut.py`, `rc_analyze.py`, `rc_cut_analyze.py`, `rc_aonly.py`, `dg_var2.py`, `dg_var2.sh`, `dg_patch.py`, `dg_repatch.sh`, `score_dump.rs`; programs' sha256 in `revert_check_programs.txt` (`score_dump_old` 138af2cc…b33e from d363ba8, `score_dump_new` f449c813…d982 and `score_dump_var` bfba23bf…7f3c from f8cfa9c, `score_dump_var2` aceb1bee…2c4d = VAR plus the cut-order switch). The earlier six-game dumps used earlier builds of the same patch (hashes in `dump_programs.txt`).
