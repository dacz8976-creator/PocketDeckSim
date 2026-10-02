# Step 8c: Dustin's decision on the 8 games the rule could not settle (Oct 2, 2026)

## The result the decision is about

Sonnet traced every changed game of steps 8 and 8b: 3,813 games (sonnet/trace-8c, result 37b49dd, then 2e581c1 and afeb9c1; on main as `trace_8c_sonnet/`). By `tightened_rule.py` (PLAN.md "The mechanic check"):

| verdict | games |
|---|---:|
| on the board | 2,414 |
| lookahead only, both halves hold | 1,391 |
| needs a judgment | 1 |
| UNEXPLAINED | 7 |

- There were 0 golden mismatches, 0 negative-control failures and 0 trace fingerprint problems.
- The 63 8b rows agree row for row with the cloud's classification (3a107f4).
- CONDITION 3 has 297 rows: 296 lookahead with both halves, and 1 needing a judgment.

## The 8, and what explains each

1. **The two prefix games: repair A on the board.** In k3 p31 i81 and km3 p31 i12 (houndoom_victini v t-weezing), R's game has one more tick than the old one. That tick is the Victory Star offer {KeepAttackCoinResults, RerollAttackCoins} to the Confused Mega Houndoom ex, right after Grimhound Flare's coins.
   - The exact counters fire at exactly that tick. In i81, `vs_confused_choice_offered` and `_chosen` are at [72] and `vs_confusion_first_built` at [61,71]. In i12 they are at [48], [48] and [47].
   - The old game ends on the attack tick before it. R keeps the coins and ends with the same winner and points.
   - By PLAN.md's text these are on the board. Only the script's stricter reading (PLAN.md:136: "A prefix difference ... is always UNEXPLAINED") flags them.
2. **The six others: repair B in lookahead.** These are the five promote games (k3 p4 i7, km3 p1 i399, km3 p4 i7, km3 p4 i360, km3 p21 i310) and the judgment game km3 p4 i106.
   - B's queued coin-target frame becomes a "pure" frame when every target has a coin Ability (Meowth's Carefree Steps, Hisuian Goodra's Securely Sheltered). k3/km3 resolve a pure frame without spending a ply, so the snipe and its coin are priced at ply 3 inside the search. The old plain ApplyDamage frame at depth 0 was not priced.
   - The probe stopped at the turn boundary and counted free steps as plies, so it couldn't see this (`8c_FIVE_LOOKAHEAD_opus.md`).
   - Check (b): reverting `queued_attack_damage_choice` to ApplyDamage for that one decision reproduces the old engine's scores for every candidate, and its choice, in all six.
   - Sonnet's revert check over all 1,405 lookahead-kind games: the 1,395 with a coin-Ability Pokémon reproduce the old choice and scores, with 0 failures. The 10 without one are repair A (`trace_8c_sonnet/REVERT_CHECK.md`).

## The question and his answer

**Asked in the laptop session, Oct 2, about 1:30 am Central** (verbatim):

> "The trace check flagged 8 changed games that the repaired rules didn't obviously explain. All 8 have now been traced to the repairs. In 2, the extra move at the very end is the Victory Star offer, and the game ends the same. In 6, the bot's search now counts a snipe into Meowth or Hisuian Goodra, coin flip included, which it didn't before. Undoing just that one change brings back the old choice in all 6. Accept these 8 as explained and pin the rules switch tonight?"

The options were "Accept all 8 and pin (Recommended)", "Accept, but re-check first" and "Hold the switch".

**His answer** (verbatim, his chosen option): "Accept all 8 and pin (Recommended)".

**So:** the 8 count as explained, the 2 by repair A on the board and the 6 by repair B in lookahead. With them, every one of the 3,813 changed games is accounted for, and all 297 CONDITION 3 games are traced. `8c_RESULT.txt` records this as the pin's gate. The rule's verdicts stand as produced (unexplained 7, judgment 1), the 8 are listed as his accepted exceptions, and nothing is left unaccounted. Victory Star smoke game 28 stays the switch's one other documented judgment exception (his word of Oct 1 evening, README).

## The coordinator's audit (Oct 2, relayed; the gates and the wording)

**Part 1 of 2 (verbatim):**

> "(2) REVERT_CHECK.md (sonnet/trace-8c afeb9c1): R-revert reproduces the old choice and every candidate's old score in 1,395 of 1,395 lookahead-kind games with a repair B card on the board, zero failures; the 10 repair A lookahead games are 9 by vs_probe + 1 on the board; VAR2 shows the queued form alone suffices in all 323 finite-cut games. (3) The cloud's independent 8c (abb49cf, trace_8c_cloud/) classified all 3,813: the same 5 unexplained games, 1 needing a judgment, and the 2 LENGTH games explained by hand as repair A on the board; no contradiction with Sonnet's. So gates 2 and 3 are met."

**Part 2 of 2:**

> "GO, with one required wording fix. All three gates are met: (1) Dustin's "Accept all 8 and pin (Recommended)", (2) the revert check 1,395 of 1,395, (3) the cloud's independent 8c agreeing game for game."

The wording it required is the line `8c_RESULT.txt` now carries.
