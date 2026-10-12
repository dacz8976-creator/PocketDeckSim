# Switch 2 precondition (b): the sorting scripts' check on step 8b (the cloud, Oct 9)

The switch-2 copies of the sorting scripts sit one folder up: `classify_8c.py` (the hand-off's many pairings) and `coin_lookahead.py`
(one smoke directory). They share `tightened_rule.py` (v3). What changed from the first switch's copies:

- **The shorter game.** When one engine's game ends before the other's, that is now judged like any other board difference. The first
  switch's scripts called it UNEXPLAINED (question 1, approved by Dustin: "1-3 sure").
- **Round 2's counters.** The reach counters are round 2's 16 exact names. coin_queued_by_attack counts only the later round's 8 attacks.
- **The probe.** The scripts read coin_probe v2 with round 2's conditions (precondition (a), RESULT_R2) and refuse output without it.
- **Fixes from the review** (tests first, `../tests_before_review_fixes.log`, 4 failing; `../tests_after_review_fixes.log`, 43 of 43):
  - A cut attack title is now read as the full name (the probe cuts long lines with "...").
  - The golden check is skipped for coin_queued_by_attack when only Mega Kangaskhan ex's Double-Punching Family fired at that tick. The
    engine queues its second punch when any opposing Pokemon has a coin Ability; the probe only when the target has one.
  - The negative controls require no queued choice, cut or return ply (`control_clean`, step 8b's requirement). "Nothing at all found"
    stays only for the probe's retry.
  - CONDITION 3 now means no reach counter fired anywhere in the game, not just before the first difference. On this check, that takes
    it from 18 games to 2: the other 16 had a Wild Swing queued later in the game.
  - A stale UNEXPLAINED.md is removed before each run; a relative `--work` folder works; the turn number is never blank.

## The check (`run_check.sh`, output in `run_check_output.txt`)

Both scripts were run on step 8b's changed games and compared with the verdicts classify_8b.py recorded then:

- classify_8c.py: 25 of 25 verdicts the same (4 ON THE BOARD, 21 LOOKAHEAD ONLY). The strict reading changes none. Golden mismatches 0,
  control failures 0.
- coin_lookahead.py (km3, pairing 35): 11 of 11 the same; its 3 controls are clean.
- None of these games is a shorter-game difference, so that case is covered by the tests only.

"In lookahead" still needs the revert check, precondition (e).
