# Why C passes up Kingambit's knockout at 010837 t09 and t11 (the cloud, Oct 14)

Asked by Fable (direct route, Oct 14). Diagnosis only: no bot or engine change is committed. The positions are `READING.md`'s
010837 t09 and t11 (part 2, around line 104).
- C is the candidate, `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` on 9a0bc5ac.
- F is the frozen `kx3` on cd20a97a.

## Short answer

**At t11 C passes on its play-out scores alone.** None of the four suspects decides it.
- **Why:** C's play-outs say the knockout loses most games and passing wins all of them.
- **The numbers:**
  - km3's move is Retreat into Kingambit, then Overlord's Blade on the 30-HP Pichu.
  - In C's play-outs that line wins 33% (25-44% over the 12 seeds).
  - EndTurn and Hang Down win 100% in every seed.
  - After 16 play-outs the lead is 4.4 to 6.7 standard errors, against a bar of 2.
- **Why the knockout line loses:** Kingambit's count stays at 2, so the next Blade does 60 + 80 = 140. That doesn't knock out the
  180-HP Mega Kangaskhan ex that comes in, and the Kangaskhan, with Team Rocket's Raticate ex, wins the race.
- **Why passing wins:** the opponent knocks out Glimmet. That makes the count 3, so the Blade does 60 + 120 = 180, exactly the
  Kangaskhan's HP. The Kangaskhan is a Mega ex, worth 3 points, so that knockout wins the game.

**At t09 the close-call extension (`_m64`) tips it.**
- **The numbers:**
  - The same play-outs prefer passing only a little: Retreat 85%, EndTurn 100%.
  - After 16 play-outs the lead clears the bar of 2 in only a few seeds. Without `_m64`, C passes in 2 of 12 seeds; with it, in
    11 of 12.
  - The extension ran in 10 of the 12 seeds; the leads ended at 2.0 to 3.6 standard errors.
- **Why the passes:** at t09 the Blade doesn't knock anything out (140 on the 180-HP Kangaskhan). Passing leaves the 20-HP
  Glimmet to be knocked out, which brings the count to 3.

**F doesn't really choose to knock out.** F's play-outs score almost every move the same, at 94-100%, so F keeps km3's move by
default. F's play-out worlds don't contain this opponent's deck.

**C's world model is the closer one here, and the pass may be right.**
- **What he did:** he declined the Pichu knockout too (he attacked with Hang Down). Glimmet was knocked out, his count was 3 by t13,
  and he had 2 points by t15.
- **The doubt:** in C's play-outs the opponent walks its Mega Kangaskhan ex into the count-3 Blade every time. The real opponent did
  not: at t13 its Active is Raticate ex, with the Kangaskhan on the Bench. So C's 100% for passing is too optimistic. Whether passing
  is better than the knockout against a careful opponent is open; the gate below answers it.

## What was run

**Builds:** the laptop's cond2 recipe (`builds/builds_cond.txt`):
- main's `pg_pos.rs` (sha256 224888a8…) and `pgd_patch.py` (fb2d3e26…);
- on cd20a97a (F) and 9a0bc5ac (C), with `--locked`;
- built on the cloud, so the program hashes differ from the laptop's.

**Reproduction:** seeds 1-12, with the trace on (`_trace`) and off.
- Both builds reproduce the committed P8 runs (`workers/P8/runs_B`, `runs_C`) line for line, and the board summary is identical.
- The trace changes no move.

| Turn | F (frozen kx3) | C (candidate) |
|---|---|---|
| t09 | Retreat:1 > Attach > Overlord's Blade, 12 of 12 | EndTurn 11, the Blade line 1 |
| t11 | Retreat:1 > Heavy Helmet on Kingambit > Attach > Overlord's Blade (knocks out Pichu), 12 of 12 | EndTurn 12 of 12 |

### The decision, from the traces (the first decision of each seed, 12 seeds)

Mean play-out win share, with the lowest and highest seed in brackets.

| Move | C t11 | F t11 | C t09 | F t09 |
|---|---:|---:|---:|---:|
| Retreat(1), km3's move (to Kingambit) | 0.33 (0.25-0.44) | 0.96 (0.88-1.00) | 0.85 (0.63-0.98) | 1.00 |
| EndTurn | 1.00 | 0.98 (0.94-1.00) | 1.00 | 1.00 |
| Hang Down (his move) | 1.00 | 0.98 | 1.00 | 1.00 |
| Retreat(2), to Alolan Muk | 0.98 | 1.00 | 1.00 | 1.00 |
| Heavy Helmet first | 0.33 | 0.96 | - | - |

- **C t11:**
  - The trace's reason in every seed: "play-outs: +0.56 to +0.75 over km's move, 4.4 to 6.7 standard errors (threshold 2)".
  - The extension ran in 5 of 12 seeds (16 to 64 rounds for 4 candidates) and only widened the lead, to 9.6-13.7 SE.
  - EndTurn is played rather than Hang Down because the two tie and EndTurn comes first in the order offered.
- **C t09:** the same kind of switch; the extension ran in 10 of 12 seeds, and the leads ended at 2.0-3.6 SE.
- **F:** "km's move has the best play-out score", or "within the noise", in every seed at both turns.

### Ruling out each mechanism

- **The `_zs3` skip bar: not involved.**
  - It applies only when km3's move is itself an attack. Here km3's move is a retreat.
  - The bar used is z = 2 in every seed, and no reason mentions the skip bar.
- **The Tool tie-break (`_tools`): not involved.**
  - No move clears or misses the bar by a tie-break, and no reason mentions it.
  - In the play-outs the Tool rule changes nothing either: on C's build, kx3 with and without `_tools` gives the same scores and the
    same pass.
- **The `_m64` extension: decisive at t09 only.**
  - Without it, C (`..._tools_zs3`) passes at t09 in 2 of 12 seeds; the other 10 play the Blade line.
  - At t11 the lead already clears the bar after 16 play-outs, in every seed.
- **km3's forecast of Overlord's Blade: an undercount, but not the cause.**
  - The undercount: `estimated_attack_damage_ex` (`players/value_functions.rs`) has no case for the Blade's mechanic
    (`ExtraDamagePerOwnKnockoutThisGame`). So km3 reads the Blade as 60 whatever the count, as the Kangaskhan investigation found
    for Double-Punching Family.
  - The counterfactual: a scratch build of C with that case added (60 + 40 x the current count).
    - It changes nothing: C passes in 11 of 12 at t09 and 12 of 12 at t11.
    - The scores barely move: Retreat 0.31 and EndTurn 1.00 at t11.
    - km3's own proposal stays the retreat.
- **The cause: how the play-out worlds are built.** The code changed between cd20a97a and 9a0bc5ac; on C's build every kx3 code
  passes.

C's build with one setting changed at a time, t11, seeds 1-3:

| Code on C's build | t11 plan | Retreat(1) | EndTurn |
|---|---|---:|---:|
| `kx3` (wide pool) | EndTurn 3 of 3 | 0.25-0.56 | 1.00 |
| `kx3_r16_c12_z2_real_t0_poolmeta` | EndTurn 3 of 3 | 0.25-0.44 | 1.00 |
| `kx3_r16_c12_z2_real_t0_tools` | EndTurn 3 of 3 | 0.25-0.56 | 1.00 |
| `kx3_r16_c12_z2_real_t0_poolmeta_tools` | EndTurn 3 of 3 | 0.25-0.44 | 1.00 |

At t09 (seeds 1-12) on C's build: `..._tools_zs3` without `_m64` passes in 2 of 12; plain `kx3` in 4 of 12; the full C in 11 of 12.

### Why the worlds differ

The opponent's real list (Pichu, Mega Kangaskhan ex, Team Rocket's Rattata and Raticate ex) is in neither pool.

- **F:** it takes the closest meta list ("closest, no list consistent": Blaziken, Lucario, Suicune and others) as it is.
  - In a print-only probe of F's 16 play-outs of the Kingambit line, the opponent's hidden cards held no Raticate ex in any of them.
  - The Kingambit line won 16 of 16.
- **C:** it infers a list from the 3 nearest lists plus the cards seen ("inferred from 3 lists").
  - All 16 inferred lists hold 2 Team Rocket's Raticate ex: the evolution of the seen Rattata.
  - The opponent evolved Raticate ex in all 16 Kingambit play-outs, and won 10.
  - The real opponent had Raticate ex: it is its Active at t13.

**Two play-outs from C's print-only probe** (seed 1, t11; the probe prints each play-out's moves and does not change play):
- **The Kingambit line (a loss):**
  - t11: Heavy Helmet on Kingambit, then Blade: Pichu knocked out, 1-1.
  - t12: Mega Kangaskhan ex in; Raticate ex evolved and its Ability used; Double-Punching Family takes Kingambit to 60.
  - t13: Blade, 140 on the Kangaskhan (40 left).
  - t14: Kangaskhan knocks out Kingambit, 1-2; Alolan Muk promoted and hit for 40.
  - t16: Muk knocked out, 1-3, opponent wins.
- **The pass:**
  - t12: the opponent retreats Pichu into Mega Kangaskhan ex, evolves Raticate ex, and knocks out Glimmet with the first punch (0-2).
    The second punch takes Kingambit to 100.
  - t13: Blade at count 3 is 180 on the 180-HP Mega Kangaskhan ex: 3 points, he wins 3-2.
  - All 16 EndTurn play-outs end this way, at turn 13.

**The depth-4 check:** see the end of this file.

## The smallest change, and the gate (for the next pilot round's design; nothing is built)

**No change to C's decision rules is indicated.**
- At t11 C does what it was built to do: it follows a 4-7 standard-error lead in its play-outs.
- The world it plays in is better informed about this opponent than F's.
- A stricter bar wouldn't reverse it at t11: even a bar of 3, as the skip bar uses, is cleared in every seed (the smallest lead
  is 4.4 SE).
- The only rule-sensitive part is t09, where `_m64` turns a small lead into a pass. That is what `_m64` is for.

**What could be wrong is the play-out opponent.** km3 on the opponent's side walks its Mega ex into the count-3 Blade, which the real
opponent avoided. Two pieces, smallest first:
1. **The Blade in km3's damage estimate.**
   - What: one case in `estimated_attack_damage_ex` (60 + 40 x the count).
   - The counterfactual shows it changes neither decision here. It is still the correct reading of the card and costs one line.
   - It isn't enough on its own: the opponent's mistake is not seeing that its own knockout of Glimmet raises the count. An
     estimate that reads the current count can't see that.
2. **Seeing that its own knockout raises the count.**
   - What: where km3 values a line in which it Knocks Out one of the Kingambit player's Pokémon, it would count the Blade at the new
     count.
   - This is the change that would make the play-out opponent careful here. It touches km3, the pinned pilot, so it needs km3's full
     identity and floor chain.
   - I would not build it before the gate shows it matters.

**The gate that decides whether anything should change.** It needs no new bot code; it uses the continuation study already on
9a0bc5ac (`playout_continuation`, `PlayoutPlayer::continuation_study`).
- **What it compares:** at 010837 t09 and t11, paired over the same worlds, R = 128:
  - (a) km3's Kingambit line (Retreat > Blade);
  - (b) Hang Down / EndTurn.
- **With three play-out opponents:**
  - km3 as now;
  - km4 (one ply deeper);
  - the scratch Blade-aware estimate (piece 1).
- **The worlds:** C's inferred worlds, and a LAB world with his opponent's list rebuilt from the game's ledger, if the ledger shows
  enough of it.
- **Reading it:**
  - If (b) still leads (a) beyond 2 SE against the deeper or Blade-aware opponent, C's pass is a real find. km3's and F's knockout
    is the weaker move, nothing changes, and the position goes into the quiz list as one where the candidate beats km3.
  - If the lead collapses against a careful opponent, the change to pursue is piece 2, gated as any km3 change: identity on every
    deck without Kingambit, floor rows on the Kingambit deck.

**Exposure:** Kingambit (B3a 043) is in his Glimmora / Muk / Kingambit / Regigigas list (deck 01 in the strength harness) and in
these pause games. Mega Kangaskhan ex appears in no list under `decks/` (the Kangaskhan investigation's grep).

## Reproduce

All of it is in the scratch folder. Nothing is committed but this file.
- **The build:** as `builds/builds_cond.txt` (cond2).
- **Each run:**
  `pg_pos --positions rl/results/pause_games_new_2026-10-13/v2/positions_all.json --deck <each v2/decks/*.txt> --seeds 1,...,12 --bot <code>_trace --only KW-261013_010837000-t11`
  The `KX_TRACE` lines are on stderr.
- **The world probe:** a print-only `eprintln!` at the end of `play_out` (C) or `playout` (F), behind a `KG_PROBE` variable that
  only the probe build reads. It printed each play-out's first move, the opponent's sampled list, hand and deck, every move and the
  result. A clean rebuild of C reproduces the original program byte for byte (cd10c78a), so the probe was a separate binary.
- **The counterfactual:** the one case above, in a scratch copy of C's engine.

## The depth-4 check (pending)

- **The run:** C's code at search depth 4 (`kx4_r16_c12_z2_real_t0_poolmeta_tools_zs3`), with km4 on both sides of the play-outs, at
  t11, seeds 1-4.
- **The question:** does a deeper play-out opponent still walk its Mega Kangaskhan ex into the count-3 Blade?
- The result will be added here when the runs finish.
