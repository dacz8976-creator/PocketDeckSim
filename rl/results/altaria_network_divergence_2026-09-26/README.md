Decision this informs: what the Altaria detector network does better than kp3, named as moves, so the difference can become a B5 feature candidate (PRESET_READING step 3, `rl/runs/diag-altaria-lucario/PRESET_READING.md`). The readout found D = +15.75 ± 2.6 (`../altaria_network_readout/kp3_rows.txt`): the network pilots Altaria much better than kp3 against a kp3 Lucario.

# Where the Altaria network beats kp3 (B2c), prepared Sept 26

**Status:** built, smoke-tested on 5 deals outside the study, reviewed, rebuilt with the review's fixes and smoke-tested again on 3 more deals outside the study (sections "Smoke test" and "Review"). The full run is for the laptop session to queue (`bash run_b2c.sh`, about 10 to 15 minutes on 16 threads). Nothing below has been run on the study's 400 deals: no probe and no play-out of them has been seen (only replay-only sync checks of deals 0–19). Everything in "Design" and "Pre-set groupings" was written before any run, including the smoke; the review's changes to them (marked "review") were made before any run of the study too.

The method is the Lucario study's B2c (`../lucario_network_divergence_2026-09-25/README.md`), with kp3 in place of k3 everywhere: kp3 is the probe, and kp3 plays both decks in the play-outs.

## Design (fixed before any run)

**The games.**
- Row `net|kp3` of `../altaria_network_readout/kp3_rows_games.jsonl`: the Altaria network (`ckpt_1800k_avg_altaria.npz`, ec40355a1833) against kp3 piloting Lucario, on the run's bar deals, seed 18,200,000,000 + i, bar seats.
- Played on the diagnostic add-on (sha256 c048388b4bcf, built against the engine at c7cb688).
- **The study uses the first 400 deals** (i < 400), as the Lucario study did. Altaria sits in seat 0 in 200 of them. They hold 7,339 network decisions (18.3 per game, at most 39).

**The replay.**
- Each line records only the network's chosen index at each of its decisions. kp3's moves and the forced moves were never recorded, so they are re-played here the way the add-on played them (`rl/pdl_rl_env/src/lib.rs`, `RawEnv::reset`, `advance` and `step`):
  - `Game::new(seed)`, with kp3 in Lucario's seat and the add-on's never-used placeholder (R) in Altaria's;
  - a Lucario move is `play_tick`, so kp3 decides with the game's own decision seeds, exactly as in the add-on;
  - an Altaria position with one canonical move is applied as forced;
  - an Altaria position with two or more is a network decision, and the recorded index is applied.
- **A game is in sync only if all of these hold, or it is rejected and counted:**
  - every recorded index is offered;
  - the engine asks for exactly as many network decisions as were recorded;
  - the final winner, points and turn equal the record;
  - the per-game counts the readout stored with each game equal the counts recomputed here: attacking and benching on offered turns (readout.py's "habits"), and the bench size at each Mega Harmony. These depend on every network move and on the moves offered, so a replay that drifts fails here even if the result happens to match.
- **The sync check must pass on all 400 deals before any probe or play-out** (`run_b2c.sh` step 1).

**The engine.**
- It is main at 7fc6ccb, the official engine's commit (`rl/engine-2026-09-25/README.md`), plus one new file, `engine/examples/net_divergence_kp.rs`, added in a scratch copy. The repo's `engine/` is not touched.
- The network games ran at c7cb688. Between c7cb688 and 7fc6ccb, the engine changes only by adding the kq and kd players and by splitting helper functions out of `hooks/core.rs` for kd. kp3 replayed all 14,000 table games move for move on 7fc6ccb.
- The sync check on the 400 deals is the proof for these games. If it failed, the fallback is to build at c7cb688 (change `C` in both scripts).

**The kp3 probes.**
- At each network decision, kp3 is asked for its move from the same view: `Game::observation` of Altaria's seat, including what has been revealed so far.
- It is asked 3 times, under 3 search seeds. The first probe's move is "kp3's move". Whether all 3 agree is recorded.

**Differences.**
- The two moves are compared by card names, as in the Lucario tool. For example, a Basic onto either empty Bench slot, or Energy onto either of two identical Pokémon, is the same move.
- Changes from the Lucario tool, all so that different moves are not read as the same:
  - a Basic placed into the Active Spot is marked "(active)";
  - a promotion or switch names its Pokémon instead of its slot;
  - (review) Energy, a Tool, an evolution or an ability on the Active is marked "(active)" too. The list has two each of Swablu, Eevee, Espeon and Darkrai, so without the mark Energy onto the Active Swablu and onto a Benched Swablu read as the same move and were never played out, which is habit 4's own question; the same held for evolving the Active Eevee against a Benched one.
- What is still read as the same: a move onto one of two same-named **Benched** Pokémon against the other (Energy, a Tool, a retreat or promotion target), even if they differ in damage or Energy. Both are on the Bench, so no pre-set row's definition is affected; it is a small undercount of differences.
- As in the Lucario study, a difference is **order only** when the network plays kp3's move later in the same turn. Order-only positions are not played out.

**The play-outs.**
- At every other differing position, both moves are played out 8 times. Each play-out starts from the position (`Game::from_state`), makes the move, and kp3 then pilots both decks to the end.
- The network's move and kp3's move share each play-out's seed. That seed sets both the chance and both kp3s' search seeds, so each pair differs only by the first move.
- A position's value is the mean over its 8 pairs of Altaria's score (win 1, tie 0.5, loss 0) after the network's move, minus after kp3's move. In points: +10 means the network's move wins Altaria 10 more games in 100.

**Seeds.** i is the deal (seed − 18,200,000,000), and j is the network decision within the game (0 to 38 here).

| Use | Seeds | Range used |
|---|---|---|
| The games (replayed, not new) | 18,200,000,000 + i | the run's bar and confirmation deals, reused on purpose |
| kp3 probes | 21,160,000,000 + i × 100,000 + j × 10 + probe (probe 0–2) | 21,160,000,000 – 21,199,900,382 |
| Play-outs | 21,110,000,000 + i × 100,000 + j × 100 + r (r 0–7) | 21,110,000,000 – 21,149,903,807 |
| Smoke (deals i = 400–404, and the review's 405–407; the same formulas) | play-outs 21,150,000,000 + …, probes 21,200,000,000 + … | 21,150,000,000 – 21,150,799,999 and 21,200,000,000 – 21,200,799,999 (drawn: 21,150,000,000 – 21,150,701,107 and 21,200,000,000 – 21,200,700,152) |

- **The overlap check.** Checked by searching every file in the repo:
  - Nothing uses 21,108,000,000 to 21,299,999,999.
  - The highest block used below it is the panel calibration's, 21,107,000,000 – 21,107,199,999, with its smokes at 21,107,99x,xxx (`decks/screen/panel_ladder_2026-09-26/`).
  - The next block above it is the cloud's, 22,000,000,000 and up.
  - START_HERE's table and every `rl/results/*/README.md` were read for this.
- **Re-checked by the review** (Sept 26, 04:10): a search of every file in the repo except the `.jsonl` data for 21,1xx,xxx,xxx and 21,2xx,xxx,xxx in any spelling (commas, underscores, bare digits, "21.1B") found only this study, its agreement in section 8 of `docs/REVIEW_2026-09-24_direction.md`, and blocks at or below 21,107,199,999 (the B2e rows and card check at 21,106,xxx,xxx, which were being edited that night, the panel calibration at 21,107,xxx,xxx, the trainer audit at 21,104 to 21,105, the Skarmory check at 21,102). The laptop's A1 build ("21,002,000,000+" in the table) stays inside 21,002,xxx,xxx.
- **Proposed row for START_HERE's seed table** (not added here; that file is shared): "21,110,000,000 – 21,200,799,999: Altaria network B2c (Sept 26): play-outs 21,110,000,000 + 100,000 i + 100 j + r, kp3 probes 21,160,000,000 + 100,000 i + 10 j + p, i < 400; smoke deals 400–407 on the same formulas (21,150,000,000 – 21,150,799,999 and 21,200,000,000 – 21,200,799,999)".
- **Sure-knockout copies.** The "sure knockout" label below uses the knockout audit's own fixed analysis seeds, 0x5eed0000 + s. They label a move and play no game.

## Pre-set groupings (written before any run)

`analyze.py` prints the following. Its names and definitions are the ones below.

**Numbers per row:**
- positions (n);
- the mean of (network − kp3) in points;
- its 95% interval by position (the Lucario study's, treating positions as independent);
- its 95% interval by game (the same mean, with game-clustered standard errors). Positions from one game aren't independent, which is why the Lucario study called its ranges "a little too narrow";
- total/game (the row's summed difference per game).

**The rules for reading them:**
- **A row "clears zero"** when its interval by position excludes zero (the Lucario rule, so the two studies compare). It is marked "*". A row that clears by position but not by game is marked "* (position only)". Only tested rows get the mark (A's pairs and B's headlines), never the looks inside a headline. A row with one position, or positions from one game, prints "-" for the interval it can't have.
- (review, before any run of the study) **A tested row under 10 positions is printed but not marked** ("too few to mark"): play-out values come in steps of 12.5 points, so two positions of +12.5 each have an interval of zero width and would "clear zero". And **the pooled row of small move-kind pairs is not a tested row** and is never marked (before, it could be marked without being counted among the tested rows).
- **The overall line:** the mean over all played-out positions, with both intervals.
- **Also printed:**
  - the share of decisions where the moves are the same, differ only in order, or differ;
  - kp3's agreement with itself across its 3 probes;
  - how many played-out positions had revealed-card memory (see the caveats).

**A. Pairs of move kinds (network, kp3).** Exactly the Lucario study's `kind()`:
- energy / tool to the Active or the Bench;
- evolve / ability (Active or Bench);
- play item / supporter / tool / stadium;
- attack, or "attack (knocks out)" by printed damage against the Active's HP left;
- place, retreat, promote, end turn, and so on.

Pairs with 20 or more positions are listed. The rest are pooled into one row.

**B. The named habits.** Each headline row is printed whatever its size.
- **What the indented rows are:** looks inside a headline (split by names, groups of 10 or more, the rest as "other"). They are not tests.
- **Rows can overlap.** One position can be in several rows (a retreat to Darkrai against an attack is in 3c, 3d and 5a).
- **What "Knockout" means here:** the sure-knockout rule, the readout's primary rule. In each of 4 copies of the true game, under the knockout audit's seeds, the attack gains Altaria at least one point.

1. **Benching a Basic.** "Benches" means the move puts a Basic onto the Bench (a Place into slot 1–3). The audit saw the network bench on 66% of offered turns against kp3's 88%.
   - 1a: the network benches, kp3's move is not a bench placement (turn 1 on);
   - 1b: kp3 benches, the network's move is not (turn 1 on);
   - 1c, 1d: the same two at setup (turn 0).
   - Looks: by the Basic's name and the other side's move.
2. **Stampede without a knockout.** The audit saw the network pass Stampede without a knockout 62% of the time, against kp3's 0%.
   - 2a: kp3's move is Stampede without a sure knockout, and the network's is not Stampede;
   - 2b: the reverse.
   - Looks: by the other side's move.
3. **Sleep: which sleep attack, and who is Active.** The sleep attacks are Sing (Swablu), Hypnoblast (Espeon), Dark Slumber (Darkrai) and Sleepy Lullaby (Igglybuff). They are read at start from the list's card texts, as the attacks that put the opponent's Active to sleep, and the script stops if the list changes. Each of these Pokémon has one attack. So at one position the two moves can never be two different sleep attacks: which sleep attack gets used is decided by who is Active, so both are grouped here.
   - 3a: the network uses a sleep attack, kp3 doesn't;
   - 3b: kp3 uses one, the network doesn't.
     - Looks: by the attack (and its attacker) and the other move.
   - "Active after" a move means one of these:
     - the Pokémon a promotion, retreat or switch brings in;
     - the Basic placed into an empty Active Spot;
     - what the Active evolves into;
     - otherwise, the current Active.
   - 3c: the two moves leave different Pokémon Active;
   - 3d: Darkrai is Active after the network's move and not after kp3's;
   - 3e: Darkrai is Active after kp3's move and not after the network's.
     - Looks for 3c outside 3d and 3e: by the pair of names.
   - The audit saw Dark Slumber used on 144 turns by the network against 418 by kp3, with Darkrai kept on the Bench for Bad Dreams.
4. **Energy target.**
   - 4a: network to a Benched Pokémon, kp3 to the Active;
   - 4b: the reverse;
   - 4c: both to the Bench, different Pokémon;
   - 4d: network to the Bench, kp3 attaches no Energy;
   - 4e: kp3 to the Bench, the network attaches no Energy.
   - Looks: by the receiving Pokémon's names or the other move.
5. **Retreat vs attack.**
   - 5a: the network retreats, kp3 attacks;
   - 5b: the network attacks, kp3 retreats.
   - Looks: by the retreat target and the attack.

**How many rows are tested:** 18 named headline rows, plus the move-kind pairs with 20 or more positions (about 10 to 20). That is about 30 rows, so one or two of the smaller ones may clear zero by chance. `analyze.py` prints the exact count.

## What this can and can't show

- **It measures what kp3 would gain by making the network's move once, at that position, and then playing on as kp3.** It doesn't measure the network's whole plan: the network's own follow-up is never played. That matters most for habits that pay off only over several turns. Keeping Darkrai on the Bench for Bad Dreams and keeping a small Bench are two examples. kp3's continuation can undo such a plan, so they may read smaller than they are, or even negative.
- **The positions are the ones the network reaches** against kp3's Lucario. kp3's own games reach other positions.
- **One matchup** (Altaria v Lucario, Lucario piloted by kp3). Nothing here says how a habit plays in other matchups. That is for a registered B5 candidate on the whole table.
- **The noise:** 8 paired play-outs per position, and positions from one game are not independent. The by-game interval is printed for that reason.
- **The group sums won't add up to D's +15.75.** Moves interact, and the network's continuation isn't what is played out.
- **Revealed-card memory.** A play-out starts from the position with the revealed-card memory empty (`Game::from_state`, as in the Lucario study). This is the same for both moves. `analyze.py` counts the positions where either player had any.
- **The labels see the whole game.** "Sure knockout" is read from copies of the whole game, hidden cards included, as the knockout audit reads it. It is a label for grouping and never a move choice.
- **Where kp3 disagrees with itself** across the 3 probes, "kp3's move" is its first probe's choice.

## Files and how to run (in WSL)

- `net_divergence_kp.rs`: the tool (replay, sync check, probes, play-outs).
- `build_b2c.sh`: builds the tool in `/home/dacz8976/engine-b2c-7fc6ccb`. That is 7fc6ccb from `git archive` plus this one example file, built with `cargo build --release --locked -j 4` under `nice -n 19`.
  - It checks that the Altaria and Lucario deck files equal the run's `identity.json` hashes.
  - It waits while another cargo build is running.
  - It writes `identity.txt`: the binary's, the example's, the decks' and the games file's sha256.
  - (review) `REBUILD=1 bash build_b2c.sh` re-copies the example into the existing scratch folder and rebuilds only the example, after checking with `tar --compare` against `git archive 7fc6ccb` that the folder's `engine/` and `decks/` contents are still 7fc6ccb's.
- `run_b2c.sh`: the study, `bash run_b2c.sh`. Defaults: deals 0–399, 16 threads, `nice -n 10`; `THREADS` and `NICE` override them. The steps:
  1. The build check: the binary, (review) the example source in this folder and in the scratch copy, the decks and the games file must all be the ones `identity.txt` records. So an edit to `net_divergence_kp.rs` without a rebuild stops the run.
  2. The sync check on all 400 deals. It must print `SYNC PASS 400 of 400`, or nothing else runs.
  3. The probes and play-outs, writing `decisions.jsonl`, `net_divergence.txt`/`.log` and `timing.txt`.
  4. `analyze.py`, writing `analysis.txt`.
  - It never overwrites an existing `decisions.jsonl`.
- `SMOKE=1 bash run_b2c.sh`: the smoke, into `smoke/`. It uses deals 400–404, 2 threads and `nice -n 19`, plus a replay-only sync check of the study's deals 0–9. (review) `SMOKE_FIRST`, `SMOKE_N`, `SMOKE_OUT`, `SYNC_FIRST` and `SYNC_N` change the smoke's deals, folder and the replay-only range; smoke deals must be 400 or above.
- `analyze.py`: the grouping above. `python3 analyze.py [--file decisions.jsonl]`.
- `identity.txt`: the build's binary and input hashes, which `run_b2c.sh` checks.
- `smoke_test.log`, `smoke/` and `smoke_review/`: the smoke tests below. `smoke/net_divergence_kp_pre_review.rs` is the source of the binary that produced `smoke/` (sha256 719e105d…ee22).
- **`decisions.jsonl`**, one line per network decision:
  - both moves, and both moves' details (kind, target, names, printed and sure knockout, Active after);
  - the board around the decision;
  - the 3 kp3 probes, "differs" and "order_only";
  - at played-out positions, the 8 + 8 play-out scores and `net_minus_kp3`.

## Build

- Built Sept 26, 03:30 to 03:55 CDT, in `/home/dacz8976/engine-b2c-7fc6ccb`. Binary `net_divergence_kp_7fc6ccb`, sha256 0d7f85b6…d111. That binary made `smoke/`.
- It took 25 minutes of wall time, because the kpr mixed rows held all 16 threads at nice 0 until 03:52. That was 11 CPU-minutes.
- There were no warnings from the new example. The engine's own warnings are the usual unused-code ones.
- **Rebuilt by the review** at 04:14 CDT with `REBUILD=1` (the tree's contents checked equal to 7fc6ccb; only the example recompiled, 5 s; no warnings from the example). **The binary to run is now sha256 ca84aa7c…c4db**, from example source dbc62824…ad29 (`identity.txt` has the full hashes). It made `smoke_review/`.

## Smoke test (Sept 26, 03:58 CDT; `smoke_test.log`, outputs in `smoke/`)

This is the builder's smoke, on the pre-review binary (0d7f85b6…). The review's rebuild changes only move labels and the `went_first`/`own_turn` fields; a re-run of deals 401 and 403 on the rebuilt binary gave the same played-out positions and the same play-out values (section "Review").

- **Deals.** The smoke used deals 400–404 of the `net|kp3` row, outside the study's 400. So no study position was probed or played out. It ran on 2 threads at `nice -n 19` with the laptop otherwise idle (load under 1.5).
- **Seeds.** It used the same seed formulas, which put its seeds just past the study's blocks: probes from 21,200,000,000 to 21,200,400,112, play-outs from 21,150,000,000 to 21,150,400,807.
- **Sync check.**
  - 5 of 5 smoke deals are in sync.
  - A replay-only check of the study's deals 0–9 is also in sync, 10 of 10. It plays no probe and no play-out.
  - In sync means: every recorded index offered, the decision count, the winner, points and turn, and the per-game attacking/benching and Mega Harmony bench counts all equal.
- **The run.**
  - 5 games, 107 network decisions.
  - kp3 made the same move at 47, the difference was order only at 20, and 40 differed and were played out 8 + 8 times.
  - kp3 agreed with itself across 3 probes at 94% of decisions.
  - No played-out position had revealed-card memory.
  - `analyze.py` ran on the output and printed every row. On 5 games that is a code test and says nothing about the network.
- **Determinism.**
  - Deal 400 run alone gave byte-identical `decisions.jsonl` lines on 1 thread and on 2 threads.
  - Those lines are also identical to deal 400's lines in the 5-deal run.
  - So the result does not depend on the thread count or on which deals are run together.
- **The sync check catches corrupted records.** Three corrupted copies of deal 400's record were each rejected:
  - one network move changed: the game drifted, and decision 6's recorded index was no longer offered;
  - the recorded turn changed: the result doesn't match;
  - the recorded bench count changed: the counts don't match.
- **The records.**
  - The network's moves in `decisions.jsonl` equal the recorded indices, decision for decision (checked by `analyze.py`).
  - Every played-out position has 8 + 8 play-outs. Order-only and same-move positions were not played out.
  - The attack labels look right. Mega Harmony shows sure knockouts that its printed 40 misses (the bench bonus). Hypnoblast knocks out a 60-HP Riolu through Weakness (40 + 20).

## Review (Sept 26, 04:05 to 04:30 CDT)

An adversarial review of the files above, before any run of the study. What was checked, and what changed.

- **The replay is the add-on's.** `rl/pdl_rl_env/src/lib.rs` (`reset`, `advance`, `step`): `Game::new(players, seed)` with the bot code in Lucario's seat and R in the network's; a bot seat is `play_tick`; the network's seat is canonicalised, one move applied as forced, two or more returned to the caller, and `step` applies the chosen index. The tool does the same, in the same order. kp3_rows.py's `play` reads the position with `readout.look` (it plays nothing) and records only the indices. The recomputed counts are readout.py's `tally` (attack/Place offered and chosen per turn, turn 0 excluded; bench size at Mega Harmony). A failed replay is rejected, printed and counted, never skipped: the run stops at step 1 unless all 400 pass, and at step 2 unless "0 rejected".
- **kp3 everywhere.** `PlayerCode::KP { max_depth: 3 }` is what `parse_player_code("kp3")` gives (the add-on's Lucario bot). The probe calls the same `decision_fn` with the same observation (`Game::observation` = what `play_tick` builds) and the same canonical move list; the play-outs create kp3 for both seats with each seat's own deck. Nothing in the tool uses k3.
- **Paired seeds.** Both moves of a play-out get the same `Game::from_state` seed, which sets both the chance stream and both players' search seeds.
- **Seeds are free** (the re-check is in "Seeds").
- **Pre-set groupings** match the README's text and the agreement in section 8. Four fixes:
  1. **(Rust) Active against Bench of the same name.** Labels now mark Energy, Tools, evolutions and abilities on the Active "(active)" ("Differences"). Before, such pairs were read as the same move and not played out. This is habit 4's own comparison. Neither smoke had such a position (0 of 107 and 0 of 37 decisions), so on the study it should be a small number, but it falls in rows the study pre-set to look at (4a, 4b, and 3c for evolutions).
  2. **(Rust) `went_first`** was wrong at setup (turn 0) in one smoke game (deal 401 read False at turn 0, True after). It is now read once per game, at the first state of turn 1. It and `own_turn` are descriptive; analyze.py uses neither.
  3. **(analyze.py) Marking rule:** a tested row under 10 positions is not marked, and the pooled row is not a tested row ("Pre-set groupings").
  4. **(analyze.py)** The overall line printed "Â±" (a double-encoded "±"); fixed.
- **Scripts.** `build_b2c.sh` gained `REBUILD=1`; `run_b2c.sh` now also checks the example source against `identity.txt` and takes smoke overrides ("Files and how to run").
- **Regression of the rebuild** (deals 401 and 403, 2 threads, nice 19; outputs not kept): same decisions, same played-out positions, the same 8 + 8 values at each, and only `net_move`/`kp3_move` text ("(active)") and deal 401's turn-0 `went_first` changed.
- **The review's smoke** (04:15 CDT, `smoke_review/`, rebuilt binary ca84aa7c…, `SMOKE=1 SMOKE_FIRST=405 SMOKE_N=3 SMOKE_OUT=smoke_review SYNC_FIRST=10 SYNC_N=10 bash run_b2c.sh`; load 0.6):
  - sync: 3 of 3 smoke deals (405–407) and 10 of 10 study deals 10–19 (replay only);
  - 37 network decisions: same move 19, order only 5, differs 13, each played out 8 + 8; kp3 agreed with itself at 92%; no revealed-card memory;
  - the network's moves equal the record decision for decision; order-only and same-move positions were not played out; `went_first` is one value per game;
  - seeds drawn: probes 21,200,500,000 – 21,200,700,152, play-outs 21,150,500,100 – 21,150,701,107;
  - 21.7 s wall, 40.9 s user CPU on 2 threads.
- **Not changed, stated:** the study's engine is 7fc6ccb, not the add-on's c7cb688 (c7cb688 is its ancestor; the step-1 sync check is the proof for these games, and all 28 deals tried so far pass: 0–19 and 400–407). The replay can't check each recorded index against the move the network saw, because the record holds only the index; the per-game counts and the result are the check, and a single changed index was caught in the builder's test.

## Time estimate for the full run

- **The smokes' cost:** 37 s wall and 74 s of CPU on 2 threads for 107 decisions and 40 played-out positions (the builder's), and 22 s wall and 41 s of CPU for 37 decisions and 13 positions (the review's). Together that is about 2.2 CPU-seconds per played-out position, and 37% of decisions played out.
- **Scaled to the study:** 7,339 decisions, so about 2,700 positions and about 5,900 CPU-seconds, or about 50 minutes on 2 threads. The review's labels may add a few positions (none in either smoke).
- **On 16 threads:** the laptop's Ryzen 7 7730U has 8 cores with 2 threads each and a lower all-core clock. So 16 threads should give 3.5 to 5 times the throughput of 2. **Expect about 10 to 15 minutes** with the laptop otherwise idle.
- **Allow up to about 25 minutes.** The smokes' 8 deals are a small sample: 37% of their decisions differed, against 42% in the Lucario study, and the cost per position differed by 1.7 times between the two smokes.
- For comparison, the Lucario study (6,368 decisions, 2,656 played-out positions, k3) took 4,130 s on 2 threads.
- The sync check on 400 deals takes seconds (10 deals: under 1 s on 2 threads).
