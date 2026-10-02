# The play-out chooser, first prototype (the cloud, Oct 2)

Set by the Fable coordinator via Dustin, Oct 2. The design is `rl/results/planning_pilot_design_2026-10-02/DESIGN.md`,
sections 5 and 9 (the addendum's amendments win). Branch `claude/playout-pilot`, cut from main (551a348). Not merged.
- The official engine's behaviour and km3 are unchanged. The new code is only under `engine/src/players/`, plus its tests and
  an example.
- The laptop reviews it once, builds it beside the pinned engine, and runs the development comparison.
- No table game was played.

## What it does

The pilot's code is `kx<N>`, for example `kx3`. It is a new player on top of km<N>.

At each decision with two or more distinct moves:
1. It asks km<N> for its move, with the same per-decision randomness km<N> would get in the game, so km<N>'s move is exactly
   km<N>'s.
2. It takes every distinct legal move as a candidate, km<N>'s first, up to a cap.
3. It plays each candidate out to the end of the game R times, with km<N> on both sides.
4. Each play-out starts from a world sampled from what the pilot may see, so its own deck order, the opponent's hand and deck,
   and every coin are fresh each time.
5. It scores each candidate by its play-outs: a win is 1, a tie ½, a loss 0.
6. It plays the best-scoring move only if that move's lead over km<N>'s move is beyond the noise. Otherwise it plays km<N>'s.

**Common random numbers.** Play-out j of every candidate starts from the same sampled world and the same game seed. So the
coin stream is the same, and so are km<N>'s decision seeds, for as long as the games run alike. The comparison is paired:
for each candidate the pilot takes the difference d_j = score(candidate, j) − score(km's move, j) and its mean and standard
error (sample sd / √R). It switches only if the best candidate's mean d > z × SE. Ties go to km's move.

**The cap** (default 12).
- km's move is always kept.
- The others are ranked by km's own score of the position right after the move, on the first sampled world. The rest are
  dropped, and each drop is named in the trace with that score and the reason.
- Most decisions have fewer distinct moves than the cap, so nothing is dropped.

## What it can see, and what it can't

It sees only its `PlayerObservation`, exactly what km3 sees:
- its hand and board;
- the public board, discards, points and counts;
- its own deck as an unordered set.

It never reads the real game state. The opponent's hidden cards come from a list:
- **REALISTIC** (the default). For each play-out a list is drawn from a candidate pool: the 8 lists under
  `decks/screen/opponents` and the 8 under `decks/research`, embedded in `engine/src/players/playout_pool.rs` with each
  file's sha256.
  - The draw is uniform among the lists consistent with the opponent's cards seen so far, matched by name: in play, under
    an evolution, attached, discarded, their Stadium, or revealed.
  - With no list consistent, it takes the closest one, and the trace says so.
  - The unseen cards come from the drawn list.
  - The pool holds no brew and none of Dustin's lists.
- **LAB** (`_lab`, a laboratory condition, labelled as such in every output).
  - The opponent's exact 20-card list is used, but only when it is one of the pool's meta lists.
  - **The meta side is never handed a brew's exact list.** If the opponent's list is not a meta list, LAB falls back to
    REALISTIC and the label says so.
  - In the strength harness, with the pilot on Dustin's deck against a panel list, LAB gets the panel list.
  - In the pause-games positions the opponent is a filler list, so LAB acts as REALISTIC there.

Never seen in either mode: the opponent's hand, the order of either deck, and coins not yet flipped.

**The no-leak test** checks this. It takes a game state, swaps a card between the opponent's hand and deck, and reverses both
decks. The pilot's observation is then the same.
- The test checks that the pilot's whole evaluation (every candidate's play-out score and difference) and its move are
  identical, in both knowledge modes, directly and through `Game::from_state(...).play_tick()`.
- A pilot that read any hidden card would see different worlds and get different play-out scores.

## Parameters

All are in the code: `kx<depth>[_r<R>][_c<cap>][_z<z>][_lab|_real][_t<seconds>][_trace]`.

| part | meaning | default |
|---|---|---|
| `<depth>` | km<depth>: the move it proposes, and both sides in every play-out | (required; 3) |
| `_r<R>` | play-outs per candidate | 16 |
| `_c<cap>` | at most this many candidates (km's move always one of them) | 12 |
| `_z<z>` | the noise threshold, in standard errors of the paired difference | 2 |
| `_lab` / `_real` | knowledge mode | `_real` |
| `_t<seconds>` | time budget per decision: stop after the rounds finished in time (at least 2). Off by default, because it makes the result depend on the machine's speed | off |
| `_trace` | one `KX_TRACE` JSON line per decision on stderr | off |

- The first decision of each game prints `KX_PARAMS` on stderr: every parameter and the knowledge label. Every trace line
  carries the full code and the label too.
- **Deterministic given seeds.** All sampling and play-out seeds come from the decision's own randomness, the engine's
  per-decision search seed (game seed, seat, decision count). Play-outs run in parallel on rayon's threads but are collected
  in order. With no time budget, the same deals give the same games: tested.

**The trace** (`_trace`, or the smoke example's `--trace-out`). Each decision line has:
- turn and seat;
- the rounds run, and any failed;
- the milliseconds the decision took;
- km's move, the move chosen, whether they differ, and the reason;
- every candidate with its play-out score, its paired difference from km's move and that difference's standard error;
- the dropped moves with their reasons.

So any of the pilot's decisions can be shown with its evidence.

**Not covered; these keep km's move, and the trace says so:**
- a setup choice made after the opponent's hidden setup, since their placed cards can't be sampled yet. When the pilot sets
  up first, which is half the deals, its setup choices get play-outs;
- a decision with a hidden stack frame of the opponent's.

A play-out that panics (an engine bug in a sampled world) drops its whole round for every candidate, so the rest stay paired.
It is counted as `failed_rounds`.

One such bug was found and fixed while building. A sampled opening hand for an opponent still to set up could hold no Basic
Pokémon, which the engine's own deal never allows, and the opponent then had no legal move. The sampler now swaps a Basic into
such a hand, as the engine repairs a real one.

## What to expect to go wrong

- **km3 plays the later turns of every play-out.** A move that only pays off if the next several decisions follow it up can be
  undervalued: charging a Benched attacker that km3 then never promotes, or a sacrifice km3 then doesn't make. Its play-outs
  score no better than km3's own move, and the pilot keeps km3's move.
  - **How the trace shows it:** the plan's first move has a score about equal to km's move (a difference within the noise),
    and km's move is kept, at a position where Dustin or a human sees the plan.
  - The test is DESIGN.md's amendment 4: run the pilot's trace on a position built for a coordinated plan (charge a Benched
    attacker, keep a sacrificial Active, promote at the right time).
  - If the plan's first move doesn't stand out there, km3's later play inside the play-outs is hiding it. A cure would be a
    play-out policy that follows plans, or two-move candidates.
- **Noise.** At R = 16 the standard error of a paired difference is often 0.08-0.15 (8-15 points of win rate). So only large
  gains switch the move, and small real gains are lost. Raising R costs time in proportion.
- **Many candidates, one winner.** The best of up to 11 rivals is chosen after seeing their scores, so its lead is biased
  upwards. At z = 2 some switches are noise. With equal moves that costs nothing on average; with a truly worse move it
  costs. A higher z reduces it.
- **REALISTIC early in a game.** Few of the opponent's cards are seen, so the drawn lists are a mixture of all 16 meta lists.
  The play-outs then model an average opponent, not this one.
- **Speed.** Measured below. It is far slower than km3, and the harness and the position runner will need hours, not
  minutes.
- **The opening.** Setup choices made second keep km's move (above).

## Tests (`engine/tests/playout_pilot_test.rs`)

Written and committed before the player (a3612b71): `tests_before.log`, where they fail to compile with no `kx` code and no
`playout_player`. After the player, all 7 pass:

| test | what it checks |
|---|---|
| `the_code_parses_with_defaults_and_parameters_and_leaves_the_other_codes_alone` | the code's grammar, defaults and errors; `km3` and `k3` parse as before |
| `an_immediate_win_is_taken` | Mega Absol ex's Darkness Claw knocks out the opponent's only Pokémon: chosen in both modes, every play-out a win |
| `within_the_noise_km3s_move_is_kept` | at an unreachable threshold km3's move, exactly km3's own choice, is kept; at 0 the best score, km3's on a tie |
| `a_capped_candidate_list_keeps_km3s_move_and_names_the_drops` | at cap 2, km3's move is kept and every other distinct move is a named drop |
| `the_choice_cannot_depend_on_the_opponents_hand_or_either_decks_order` | the no-leak test (above), both modes, directly and through `Game` |
| `the_same_seeds_give_the_same_moves` | 12 ticks from a position, twice, the same moves |
| `a_whole_game_plays_to_the_end` | a whole game from `Game::new`, setup included, with no panic |
