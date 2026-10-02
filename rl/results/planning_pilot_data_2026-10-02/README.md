# The planning pilot's data (the cloud, Oct 2)

Set by the Fable coordinator via Dustin, Oct 2, on the new branch `claude/planning-pilot-data`, cut from main (a9b8ce5):
- The project now builds a pilot for playing strength on an experimental branch.
- The official engine (`rl/engine-2026-10-02`, main-8626a35) and km3 stay the reference.
- This job builds the data pipeline any fitted evaluation needs. It changes nothing in how the official engine or km3 plays.

This README was written and pushed before any game was played. The results sections are added after the run.

## What is built

**`engine/examples/pilot_data.rs`**, a scratch example like `legality_scan`.
- It plays self-play games with km3 on both sides.
- It writes one row for every decision point of each side's own turn: a move the side chooses among two or more in its own
  turn (`current_player` is the mover). The setup choices of turn 0 (the Active and Bench) are also written, marked
  `setup = 1`: km evaluates them with its setup terms only, since the opponent's board is hidden then.
- Each row holds:
  - the deal: pairing, game index i, seed, tick (`play_tick` number, from 0, as `legality_scan` and the traces count it), so
    any row can be replayed;
  - the position's features from the mover's view (below);
  - the move chosen (its kind) and how many moves were offered;
  - the game's result for the mover (win, loss or tie), its final points and the opponent's, and the game's length.
- The games are `legality_scan`'s.
  - Same seat rule: the first-named list sits in seat 0 when i is even, in seat 1 when i is odd.
  - Same players (`create_players` with km3 twice) and same `Game::new(players, seed)`.
  - The example only reads states between ticks.
  - A check plays the same deals through `legality_scan` built from main (untouched) and compares the move fingerprints.
- Output: one gzipped TSV per run, with a header line of column names.

**`engine/src/players/pilot_features.rs`**, a child module of `value_functions.rs`.
- It is declared there by one `#[path]` line, so it can read km's private terms.
- It computes the features. Nothing calls it except the example, so no player's evaluation changes.
- On every row the example checks that km's terms, weighted as km weights them, add up to
  `public_clock_effect_km_value_function` for that side.

## The features (from the mover's view; `my_` the mover, `opp_` the opponent)

**km's terms, each separately.** These are `extract_features` for both sides with km's flags (`EvalFeatures::KM`), as
`parametric_value_function_ex6` computes them for km3:
- points, Pokémon value, hand size, deck size;
- the Active's retreat cost, Active online score, Active safety, Active Tool;
- is winner;
- turns until the opponent wins: kt's clock with km's Stadium bonus;
- online Pokémon count and Energy distance to online (both weighted 0 in km, and kept anyway);
- discard size;
- the discard-Energy credit (part F).

Also, as columns:
- `km_value`, km's total for the mover;
- at setup, the opening-Active term (koa's switch A).

**km's clock, in parts** (kt's clock with km's flags), for the clock on each side's Pokémon:
- the turns before the threat's first hit;
- the Active victim's remaining HP;
- the first hit's damage and every later hit's;
- the turns for the benched victims;
- the threat's slot.

So "the damage the opponent's clock says the Active takes" is `my_clock_first_hit` and `my_clock_later_hit`.

**The candidates the design will want**, for both sides.
- Each Benched slot 1-3:
  - present, remaining HP, Energy attached;
  - missing Energy to its cheapest and its priciest attack;
  - the same for what it evolves into, by the evolution's attacks: the highest evolutions in the owner's deck and hand
    for the mover; for the opponent, whose deck is hidden, the highest evolutions in the card pool;
  - its best attack's damage, its own or its evolution's.
- Over the Bench:
  - count;
  - total Energy;
  - the fewest Energy missing to any attack (own or by evolution);
  - how many are ready to attack.
  - The **likely attacker** on the Bench: the Benched Pokémon whose best attack (own or by evolution) does the most damage.
    Its Energy (`bench_attacker_energy`), its missing Energy to that attack, and that damage.
  - The likely attacker is chosen from the position alone, with no hindsight. Its Energy is the "Bench Energy on the eventual
    attacker" the baseline's sign question reads.
- The Active:
  - Energy;
  - missing Energy to its cheapest and priciest attack, and by evolution;
  - its best attack's damage;
  - whether it can attack this turn (the mover's) or the coming turn (the opponent's): the fewest Energy missing is no more
    than the Energy still attachable then, and no Special Condition stops it;
  - whether it can by the turn after;
  - the points at risk if it is Knocked Out (1, 2 for ex, 3 for Mega ex).
- Context: turn number, went first, Energy still attachable this turn, the mover's points and the opponent's.

## The pool (`pool.tsv`), fixed before any game

There are 16 lists, every pairing between two of them (120 pairings), with the seat alternating by game, so each list plays
first and second.
- **The 8 panel lists** (`decks/screen/opponents/t-*.txt`).
- **Early aggression** (attackers that need nothing or one Stage 1 step, at 1-2 Energy):
  - Dustin's 04 (Hoopa ex, Darkrai ex, Absol: Basics only);
  - Dustin's 09 (Heliolisk and Mega Manectric ex, Stage 1 at 1-2 Energy);
  - brew-02 (Maushold, Stage 1 at 1 Energy for 60);
  - brew-09 (Mega Sableye ex, a Basic at 2 Energy for 80).
- **Slow setup** (Stage 2 or 3-4 Energy attackers):
  - Dustin's 08 (Garchomp, Stage 2 at 3 Energy);
  - Dustin's 11 (Haxorus, Stage 2, and Archaludon at 4 Energy);
  - brew-10 (Giratina ex at 4 Energy);
  - Dustin's 01 (Kingambit, Stage 2; Muk and Regigigas at 3 Energy).

The classes are read from the lists. The run checks them: the results give each list's mean turn of its first attack and
its mean game length.

## The held-out group (`HELD_OUT.txt`), fixed before any game

No development data is generated on these lists, on either side of a game. They are held out by family, so no list in the
pool shares its main attacker with one of them:
- **Sharpedo** (early): l-sharpedo, draft A and its Wallace version.
- **Raticate** (early): Dustin's 13, 14 and 15.
- **Entei** (early; the Charizard Y list is slow): brew-08, draft D, l-charizardy and its two gauntlet swaps.
- **Hatterene** (slow): brew-05, brew-05b, draft C.
- **Wailord** (slow): Dustin's 03, draft B.
- **Skarmory stall** (slow): Dustin's 07.
- **Scoreboard v3's two gauntlet lists:** g-dragonair_mega_rayquaza and g-mega_altaria_greninja.

So all four of Dustin's current drafts are held out.

Two overlaps remain:
- g-mega_altaria_greninja shares Mega Altaria ex with the panel's t-altaria. The panel is in the pool by instruction.
- g-dragonair_mega_rayquaza shares a Dragonair line with Dustin's 11.

The panel lists are close variants of the table's research lists (`decks/research/`). So the table's 28 cells are not a
held-out test of a pilot developed on this pool.

## Seeds, size, and the held-out games of the fit

- **Seeds:** 24,000,000,000 + pairing × 100,000 + i. This is a new block above every range in START_HERE's table; its row is
  added there on this branch.
  - The timing check, which sizes the run, uses 24,099,000,000 + pairing × 1,000 + i, outside the dataset.
  - The fingerprint check reuses dataset deals.
- **Size:** about an hour on two threads (`RAYON_NUM_THREADS=2`). The same number of games is played in each pairing, set
  from the timing check before the run and written here before it starts.
  - **Set before the run:** the timing check (`timing/timing_games.jsonl`) played 18 games (2 in each of pairings 0, 15, 30,
    45, 60, 75, 90, 105 and 119). On two threads it took 6.6 s: 2.7 games/s and 142 rows/s, about 52 rows a game, and km's
    check matched on all 941 rows.
  - So the run is **80 games in every pairing (i < 80), 9,600 games**, about an hour at that rate.
  - Command: `RAYON_NUM_THREADS=2 pilot_data --pool rl/results/planning_pilot_data_2026-10-02/pool.tsv --root .
    --seed-base 24000000000 --stride 100000 --games 80 --rows rows.tsv --games-out games.jsonl`, from the repository root.
  - **Added during the first pass (19:53 UTC, from its timing only, before any result was read):** the first pairings ran
    at about 5 games/s, so the 9,600 games take about 33 minutes, half the hour asked. A second pass follows at once:
    `--first-game 80 --games 80` (i = 80 to 159 in every pairing, the same seed formula). The two passes together are the
    dataset: **19,200 games, 160 a pairing**.
- **The baseline fit's held-out games:** every game with i % 5 == 4, all of its rows together (about 20%). The fit uses the
  battle rows only (`setup = 0`) and leaves out ties.
- **The fit is a sanity check only:** a plain logistic regression of the win on the features, on standardised features with a
  small ridge. It reports:
  - which features carry weight;
  - whether the fitted sign of `my_bench_attacker_energy` is positive;
  - the held-out log loss and accuracy against always predicting the base rate.

  No pilot changes and no claim is made from it.

## Where it stopped (Oct 2, 20:45 UTC)

The coordinator switched the cloud to the play-out pilot (Fable via Dustin, Oct 2): "commit what you have of it, note where it
stopped". So:
- **The first pass finished:** 9,600 games, 80 in every pairing (i < 80), the whole pool. Its rows and games are here.
- **The second pass (i = 80-159) was cancelled before it started.** The dataset is the first pass only, about 50 minutes of
  generation, not the hour planned.
- **One conflict for whoever picks this up.** The design's locked final-exam list (`rl/strength/heldout.json`, 8521b291), fixed
  after this pool, holds out Dustin's 04, 08 and 11. All three are in this pool. Rows with those lists on either side must be
  dropped before this data is used for development.

## Results of the first pass

Files:
- `data/rows_pass1.tsv.gz`: 467,146 rows, gzipped TSV with a header.
- `data/games_pass1.jsonl`: one line a game.
- `data/run_pass1_stdout.txt`: per-pairing times.
- `summary.txt` and `feature_stats.tsv`: from `summarize.py`.
- `baseline_fit.txt`: from `baseline_fit.py`.
- `identity/`: the fingerprint check.

The program was built from 9efbb0f, sha256 82ba2129…c3ad.

**The games are km3's own.** `legality_scan`, built from main (a9b8ce5, an untouched engine), played 80 of the same deals: 16
in each of pairings 0, 45, 92, 104 and 119. All 80 move fingerprints are equal to this example's (`identity/`).

**Size and speed.**
- 9,600 games, 467,146 rows (48.7 a game), in 3,022 s on two threads: **3.18 games/s and 155 rows/s**, about 1.6 games/s per
  thread.
- My own builds ran beside it on the other two cores at times, so treat that as a floor.
- km's check (its terms add up to km's value) matched on all 467,146 rows.
- The rows: 449,614 in the mover's own turn, 17,532 in the opponent's turn (promotions and the like), and 15,184 setup
  choices.
- The rows by kind of move: Play 126,086, Attach 81,547, Attack 69,098, Place 64,613, Evolve 24,321, Promote 15,737,
  Retreat 15,511, EndTurn 15,120, and the rest.
- At this rate a full run of 100,000 games is about 9 hours on two threads (about 5 million rows, about 160 MB gzipped).

**Outcome balance.**
- Seat 0 won 4,750, seat 1 won 4,832, and 18 games were ties.
- The player going first won 48.0% of decided games.
- Rows by the mover's result: 236,848 wins, 229,260 losses, 1,038 ties.
- Mean game length 10.3 turns (1 to 27).

**The class check.** Mean turn of the first attack: early 3.81, panel 3.22, slow 4.68. The slow lists do attack later, but
the classes hold only in part:
- brew-09 (5.15) and brew-02 (4.48) attack late for "early" lists;
- Dustin's 08 attacks early (2.79) for a "slow" one.

Per list, in `summary.txt`.

**The features.** 139, ranges in `feature_stats.tsv`. Only two are constant: `my_is_winner` and `opp_is_winner`, which are 0 at
every decision point by construction. Nothing else is dead.

**The baseline fit** (`baseline_fit.txt`; a sanity check only, no claim).
- 450,955 battle rows without ties. The held-out games (i % 5 == 4) have 90,017 rows.
- Held-out log loss / accuracy:

  | model | log loss | accuracy |
  |---|---|---|
  | base rate | 0.693 | 50.8% |
  | km's value alone | 0.631 | 61.1% |
  | all 134 features | 0.525 | 72.5% |

- The weightiest features (standardised):
  - the mover's Energy distance to online (−1.35);
  - the opponent's Pokémon value (−1.00);
  - the deck sizes (mine −0.97, the opponent's +0.93);
  - the opponent's evolution readiness;
  - the opponent's clock (the first hit on the opponent's Active, +0.75).
- **The fitted sign of `my_bench_attacker_energy` (Energy on the likely benched attacker) is negative:**
  - −0.142 in the full model, rank 65 of 134;
  - negative in all five folds (−0.162 to −0.129);
  - negative in a small model of km's terms and the two Bench Energy features (−0.054).
- `my_bench_energy_total` is +0.027 in the full model and −0.048 in the small one.
- This is a correlation in km3's own games, not a value. km3 puts Energy on the Bench mostly when its Active can't use it,
  which is itself a losing sign, and the features overlap heavily. It doesn't say that Bench Energy is bad. It says that a
  linear fit on km3 self-play can't answer that question.
