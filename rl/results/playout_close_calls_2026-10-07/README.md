# Close calls: more play-outs where the best moves are within the noise (the cloud, Oct 7)

Set by the Fable coordinator via Dustin, Oct 7.
- **Why.** At quiz 4's Q11, kx3 had the right move among its candidates and picked an equal one at R = 16.
- **The ask.** When the best candidates are within the z bar after R rounds, continue in blocks of 16 up to R_max (a
  parameter, e.g. 64), for those candidates only, with the same common random numbers extended, and decide at the end.
  Trace the rounds used. Report the time cost on the development positions and the 8 continuation positions, and how
  many decisions change against R = 16.
- **Where it lives.** Branch `claude/playout-pilot`, nothing merged.
- **What doesn't change.** km3, `mod.rs`, the official engine, and kx3's default play (the parameter is off unless the
  code names it).
- **No table games.**

## The fix round: combined with the skip bar (Oct 7, evening)

Set by Fable via Dustin, Oct 7. The skip bar (`_zs3`) and close calls (`_m<R_max>`) were accepted on their own. The
laptop's review of 7d3639d0 found a gap in how they combine (no high defect; nothing run):
- **Closeness was tested at z = 2**, but with `_zs3` the switch away from km3's attack is decided at 3. A lead of 2 to 3
  standard errors over km3's attack never triggered an extension, and whether a kept skip got more rounds depended on an
  unrelated third candidate being close.
- **The extension stopped at the first block where the best cleared z:** up to 4 looks at 2 standard errors, with no
  adjustment. The brief had said "decide at the end".

The ask: fix both, (c) optionally skip a candidate equal to km3's move in every round, add a combination test for
`_tools _zs3 _m64`, self-check digests for the exact combined code, re-run the 26-case skip scan with it, and note that
the `_tools` tie-break can play a placement the extension dropped. Branch `claude/playout-pilot`; km3 untouched.

**The addendum (Fable via Dustin, Oct 7, later): drop (c).** Astra's point: rare draws or events can separate tied
candidates later, so a tie through 16 rounds is not proof a move can't win. (c) had been built (ec283c53), so it is
removed (76cd08f4), with a test that a move tied with km3's through the first 16 rounds is still extended and can win
at R_max. (a), (b) and the rest stand.

**The second addendum (Fable via Dustin, Oct 7, on the equal-exclusion):** don't simply delete the first version's rule
that a move equal to the best in every round is no close call. Deleting it would extend every candidate at decisions
that are already settled (every candidate won, or lost, every play-out), adding time for nothing. Instead, a move tied
with the best in every round joins an extension already running for a non-tied close move; ties alone never start one.
That covers a move tied with km3's move when km3's is the best, and one tied with a best that is another move. Built in
4e7d8ce5, tests first (6b5b713d).

**The fix round accepted (Fable via Dustin, Oct 7):** 54209409 is accepted, (c)'s removal and its test included. The
skip-bar finding (km3's attack kept at 7 of 9 true skips alone, 2 of 9 under `_m64`) is accepted as a finding, with
nothing to build. The same message dropped the equal-exclusion outright. It arrived after the second addendum, which
answers it, so the addendum's version stands: ties join, never start. It also asked for a test that a move tied with
the best through 16 rounds is extended and can overtake at R_max. Gate 2 gave one: dev04 as stored, where Psychic
does. Everything below is at 4e7d8ce5 unless it says otherwise.

### In short

- **Fixed: tests first c0a36092, code ec283c53; (c) dropped: tests ce1a0b13, code 76cd08f4; ties join: tests 6b5b713d,
  code 4e7d8ce5.**
  - (a) km3's move is close to a best that is another move when the best's lead is within the bar the decision will
    use: z_skip for a switch from km3's attack to a line that skips it.
  - (b) Every extended candidate plays to R_max, and the decision is made once, at the end.
  - (c) was built and then dropped: a move tied with km3's in every round so far is extended like any other.
    - At the continuation position B-210952-t16, the turn's Water to the Active ties km3's move in all 16 rounds. Over
      64 rounds it leads km3's move by +0.125 (3.0 standard errors) and is played.
    - With (c) it wasn't extended, and Binding Snow was played instead.
  - Ties with the best join a running extension but never start one.
    - At B-214254-t10 km3's Irida is the best after 16 rounds and the Lucky Ice Pop ties it round for round. 7 other
      candidates are extended for moves within the noise, and the Lucky Ice Pop now joins them.
    - At dev04's Tool placement, the Poncho on Bench spot 3 ties km3's Poncho on the Active. It joins, and over 64
      rounds km3's Poncho leads it by +0.062 (2.0 standard errors), so the Tool tie-break no longer plays it.
    - At dev04 as stored, km3's Poncho play is the best after 16 rounds and Psychic ties it round for round. Psychic
      joins, overtakes it over 64 rounds (0.641 against 0.578) and is played.
    - A settled decision, where every candidate won (or lost) every play-out, starts no extension.
- **The combined code undoes most of the skip bar.** At the 26 development-run cases,
  `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64`:
  - **keeps km3's attack at 2 of the 9 true skips.** The skip bar alone kept 7. At 5 of those 7, 64 rounds put the
    skip's lead at 3.2 to 6.2 standard errors, past the bar of 3, so the skip is played.
  - **touches 6 of the 15 moves before an attack** (those that reproduce): 4 go back to km3's attack and 2 to another
    move. The skip bar alone touched none.
  - **Why:** the bar is a number of standard errors, so it measures confidence, not size. With 4 times the rounds the
    standard error halves, and a lead that holds clears it. In km3's play-outs the skip lines keep their lead.
  - **Q12** (Supernatural Feather) is one of the 2 still kept: over 64 rounds End Turn leads by only +0.094 (1.1
    standard errors).
- **Gate 2** (the 20 positions, 64 decisions, `_tools_zs3` with and without `_m64`):
  - 37 decisions extended, all to 64 rounds, and 9 choices change.
  - Time x2.6: 636 s to 1,676 s. The container has run faster since its restart in the night, so compare the ratios,
    not the seconds, with earlier runs.
  - Dropping (c) changed one choice: B-210952-t16 now plays the Water to the Active, the addendum's test case.
  - Ties joining changed two: dev04 as stored (Psychic) and dev04's Tool placement (km3's Poncho kept).
  - The first version, on the same decisions without `_tools_zs3`, extended 38 and changed 8.
- **Gate 1 passed** at 4e7d8ce5: suite 2,094/0, km3 unchanged, and the self-checks unchanged with the parameters off.
- **Digests for the combined code:**
  - in the `_lab` form, `kx3_r2_c3_lab_tools_zs3_m64`: **8c1244aec5c8419d** (2 games). It was 2284c591ed14a534 before
    ties joined. At R = 2 a tie with the best is common, so the extensions grow and the games change.
  - the exact code, `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64`, 12 games as the laptop's pre-registration runs
    it: **724e581a9c51711f** (9-3, 132 turns, 3 h 44 min on 4 cores, at 4e7d8ce5). The laptop's pre-registration
    (`rl/results/strength_2026-10-08_kx3_combined` on main, built from 172cbe9c, the same code) printed the same
    digest, and the same `_lab` digest 8c1244aec5c8419d.
- **The Tool tie-break** comes after the extension's decision and looks at every candidate, so it can play a placement
  the extension left at 16 rounds. At gate 2 that happened at 1 of its 19 tie-breaks (dev06's Heavy Helmet), where it
  changed the choice.
- **The skip-bar finding is accepted as a finding (Fable, Oct 7); nothing is built for it.** With `_m64` on, the skip
  bar (a number of standard errors) protects km3's attack only where the skip's lead is small.

### What changed (ec283c53; 76cd08f4 for (c); 4e7d8ce5 for ties)

- **`close_call`** (`engine/src/players/playout_player.rs`, now public) after the R rounds, with the best the candidate
  with the highest mean:
  - **km3's move** is close when the best is another move and its lead is within the bar the decision will use for that
    switch (`decision_bar`: z_skip from km3's attack to a line that skips it in more than half of its play-outs,
    z_attack with `_za`, else z). Nothing else needs to be close.
  - **Any other move** is close when the best leads it by no more than z standard errors (paired), unless the two are
    equal in every round. That part is as before.
  - **A move tied with the best in every round** (km3's move when it is the best, or a best that is another move)
    isn't close, so it can't start an extension. But when a move within the noise starts one, it joins (4e7d8ce5). A
    settled decision, where every candidate won or lost every play-out, is not extended.
  - **A move tied with km3's in every round** is treated like any other (76cd08f4). ec283c53 had left it out; the
    addendum dropped that.
    - When the best is another move, the tied move is exactly as close to it as km3's move, at z. So it is extended
      whenever km3's move is close at z.
    - In the skip bar's gap (a lead of 2 to 3 standard errors to a line that skips km3's attack), km3's attack is close
      at z_skip but a move tied with it is not, since it is held to z like any other move.
    - When km3's move is itself the best, a move tied with it is tied with the best, and joins as above.
- **The extension.** If anything is close, the best, the moves close to it, the moves tied with the best and km3's
  move play rounds R to R_max in one pass. There are no blocks, no re-checks and nobody is dropped. The rounds come from the same worlds and seeds a
  larger R would use. The others keep their R rounds.
- **The decision** is made once, at the end, among the extended candidates on their R_max rounds, with the same bar as
  before. The reason still ends with "close call: play-outs extended from 16 to 64 rounds for n candidates".
- **R_max** needn't be R plus a whole number of blocks any more.
- With the parameters off nothing changes.

### Tests (`engine/tests/playout_close_calls_test.rs`)

Written first; `combined/tests_before.log` shows them against the code before the fix. There, `close_call` couldn't
be called from a test, and 3 of the other 5 failed:
- (c), since dropped, at seed 20,000,000,240: a move equal to km3's was extended;
- (b) at the same seed: a candidate stopped at 36 of 40 rounds;
- the combination at seed 20,000,000,301: the extension stopped at 40 of 64.

The tests:
- **`close_call` on given rounds:**
  - End Turn leading km3's attack by 2.65 standard errors, in a line that never attacks, is a close call with `_zs3`
    (and with `_za3`), and clear at z.
  - It is also clear when the same lead is a line that attacks later in the turn, or past the skip bar (3.4).
  - A third move doesn't change that.
  - A move tied with km3's in every round is extended, as close to the best as km3's move is (after the addendum; it
    first said the opposite).
  - A move tied with the best, another move or km3's own, joins when a non-tied move within the noise starts the
    extension. A tie alone starts none, and settled decisions (all won, all lost) aren't extended. This rewrites the
    first version's "equal to the best: no close call" check.
- **A move tied with km3's through 16 rounds is extended and can win** (the addendum's test): at B-210952-t16 with
  `_tools _zs3` (LAB, cap 12, z 2, the position's seed 24,200,001,005), the turn's Water to the Active is played at
  R_max 64.
- **A move tied with the best through 16 rounds can overtake at R_max** (the acceptance message's test; the rule was
  already built, so this test came after the change; its "before" is gate 2's data at 76cd08f4): dev04 as stored, seed
  24,200,002,004, `_tools _zs3 _m64`. km3's Poncho play is the best after 16 rounds and Psychic ties it round for round.
  Psychic plays 64 rounds, scores more than the Poncho and is played. At 76cd08f4 it kept its 16 rounds and the Poncho
  was played.
- **A move tied with km3's best move joins the extension** (the second addendum's test, `_tools _zs3 _m64`, LAB, cap
  12, z 2):
  - B-214254-t10, seed 24,200,001,001: the Lucky Ice Pop ties km3's Irida;
  - dev04 at its Tool placement, seed 24,200,002,004: the Poncho on Bench spot 3 ties km3's Poncho on the Active.
  - In both, km3's move is the best after 16 rounds, a move that isn't tied is extended, and the tied move plays all
    64 rounds. Where the Tool tie-break plays the placement, it is on 64 rounds.
- **R = 4, R_max = 40:** every candidate plays 4 or 40 rounds, and the decision is the rule on the 40.
- **`_tools _zs3 _m64` together, at km3's attacks** (test decks, R = 8):
  - Seeds 20,000,000,301 and 324 are the review's gap: the best skips km3's attack with a lead of 2.05 standard errors.
    Both are now extended.
  - Every extended candidate plays the same 64 worlds as a plain 64-round run.
  - The decision is the skip bar's on those rounds.
  - The code `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` spells all three.
- **The same at a Tool placement** (deck 05's Protective Poncho): the Tool tie-break comes after the extension's
  decision.
- The earlier R4/R_max 20 test, and the combination test, check that a move tied with km3's is extended whenever km3's
  move is close at z, or is the best and an extension runs.
- `combined/tests_before_drop_c.log`: the first addendum's tests against ec283c53, where 4 of 8 fail, each on a tied
  move left unextended.
- `combined/tests_before_equal_join.log`: the second addendum's tests against 76cd08f4, where 3 of 10 fail, each on a
  tie left out of a running extension.

### The 26 development-run cases (`combined/combined_scan.*`)

**How.** The skip bar's scan again (`trainer_habits scripted --attack-scan`): the development run's 560 kx3 games are
replayed exactly, and at the 26 decisions where kx3 left an attack km3 proposed, kx3 decides again from the game's own
observation and randomness. This time it uses the combined code, and `_tools_zs3` without the extension to tell the
two apart.

| | the 9 true skips: km3's attack kept | the 17 moves before an attack: touched |
|---|---|---|
| `_zs3` (the skip bar's scan) | 7 | 0 of the 15 that reproduce |
| `_tools_zs3` | 7 | 1 (06 v Lucario's Copycat goes back to km3's attack) |
| **`_tools_zs3_m64`** (the combined code) | **2** | **6**: 4 back to km3's attack, 2 to another move |

- **"Touched"** means kx3 plays something other than the game's move. The 2 that don't reproduce play km3's attack
  under every code, including the game's own.
- **Extended to 64 rounds:** 18 of the 26 (8 of the 9 true skips, 10 of the 17).
- **Time:** 2,120 s for the 26 decisions at 76cd08f4, against 723 s without the extension (x2.9). At 4e7d8ce5 it was
  1,207 s, but on the container after its restart, which runs faster: the `kx3_r2_c3_lab` self-check took 96 s, against
  146 to 151 s before.
- **Ties joining (4e7d8ce5) changed none of the 26 choices, and no decision's extension.**
- **Dropping (c) changed none of the 26 choices.** One decision (06 v Altaria, t7) now extends 6 candidates instead of
  3. With (c), the time was 1,828 s.

**The 9 true skips with the combined code:**

| case | km3's attack | the skip | after 16 rounds (`_tools_zs3`) | after 64 rounds |
|---|---|---|---|---|
| 01 v Hydreigon, t9 (Copycat first) | Giga Turbo | Copycat, then End Turn | Copycat stands (its line attacks) | **End Turn now**, +0.312 at 4.5 SE |
| 01 v Hydreigon, t9 (End Turn) | Giga Turbo | End Turn | kept (3.0 SE) | End Turn stands, 3.8 SE |
| 03 v Vespiquen, t8 | Wondrous Waves | Retreat:3 | kept (2.7) | Retreat stands, 4.6 |
| 05 v Lucario, t5 | Psychic | End Turn | stands (3.9) | not a close call: stands |
| 06 v Lucario, t3 | Peck | Retreat:2 | kept (2.4) | **kept**: +0.172 at 2.1 |
| 09 v Hydreigon, t2 | Thunder Shock | End Turn | kept (2.2) | End Turn stands, 3.2 |
| 09 v Suicune, t4 | Lightning Accelerator | Retreat:2 | kept (2.6) | Retreat stands, 6.2 |
| 10 v Altaria, t3 (Q12) | Supernatural Feather | End Turn | kept (2.1) | **kept**: +0.094 at 1.1 |
| Shark v Blaziken, t2 | Gnaw | End Turn | kept (2.2) | End Turn stands, 4.0 |

**The 6 moves before an attack it touches:**
- **Back to km3's attack (4):**
  - 06 v Sceptile (deal 3), t2, Field Blower: +0.078 at 1.7 SE over 64 rounds.
  - 06 v Sceptile (deal 4), t4, Retreat:3: the best at 64 is End Turn, a skip at 2.4 SE, under the bar.
  - Shark v Altaria, t5, Misty: km3's Turbo Shark is the best over 64 rounds.
  - Shark v Sceptile, t2, the Stadium: +0.156 at 1.9 SE.
- **To another move (2):**
  - 01 v Vespiquen, t5: the Stadium becomes End Turn, a skip at just over 3.0 SE.
  - 06 v Lucario, t5: Copycat becomes Retreat:1, which attacks later (+0.125, just over 2.0 SE).

Every case's row and reasons are in `combined/combined_scan.txt`.

### Gate 2 (`combined/gate2/`, `combined/gate2_summary.*`)

**How.** As the first version's gate 2 (below), with `playout_tool_rule --extension --combined`: the 20 positions (the 8
continuation positions, and the 12 development positions as stored and at their Tool placement), 2 decision seeds each,
LAB, cap 12, z 2. kx3 decides with `_tools_zs3` at R = 16 and with `_tools_zs3_m64`. Times are wall times on the cloud's
4 cores, one decision at a time.

| set | decisions | close calls (extended to 64) | choice changed | time, R = 16 | time, `_m64` | ratio |
|---|---|---|---|---|---|---|
| the 8 continuation positions | 16 | 11 | 4 | 295 s | 713 s | 2.42 |
| the 12 development positions, as stored | 24 | 16 | 3 | 221 s | 652 s | 2.95 |
| the same, at the Tool placement | 24 | 10 | 2 | 119 s | 310 s | 2.60 |
| all | 64 | 37 | 9 | 636 s | 1,676 s | 2.64 |

- **The seconds** are from the container after its restart, which runs faster than before. Compare the ratios with the
  earlier runs, not the seconds.
- **Every extended decision ran to 64 rounds,** as (b) asks. A median of 4 candidates were extended (km3's move
  included), from 2 to 12. No round failed.
- **The median decision** went from 6.7 s to 19.4 s.
- **The earlier heads, the same 64 decisions:**
  - Before ties joined (76cd08f4): the same 37 decisions extended, 149 candidates in all against 169 now, 7 changes, x2.48.
  - With (c) (ec283c53): 121 candidates, 7 changes, x2.23. One choice differed: B-210952-t16 played Binding Snow.
- **The first version** extended 38 of the same decisions, changed 8 and took 2,994 s with `_m64`. Its R = 16 was plain;
  `_tools_zs3` already decides 23 of the 64 differently at R = 16, mostly through the Tool rule (21 Tool tie-breaks).
- **The skip bar plays no part here.** km3's move is an attack at only one of the 20 positions, as before.

**The 9 changes** (all with both reasons in `combined/gate2_summary.txt`):

| position | R = 16 (`_tools_zs3`) | with `_m64` |
|---|---|---|
| B-205731-t10 | km3's retreat kept (+0.125, 1 SE) | the turn's Water to the Active: +0.141 at 2.9 SE |
| B-210952-t16 | km3's bench of the Vulpix kept (Binding Snow +0.094, 1.9 SE) | the turn's Water to the Active, tied with km3's move for 16 rounds: +0.125 at 3.0 SE over 64 (with (c): Binding Snow) |
| B-205731-t02 (both seeds) | km3's Water to the Active kept (+0.188, 1.4 SE) | End Turn: +0.125 at 2.0 SE; +0.172 at 2.8 SE |
| dev04, as stored | km3's Poncho play, the best (Psychic ties it in all 16 rounds) | Psychic, which joined the extension: 0.641 against the Poncho's 0.578 over 64 rounds |
| dev04, Protective Poncho placement | the Tool tie-break plays the Poncho on Bench spot 3 (tied with km3's Poncho on the Active) | km3's Poncho on the Active kept: over 64 rounds it leads spot 3 by +0.062 (2.0 SE), beyond the noise |
| dev05, as stored | a retreat to Bench spot 3 (+0.438, 3.4 SE) | the retreat to spot 1: +0.391 at 4.6 SE |
| dev06, as stored | the turn's Darkness to Bench spot 1 (+0.250, 2.2 SE) | to spot 2: +0.125 at 2.0 SE |
| dev06, Heavy Helmet placement | the Helmet on Bench spot 1 (+0.250, 2.2 SE) | no move clears the bar (spot 1's lead is +0.031 over 64 rounds); the Tool tie-break plays the Helmet on spot 3, left at 16 rounds |

- **Against the first version:**
  - 4 of the 7 are its own changes, to the same moves: B-205731-t10, B-210952-t16, and B-205731-t02 at both seeds.
  - dev06's Helmet changed in the first version too, but to another move.
  - At dev05 the extension plays what the first version played.
  - The two dev04 changes come from ties joining.

### Gate 1 and the digests (`combined/checks/`, at 4e7d8ce5 in a separate worktree)

- **The suite:** 2,094 passed, 0 failed (2,092 at 76cd08f4, 2,091 at ec283c53).
  - The overtake test was added after this run, so it isn't in that count. It passes on its own, with the other tie
    tests (5 of 5).
- **km3's 240 games** (seed 7100): game for game equal to the official program's (digest 9dde28db2de6c9bc), and equal to
  the pinned record on every line but the wall time.
- **The harness self-checks** (`strength_selfcheck.txt`):
  - km3: 81b572198c04d5d1, unchanged.
  - `kx3_r2_c3_lab`: 3a2eb43bd9053639 twice, unchanged.
  - `kx3_r2_c3_lab_tools_zs3_m64`, the combined code in the `_lab` form: **8c1244aec5c8419d** (2 games, 21 turns,
    566 s on the faster container).
    - At ec283c53 and 76cd08f4 it was 2284c591ed14a534.
    - At R = 2 a tie with the best is common, so ties joining grows the extensions and changes the games.
- **The exact code** (`strength_selfcheck_exact.txt`): `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64`, 12 games,
  t-altaria v t-suicune, as `strength_prereg.py` runs it, at 4e7d8ce5:
  `selfcheck pilot=kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64 games=12 seat0_wins=9 seat1_wins=3 ties=0 turns=132
  digest=724e581a9c51711f`.
  - It took 13,445 s (3 h 44 min), 02:13 to 05:57 UTC on Oct 8, on the faster container. The same code without
    `_zs3_m64` took 2 h 8 min on the slower one.
  - Runs at ec283c53 and 76cd08f4 were stopped when their rule changed.

### The Tool tie-break and the extension

- **The order.** The extension decides first, among the extended candidates. Only when no move clears the bar does the
  Tool tie-break act, as before.
- **It looks at every candidate.** It plays km3's preferred placement with an effect wherever that is among the
  candidates, extended or not. So it can play a placement the extension left at 16 rounds. Its comparison with km3's
  move ("unless km3's leads it beyond the noise") is then on those 16 rounds.
- **At gate 2** the tie-break played the placement at 19 of the 64 decisions. At 1 of those, others were extended to 64
  rounds but the placement it played had only its 16. That was 3 before ties joined, and 4 with (c).
  - dev04's (seed 24,200,002,004) and dev11's (24,200,012,011) placements tie km3's move, so they now join.
  - At dev04, over 64 rounds km3's Poncho on the Active leads the placement beyond the noise, so km3's move is kept.
  - **dev06's Heavy Helmet** (seed 24,200,002,006) changed the choice. At R = 16 the Helmet on Bench spot 1 cleared the
    bar (+0.250, 2.2 SE). Over 64 rounds its lead fell to +0.031, so no move cleared the bar. The tie-break then played
    km3's preferred placement with an effect, the Helmet on spot 3, compared with km3's move on 16 rounds only (+0.000).

### Files (the fix round, `combined/`)

- `tests_before.log`: the tests against the code before the fix.
- `tests_before_drop_c.log`: the first addendum's tests against ec283c53, with (c).
- `tests_before_equal_join.log`: the second addendum's tests against 76cd08f4.
- `attack_scan_poolmeta_tools_zs3_m64.jsonl` and `attack_scan_poolmeta_tools_zs3.jsonl`: the 26 cases, with every
  candidate's rounds and the decision's time.
- `combined_scan.py` and `combined_scan.txt`: the 26 cases' table and reasons.
- `gate2/extension.jsonl` and `extension_stdout.txt`: the 64 decisions, both ways, at 4e7d8ce5.
- `gate2_summary.py` and `gate2_summary.txt`: the gate 2 table, the changes, the tie-breaks and every decision.
- `checks/`: gate 1 and the digests.

## The first version (7d3639d0)

As first built and measured. The fix round above changed (a) and (b); the numbers below are the first version's.

### In short

- **Close calls are common, and the extension changes about 1 decision in 8.**
  - At the gate positions (64 decisions: the 8 continuation positions, and the 12 development positions as stored and at
    their Tool placement, 2 seeds each), 38 had a close call. 8 choices changed.
  - In 7 of the 8, R = 16 had kept km3's move: the best move's lead was within the noise (6), or km3's move was narrowly
    best (1). The extra rounds made a switch clear.
  - In the 8th, R = 16 had switched on a lead of 2.2 standard errors that shrank to +0.031 over 64 rounds, so km3's move
    is kept.
- **The time cost is 2.4x overall:** 1,271 s → 2,994 s for the 64 decisions; the median decision went from 14.5 s to
  32.2 s.
  - Most close calls stay close: 32 of the 38 ran to 64 rounds.
  - By set: the continuation positions x2.0, the development positions as stored x2.8, at the Tool placement x2.5.
- **At quiz 4's 12 positions, kx3 deciding from the game's own randomness changes 4 choices.**
  - **Q11:** now Turbo Shark, Dustin's move. Over 64 rounds it scores 0.438, against 0.391 for Misty and 0.375 for the
    retreat kx3 played.
  - **Q07:** now the retreat into Stoutland, Dustin's move again: 0.625 against 0.594 for the Psychic line.
  - **Q04:** End Turn instead of the Energy.
  - **Q10:** the retreat instead of the Bench Energy.
  - The leads at Q07 and Q11 are still small after 64 rounds, so they lean Dustin's way rather than prove him right.
- **Where the cost goes.** Most of the extra time (1,499 of 1,716 s, 87%) and 7 of the 8 changes come from close calls
  that involve km3's move. That is, whether to switch at all.
  - The third kind (the best clears the bar, but another move is within the noise of it: Q11's kind) is 5 extensions,
    217 s, and 1 change.
  - A cheaper version could stop at the first kind. Not built.
- **Gates.**
  - Gate 1 passed: suite 2,087/0, km3 unchanged, and the self-checks unchanged with the parameter off.
  - Gate 2 is the gate-position run above.

### What was built

- **The parameter.** `_m<R_max>`, e.g. `kx3_r16_c12_z2_real_t0_poolmeta_m64`. R_max must exceed R, and it can't be
  combined with a time budget. Off, nothing changes.
- **What counts as a close call.** After the R rounds, take the best candidate. Every other within z standard errors of
  it (paired, over the same rounds) is a close call.
  - A pair equal in every round so far doesn't count: more rounds wouldn't separate them.
- **What happens on a close call.** Those candidates and km3's move play 16 more rounds.
  - **The same worlds a larger R would use:** round j's world and game seed come from the decision's own randomness and
    j.
  - **Re-checked after each block:** a candidate the best now leads beyond the noise drops out, keeping its rounds. The
    extension stops when no close call is left, or at R_max.
  - **The decision** is made among the candidates still in play, by the usual rule on their rounds.
- **The trace.**
  - Each candidate reports its rounds.
  - The reason ends with "close call: play-outs extended from 16 to 64 rounds for 4 candidates".
  - The `KX_TRACE` line carries each candidate's rounds when the parameter is on.
- **Code.** `close_call` and the extension in `evaluate`, `engine/src/players/playout_player.rs` (22958cd1).
- **Tests.** Three in `engine/tests/playout_close_calls_test.rs`, written first (`tests_before.log`, eea12479), on
  test-deck decisions with R = 4 and R_max = 20 or 68 (seeds 20,000,000,240-247):
  - the code;
  - a decision without a close call is the plain decision, field for field;
  - an extended candidate's play-outs are exactly those of a plain run with as many rounds: scores, differences and
    attack counts alike, which checks that the common random numbers really extend;
  - km3's move and the best are always extended;
  - blocks of 16, and determinism (replaced in the fix round: every extended candidate plays to R_max).
  - Of the 8 test decisions, 6 had a close call.

### The gate positions (`gate2/`, `summary.txt`)

**How it was run.** `playout_tool_rule --extension`:
- **The positions** are gate 2's 20: the 8 continuation positions, and the 12 development positions both as stored and
  advanced to their Tool placement. That makes 32 decision points.
- **Two decision seeds each:** the position's seed and that + 10,000, inside the registered block.
- **Each decision runs twice:** kx3 with R = 16 (LAB, cap 12, z 2) and with `_m64`.
- **Times** are wall times on the cloud's 4 cores, one decision at a time, with nothing else running.

| set | decisions | close calls (extended) | choice changed | time, R = 16 | time, `_m64` | ratio |
|---|---|---|---|---|---|---|
| the 8 continuation positions | 16 | 11 | 4 | 603 s | 1,188 s | 1.97 |
| the 12 development positions, as stored | 24 | 17 | 1 | 431 s | 1,207 s | 2.80 |
| the same, at the Tool placement | 24 | 10 | 3 | 237 s | 600 s | 2.53 |
| all | 64 | 38 | 8 | 1,271 s | 2,994 s | 2.36 |

**The extension's shape.**
- **Rounds played:** 32 of the 38 close calls ran to 64 rounds, 5 stopped at 32, and 1 at 48.
- **Candidates extended:** a median of 4 (km3's move included), from 2 to 12.
- **No round failed.**

**The 8 changes** (every one with both reasons is in `summary.txt`):

| position | R = 16 | `_m64` |
|---|---|---|
| B-205731-t10 | km3's retreat kept (+0.125, 1 SE) | the turn's Water to the Active: +0.141 at 2.9 SE over 64 rounds |
| B-210952-t16 | km3's bench of the Vulpix kept (+0.094, 1.9 SE) | the Water to the Active: +0.125 at 3.0 SE |
| B-205731-t02 (both seeds) | km3's Water to Carvanha kept (+0.188, 1.4 SE) | End Turn: +0.219 at 2.5 SE (32 rounds); +0.172 at 2.8 SE (64) |
| dev06, Heavy Helmet placement | a switch to the Bench (+0.250, 2.2 SE) | km3's placement kept: the lead is +0.031 over 64 rounds |
| dev09, Heavy Helmet placement | km3's Benched Indeedee ex kept (+0.062, 1 SE) | the Benched Wailmer (Retreat Cost 3, where the Helmet works): +0.078 at 2.3 SE |
| dev10, as stored | km3's Heavy Helmet kept (+0.062, 0.6 SE) | Copycat: +0.156 at 2.1 SE |
| dev10, Heavy Helmet placement | km3's Benched Indeedee ex (it was best) | the Active Wailord (Retreat Cost 4, where the Helmet works): +0.281 at 3.0 SE (32 rounds) |

**Where the cost goes,** by what the close call was after 16 rounds:

| close call | extended | changed | extra time |
|---|---|---|---|
| the best leads km3's move, but within the noise (R = 16 keeps km3's) | 18 | 6 | 958 s |
| km3's move is the best, another within the noise of it | 15 | 1 | 541 s |
| the best clears the bar, another within the noise of it (Q11's kind) | 5 | 1 | 217 s |

### Quiz 4's positions (`quiz/`)

**How.** kx3 decided again at each of the 12 positions from the game's own observation and randomness
(`trainer_habits positions --kx3`).
- **The code** is the development run's own (`kx3_r16_c12_z2_real_t0_poolmeta`, REALISTIC, the meta pool). It replays
  every logged move, so the R = 16 column is the game itself. Then again with `_m64`.
- **Q09** comes from the exam run and the rest from the development run.

| Q | km3's move | kx3 in the game (R = 16) | kx3 with `_m64` | rounds | time, R = 16 / `_m64` |
|---|---|---|---|---|---|
| Q01 | Darkness to the Active | Darkness to Bench 3 | the same | 48 | 46 s / 97 s |
| Q02 | Lucky Ice Pop | Darkness to Bench 1 | the same | 16 | 59 s / 54 s |
| Q03 | evolve the Active | retreat | the same | 16 | 7 s / 6 s |
| Q04 | Poké Ball | Water to the Active | **End Turn** | 64 | 58 s / 179 s |
| Q05 | Pokémon Center Lady | Water to Bench 2 | the same | 16 | 6 s / 6 s |
| Q06 | Watch Over | Psychic to Bench 2 | the same | 32 | 14 s / 23 s |
| Q07 | Psychic to the Benched Stoutland | Psychic to the Active, then attack | **retreat into Stoutland** (Dustin's) | 64 | 30 s / 70 s |
| Q08 | Watch Over | retreat | the same | 64 | 19 s / 51 s |
| Q09 | Watch Over | Poké Ball | the same | 64 | 27 s / 47 s |
| Q10 | Lightning to the Active | Lightning to Bench 3 | **retreat** | 64 | 14 s / 36 s |
| Q11 | bench the Vulpix | retreat into the Vulpix | **Turbo Shark** (Dustin's) | 64 | 18 s / 55 s |
| Q12 | Supernatural Feather | End Turn | the same | 16 | 10 s / 11 s |

- **Q11:** the four moves still in play after 64 rounds are Turbo Shark 0.438, Misty 0.391, the retreat 0.375, and km3's
  bench of the Vulpix 0.172.
  - Turbo Shark leads km3's move by 4.4 SE but Misty only slightly. That fits the continuation study's verdict that
    these three are about equal.
- **Q07:** the retreat into Stoutland scores 0.625 and the Psychic line 0.594: very close.
- **Q12** isn't helped: End Turn isn't a close call there (km3's attack trails beyond the noise at R = 16). The skip bar
  is what keeps that attack.
- The quiz positions cost x2.1 in all (308 s → 634 s), about like the gate positions.

### Gate 1 (`checks/`, at 461e78ab in a separate worktree)

- **The suite:** 2,087 passed, 0 failed.
- **km3's 240 games** (seed 7100): game for game equal to the official program's, and equal to the pinned record on
  every line but the wall time.
- **The harness self-checks.**
  - km3: 81b572198c04d5d1, unchanged.
  - `kx3_r2_c3_lab`: 3a2eb43bd9053639 twice, unchanged.
  - `kx3_r2_c3_lab_m20`: d0c281641a7db61f. It's a different digest, as it should be: with R = 2 almost every decision
    is a close call, and the extension changes some choices. The same winners and turns, 2 games. It is the reference
    for a build of this version with the parameter on.

### Files

- `tests_before.log`: the tests before the code.
- `gate2/extension.jsonl` and `extension_stdout.txt`: the 64 decisions, both ways.
- `quiz/`
  - `at.json` and `at_exam.json`: the positions.
  - `index_poolmeta.json` and `index_poolmeta_m64.json`: kx3's two decisions at each, with every candidate's rounds.
- `summary.py` and `summary.txt`: the tables, the changes and every decision.
- `checks/`: gate 1.
- `engine/examples/playout_tool_rule.rs`: the `--extension` mode. `engine/examples/trainer_habits.rs`: `positions --kx3`
  keeps the decision's time and each candidate's rounds.
