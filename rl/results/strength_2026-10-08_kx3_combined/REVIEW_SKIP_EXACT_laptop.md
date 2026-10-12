# The laptop's review of the exact attack-skip measure (Oct 12)

A reader workflow on Oct 12 (4 reviewers, each major finding checked by an adversarial verifier; scripts in the laptop's scratch,
`/home/dacz8976/review_skip/scratch_*`) read `SKIP_ATTACK_EXACT.md` and `skip_exact/` as committed at e32ebe66. In short: the
numbers are right, the replay is sound with one undisclosed weakness, and the measure is not the one the pre-registration
promised, so it cannot say whether the candidate leaves km3's attack more often, or whether the skip bar `_zs3` works.

## What holds

- **Every number reproduces.** Each turn-level and decision-level cell of `exact_summary.txt` and `SKIP_ATTACK_EXACT.md` was
  recomputed from `decisions_*.jsonl` with independent code. That covers 101 / 73 / 43 skip turns of 2,034 / 1,981 / 1,892
  attack-chance turns, and candidate − frozen +1.3 ± 1.1, with every group and deck row. A 2,000-resample bootstrap over keys agrees:
  [+0.2, +2.4].
- **The replay matches the logs.** In all 560 games of each bot, every decision's move, turn and legal-move count equals the log.
  None was skipped, every ending matches, the programs and engine trees are right, and the frozen games are the development run's.
  The bots' search randomness is kept apart from deals and coin flips (game.rs:209-232 at 172cbe9c).

## What is weaker than the write-up says

- **About 23% of games were matched by trial.** A move label sometimes fits more than one legal move: DiscardOwnCards after
  Supernatural Feather (deck 10), ApplyDamage after Tongue Whip (deck 06), DiscardToolFromPokemon after Field Blower, and
  MoveRandomOpponentEnergyToActive after Psychic.
  - The replay then tries options and accepts the first path that fits the log: ambiguous in 130 / 134 / 131 games, retried in
    68 / 71 / 75, up to 59 attempts. Deck 10 is ambiguous in 65 of 80 games for every bot.
  - Checked against the active Pokémon and bench counts the log records, no mismatch was found after such choices. But
    identity there is shown to fit the log, not proven.
  - The headline is fragile to it. Candidate − frozen is:
    - +1.3 ± 1.1 on all games;
    - +0.8 ± 1.2 without the ambiguous keys;
    - +0.7 ± 1.1 without the retried keys;
    - +1.0 ± 1.1 when each game is cut at its first ambiguous choice.

    Deck 10's +3.0 ± 2.7 becomes −0.1 ± 3.8 under that cut.
- **The check could be stricter at no cost.** It compares labels, turns and legal-move counts, and the ending. It does not compare
  the points, active Pokémon and bench size logged at each decision, or each game's plies and the opponent's decision count. The
  negative control covers one kind of change, on one arm, all on deck 09, and missed 2 of 20.
- **The pre-registered "win rate of games with v without" is not reported.** It is: candidate 59.0% v 61.8% (score −2.9 ± 11.5),
  frozen 59.7% v 57.0%, km3 23.8% v 42.1% (−18.6 ± 13.7).

## The definition

The pre-registration (PREREGISTRATION.md:7) counts a turn where **km3 proposed an attack**, kx3 played something else, and no attack
followed. This measure counts any turn with a legal attack and none made. Since an attack ends the turn, the pre-registered turns are a
strict subset.
- The frozen arm's pre-registered count exists: the development run's scan, `rl/results/playout_attack_skip_2026-10-07/` on
  claude/playout-pilot, 1,902 records joining all of decisions_frozen. It is **8 turns**, against this measure's 73.
- km3's pre-registered count is 0 by construction, against 43 here.
- The candidate's was never produced. Its logs place it between 3 and 96.

So the candidate's +28 turns cannot be attributed to leaving km3's attack. They mix three things: km3's own skips (9 candidate turns
are identical to km3's game), turns after the game left km3's, and setup changes that led to no attack. The pre-registered measure for
the candidate is `trainer_habits scripted --attack-scan` on the 172cbe9c build over the candidate's 560 games, or km3's proposal at each
decision from the same replay (asked of the cloud on Oct 12).

## Skips and winning (by game and paired)

- For both kx3 versions, skipping goes with neither winning nor losing. The candidate has 0.180 skip turns per game in wins and
  0.181 in losses. For km3, skipping goes with losing.
- Paired with the frozen kx3: on the 57 keys where the candidate skipped more, it scored +14.0 ± 12.4 better. Dropping every key
  where the candidate skipped leaves +3.1 ± 3.1 of the +3.9.
- By group, candidate − frozen in skip share: fast +2.0 ± 1.5, setup +1.6 ± 1.9, middle −1.2 ± 1.9.

## The skip bar `_zs3`

It acts only where km3's move is an attack, so this measure cannot test it. The bar's whole target in the frozen games is 8 of 1,981
turns, about 0.4 points against ±1.1.
- The best available evidence is the 615 km3 attack proposals at positions both kx3 versions reached identically. At 3 of them the
  candidate passed up the attack for the whole turn where the frozen kx3 attacked; the reverse happened at 0 (p = 0.25).
- On km3's own path the candidate left km3's attack for the whole turn at 4 of 501 proposals, the frozen kx3 at 6 of 943.
- That fits the close-calls finding that with `_m64` the bar keeps km3's attack at only 2 of 9 such skips: a lasting play-out
  preference clears 3 standard errors once there are 64 rounds.
- No sign, then, that the bar works in the combined code. The pre-registered scan would settle it.

## For the hand check

There are 13 candidate skip turns at a position identical to the frozen kx3's game (same deal, same logged moves up to the turn),
where the frozen kx3 attacked and the candidate did not, in games the candidate won (5 of them games the frozen kx3 lost):
03 v Blaziken 3|1 t8; 06 v Altaria 4|0 t5 and 4|1 t2; 06 v Blaziken 0|0 t3; 06 v Hydreigon 1|1 t2; 06 v Lucario 4|0 t4;
09 v Altaria 0|0 t3 and 1|0 t4; 10 v Altaria 1|0 t7; 10 v Vespiquen 1|1 t4 and 4|0 t6; draft A v Blaziken 0|0 t6; draft A v Lucario
3|0 t2. Judging them needs the board at each decision (asked of the cloud as skip_boards.jsonl).
